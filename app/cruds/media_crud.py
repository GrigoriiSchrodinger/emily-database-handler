from sqlalchemy.orm import Session

from app import models
from app.logger import logger


def get_media_by_channel_id(db: Session, channel: str, id_post: int):
    logger.debug(
        "Начало получения медиа из БД",
        extra={"tags": {"channel": channel, "id_post": id_post}}
    )
    try:
        media = db.query(models.AllNews.image, models.AllNews.video).filter(
            models.AllNews.channel == channel,
            models.AllNews.id_post == id_post
        ).first()

        if not media:
            logger.warning(
                "Медиа не найдены в базе данных",
                extra={"tags": {"channel": channel, "id_post": id_post}}
            )
            return []

        list_media = []
        if media.image:
            list_media.extend(media.image)
        if media.video:
            list_media.extend(media.video)

        logger.info(
            f"Успешно получено {len(list_media)} медиафайлов",
            extra={"tags": {"channel": channel, "id_post": id_post}}
        )
        return list_media

    except Exception as e:
        logger.error(
            "Ошибка запроса к базе данных",
            extra={"tags": {"error": str(e), "channel": channel}},
            exc_info=True
        )
        raise


def add_media_file(db: Session, media: list, id_post: int, channel: str):
    logger.debug(
        "Начало добавления медиа в БД",
        extra={"tags": {"id_post": id_post, "channel": channel}}
    )
    try:
        db_post = db.query(models.AllNews).filter(
            models.AllNews.id_post == id_post,
            models.AllNews.channel == channel
        ).first()

        if not db_post:
            logger.warning(
                "Пост не найден для добавления медиа",
                extra={"tags": {"id_post": id_post, "channel": channel}}
            )
            return None

        list_image = [file["filename"] for file in media if file["content_type"] == "image/jpeg"]
        list_video = [file["filename"] for file in media if file["content_type"] == "video/mp4"]

        db_post.image = list_image
        db_post.video = list_video

        db.commit()
        db.refresh(db_post)

        logger.info(
            f"Добавлено {len(list_image)} изображений и {len(list_video)} видео",
            extra={"tags": {
                "id_post": id_post,
                "channel": channel,
                "images_count": len(list_image),
                "videos_count": len(list_video)
            }}
        )
        return db_post

    except Exception as e:
        logger.error(
            "Ошибка сохранения в базу данных",
            extra={"tags": {"error": str(e), "id_post": id_post}},
            exc_info=True
        )
        db.rollback()
        raise
