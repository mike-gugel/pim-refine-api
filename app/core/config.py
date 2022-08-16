from functools import lru_cache

import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):
    PRODUCTION: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 seconds * 60 minutes * 24 hours * 14 days = 14 days
    ACCESS_TOKEN_LIFETIME: int = 60 * 60 * 24 * 14
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", "http://localhost:8080"]'
    BACKEND_CORS_ORIGINS: Union[List[AnyHttpUrl], List[str]] = []

    # 60 seconds * 60 minutes * 8 hours = 8 hours
    CACHE_TTL: int = 60 * 60 * 8

    CRAWLAB_API_URL: AnyHttpUrl
    CRAWLAB_API_KEY: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    BDX_SERVER: str
    BDX_USER: str
    BDX_PASSWORD: str
    BDX_DB: str
    BDX_TYPE: str = "postgresql"

    DGE_HOST: str
    DGE_USER: str
    DGE_PASSWORD: str

    GOOGLE_OAUTH_CLIENT_ID: str
    GOOGLE_OAUTH_CLIENT_SECRET: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    P_INFO_API_URL: AnyHttpUrl
    P_INFO_API_KEY: str

    ICECAT_USER: str
    ICECAT_API_KEY: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    BDX_SQLALCHEMY_DATABASE_URI: Optional[AnyUrl] = None

    PAW_HOST: str
    PAW_USER: str
    PAW_PASSWORD: str

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    @validator("BDX_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_bdx_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return AnyUrl.build(
            scheme=values.get("BDX_TYPE"),
            user=values.get("BDX_USER"),
            password=values.get("BDX_PASSWORD"),
            host=values.get("BDX_SERVER"),
            path=f"/{values.get('BDX_DB') or ''}",
        )

    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache
def load_settings():
    return Settings()

settings = load_settings()
