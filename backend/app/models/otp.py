from datetime import datetime, timezone
from typing import Literal

from beanie import Document, PydanticObjectId
from pydantic import Field


class OtpVerification(Document):
    user_id: PydanticObjectId
    purpose: Literal["registration", "password_reset"]
    code_hash: str
    attempts: int = 0
    verified: bool = False
    # A MongoDB TTL index on this field (expireAfterSeconds=0) auto-deletes
    # the document once the current time passes expires_at — see database.py.
    expires_at: datetime
    last_sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "otp_verifications"
        indexes = ["user_id"]
