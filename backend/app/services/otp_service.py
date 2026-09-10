import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.config import settings
from app.models.otp import OtpVerification
from app.services.email.adapter import get_email_provider

Purpose = Literal["registration", "password_reset"]


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def issue_otp(user_id: PydanticObjectId, email: str, purpose: Purpose) -> None:
    """Creates (or replaces) a pending OTP for this user+purpose and sends it.
    Enforces the resend cooldown. Only the hash is ever stored."""
    now = datetime.now(timezone.utc)

    existing = await OtpVerification.find_one(
        OtpVerification.user_id == user_id,
        OtpVerification.purpose == purpose,
        OtpVerification.verified == False,  # noqa: E712
    )
    if existing:
        elapsed = (now - existing.last_sent_at).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            wait = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {wait}s before requesting another code.",
            )
        await existing.delete()

    code = _generate_code()
    otp = OtpVerification(
        user_id=user_id,
        purpose=purpose,
        code_hash=_hash_code(code),
        expires_at=now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        last_sent_at=now,
    )
    await otp.insert()

    provider = get_email_provider()
    await provider.send_otp(email, code, purpose)


async def verify_otp(user_id: PydanticObjectId, purpose: Purpose, code: str) -> None:
    """Raises HTTPException on any failure. On success, deletes the OTP
    record (it's single-use)."""
    otp = await OtpVerification.find_one(
        OtpVerification.user_id == user_id,
        OtpVerification.purpose == purpose,
        OtpVerification.verified == False,  # noqa: E712
    )
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending verification found. Please request a new code.",
        )

    now = datetime.now(timezone.utc)
    if now > otp.expires_at:
        await otp.delete()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code expired. Please request a new one.",
        )

    if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        await otp.delete()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many incorrect attempts. Please request a new code.",
        )

    if _hash_code(code) != otp.code_hash:
        otp.attempts += 1
        await otp.save()
        remaining = settings.OTP_MAX_ATTEMPTS - otp.attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incorrect code. {remaining} attempt(s) left.",
        )

    otp.verified = True
    await otp.save()
    await otp.delete()
