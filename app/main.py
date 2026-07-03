from fastapi import FastAPI

from app.api.chat import router as chat_router

app = FastAPI(
    title="AI Chat Backend",
    description="AI Chat Backend v1",
    version="0.1.1"
)

@app.get("/")
def root():
    return {"message": "AI Chat Backend is running"}

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

app.include_router(chat_router)
