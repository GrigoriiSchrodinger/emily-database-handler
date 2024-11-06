from sqlalchemy.orm import Session
from . import models, schemas

def get_post_by_channel_id(db: Session, channel: str, id_post: int):
    return db.query(models.Post).filter(
        models.Post.channel == channel,
        models.Post.id_post == id_post
    ).first()

def create_post(db: Session, post: schemas.NewPost):
    db_post = models.Post(
        channel=post.channel,
        id_post=post.id_post,
        time=post.time,
        url=post.url
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post