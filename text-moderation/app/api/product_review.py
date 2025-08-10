import logging
import random

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.core.models import FeedbackRequest
from app.core import get_suggestions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/suggest-reply")
async def suggest_reply(data: FeedbackRequest):
    suggestions = await get_suggestions(data)  # async now
    return JSONResponse(
        status_code=200,
        content={
            "status": "200",
            "message": "Suggest reply successfully.",
            "data": {
                "suggestions": suggestions,
                "random_suggestion": random.choice(suggestions) if suggestions else None
            },
        },
    )

