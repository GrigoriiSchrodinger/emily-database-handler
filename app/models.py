import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String, nullable=False)
    id_post = Column(Integer, nullable=False)
    time = Column(DateTime, default=datetime.datetime.utcnow)
    url = Column(String, nullable=False)