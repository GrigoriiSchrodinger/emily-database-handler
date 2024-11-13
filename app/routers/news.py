import os
import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends
from fastapi import File, UploadFile
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import SessionLocal
from ..schemas import NewsExists

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

UPLOAD_DIR = "media"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", response_model=schemas.PostBase)
def create_user(post: schemas.NewPost, db: Session = Depends(get_db)):
    return crud.create_post(db=db, post=post)


@router.post("/upload-media/{id_post}")
async def upload_media(id_post: int, files: List[UploadFile] = File(...)):
    uploaded_files = []

    # Создаем поддиректорию для конкретного поста
    post_dir = os.path.join(UPLOAD_DIR, str(id_post))
    os.makedirs(post_dir, exist_ok=True)

    for file in files:
        # Проверяем тип файла
        if not file.content_type.startswith(('image/', 'video/')):
            raise HTTPException(
                status_code=400,
                detail="Разрешены только изображения и видео"
            )

        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Сохраняем файл
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append({
                "filename": file.filename,
                "original_name": file.filename,
                "content_type": file.content_type
            })
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при загрузке файла: {str(e)}"
            )

    return JSONResponse(
        content={
            "message": "Файлы успешно загружены",
            "id_post": id_post,
            "files": uploaded_files
        },
        status_code=200
    )


@router.get("/exists/{channel}/{id_post}", response_model=NewsExists)
def check_post_exists(channel: str, id_post: int, db: Session = Depends(get_db)):
    db_post = crud.get_post_by_channel_id(db, channel=channel, id_post=id_post)
    if db_post:
        return {"exists": True}
    else:
        return {"exists": False}
