import logging

import httpx

from app.config import settings
from app.services.email.base import EmailProvider

logger = logging.getLogger("email.sendgrid")

_SUBJECTS = {
    "registration": "Verify your email",
    "password_reset": "Reset your password",
}


class SendgridEmailProvider(EmailProvider):
    """Real email delivery via SendGrid. Requires SENDGRID_API_KEY in the
    environment — set EMAIL_PROVIDER=sendgrid to activate."""

    API_URL = "https://api.sendgrid.com/v3/mail/send"

    async def send_otp(self, to_email: str, code: str, purpose: str) -> None:
        if not settings.SENDGRID_API_KEY:
            logger.warning(
                "EMAIL_PROVIDER=sendgrid but SENDGRID_API_KEY is not set; "
                "falling back to logging the code instead of sending it."
            )
            print(f"[SENDGRID - NOT CONFIGURED] OTP for {to_email}: {code}")
            return

        subject = _SUBJECTS.get(purpose, "Your verification code")
        html = (
            f"<p>Your verification code is <strong>{code}</strong>.</p>"
            f"<p>It expires in {settings.OTP_EXPIRY_MINUTES} minutes.</p>"
        )
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": settings.EMAIL_FROM},
            "subject": subject,
            "content": [{"type": "text/html", "value": html}],
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.API_URL,
                headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"},
                json=payload,
            )
            response.raise_for_status()
