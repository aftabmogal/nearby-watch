import logging

import httpx

from app.config import settings
from app.services.email.base import EmailProvider

logger = logging.getLogger("email.resend")

_SUBJECTS = {
    "registration": "Verify your email",
    "password_reset": "Reset your password",
}


class ResendEmailProvider(EmailProvider):
    """Real email delivery via Resend (https://resend.com). Requires
    RESEND_API_KEY in the environment — set EMAIL_PROVIDER=resend to activate."""

    API_URL = "https://api.resend.com/emails"

    async def send_otp(self, to_email: str, code: str, purpose: str) -> None:
        if not settings.RESEND_API_KEY:
            logger.warning(
                "EMAIL_PROVIDER=resend but RESEND_API_KEY is not set; "
                "falling back to logging the code instead of sending it."
            )
            print(f"[RESEND - NOT CONFIGURED] OTP for {to_email}: {code}")
            return

        subject = _SUBJECTS.get(purpose, "Your verification code")
        html = (
            f"<p>Your verification code is <strong>{code}</strong>.</p>"
            f"<p>It expires in {settings.OTP_EXPIRY_MINUTES} minutes. "
            f"If you didn't request this, you can ignore this email.</p>"
        )
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.API_URL,
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                json={
                    "from": settings.EMAIL_FROM,
                    "to": [to_email],
                    "subject": subject,
                    "html": html,
                },
            )
            response.raise_for_status()
