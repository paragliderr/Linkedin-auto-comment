from fastapi import APIRouter

from backend.schemas.edit_comment_schema import EditCommentRequest
from backend.services.edit_comment_service import update_comment

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.post("/edit")
def edit_comment(data: EditCommentRequest):

    success = update_comment(
        data.id,
        data.edited_comment
    )

    return {
        "success": success
    }