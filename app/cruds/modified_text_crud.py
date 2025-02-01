from sqlalchemy.orm import Session

from .. import schemas, models
from app.cruds.crud import generate_unique_number


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