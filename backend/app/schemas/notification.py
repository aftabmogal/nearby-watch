from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: str
    post_id: str
    message: str
    is_read: bool
    created_at: datetime
