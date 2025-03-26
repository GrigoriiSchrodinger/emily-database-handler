from datetime import datetime
from typing import List, Optional
from typing import Union
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

class PostSendNews(PostBase):
    seed: str
    text: str
    created_at: datetime

class DetailBySeedResponse(PostBase):
    content: str
    channel: str
    id_post: int
    outlinks: list[str]
    new_content: str | None
    media_resolution: bool

class DetailByChannelIdPostResponse(PostBase):
    content: str
    channel: str
    id_post: int
    outlinks: list[str]
    new_content: str | None

class PostSendNewsList(PostBase):
    send: list[PostSendNews]

class PostSendQueue(PostBase):
    seed: str
    text: str
    created_at: datetime

class PostSendQueueList(PostBase):
    queue: list[PostSendQueue]

class SendPost(PostBase):
    channel: str
    id_post: int
    message_id: int

class ModifiedPost(PostBase):
    channel: str
    id_post: int
    text: str

class UpdateModifiedPost(PostBase):
    channel: str
    id_post: int
    new_text: str

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

class SettingAutomaticSendingResponse(BaseModel):
    automatic_sending: bool

class ToggleMediaResolution(PostBase):
    seed: str

class ToggleMediaResolutionResponse(PostBase):
    media_resolution: bool

class RelationshipNews(PostBase):
    seed_news: str
    related_new_seed: str

class RelationshipNewsResponse(BaseModel):
    status: str
    seed_news: str
    related_seed: str
    message_id: int

class RelationshipNewsError(BaseModel):
    status: str
    message: str

RelationshipNewsResult = Union[RelationshipNewsResponse, RelationshipNewsError]

class GetRelationshipIdMessage(BaseModel):
    tied: Union[int, bool]