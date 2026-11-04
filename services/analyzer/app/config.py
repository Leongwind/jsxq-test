from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    llm_base_url: str = Field(default="https://api.openai.com/v1")
    llm_api_key: str = Field(default="")
    llm_model: str = Field(default="")
    llm_mode: Literal["live", "test"] = "live"
    llm_timeout_seconds: float = Field(default=40.0, gt=0, le=40)
    service_timeout_seconds: float = Field(default=45.0, gt=0, le=45)


@lru_cache
def get_settings() -> Settings:
    return Settings()
