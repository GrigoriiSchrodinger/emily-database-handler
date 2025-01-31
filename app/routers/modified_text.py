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
    prefix="/modified-text",
    tags=["modified-text"]
)

@router.post("/create", response_model=schemas.PostBase)
def create_modified_news(post: schemas.ModifiedPost, db: Session = Depends(get_db)):
    return crud.create_modified_news(db, post=post)

@router.post("/update-text-news", response_model=schemas.PostBase)
def update_text_news(post: schemas.UpdateModifiedPost, db: Session = Depends(get_db)):
    return crud.update_text_news(db, post=post)

@router.get("/get-news/{id_post}/{channel}", response_model=schemas.ModifiedTextResponse)
def get_modified_text(channel: str, id_post: int, db: Session = Depends(get_db)):
    return crud.get_modified_text_by_channel_id_post(db, channel=channel, id_post=id_post)