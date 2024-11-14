from datetime import datetime
from typing import List

from pydantic import BaseModel


class PostBase(BaseModel):
    pass


class NewPost(PostBase):
    channel: str
    id_post: int
    time: datetime
    url: str


class NewsExists(PostBase):
    exists: bool


class UploadedFileInfo(BaseModel):
    filename: str
    original_name: str
    content_type: str
    file_path: str


class UploadMediaResponse(BaseModel):
    message: str
    id_post: int
    files: List[UploadedFileInfo]
    total_files: int
