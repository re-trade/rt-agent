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

app.include_router(review_router, prefix="/review", tags=["comment_review"])

@app.get("/")
def root():
    return {"status": "200", "message": "Welcome to Comment Moderation API", "data": None}
