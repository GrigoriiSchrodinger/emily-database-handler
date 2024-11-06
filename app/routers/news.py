from fastapi import APIRouter

from app.database import SessionLocal

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()