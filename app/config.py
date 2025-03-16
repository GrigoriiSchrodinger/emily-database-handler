import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DataBaseManager"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./database.db"

    class Config:
        env_file = ".env"


settings = Settings()

load_dotenv()
ENV = os.getenv('ENV', "localhost")
