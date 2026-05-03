content = open("app/config.py", "w", encoding="utf-8")
content.write("""from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://boliviabus:boliviabus123@localhost:5432/boliviabus"
    SECRET_KEY: str = "bolivia-bus-secret-key-2024-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"

settings = Settings()
""")
content.close()
print("config.py creado OK")