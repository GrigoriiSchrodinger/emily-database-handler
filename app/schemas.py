from typing import  List

from fastapi import UploadFile, File
from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    pass

class NewPost(PostBase):
    channel: str
    id_post: int
    time: datetime
    url: str
    images: List[UploadFile] = File(None)
    videos: List[UploadFile] = File(None)

class NewsExists(PostBase):
    exists: bool