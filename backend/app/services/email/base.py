from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    async def send_otp(self, to_email: str, code: str, purpose: str) -> None:
        """Send a one-time verification code to to_email. purpose is
        'registration' or 'password_reset', useful for subject/copy."""
        raise NotImplementedError
