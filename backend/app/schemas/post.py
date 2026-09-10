from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class PostOut(BaseModel):
    id: str
    author_id: str
    author_name: str
    type: Literal["lost_pet", "lost_item", "found_item", "alert"]
    title: str
    description: str
    photos: List[str]
    latitude: float
    longitude: float
    address_label: Optional[str] = None
    status: Literal["active", "resolved"]
    report_count: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    distance_km: Optional[float] = None  # populated only on /posts/nearby


class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["active", "resolved"]] = None
