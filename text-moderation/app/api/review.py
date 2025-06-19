import logging
import json
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.core import review_comment, CommentRequest, CommetnResponse

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
async def correct_spell(input: CommentRequest):
    try:
        logger.info(f"Received {len(input.comment)} comments for review.")
        result = await review_comment(input.comment)

        # Trả về kết quả
        response = {
            "status": "200",
            "message": "Review comment successfully.",
            "data": result,
        }
        logger.info("Review comment completed successfully.")
        return response

    except Exception as e:
        logger.error(f"Error Review Comment: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "500",
                "message": str(e),
                "data": None,
            },
        )
