import logging

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


from app.api.chat import router as chat_router
from app.api.summary import router as summary_router
from app.core.config import settings
from app.core.exceptions import BizException
from app.db.session import get_db


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI Chat Backend",
    description="AI Chat Backend v1",
    version=settings.app_version,
    debug=settings.debug,
)


@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    logger.warning(
        "BizException | path=%s | error_code=%s | message=%s",
        request.url.path,
        exc.error_code,
        exc.message,
    )

    return JSONResponse(
        status_code=exc.code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "UnhandledException | path=%s | error=%s",
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "服务暂时不可用，请稍后重试",
        },
    )


@app.get("/")
def root():
    return {
        "message": "AI Chat Backend is running",
        "env": settings.app_env,
    }

# 获取版本信息接口
@app.get("/version")
def version():
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }


# 健康检查接口
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "env": settings.app_env,
        "debug": settings.debug,
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
        #  我们只返回有没有配置 API Key，不要把真实 API Key 返回给前端。
        "llm_api_key_configured": bool(settings.llm_api_key),
    }


@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text(
                """
                SELECT
                    1 AS database_health,
                    current_database() AS database_name,
                    current_user AS database_role
                """
            )
        ).mappings().one()

        return {
            "status": "ok",
            "database": result["database_name"],
            "role": result["database_role"],
        }

    except SQLAlchemyError as exc:
        logger.exception(
            "Database health check failed | error_type=%s",
            exc.__class__.__name__,
        )

        raise BizException(
            message="数据库暂时不可用，请稍后重试",
            code=503,
            error_code="DATABASE_UNAVAILABLE",
        ) from exc


app.include_router(chat_router)
app.include_router(summary_router)
