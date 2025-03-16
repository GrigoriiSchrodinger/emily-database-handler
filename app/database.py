from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Инициализация подключения к базе данных
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

    # Проверка и создание настройки automatic_sending
    db = SessionLocal()
    try:
        from app.models import Setting

        # Проверяем существование записи automatic_sending
        automatic_sending = db.query(Setting).filter(Setting.name_setting == "automatic_sending").first()

        # Если запись не существует, создаем её со значением True (1)
        if not automatic_sending:
            new_setting = Setting(name_setting="automatic_sending", bool=True)
            db.add(new_setting)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Ошибка при инициализации настроек: {e}")
    finally:
        db.close()


# Создаем таблицы и инициализируем настройки
Base.metadata.create_all(bind=engine)
