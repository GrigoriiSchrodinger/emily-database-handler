import datetime
import hashlib

from sqlalchemy.orm import Session

from app.logger import logger


def generate_unique_number(id_post: int, channel: str) -> str:
    logger.debug("Генерация уникального номера",
                 extra={"tags": {"service": "unique_number", "id_post": id_post, "channel": channel}})
    seed = f"{id_post}-{channel}"
    result = hashlib.sha256(seed.encode()).hexdigest()
    logger.debug("Успешная генерация номера", extra={"tags": {"result_length": len(result)}})
    return result


def get_6_hours(time_offset: int = 10):
    logger.debug("Расчет временного интервала", extra={"tags": {"service": "time_calculation", "hours_offset": 10}})
    result = datetime.datetime.now() - datetime.timedelta(hours=time_offset)
    return result


def get_post_text_last_6_hours(db: Session, model, time_offset: int = 10):
    logger.debug("Начало запроса к БД", extra={"tags": {"db_query": True, "model": model.__name__}})

    try:
        time_filter = get_6_hours(time_offset=time_offset)
        query = db.query(model).filter(model.created_at >= time_filter)

        logger.debug("Выполнение SQL запроса", extra={"tags": {
            "query_filter": str(time_filter),
            "model_columns": str(model.__table__.columns.keys())
        }})

        entries = query.all()

        logger.debug("Успешное получение записей", extra={"tags": {
            "entries_count": len(entries),
            "db_operation": "select"
        }})

        return [
            {
                "seed": entry.all_news.seed,
                "text": entry.all_news.text,
                "created_at": entry.created_at
            }
            for entry in entries if entry.all_news and entry.all_news.text
        ]

    except Exception as e:
        logger.error("Ошибка при выполнении запроса", extra={"tags": {
            "db_error": True,
            "error_message": str(e)
        }})
        raise
