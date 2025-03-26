from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..cruds import all_news_crud
from ..database import SessionLocal
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
    return all_news_crud.create_post(db=db, post=post)

@router.post("/create-relationship", response_model=schemas.RelationshipNewsResult)
def create_relationship_news(news: schemas.RelationshipNews, db: Session = Depends(get_db)):
    return all_news_crud.create_relationship_news(db=db, news=news)

@router.get("/related-news/{seed}", response_model=schemas.GetRelationshipIdMessage)
def get_related_news(seed: str, db: Session = Depends(get_db)):
    return all_news_crud.get_related_news(seed=seed, db=db)

@router.get("/detail-by-seed/{seed}", response_model=schemas.DetailBySeedResponse)
def get_detail_news_by_seed(seed: str, db: Session = Depends(get_db)):
    return all_news_crud.get_post_details_by_seed(seed=seed, db=db)

@router.get("/detail-by-channel-id_post/{channel}/{id_post}", response_model=schemas.DetailByChannelIdPostResponse)
def get_detail_news_by_channel_id_post(channel: str, id_post: int, db: Session = Depends(get_db)):
    return all_news_crud.get_post_details_by_channel_id_post(channel=channel, id_post=id_post, db=db)

@router.get("/exists-news/{channel}/{id_post}", response_model=NewsExists)
def check_post_exists(channel: str, id_post: int, db: Session = Depends(get_db)):
    db_post = all_news_crud.get_post_by_channel_id(db, channel=channel, id_post=id_post)
    if db_post:
        return {"exists": True}
    else:
        return {"exists": False}
