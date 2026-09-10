import motor.motor_asyncio
from beanie import init_beanie

from app.config import settings
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.otp import OtpVerification
from app.models.post import Post
from app.models.user import User

_client: motor.motor_asyncio.AsyncIOMotorClient | None = None


async def init_db() -> None:
    global _client
    # tz_aware=True is important: without it, pymongo/motor returns naive
    # datetimes on read, which breaks any comparison against
    # datetime.now(timezone.utc) (e.g. OTP expiry checks) with a TypeError.
    _client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI, tz_aware=True)
    db = _client[settings.MONGO_DB_NAME]

    await init_beanie(
        database=db,
        document_models=[User, Post, Comment, Notification, OtpVerification],
    )

    # OTP expiry cleanup: a MongoDB TTL index deletes each document once the
    # current server time passes its own `expires_at` value — no cron job,
    # no background worker, Mongo handles it natively.
    await db["otp_verifications"].create_index("expires_at", expireAfterSeconds=0)
