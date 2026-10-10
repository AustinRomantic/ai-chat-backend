import os
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")

test_database_url = os.getenv("TEST_DATABASE_URL")

if not test_database_url:
    raise RuntimeError(
        "TEST_DATABASE_URL 未配置，请检查 .env"
    )

database_name = make_url(test_database_url).database

if database_name != "ai_chat_test_db":
    raise RuntimeError(
        "自动化测试只能使用 ai_chat_test_db"
    )

# 必须在导入 app 模块前覆盖环境变量。
os.environ["DATABASE_URL"] = test_database_url

# 测试中会 Mock LLM，不使用真实 Key。
os.environ["LLM_API_KEY"] = "test-api-key"


import app.models  # noqa: E402, F401
from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import (  # noqa: E402
    SessionLocal,
    engine,
)
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402


@pytest.fixture(autouse=True)
def reset_test_database() -> Generator[None, None, None]:
    """
    每条测试开始前重建业务表，结束后删除。

    这里只操作 ai_chat_test_db。
    """

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        user = User(
            email=settings.dev_user_email,
            display_name=settings.dev_user_display_name,
        )

        db.add(user)
        db.commit()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client