import json
import logging

from fastapi import APIRouter, Depends

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/check")
async def correct_spell():
    response = {
            "status": "200",
            "message": "Check health successfully.",
            "data": "OK",
    }
    logger.info("Review comment completed successfully.")
    return response
