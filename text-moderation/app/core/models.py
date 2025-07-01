from pydantic import BaseModel

class CommentRequest(BaseModel):
    comment: str = None
    
class Review(BaseModel):
    status: bool
    message: str

class CommentResponse(BaseModel):
    status: str
    message: str
    data: list = None