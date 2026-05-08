from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ff manus, from .env load"""

    # project base config
    env: str = "development"
    log_level: str = "INFO"
    app_config_filepath: str = "config.yaml"

    # database
    sqlalchemy_database_uri: str = "postgresql+asyncpg://postgres:postgres@localhost:5435/manus"

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6380
    redis_db: int = 0
    redis_password: str | None = None

    # Tencent Cloud COS object storage configuration
    cos_secret_id: str = ""
    cos_secret_key: str = ""
    cos_region: str = ""
    cos_scheme: str = "https"
    cos_bucket: str = ""
    cos_domain: str = ""

    # Sandbox configuration
    sandbox_address: Optional[str] = None
    sandbox_image: Optional[str] = None
    sandbox_name_prefix: Optional[str] = None
    sandbox_ttl_minutes: Optional[int] = 60
    sandbox_network: Optional[str] = None
    sandbox_chrome_args: Optional[str] = ""
    sandbox_https_proxy: Optional[str] = None
    sandbox_http_proxy: Optional[str] = None
    sandbox_no_proxy: Optional[str] = None

    # Use Pydantic v2 syntax to describe environment variable settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """get ff manus project config, cache it to avoid repeat reading"""
    settings = Settings()
    return settings
