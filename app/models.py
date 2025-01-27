import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class AllNews(Base):
    __tablename__ = "all_news"

    id = Column(Integer, primary_key=True, index=True)
    seed = Column(String, nullable=False)
    text = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    id_post = Column(Integer, nullable=False)
    time = Column(DateTime, default=datetime.datetime.now())
    url = Column(String, nullable=False)
    outlinks = Column(JSON, nullable=False)
    image = Column(JSON, nullable=True)
    video = Column(JSON, nullable=True)
    media_resolution = Column(Boolean, nullable=False, default=True)

    send_news = relationship("SendNews", back_populates="all_news")
    queue_entries = relationship("Queue", back_populates="all_news")
    moderators_queue = relationship("ModeratorsQueue", back_populates="all_news")

class SendNews(Base):
    __tablename__ = "send_news"

    id = Column(Integer, primary_key=True, index=True)
    seed = Column(String, ForeignKey('all_news.seed'), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())

    all_news = relationship("AllNews", back_populates="send_news")

class ModifiedText(Base):
    __tablename__ = "modified_text"

    id = Column(Integer, primary_key=True, index=True)
    seed = Column(String, ForeignKey('all_news.seed'), nullable=False)
    text = Column(String, nullable=False)


class Queue(Base):
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True, index=True)
    seed = Column(String, ForeignKey('all_news.seed'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())

    all_news = relationship("AllNews", back_populates="queue_entries")

class ModeratorsQueue(Base):
    __tablename__ = "moderators_queue"

    id = Column(Integer, primary_key=True, index=True)
    seed = Column(String, ForeignKey('all_news.seed'), nullable=False)
    sending_time = Column(DateTime)

    all_news = relationship("AllNews", back_populates="moderators_queue")

class Setting(Base):
    __tablename__ = "Setting"

    id = Column(Integer, primary_key=True, index=True)
    name_setting = Column(String, nullable=False)
    bool = Column(Boolean, nullable=False, default=True)