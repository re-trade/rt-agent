import base64
from io import BytesIO
from collections import Counter
from PIL import Image
import torch
from qdrant_client.http.models import Distance, VectorParams
from transformers import CLIPProcessor, CLIPModel
from qdrant_client import QdrantClient
from app.models.request_models import SearchResults, SimilarityResult
from app.config import settings
from app.services.openai_service import openai_service
from fastapi import UploadFile


def make_thumbnail_data_uri(image: Image.Image, size: int = 64) -> str:
    img = image.convert("RGB")
    img.thumbnail((size, size), Image.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


class SimilarityService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", use_fast=True)
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.model.eval()

        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.client = QdrantClient(url=settings.QDRANT_URL, prefer_grpc=True)
        self.ensure_collection_exists()

    def get_image_embedding(self, image: Image.Image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            feats = self.model.get_image_features(**inputs)
        feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
        return feats[0].cpu().numpy().tolist()

    async def search_similar(self, image: Image.Image, limit: int = 10, similarity_threshold: float = 0.9) -> SearchResults:
        emb = self.get_image_embedding(image)

        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=emb,
            limit=limit,
            score_threshold=0.0
        )

        thumbnail = make_thumbnail_data_uri(image)

        if not hits or all(hit.score < similarity_threshold for hit in hits):
            try:
                buffer = BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)
                file = UploadFile(
                    filename="image.jpg",
                    file=buffer,
                    content_type="image/jpeg"
                )
                analysis = await openai_service.analyze_image(file)

                return SearchResults(
                    results=[
                        SimilarityResult(
                            label="AI Analysis: " + analysis,
                            confidence=100.0,
                            score=None
                        )
                    ],
                    thumbnail=thumbnail,
                    fallback_used=True
                )
            except Exception as e:
                return SearchResults(results=[], thumbnail=thumbnail, fallback_used=True)

        labels = [hit.payload.get("label", "unknown") for hit in hits]
        scores = [hit.score for hit in hits]
        counter = Counter(labels)
        total = len(hits)

        results = [
            SimilarityResult(
                label=lbl,
                confidence=round((cnt / total) * 100, 2),
                score=round(sum(scores[i] for i, l in enumerate(labels) if l == lbl) / cnt, 3)
            )
            for lbl, cnt in counter.most_common()
        ]

        return SearchResults(results=results, thumbnail=thumbnail, fallback_used=False)

    def health_check(self):
        try:
            collection_info = self.client.get_collection(self.collection_name)
            config = collection_info.config

            if hasattr(config, "vector_config"):
                vector_sizes = {
                    name: vc.size for name, vc in config.vector_config.items()
                }
            elif hasattr(config, "params") and hasattr(config.params, "vector_size"):
                vector_sizes = {"default": config.params.vector_size}
            else:
                vector_sizes = "unknown"

            return {
                "status": "healthy",
                "qdrant": True,
                "collection": self.collection_name,
                "vectors": vector_sizes
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def ensure_collection_exists(self):
        existing_collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name in existing_collections:
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=512,
                distance=Distance.COSINE
            )
        )
        print(f"Collection '{self.collection_name}' created with vector size 512 (CLIP output).")

similarity_service = SimilarityService()
