from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from backend.routes.comment_routes import router as comment_router


app = FastAPI(title="LinkedIn Auto Comment Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Backend is running"}


app.include_router(comment_router)