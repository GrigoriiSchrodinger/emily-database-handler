from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import SessionLocal

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", response_model=schemas.PostBase)
def create_user(post: schemas.NewPost, db: Session = Depends(get_db)):
    return crud.create_post(db=db, post=post)

@router.get("/exists/{channel}/{id_post}", response_model=bool)
def check_post_exists(channel: str, id_post: int, db: Session = Depends(get_db)):
    db_post = crud.get_post_by_channel_id(db, channel=channel, id_post=id_post)
    if db_post:
        return True
    else:
        return False
