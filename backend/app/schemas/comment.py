from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    id: str
    post_id: str
    author_id: str
    author_name: str
    text: str
    created_at: datetime
