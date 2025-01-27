import logging
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
from starlette import status

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


@router.post("/create/send-news", response_model=schemas.PostBase)
def create_send_news(post: schemas.SendPost, db: Session = Depends(get_db)):
    return crud.create_send_news(db=db, post=post)

@router.get("/send-news", response_model=schemas.PostSendNewsList)
def get_send_news_by_24_hours(db: Session = Depends(get_db)):
    return {"send": crud.get_texts_last_24_hours_send_news(db)}

@router.get("/queue", response_model=schemas.PostSendQueueList)
def get_queue_news_by_24_hours(db: Session = Depends(get_db)):
    return {"queue": crud.get_texts_last_24_hours_queue(db)}

@router.get("/detail-by-seed/{seed}", response_model=schemas.DetailBySeedResponse)
def get_detail_news_by_seed(seed: str, db: Session = Depends(get_db)):
    return crud.get_post_details_by_seed(seed=seed, db=db)

@router.get("/detail-by-channel-id_post/{channel}/{id_post}", response_model=schemas.DetailByChannelIdPostResponse)
def get_detail_news_by_channel_id_post(channel: str, id_post: int, db: Session = Depends(get_db)):
    return crud.get_post_details_by_channel_id_post(channel=channel, id_post=id_post, db=db)

@router.post("/create-news-queue", response_model=schemas.PostBase)
def get_send_news_by_24_hours(post: schemas.CreateNewsQueue, db: Session = Depends(get_db)):
    return crud.create_news_queue(db, post=post)

@router.post("/create-modified-news", response_model=schemas.PostBase)
def create_modified_news(post: schemas.ModifiedPost, db: Session = Depends(get_db)):
    return crud.create_modified_news(db, post=post)

@router.post("/update-modified-news", response_model=schemas.PostBase)
def update_modified_news(post: schemas.UpdateModifiedPost, db: Session = Depends(get_db)):
    return crud.update_modified_text(db, post=post)

@router.get("/modified-text/{id_post}/{channel}", response_model=schemas.ModifiedTextResponse)
def get_modified_text(channel: str, id_post: int, db: Session = Depends(get_db)):
    return crud.get_modified_text_by_channel_id_post(db, channel=channel, id_post=id_post)

@router.post("/add-news-moder-queue", response_model=schemas.PostBase)
def add_news_moder_queue(post: schemas.AddNewsModerQueue, db: Session = Depends(get_db)):
    return crud.add_news_to_moder_queue(db, post=post)

@router.get("/get-news-moder-queue-for-send", response_model=schemas.GetNewsModerQueue)
def get_news_moder_queue(db: Session = Depends(get_db)):
    return {"seed": crud.get_news_moder_queue_for_send(db)}

@router.delete("/delete-news-moder-queue/{seed}", response_model=schemas.BaseModel)
def delete_news_moder_queue(seed: str, db: Session = Depends(get_db)):
    logging.info(f"Попытка удаления записи из очереди модерации с seed: {seed}")
    entry = crud.delete_news_moder_queue_by_seed(db, seed=seed)
    if entry is None:
        logging.warning(f"Запись с seed: {seed} не найдена в очереди модерации")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Запись не найдена"}
        )
    logging.info(f"Запись с seed: {seed} успешно удалена из очереди модерации")
    return entry

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
    logging.debug("Дернулась ручка /exists/{channel}/{id_post}")
    db_post = crud.get_post_by_channel_id(db, channel=channel, id_post=id_post)
    if db_post:
        return {"exists": True}
    else:
        return {"exists": False}

@router.post("/download-media/{id_post}/{channel}")
async def download_media(id_post: int, channel: str, db: Session = Depends(get_db)):
    """
    Скачивает медиафайлы для конкретного поста.
    """
    from fastapi.responses import StreamingResponse
    import io
    import zipfile
    
    media_files = crud.get_media_by_channel_id(db=db, channel=channel, id_post=id_post)
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

@router.delete("/delete-news-queue/{channel}/{id_post}", response_model=schemas.BaseModel)
def delete_news_queue_entry(channel: str, id_post: int, db: Session = Depends(get_db)):
    entry = crud.delete_queue_entry_by_seed(db, channel=channel, id_post=id_post)
    if entry is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Запись не найдена"})
    return entry

@router.get("/automatic-sending", response_model=schemas.SettingAutomaticSendingResponse)
def get_setting(db: Session = Depends(get_db)):
    return crud.get_automatic_sending(db)

@router.post("/toggle-automatic-sending", response_model=schemas.BaseModel)
def toggle_automatic_sending(db: Session = Depends(get_db)):
    return crud.toggle_automatic_sending(db)

@router.post("/toggle-media-resolution-by-seed", response_model=schemas.BaseModel)
def toggle_media_resolution(seed: schemas.ToggleMediaResolution, db: Session = Depends(get_db)):
    return crud.toggle_media_resolution_by_seed(seed=seed.seed, db=db)

@router.post("/media-resolution-by-seed", response_model=schemas.ToggleMediaResolutionResponse)
def toggle_media_resolution(seed: schemas.ToggleMediaResolution, db: Session = Depends(get_db)):
    return crud.get_media_resolution_by_seed(seed=seed.seed, db=db)