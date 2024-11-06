from sqlalchemy.orm import Session
from . import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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