from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = Field(default="News & Weather Agent")
    environment: str = Field(default="development")

    accuweather_api_key: Optional[str] = Field(
        default=None, description="Accuweather API key"
    )
    news_api_key: Optional[str] = Field(default=None, description="NewsAPI.org API key")
    deepseek_api_key: Optional[str] = Field(
        default=None, description="Deepseek LLM API key"
    )

    log_level: str = Field(default="INFO")

    deepseek_model: str = "deepseek-v4-flash"
    deepseek_extra_body: dict = Field(
        default_factory=lambda: {"thinking": {"type": "disabled"}}
    )

    db_url: str = "postgresql://postgres:postgres@localhost:5442/postgres"

    api_key: Optional[str] = Field(default="dev-secret-key-12345")


settings = Settings()
