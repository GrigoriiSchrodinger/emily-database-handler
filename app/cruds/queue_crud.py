import datetime

from sqlalchemy.orm import Session

from .. import schemas, models
from app.cruds.crud import generate_unique_number, get_post_text_last_6_hours


def create_news_queue(db: Session, post: schemas.CreateNewsQueue):
    db_post = models.Queue(
        seed=generate_unique_number(post.post_id, post.channel),
        created_at=datetime.datetime.now(),
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_texts_last_24_hours_queue(db: Session):
    return get_post_text_last_6_hours(db, models.Queue)

def delete_queue_entry_by_seed(db: Session, channel: str, id_post: int):
    entry = db.query(models.Queue).filter(models.Queue.seed == generate_unique_number(channel=channel, id_post=id_post)).first()
    if not entry:
        return None

    db.delete(entry)
    db.commit()

    return entry