from datetime import datetime, timezone
from typing import List, Literal, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import GEOSPHERE, IndexModel

PostType = Literal["lost_pet", "lost_item", "found_item", "alert"]
PostStatus = Literal["active", "resolved"]


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float]  # [longitude, latitude] — GeoJSON order, NOT lat/lng


class Post(Document):
    author_id: PydanticObjectId
    type: PostType
    title: str
    description: str
    photos: List[str] = Field(default_factory=list)  # up to MAX_PHOTOS_PER_POST URLs
    location: GeoJSONPoint
    address_label: Optional[str] = None
    status: PostStatus = "active"
    report_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

    class Settings:
        name = "posts"
        indexes = [
            IndexModel([("location", GEOSPHERE)]),
            "author_id",
            "status",
        ]
