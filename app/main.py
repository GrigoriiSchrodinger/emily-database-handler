from fastapi import FastAPI
from .routers import users
from .config import settings
from .database import engine, Base

# Создаем все таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="This is a sample API with a real database.",
    version="1.0.0"
)

# Подключаем роутер
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
