from pydantic import BaseModel
from datetime import datetime

class UserGet(BaseModel):
    id: int
    age: int
    city: str
    country: str
    gender: int
    exp_group: int
    os: str
    source: str

    class Config:
        orm_mode = True


class PostGet(BaseModel):
    id: int
    text: str
    topic: str

    class Config:
        orm_mode = True


class FeedGet(BaseModel):
    user: UserGet
    post: PostGet
    action: str
    time: datetime

    class Config:
        orm_mode = True