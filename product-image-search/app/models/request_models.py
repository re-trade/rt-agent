from pydantic import BaseModel, Field
from typing import Optional, List

class ImageAnalysisRequest(BaseModel):
    prompt: Optional[str] = Field(None, 
                                  description="Optional custom prompt for image analysis")

class SimilarityResult(BaseModel):
    label: str
    confidence: float
    score: Optional[float] = None

class SearchResults(BaseModel):
    results: List[SimilarityResult]
    thumbnail: str
    fallback_used: bool = False
    extra_result: Optional[str] = None