from sqlalchemy.orm import Session

from app.cruds.crud import generate_unique_number
from app.logger import logger
from .. import schemas, models


def create_modified_news(db: Session, post: schemas.ModifiedPost):
    try:
        logger.debug(f"Создание новой модифицированной новости. ID поста: {post.id_post}, Канал: {post.channel}")
        db_post = models.ModifiedText(
            seed=generate_unique_number(post.id_post, post.channel),
            text=post.text
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        logger.debug(f"Успешно создана модифицированная новость. ID записи: {db_post.id}")
        return db_post
    except Exception as e:
        logger.error(f"Ошибка при создании новости: {str(e)}", exc_info=True)
        db.rollback()
        raise


def update_text_news(db: Session, post: schemas.UpdateModifiedPost):
    try:
        seed = generate_unique_number(channel=post.channel, id_post=post.id_post)
        logger.debug(f"Обновление текста новости. Seed: {seed}")

        modified_text = db.query(models.ModifiedText).filter(models.ModifiedText.seed == seed).first()

        if not modified_text:
            logger.warning(f"Запись с seed {seed} не найдена")
            return None

        logger.debug(f"Обновление текста с '{modified_text.text}' на '{post.new_text}'")
        modified_text.text = post.new_text
        db.commit()
        db.refresh(modified_text)
        logger.info(f"Текст успешно обновлен. Seed: {seed}")
        return modified_text
    except Exception as e:
        logger.error(f"Ошибка при обновлении текста: {str(e)}", exc_info=True)
        db.rollback()
        raise
