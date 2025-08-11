from app.api import api_v1
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="Comment Moderation API")
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if settings.ENV == 'production':
    app.include_router(api_v1, prefix="/api/text-moderation/v1")
else:
    app.include_router(api_v1, prefix="/api/v1")
