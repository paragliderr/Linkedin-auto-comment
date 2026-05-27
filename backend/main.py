from fastapi import FastAPI

from backend.routes.comment_routes import router as comment_router


app = FastAPI(title="LinkedIn Auto Comment Backend")


@app.get("/")
def home():
    return {"message": "Backend is running"}


app.include_router(comment_router)