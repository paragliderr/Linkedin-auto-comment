from fastapi import APIRouter, HTTPException
import subprocess
import sys
import os 

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/check-session")
async def check_session():
    session_exists = os.path.exists("session.pkl") 
    return {"exists": session_exists}

@router.post("/login")
async def trigger_linkedin_login():
    try:
        subprocess.Popen([sys.executable, "-m", "auto_sel.auth.unified_login"])
        
        return {"success": True, "message": "Login browser opened! Please check your windows."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))