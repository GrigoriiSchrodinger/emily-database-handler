from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from .. import schemas
from ..cruds import modified_text_crud
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
    return modified_text_crud.create_modified_news(db, post=post)


@router.post("/update-text-news", response_model=schemas.PostBase)
def update_text_news(post: schemas.UpdateModifiedPost, db: Session = Depends(get_db)):
    return modified_text_crud.update_text_news(db, post=post)
