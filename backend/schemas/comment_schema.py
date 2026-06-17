from pydantic import BaseModel


class CommentRequest(BaseModel):
    post_text: str
    goal: str = ""


class CommentResponse(BaseModel):
    comment: str
    
class ImproveCommentRequest(BaseModel):
    comment: str
    instruction: str


class ImproveCommentResponse(BaseModel):
    comment: str