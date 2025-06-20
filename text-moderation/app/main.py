from app.api.health import router as health_router
from app.api.review import router as review_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(review_router, prefix="/comment", tags=["Comment Moderation"])
app.include_router(health_router, tags=["Health Check"])
