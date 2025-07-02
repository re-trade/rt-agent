from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Optional
from app.services.openai_service import openai_service

router = APIRouter()

@router.post("/analyze-image")
async def analyze_image_endpoint(
    file: UploadFile = File(...),
):
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported image type")
    
    response = await openai_service.analyze_image(file)
    
    return {"analysis": response}