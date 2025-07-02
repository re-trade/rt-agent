import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    APP_API_KEY: str = os.getenv('APP_API_KEY', '')
    
    QDRANT_URL: str = os.getenv('QDRANT_URL', 'http://localhost:6333')
    QDRANT_COLLECTION_NAME: str = os.getenv('QDRANT_COLLECTION_NAME', 'retrade')

    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    APP_HOST: str = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT: int = int(os.getenv('APP_PORT', 9090))

    @classmethod
    def validate_config(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in .env file")

settings = Settings()