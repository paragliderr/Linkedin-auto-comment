from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.browser_ai import session_manager as sm

router = APIRouter(prefix="/browser-ai", tags=["BrowserAI"])


class StartRequest(BaseModel):
    url: str


@router.post("/start")
def start(req: StartRequest):
    try:
        return sm.start_or_save(req.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close")
def close():
    return sm.close_session()