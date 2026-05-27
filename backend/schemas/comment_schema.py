from pydantic import BaseModel


class CommentRequest(BaseModel):
    post_text: str


class CommentResponse(BaseModel):
    comment: str