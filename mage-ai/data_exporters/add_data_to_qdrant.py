import os
import numpy as np
from pandas import DataFrame
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from mage_ai.data_preparation.decorators import data_exporter
from load_helpers.qdrant_helper import get_qdrant_config_from_env

@data_exporter
def load_data_to_qdrant(product_vectors: DataFrame, **kwargs) -> None:
    """
    Upsert vector sản phẩm vào QdrantDB từ DataFrame đầu vào.
    """
    config = get_qdrant_config_from_env()
    qdrant_host = config['qdrant_host']
    qdrant_port = config['qdrant_port']
    collection_name = config['collection_name']
    vector_size = config['vector_size']
    distance_metric = kwargs.get("distance_metric", Distance.COSINE)

    print(f"📦 Qdrant Config: host={qdrant_host}, port={qdrant_port}, collection={collection_name}, size={vector_size}")

    client = QdrantClient(host=qdrant_host, port=qdrant_port)
    
    try:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance_metric)
        )
        print(f"✅ Collection '{collection_name}' is ready.")
    except Exception as e:
        print(f"❌ Error creating collection: {str(e)}")
        return
    points = []
    try:
        for _, row in product_vectors.iterrows():
            vector = row["vector"]
            if isinstance(vector, np.ndarray):
                vector = vector.tolist()

            point = PointStruct(
                id=row["product_id"],
                vector=vector,
                payload={
                    "product_id": row["product_id"],
                    "combined_features": row["combined_features"]
                }
            )
            points.append(point)
    except Exception as e:
        print(f"❌ Error preparing points: {str(e)}")
        return
    batch_size = 1000
    try:
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            client.upsert(collection_name=collection_name, points=batch)
            print(f"✅ Inserted batch {i // batch_size + 1} with {len(batch)} points")
        print(f"🎉 Total upsert {len(points)} vectors to Qdrant.")
    except Exception as e:
        print(f"❌ Upsert failed: {str(e)}")

    print("🚀 Qdrant vector sync completed.")
