from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "DataBaseManager"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./database.db"

    class Config:
        env_file = ".env"

settings = Settings()
