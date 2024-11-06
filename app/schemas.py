from pydantic import BaseModel, EmailStr
from datetime import datetime

class PostBase(BaseModel):
    channel: str
    id_post: int
    time: datetime
    url: str

class NewPost(PostBase):
    pass