from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "My FastAPI Project"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./test.db"  # SQLite база данных

    class Config:
        env_file = ".env"

settings = Settings()
