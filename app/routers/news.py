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


@router.post("/upload-media/{id_post}/{channel}", response_model=schemas.UploadMediaResponse)
async def upload_media(id_post: int, channel: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """
    Загружает медиафайлы (изображения и видео) для конкретного поста.
    
    Args:
        :param id_post: (int) Идентификатор поста
        :param files: (List[UploadFile]) Список файлов для загрузки
        :param db:
        :param channel: str
    
    Returns:
        JSONResponse: Информация о загруженных файлах
    
    Raises:
        HTTPException: При ошибке загрузки или неверном типе файла
    """
    uploaded_files = []
    allowed_types = ('image/', 'video/')

    # Создаем поддиректорию для конкретного поста
    post_dir = os.path.join(UPLOAD_DIR, str(id_post))
    os.makedirs(post_dir, exist_ok=True)

    for file in files:
        # Проверяем допустимость типа файла
        if not any(file.content_type.startswith(type_) for type_ in allowed_types):
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимый тип файла. Разрешены только: {', '.join(allowed_types)}"
            )

        try:
            # Генерируем уникальное имя файла с сохранением расширения
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(post_dir, unique_filename)

            # Сохраняем файл с использованием контекстного менеджера
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Добавляем информацию о загруженном файле
            uploaded_files.append({
                "filename": unique_filename,
                "content_type": file.content_type,
            })

        except Exception as e:
            # Если произошла ошибка, удаляем созданную директорию
            if len(uploaded_files) == 0:
                shutil.rmtree(post_dir, ignore_errors=True)
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при загрузке файла {file.filename}: {str(e)}"
            )
    print(uploaded_files)
    crud.add_media_file(db, id_post=id_post, media=uploaded_files, channel=channel)
    return JSONResponse(
        content={
            "message": "Файлы успешно загружены",
            "id_post": id_post,
            "channel": channel,
            "files": uploaded_files,
            "total_files": len(uploaded_files)
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
