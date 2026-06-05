from typing import List, Optional
from unified_pipeline import run
from fastapi import APIRouter, Query

from backend.schemas.comment_schema import CommentRequest, CommentResponse
from backend.services.comment_service import generate_comment_service

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/generate", response_model=CommentResponse)
def generate_comment(request: CommentRequest):
    comment = generate_comment_service(request.post_text)
    return CommentResponse(comment=comment)


@router.post("/run")
def run_pipeline(
    scraper_type: str = "selenium",
    keywords: Optional[List[str]] = Query(default=[]),
    match_mode: str = Query(default="any")
):
    results = run(
        scraper_type=scraper_type,
        keywords=keywords,
        match_mode=match_mode
    )
    return results