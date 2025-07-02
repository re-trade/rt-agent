from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
from io import BytesIO
from app.services.similarity_service import similarity_service
from app.services.openai_service import openai_service

router = APIRouter()

def process_image(image_file) -> Image.Image:
    try:
        return Image.open(BytesIO(image_file)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

@router.post("/search")
async def search_similar_images(
    file: UploadFile = File(...),
    limit: int = 10,
    similarity_threshold: float = 0.5
):
    
    contents = await file.read()
    image = process_image(contents)

    try:
        results = await similarity_service.search_similar(image, limit, similarity_threshold)

        if not results.fallback_used:
            filtered_results = [
                result for result in results.results
                if result.score is not None and result.score >= similarity_threshold
            ]

            if not filtered_results:
                results.fallback_used = True

            results.results = filtered_results

        if results.fallback_used:
            await file.seek(0)
            results.extra_result = await openai_service.analyze_image(file)
        return results

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error searching similar images: {str(e)}")

@router.get("/similarity-health")
async def similarity_health_check():
    return similarity_service.health_check()