from dotenv import load_dotenv
import os
load_dotenv()

class Configs:
    ENV: str = os.getenv('ENV', 'development')
    PORT: int = int(os.getenv('PORT', 8000))
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    HOST: str = os.getenv('HOST', '0.0.0.0')

settings = Configs()