from sqlalchemy.orm import Session

from app import models
from app.models import Setting
from app.schemas import ToggleMediaResolutionResponse
from app.logger import logger


def get_automatic_sending(db: Session):
    logger.debug("Получение настройки автоматической отправки", extra={"tags": {"operation": "get_setting"}})
    automatic_sending_setting = db.query(models.Setting).filter(models.Setting.name_setting == "automatic_sending").first()
    
    if automatic_sending_setting:
        logger.debug("Настройка найдена", extra={"tags": {"value": automatic_sending_setting.bool}})
    else:
        logger.warning("Настройка не найдена в базе данных")
    
    return {"automatic_sending": automatic_sending_setting.bool if automatic_sending_setting else None}


def toggle_automatic_sending(db: Session):
    logger.info("Переключение настройки автоматической отправки", extra={"tags": {"operation": "toggle_setting"}})
    setting = db.query(Setting).filter_by(name_setting="automatic_sending").first()

    if setting:
        old_value = setting.bool
        setting.bool = not setting.bool
        try:
            db.commit()
            logger.debug("Настройка успешно обновлена", 
                       extra={"tags": {"old_value": old_value, "new_value": setting.bool}})
        except Exception as e:
            logger.error("Ошибка при сохранении настроек", 
                       extra={"tags": {"error": str(e)}})
            raise
    else:
        logger.warning("Попытка переключения несуществующей настройки")
    
    return setting


def toggle_media_resolution_by_seed(db: Session, seed: str):
    logger.debug("Поиск поста по seed", extra={"tags": {"operation": "find_post", "seed": seed}})
    post = db.query(models.AllNews).filter(models.AllNews.seed == seed).first()

    if not post:
        logger.error("Пост не найден", extra={"tags": {"seed": seed}})
        return None

    try:
        old_resolution = post.media_resolution
        post.media_resolution = not post.media_resolution
        db.commit()
        db.refresh(post)
        logger.info("Разрешение медиа успешно изменено", 
                  extra={"tags": {"old_value": old_resolution, "new_value": post.media_resolution}})
    except Exception as e:
        logger.error("Ошибка при обновлении разрешения медиа", 
                  extra={"tags": {"error": str(e), "seed": seed}})
        raise
    
    return post

def get_media_resolution_by_seed(db: Session, seed: str) -> ToggleMediaResolutionResponse:
    logger.debug("Запрос разрешения медиа по seed", extra={"tags": {"operation": "get_media", "seed": seed}})
    post = db.query(models.AllNews).filter(models.AllNews.seed == seed).first()
    
    if post:
        logger.debug("Разрешение медиа получено", extra={"tags": {"value": post.media_resolution}})
    else:
        logger.warning("Пост не найден при запросе разрешения медиа", extra={"tags": {"seed": seed}})
    
    return ToggleMediaResolutionResponse(media_resolution=post.media_resolution)
