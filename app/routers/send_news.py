from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/send-news",
    tags=["send-news"]
)

@router.post("/create", response_model=schemas.PostBase)
def create_send_news(post: schemas.SendPost, db: Session = Depends(get_db)):
    return crud.create_send_news(db=db, post=post)

@router.get("/get-news/by/hours", response_model=schemas.PostSendNewsList)
def get_send_news_by_24_hours(db: Session = Depends(get_db)):
    return {"send": crud.get_texts_last_24_hours_send_news(db)}