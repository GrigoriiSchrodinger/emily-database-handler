import logging

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import news

# Создаем все таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.include_router(news.router)

if __name__ == "__main__":
    try:
        import uvicorn

        logging.debug("Starting uvicorn")
        uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
    except Exception as error:
        logging.error(error)
