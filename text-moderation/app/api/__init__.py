from .health import router as health_router
from .review import router as review_router
from .product_review import router as product_review_router
from fastapi import APIRouter

api_v1 = APIRouter()
api_v1.include_router(review_router, prefix="/comment", tags=["Comment Moderation"])
api_v1.include_router(health_router, prefix="/health", tags=["Health Check"])
api_v1.include_router(product_review_router, prefix="/product-review", tags=["Product Review"])
