import datetime

from sqlalchemy.orm import Session

from app.cruds.crud import generate_unique_number, get_post_text_last_6_hours
from app.logger import logger
from .. import schemas, models


def create_news_queue(db: Session, post: schemas.CreateNewsQueue):
    logger.info("Создание новой записи в очереди новостей", extra={"tags": {"operation": "create_news_queue"}})
    try:
        db_post = models.Queue(
            seed=generate_unique_number(post.post_id, post.channel),
            created_at=datetime.datetime.now(),
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        logger.debug(f"Создана новая запись в очереди: ID {db_post.id}, seed {db_post.seed}",
                     extra={"tags": {"operation": "create_news_queue"}})
        return db_post
    except Exception as e:
        logger.error(f"Ошибка при создании записи: {str(e)}",
                     extra={"tags": {"operation": "create_news_queue", "error": True}})
        raise


def get_texts_last_24_hours_queue(db: Session):
    logger.info("Запрос последних текстов за 24 часа из очереди",
                extra={"tags": {"operation": "get_texts_last_24h"}})
    try:
        result = get_post_text_last_6_hours(db, models.Queue, time_offset=3)
        logger.debug(f"Получено {len(result)} записей из очереди",
                     extra={"tags": {"operation": "get_texts_last_24h"}})
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении записей: {str(e)}",
                     extra={"tags": {"operation": "get_texts_last_24h", "error": True}})
        raise


def delete_queue_entry_by_seed(db: Session, channel: str, id_post: int):
    logger.info(f"Удаление записи очереди: канал {channel}, пост {id_post}",
                extra={"tags": {"operation": "delete_queue_entry"}})
    try:
        seed = generate_unique_number(channel=channel, id_post=id_post)
        entry = db.query(models.Queue).filter(models.Queue.seed == seed).first()

        if not entry:
            logger.warning("Запись для удаления не найдена",
                           extra={"tags": {"operation": "delete_queue_entry", "warning": True}})
            return None

        db.delete(entry)
        db.commit()
        logger.debug(f"Удалена запись с seed {seed}",
                     extra={"tags": {"operation": "delete_queue_entry"}})
        return entry
    except Exception as e:
        logger.error(f"Ошибка удаления записи: {str(e)}",
                     extra={"tags": {"operation": "delete_queue_entry", "error": True}})
        raise
