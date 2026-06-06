from pydantic import BaseModel


class EditCommentRequest(BaseModel):
    id: int
    edited_comment: str