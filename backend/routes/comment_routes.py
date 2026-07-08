import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
import pandas as pd
from pathlib import Path

from unified_pipeline import run , get_job
from backend.schemas.comment_schema import (
    CommentRequest, CommentResponse,
    ImproveCommentRequest, ImproveCommentResponse
)
from backend.services.comment_service import generate_comment_service, improve_comment_service
from auto_sel.auth.session import load_session
from auto_sel.scraper.post_comment import post_comment as post_comment_fn
from backend.services.post_status_service import mark_as_posted

router = APIRouter(prefix="/comments", tags=["Comments"])

_driver = None

def get_driver():
    global _driver
    if _driver is not None:
        try:
            _ = _driver.current_url  
        except Exception:
            _driver = None  
    if _driver is None:
        _driver = load_session()

    return _driver


class PostCommentRequest(BaseModel):
    post_url: str
    comment_text: str


@router.post("/post-to-linkedin")
def post_to_linkedin(request: PostCommentRequest):

    driver = get_driver()

    success = post_comment_fn(
        driver,
        request.post_url,
        request.comment_text
    )

    if success:
        mark_as_posted(
            request.post_url
        )

    return {"success": success}

@router.delete("/post")
def delete_post(post_text: str = Query(...)):
    from utils.app_paths import POSTS_CSV_PATH
    CSV_PATH = POSTS_CSV_PATH
    if not CSV_PATH.exists():
        return {"status": "ok"}
    df = pd.read_csv(CSV_PATH)
    df = df[df["post_text"].str.strip() != post_text.strip()]
    df.to_csv(CSV_PATH, index=False)
    return {"status": "deleted"}


@router.post("/generate", response_model=CommentResponse)
def generate_comment(request: CommentRequest):
    return CommentResponse(comment=generate_comment_service(request.post_text, request.goal))


@router.post("/improve", response_model=ImproveCommentResponse)
def improve_comment_route(request: ImproveCommentRequest):
    return ImproveCommentResponse(comment=improve_comment_service(request.comment, request.instruction))


@router.post("/run")
def run_pipeline(
    scraper_type: str = "selenium",
    keywords: Optional[List[str]] = Query(default=[]),
    match_mode: str = Query(default="any"),
    goal: str = Query(default="")
):
    return run(scraper_type=scraper_type, keywords=keywords, match_mode=match_mode, goal=goal)

@router.get("/run/status/{job_id}")
def get_run_status(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"status": "not_found"}
    return job