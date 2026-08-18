from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="AI Chat Backend", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_version: str = Field(default="0.2.0", alias="APP_VERSION")
    debug: bool = Field(default=True, alias="DEBUG")

    llm_provider: str = Field(default="deepseek", alias="LLM_PROVIDER")
    llm_base_url: str = Field(default="https://api.deepseek.com", alias="LLM_BASE_URL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="deepseek-v4-flash", alias="LLM_MODEL")
    llm_timeout: int | float = Field(default=60, alias="LLM_TIMEOUT")
    llm_max_retries: int = Field(default=2, alias="LLM_MAX_RETRIES")
    llm_retry_interval: float = Field(default=1.0, alias="LLM_RETRY_INTERVAL")

    database_url: str = Field(alias="DATABASE_URL")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()