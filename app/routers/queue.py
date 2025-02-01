from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from .. import schemas
from ..cruds import queue_crud
from ..database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/queue",
    tags=["queue"]
)

@router.post("/create", response_model=schemas.PostBase)
def get_send_news_by_24_hours(post: schemas.CreateNewsQueue, db: Session = Depends(get_db)):
    return queue_crud.create_news_queue(db, post=post)

@router.get("/get-news/by/hours", response_model=schemas.PostSendQueueList)
def get_queue_news_by_24_hours(db: Session = Depends(get_db)):
    return {"queue": queue_crud.get_texts_last_24_hours_queue(db)}

@router.delete("/delete-news/{channel}/{id_post}", response_model=schemas.BaseModel)
def delete_news_queue_entry(channel: str, id_post: int, db: Session = Depends(get_db)):
    entry = queue_crud.delete_queue_entry_by_seed(db, channel=channel, id_post=id_post)
    if entry is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Запись не найдена"})
    return entry