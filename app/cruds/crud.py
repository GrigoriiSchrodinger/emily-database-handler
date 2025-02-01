import datetime
import hashlib

from sqlalchemy.orm import Session

def generate_unique_number(id_post: int, channel: str) -> str:
    seed = f"{id_post}-{channel}"
    return hashlib.sha256(seed.encode()).hexdigest()

def get_6_hours():
    return datetime.datetime.now() - datetime.timedelta(hours=10)

def get_post_text_last_6_hours(db: Session, model):
    entries = db.query(model).filter(model.created_at >= get_6_hours()).all()
    return [
        {
            "seed": entry.all_news.seed,
            "text": entry.all_news.text,
            "created_at": entry.created_at
        }
        for entry in entries if entry.all_news and entry.all_news.text
    ]

# def add_news_to_moder_queue(db: Session, post: schemas.AddNewsModerQueue):
#     db_post = models.ModeratorsQueue(
#         seed=generate_unique_number(post.id_post, post.channel),
#         sending_time=datetime.datetime.now()+datetime.timedelta(minutes=10),
#     )
#     db.add(db_post)
#     db.commit()
#     db.refresh(db_post)
#     return db_post
#
# def get_news_moder_queue_for_send(db: Session):
#     current_time = datetime.datetime.now()
#     entries = db.query(models.ModeratorsQueue).filter(models.ModeratorsQueue.sending_time < current_time).all()
#     return [entry.seed for entry in entries]
#
# def delete_news_moder_queue_by_seed(db: Session, seed: str):
#     entry = db.query(models.ModeratorsQueue).filter(models.ModeratorsQueue.seed == seed).first()
#     if entry:
#         db.delete(entry)
#         db.commit()
#     return entry





