import datetime
import hashlib

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from . import models, schemas


def generate_unique_number(id_post: int, channel: str) -> str:
    seed = f"{id_post}-{channel}"
    return hashlib.sha256(seed.encode()).hexdigest()

def get_6_hours():
    return datetime.datetime.now() - datetime.timedelta(hours=6)

def get_post_by_channel_id(db: Session, channel: str, id_post: int):
    unique_number = generate_unique_number(channel=channel, id_post=id_post)
    return db.query(models.AllNews).filter(models.AllNews.seed == unique_number).first()

def get_post_details_by_seed(db: Session, seed: str):
    try:
        post = db.query(models.AllNews).filter(models.AllNews.seed == seed).one()
        return {
            "content": post.text,
            "channel": post.channel,
            "id_post": post.id_post,
            "outlinks": post.outlinks
        }
    except NoResultFound:
        return None

def get_post_details_by_channel_id_post(db: Session, channel: str, id_post: int):
    seed = generate_unique_number(channel=channel, id_post=id_post)
    return get_post_details_by_seed(db=db, seed=seed)

def get_post_text_last_6_hours(db: Session, model):
    entries = db.query(model).filter(model.created_at >= get_6_hours()).all()
    return [
        {
            "seed": entry.all_news.seed,
            "text": entry.all_news.text,
            "created_at": entry.created_at
        }
        for entry in entries if entry.all_news
    ]

def get_texts_last_24_hours_send_news(db: Session):
    return get_post_text_last_6_hours(db, models.SendNews)

def get_texts_last_24_hours_queue(db: Session):
    return get_post_text_last_6_hours(db, models.Queue)

def create_news_queue(db: Session, post: schemas.CreateNewsQueue):
    db_post = models.Queue(
        seed=generate_unique_number(post.post_id, post.channel),
        created_at=datetime.datetime.now(),
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_queue_entry_by_seed(db: Session, channel: str, id_post: int):
    entry = db.query(models.Queue).filter(models.Queue.seed == generate_unique_number(channel=channel, id_post=id_post)).first()
    if not entry:
        return None

    db.delete(entry)
    db.commit()

    return entry

def get_media_by_channel_id(db: Session, channel: str, id_post: int):
    media = db.query(models.AllNews.image, models.AllNews.video).filter(
        models.AllNews.channel == channel,
        models.AllNews.id_post == id_post
    ).first()

    if not media:
        return []

    list_media = []
    if media.image:
        list_media.extend(media.image)
    if media.video:
        list_media.extend(media.video)

    return list_media

def add_media_file(db: Session, media: list, id_post: int, channel: str):
    db_post = db.query(models.AllNews).filter(
        models.AllNews.id_post == id_post,
        models.AllNews.channel == channel
    ).first()

    if not db_post:
        return None

    list_image = [file["filename"] for file in media if file["content_type"] == "image/jpeg"]
    list_video = [file["filename"] for file in media if file["content_type"] == "video/mp4"]

    db_post.image = list_image
    db_post.video = list_video

    db.commit()
    db.refresh(db_post)
    return db_post

def create_post(db: Session, post: schemas.NewPost):
    db_post = models.AllNews(
        channel=post.channel,
        seed=generate_unique_number(post.id_post, post.channel),
        text=post.text,
        id_post=post.id_post,
        time=post.time,
        url=post.url,
        outlinks=post.outlinks
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def create_send_news(db: Session, post: schemas.SendPost):
    db_post = models.SendNews(
        seed=generate_unique_number(post.id_post, post.channel),
        created_at=datetime.datetime.now()
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
