from dataclasses import Field
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
    # Application settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Threat Intelligence Dashboard"

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # Allowed origins for CORS
    cors_allow_origins: list[str] = Field(["*"], env="CORS_ALLOW_ORIGINS")

    # External API settings
    NVD_API_URL: str = os.getenv("NVD_API_URL", "https://services.nvd.nist.gov/rest/json/cves/2.0")
    NVD_API_KEY: Optional[str] = os.getenv("NVD_API_KEY")

    ABUSEIPDB_API_URL: str = os.getenv("ABUSEIPDB_API_URL", "https://api.abuseipdb.com/api/v2")
    ABUSEIPDB_API_KEY: Optional[str] = os.getenv("ABUSEIPDB_API_KEY")

    OTX_API_URL: str = os.getenv("OTX_API_URL", "https://otx.alienvault.com/api/v1")
    OTX_API_KEY: Optional[str] = os.getenv("OTX_API_KEY")

    class Config:
        case_sensitive = True
settings = Settings()