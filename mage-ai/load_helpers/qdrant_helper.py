import os

def get_qdrant_config_from_env():
    qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
    qdrant_port = int(os.getenv('QDRANT_HTTP', 6333))
    collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'products_vector')
    vector_size = int(os.getenv('VECTOR_SIZE', 100))

    return {
        'qdrant_host': qdrant_host,
        'qdrant_port': qdrant_port,
        'collection_name': collection_name,
        'vector_size': vector_size
    }