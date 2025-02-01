import datetime

from sqlalchemy.orm import Session

from app import models, schemas
from app.cruds.crud import generate_unique_number, get_post_text_last_6_hours


def create_send_news(db: Session, post: schemas.SendPost):
    db_post = models.SendNews(
        seed=generate_unique_number(post.id_post, post.channel),
        created_at=datetime.datetime.now()
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_texts_last_24_hours_send_news(db: Session):
    return get_post_text_last_6_hours(db, models.SendNews)