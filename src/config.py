from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GITHUB_TOKEN: Optional[str] = None
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 300  # 5 minutes
    RATE_LIMIT: str = "100/minute"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()