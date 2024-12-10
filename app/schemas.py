from datetime import datetime
from typing import List

from pydantic import BaseModel


class PostBase(BaseModel):
    pass


class NewPost(PostBase):
    channel: str
    text: str
    id_post: int
    time: datetime
    url: str
    outlinks: list

class CreateNewsQueue(PostBase):
    channel: str
    post_id: int

class CreateNewsRate(PostBase):
    channel: str
    post_id: int
    value: float

class PostSendNews(PostBase):
    texts: list[str]

class PostSendQueue(PostBase):
    texts: list[str]

class SendPost(PostBase):
    channel: str
    text: str
    id_post: int

class DeletePostByQueue(PostBase):
    channel: str
    id_post: int

class MediaFile(PostBase):
    media: list

class GetNewsMaxValueResponse(PostBase):
    channel: str
    content: str
    id_post: int
    outlinks: list[str]

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
