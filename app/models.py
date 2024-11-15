import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON

from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    id_post = Column(Integer, nullable=False)
    time = Column(DateTime, default=datetime.datetime.utcnow)
    url = Column(String, nullable=False)
    image = Column(JSON, nullable=True)
    video = Column(JSON, nullable=True)
