from fastapi import APIRouter, HTTPException
import subprocess
import sys
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COOKIES_PATH = os.path.join(BASE_DIR, "auto_sel", "auth", "cookies.pkl")


@router.get("/check-session")
async def check_session():
    return {"exists": os.path.exists(COOKIES_PATH)}


@router.post("/login")
async def trigger_linkedin_login():
    try:
        subprocess.Popen([sys.executable, "-m", "auto_sel.auth.unified_login"])
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))