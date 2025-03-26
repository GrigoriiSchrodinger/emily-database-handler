import datetime

from sqlalchemy.orm import Session

from app import models, schemas
from app.cruds.crud import generate_unique_number, get_post_text_last_6_hours
from app.logger import logger


def create_send_news(db: Session, post: schemas.SendPost):
    logger.debug(
        "Начало создания записи SendNews",
        extra={"tags": {"function": "create_send_news", "post_id": post.id_post, "channel": post.channel}}
    )
    try:
        seed = generate_unique_number(post.id_post, post.channel)
        db_post = models.SendNews(
            seed=seed,
            created_at=datetime.datetime.now()
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        all_news_entry = db.query(models.AllNews).filter(models.AllNews.seed == seed).first()
        if all_news_entry:
            all_news_entry.message_id = post.message_id
            db.commit()

        logger.debug(
            "Успешно создана запись SendNews и обновлена запись AllNews",
            extra={
                "tags": {"function": "create_send_news", "seed": db_post.seed, "created_at": str(db_post.created_at)}}
        )
        return db_post
    except Exception as e:
        logger.error(
            f"Ошибка при создании записи SendNews - {e}",
            extra={"tags": {"function": "create_send_news"}},
            exc_info=True
        )
        raise


def get_texts_last_24_hours_send_news(db: Session):
    logger.debug(
        "Запрос последних текстов SendNews за 24 часа",
        extra={"tags": {"function": "get_texts_last_24_hours_send_news"}}
    )
    try:
        result = get_post_text_last_6_hours(db, models.SendNews)
        logger.debug(
            f"Найдено {len(result)} записей SendNews",
            extra={"tags": {"function": "get_texts_last_24_hours_send_news", "results_count": len(result)}}
        )
        return result
    except Exception as e:
        logger.error(
            f"Ошибка при получении текстов SendNews {e}",
            extra={"tags": {"function": "get_texts_last_24_hours_send_news"}},
            exc_info=True
        )
        raise
