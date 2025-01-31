import datetime
import hashlib

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from . import models, schemas
from .models import Setting
from .schemas import ModifiedTextResponse, ToggleMediaResolutionResponse


def generate_unique_number(id_post: int, channel: str) -> str:
    seed = f"{id_post}-{channel}"
    return hashlib.sha256(seed.encode()).hexdigest()

def get_6_hours():
    return datetime.datetime.now() - datetime.timedelta(hours=10)

def get_post_by_channel_id(db: Session, channel: str, id_post: int):
    unique_number = generate_unique_number(channel=channel, id_post=id_post)
    return db.query(models.AllNews).filter(models.AllNews.seed == unique_number).first()


def get_post_details_by_seed(db: Session, seed: str):
    try:
        post = db.query(models.AllNews).filter(models.AllNews.seed == seed).one()

        modified_text = db.query(models.ModifiedText).filter(models.ModifiedText.seed == seed).first()
        new_content = modified_text.text if modified_text else None
        return {
            "content": post.text,
            "channel": post.channel,
            "id_post": post.id_post,
            "outlinks": post.outlinks,
            "new_content": new_content,
            "media_resolution": post.media_resolution
        }
    except NoResultFound:
        return None

def get_post_details_by_channel_id_post(db: Session, channel: str, id_post: int):
    seed = generate_unique_number(channel=channel, id_post=id_post)
    return get_post_details_by_seed(db=db, seed=seed)

def get_modified_text_by_channel_id_post(db: Session, channel: str, id_post: int) -> ModifiedTextResponse:
    seed = generate_unique_number(channel=channel, id_post=id_post)
    modified_text = db.query(models.ModifiedText).filter(models.ModifiedText.seed == seed).first()
    return ModifiedTextResponse(text=modified_text.text)

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

def create_modified_news(db: Session, post: schemas.ModifiedPost):
    db_post = models.ModifiedText(
        seed=generate_unique_number(post.id_post, post.channel),
        text=post.text
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_text_news(db: Session, post: schemas.UpdateModifiedPost):
    seed = generate_unique_number(channel=post.channel, id_post=post.id_post)
    modified_text = db.query(models.ModifiedText).filter(models.ModifiedText.seed == seed).first()

    if not modified_text:
        return None

    modified_text.text = post.new_text
    db.commit()
    db.refresh(modified_text)
    return modified_text

def add_news_to_moder_queue(db: Session, post: schemas.AddNewsModerQueue):
    db_post = models.ModeratorsQueue(
        seed=generate_unique_number(post.id_post, post.channel),
        sending_time=datetime.datetime.now()+datetime.timedelta(minutes=10),
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_news_moder_queue_for_send(db: Session):
    current_time = datetime.datetime.now()
    entries = db.query(models.ModeratorsQueue).filter(models.ModeratorsQueue.sending_time < current_time).all()
    return [entry.seed for entry in entries]

def delete_news_moder_queue_by_seed(db: Session, seed: str):
    entry = db.query(models.ModeratorsQueue).filter(models.ModeratorsQueue.seed == seed).first()
    if entry:
        db.delete(entry)
        db.commit()
    return entry

def get_automatic_sending(db: Session):
    automatic_sending_setting = db.query(models.Setting).filter(models.Setting.name_setting == "automatic_sending").first()
    return {"automatic_sending": automatic_sending_setting.bool if automatic_sending_setting else None}

def toggle_automatic_sending(db: Session):
    setting = db.query(Setting).filter_by(name_setting="automatic_sending").first()
    
    if setting:
        setting.bool = not setting.bool
        db.commit()

    return setting

def toggle_media_resolution_by_seed(db: Session, seed: str):
    print(f"Searching for seed: {seed}")
    post = db.query(models.AllNews).filter(models.AllNews.seed == seed).first()
    
    if not post:
        print("Post not found")
        return None

    print(f"Current media_resolution: {post.media_resolution}")
    post.media_resolution = not post.media_resolution
    db.commit()
    db.refresh(post)
    print(f"Updated media_resolution: {post.media_resolution}")
    return post

def get_media_resolution_by_seed(db: Session, seed: str) -> ToggleMediaResolutionResponse:
    post = db.query(models.AllNews).filter(models.AllNews.seed == seed).first()
    return ToggleMediaResolutionResponse(
            media_resolution=post.media_resolution
        )