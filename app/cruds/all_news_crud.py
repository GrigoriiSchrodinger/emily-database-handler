from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from .. import schemas, models
from app.cruds.crud import generate_unique_number


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

def get_post_by_channel_id(db: Session, channel: str, id_post: int):
    unique_number = generate_unique_number(channel=channel, id_post=id_post)
    return db.query(models.AllNews).filter(models.AllNews.seed == unique_number).first()