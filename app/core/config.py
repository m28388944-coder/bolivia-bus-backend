from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Base
    APP_NAME: str = "Bolivia Bus API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    POSTGRES_USER: str = "boliviabus"
    POSTGRES_PASSWORD: str = "boliviabus123"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "boliviabus_db"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # JWT
    SECRET_KEY: str = "supersecretkey_boliviabus_2024_cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Terminal fee (Derecho de Terminal Bolivia)
    TERMINAL_FEE: float = 2.50

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
