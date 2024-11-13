from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import SessionLocal
from ..schemas import NewsExists
import os

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create", response_model=schemas.PostBase)
def create_post(
    post: schemas.NewPost,
    db: Session = Depends(get_db)
):
    media_paths = {"images": [], "videos": []}
    print(media_paths)
    if post:
        for image in post.images:
            file_path = f"media/img/{image.filename}"
            with open(file_path, "wb") as f:
                f.write(image.file.read())
            media_paths["images"].append(file_path)

    if post:
        for video in post.videos:
            file_path = f"media/video/{video.filename}"
            with open(file_path, "wb") as f:
                f.write(video.file.read())
            media_paths["videos"].append(file_path)

    # Создание поста в БД через crud
    db_post = crud.create_post(db=db, post=post)

    return db_post

@router.get("/exists/{channel}/{id_post}", response_model=NewsExists)
def check_post_exists(channel: str, id_post: int, db: Session = Depends(get_db)):
    db_post = crud.get_post_by_channel_id(db, channel=channel, id_post=id_post)
    if db_post:
        return {"exists": True}
    else:
        return {"exists": False}
