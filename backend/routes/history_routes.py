from fastapi import APIRouter

from backend.services.history_service import get_saved_comments

router = APIRouter(
    prefix="/history",
    tags=["History"]
)


@router.get("/")
def get_history():

    return get_saved_comments()