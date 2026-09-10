import logging

from app.services.email.base import EmailProvider

logger = logging.getLogger("email.console")

_PURPOSE_LABEL = {
    "registration": "Verify your email",
    "password_reset": "Reset your password",
}


class ConsoleEmailProvider(EmailProvider):
    """Default provider for local development. No API key, no network call —
    just prints/logs the code so you can copy it straight from the terminal."""

    async def send_otp(self, to_email: str, code: str, purpose: str) -> None:
        label = _PURPOSE_LABEL.get(purpose, purpose)
        banner = (
            f"\n{'=' * 50}\n"
            f"[EMAIL OTP - DEV MODE]\n"
            f"To:      {to_email}\n"
            f"Purpose: {label}\n"
            f"Code:    {code}\n"
            f"{'=' * 50}\n"
        )
        logger.info(banner)
        print(banner)
