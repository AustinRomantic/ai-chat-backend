from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.core.config import settings


app = FastAPI(
    title="AI Chat Backend",
    description="AI Chat Backend v1",
    version="0.1.1",
    debug=settings.debug,
)


@app.get("/")
def root():
    return {
        "message": "AI Chat Backend is running",
        "env": settings.app_env,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "env": settings.app_env,
        "debug": settings.debug,
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
        #  我们只返回有没有配置 API Key，不要把真实 API Key 返回给前端。
        "llm_api_key_configured": bool(settings.llm_api_key),
    }


app.include_router(chat_router)
