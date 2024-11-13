from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    pass

class NewPost(PostBase):
    channel: str
    id_post: int
    time: datetime
    url: str

class NewsExists(PostBase):
    exists: bool