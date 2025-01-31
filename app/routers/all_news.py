from fastapi import Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import SessionLocal

from fastapi import APIRouter

from ..schemas import NewsExists

router = APIRouter(
    prefix="/all-news",
    tags=["all-news"]
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

@router.get("/detail-by-seed/{seed}", response_model=schemas.DetailBySeedResponse)
def get_detail_news_by_seed(seed: str, db: Session = Depends(get_db)):
    return crud.get_post_details_by_seed(seed=seed, db=db)

@router.get("/detail-by-channel-id_post/{channel}/{id_post}", response_model=schemas.DetailByChannelIdPostResponse)
def get_detail_news_by_channel_id_post(channel: str, id_post: int, db: Session = Depends(get_db)):
    return crud.get_post_details_by_channel_id_post(channel=channel, id_post=id_post, db=db)

@router.get("/exists-news/{channel}/{id_post}", response_model=NewsExists)
def check_post_exists(channel: str, id_post: int, db: Session = Depends(get_db)):
    db_post = crud.get_post_by_channel_id(db, channel=channel, id_post=id_post)
    if db_post:
        return {"exists": True}
    else:
        return {"exists": False}