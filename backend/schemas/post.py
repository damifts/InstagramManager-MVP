from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    testo: str = Field(min_length=1, max_length=3000)
    social_target: str
    data_programmazione: datetime | None = None


class Post(PostCreate):
    id: str
    created_at: datetime
    status: str = "draft"
