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

from .. import schemas
from ..cruds import media_crud
from ..database import SessionLocal

router = APIRouter(
    prefix="/media",
    tags=["media"]
)

UPLOAD_DIR = "media"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload/{id_post}/{channel}", response_model=schemas.UploadMediaResponse)
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
    post_dir = os.path.join(UPLOAD_DIR, channel, str(id_post))
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
    media_crud.add_media_file(db, id_post=id_post, media=uploaded_files, channel=channel)
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

@router.post("/download/{id_post}/{channel}")
async def download_media(id_post: int, channel: str, db: Session = Depends(get_db)):
    """
    Скачивает медиафайлы для конкретного поста.
    """
    from fastapi.responses import StreamingResponse
    import io
    import zipfile

    media_files = media_crud.get_media_by_channel_id(db=db, channel=channel, id_post=id_post)
    if not media_files:
        raise HTTPException(
            status_code=404,
            detail=f"Медиа файлы для канала {channel}, поста {id_post} отсутствуют"
        )

    post_dir = Path(UPLOAD_DIR) / channel / str(id_post)
    if not post_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Директория для поста {id_post} не найдена"
        )

    zip_buffer = io.BytesIO()
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in media_files:
                file_path = post_dir / filename
                if not file_path.exists():
                    continue
                zip_file.write(file_path, filename)

        if zip_buffer.tell() == 0:
            raise HTTPException(
                status_code=404,
                detail="Не найдено доступных файлов для скачивания"
            )

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=media_{channel}_{id_post}.zip"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании архива: {str(e)}"
        )