from sqlalchemy.orm import Session

from app import models


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