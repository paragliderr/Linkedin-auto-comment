from fastapi import APIRouter, HTTPException
import threading
import os

from auto_sel.auth.unified_login import unified_login
from utils.app_paths import COOKIES_PATH

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/check-session")
async def check_session():
    return {"exists": os.path.exists(COOKIES_PATH)}


@router.post("/login")
async def trigger_linkedin_login():
    try:
        threading.Thread(
            target=unified_login,
            daemon=True
        ).start()
        
        return {"success": True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))