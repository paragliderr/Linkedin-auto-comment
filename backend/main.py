import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.comment_routes import router as comment_router
from backend.routes.history_routes import router as history_router
from backend.routes.edit_comment_routes import router as edit_comment_router

app = FastAPI(title="LinkedIn Auto Comment Backend")

DIST_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend",
    "dist"
)

app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(DIST_DIR, "assets")),
    name="assets"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return FileResponse(
        os.path.join(DIST_DIR, "index.html")
    )

app.include_router(comment_router)
app.include_router(history_router)
app.include_router(edit_comment_router)