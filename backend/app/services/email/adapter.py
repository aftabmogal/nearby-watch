from app.config import settings
from app.services.email.base import EmailProvider
from app.services.email.console_provider import ConsoleEmailProvider
from app.services.email.resend_provider import ResendEmailProvider
from app.services.email.sendgrid_provider import SendgridEmailProvider


def get_email_provider() -> EmailProvider:
    provider = settings.EMAIL_PROVIDER.lower().strip()
    if provider == "resend":
        return ResendEmailProvider()
    if provider == "sendgrid":
        return SendgridEmailProvider()
    return ConsoleEmailProvider()
