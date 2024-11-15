from sqlalchemy.orm import Session

from . import models, schemas


def get_post_by_channel_id(db: Session, channel: str, id_post: int):
    return db.query(models.Post).filter(
        models.Post.channel == channel,
        models.Post.id_post == id_post
    ).first()

def add_media_file(db: Session, media: list, id_post: int, channel: str):
    db_post = db.query(models.Post).filter(models.Post.id_post == id_post, models.Post.channel == channel).first()
    
    if not db_post:
        return None
        
    list_image = list()
    list_video = list()


    for file in media:
        if file["content_type"] == "video/mp4":
            list_video.append(file["filename"])
        elif file["content_type"] == "image/jpeg":
            list_image.append(file["filename"])
    
    db_post.image = list_image
    db_post.video = list_video
    
    db.commit()
    db.refresh(db_post)
    return db_post

def create_post(db: Session, post: schemas.NewPost):
    db_post = models.Post(
        channel=post.channel,
        text=post.text,
        id_post=post.id_post,
        time=post.time,
        url=post.url
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
