from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="AI Chat Backend", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    llm_base_url: str = Field(default="", alias="LLM_BASE_URL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="deepseek-chat", alias="LLM_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()