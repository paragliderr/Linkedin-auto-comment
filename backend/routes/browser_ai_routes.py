from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.browser_ai import session_manager as sm

router = APIRouter(prefix="/browser-ai", tags=["BrowserAI"])


class StartRequest(BaseModel):
    url: str
    input_css: str
    send_css: str
    reply_css: str


class MessageRequest(BaseModel):
    message: str


@router.get("/check-session")
def check_session():
    return sm.check_session()


@router.post("/start")
def start(req: StartRequest):
    return sm.start_session(req.url, req.input_css, req.send_css, req.reply_css)


@router.post("/save-session")
def save():
    return sm.save_session()


@router.post("/message")
def message(req: MessageRequest):
    try:
        reply = sm.send_message(req.message)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close")
def close():
    return sm.close_session()