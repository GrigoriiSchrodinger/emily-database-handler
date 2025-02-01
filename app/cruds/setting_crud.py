from sqlalchemy.orm import Session

from app import models
from app.models import Setting
from app.schemas import ToggleMediaResolutionResponse


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
