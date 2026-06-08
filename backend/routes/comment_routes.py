from typing import List, Optional
from unified_pipeline import run
from fastapi import APIRouter, Query

from backend.schemas.comment_schema import CommentRequest, CommentResponse
from backend.services.comment_service import generate_comment_service

import pandas as pd
from pathlib import Path
    

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.delete("/post")
def delete_post(post_text: str = Query(...)):
    CSV_PATH = Path("data/linkedin_posts.csv")
    
    if not CSV_PATH.exists():
        return {"status": "ok"}
    
    df = pd.read_csv(CSV_PATH)
    df = df[df["post_text"].str.strip() != post_text.strip()]
    df.to_csv(CSV_PATH, index=False)
    
    return {"status": "deleted"}

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