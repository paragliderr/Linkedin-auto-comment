from fastapi import APIRouter

from backend.schemas.comment_schema import CommentRequest, CommentResponse
from backend.services.comment_service import generate_comment_service


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/generate", response_model=CommentResponse)
def generate_comment(request: CommentRequest):
    comment = generate_comment_service(request.post_text)
    return CommentResponse(comment=comment)