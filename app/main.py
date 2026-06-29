from fastapi import FastAPI

app = FastAPI(
    title="AI Chat Backend",
    description="AI Chat Backend v1",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "AI Chat Backend is running"}

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
