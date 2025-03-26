from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session

from app.cruds.crud import generate_unique_number
from app.logger import logger
from .. import schemas, models
from ..schemas import GetRelationshipIdMessage


def create_post(db: Session, post: schemas.NewPost):
    try:
        logger.info(
            "Creating new post",
            extra={"tags": {"channel": post.channel, "id_post": post.id_post}}
        )
        db_post = models.AllNews(
            channel=post.channel,
            seed=generate_unique_number(post.id_post, post.channel),
            text=post.text,
            id_post=post.id_post,
            time=post.time,
            url=post.url,
            outlinks=post.outlinks
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        logger.info(
            "Post created successfully",
            extra={"tags": {"seed": db_post.seed, "channel": post.channel}}
        )
        return db_post
    except SQLAlchemyError as e:
        logger.error(
            "Error creating post",
            extra={"tags": {"error": str(e), "channel": post.channel}},
            exc_info=True
        )
        raise

def create_relationship_news(db: Session, news: schemas.RelationshipNews) -> schemas.RelationshipNewsResult:
    try:
        logger.info(
            "Creating relationship between news",
            extra={"tags": {"seed_news": news.seed_news, "related_seed": news.related_new_seed}}
        )

        related_news = db.query(models.AllNews).filter(
            models.AllNews.seed == news.related_new_seed
        ).first()

        if not related_news:
            logger.warning(
                "Related news not found",
                extra={"tags": {"related_seed": news.related_new_seed}}
            )
            return schemas.RelationshipNewsError(
                status="error",
                message="Related news not found"
            )

        # Обновляем tied для основной новости
        db.query(models.AllNews).filter(
            models.AllNews.seed == news.seed_news
        ).update({
            models.AllNews.tied: related_news.message_id
        })

        db.commit()

        logger.info(
            "Relationship created successfully",
            extra={"tags": {
                "seed_news": news.seed_news,
                "related_seed": news.related_new_seed,
                "message_id": related_news.message_id
            }}
        )

        return schemas.RelationshipNewsResponse(
            status="success",
            seed_news=news.seed_news,
            related_seed=news.related_new_seed,
            message_id=related_news.message_id
        )

    except SQLAlchemyError as e:
        logger.error(
            "Error creating relationship",
            extra={"tags": {
                "error": str(e),
                "seed_news": news.seed_news,
                "related_seed": news.related_new_seed
            }},
            exc_info=True
        )
        db.rollback()
        raise


def get_related_news(db: Session, seed: str) -> GetRelationshipIdMessage:
    news = db.query(models.AllNews).filter(models.AllNews.seed == seed).first()

    if news and news.tied:
        return GetRelationshipIdMessage(tied=news.tied)

    return GetRelationshipIdMessage(tied=False)

def get_post_details_by_seed(db: Session, seed: str):
    try:
        logger.info("Fetching post by seed", extra={"tags": {"seed": seed}})
        post = db.query(models.AllNews).filter(models.AllNews.seed == seed).one()

        modified_text = db.query(models.ModifiedText).filter(models.ModifiedText.seed == seed).first()
        logger.debug(
            "Modified text check",
            extra={"tags": {"exists": modified_text is not None, "seed": seed}}
        )
        new_content = modified_text.text if modified_text else None
        return {
            "content": post.text,
            "channel": post.channel,
            "id_post": post.id_post,
            "outlinks": post.outlinks,
            "new_content": new_content,
            "media_resolution": post.media_resolution
        }
    except NoResultFound:
        logger.warning("Post not found by seed", extra={"tags": {"seed": seed}})
        return None
    except Exception as e:
        logger.error(
            "Error fetching post details",
            extra={"tags": {"seed": seed, "error": str(e)}},
            exc_info=True
        )
        raise


def get_post_details_by_channel_id_post(db: Session, channel: str, id_post: int):
    logger.info(
        "Generating seed for channel/id_post",
        extra={"tags": {"channel": channel, "id_post": id_post}}
    )
    seed = generate_unique_number(channel=channel, id_post=id_post)
    return get_post_details_by_seed(db=db, seed=seed)


def get_post_by_channel_id(db: Session, channel: str, id_post: int):
    try:
        logger.info(
            "Searching post by channel/id",
            extra={"tags": {"channel": channel, "id_post": id_post}}
        )
        unique_number = generate_unique_number(channel=channel, id_post=id_post)
        result = db.query(models.AllNews).filter(models.AllNews.seed == unique_number).first()
        logger.debug(
            "Post search result",
            extra={"tags": {"found": result is not None, "channel": channel}}
        )
        return result
    except SQLAlchemyError as e:
        logger.error(
            "Database error in post search",
            extra={"tags": {"channel": channel, "error": str(e)}},
            exc_info=True
        )
        raise
