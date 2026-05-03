from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str = "boliviabus"
    POSTGRES_PASSWORD: str = "boliviabus123"
    POSTGRES_DB: str = "boliviabus_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: str = "postgresql://boliviabus:boliviabus123@localhost:5432/boliviabus_db"
    SECRET_KEY: str = "bolivia-bus-secret-key-2024-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    EMAIL_FROM: str = "noreply@boliviabus.bo"
    EMAIL_FROM_NAME: str = "Bolivia Bus"

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_FROM: str = ""
    TWILIO_WA_FROM: str = ""

    class Config:
        env_file = ".env"

settings = Settings()

