from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "local_finder"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email / OTP
    EMAIL_PROVIDER: str = "console"  # "console" | "resend" | "sendgrid"
    RESEND_API_KEY: str = ""
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@localfinder.dev"
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 30

    # File storage
    STORAGE_BACKEND: str = "local"  # "local" for now; swap for "s3"/"cloudinary" later
    UPLOAD_DIR: str = "uploads/posts"
    MAX_PHOTOS_PER_POST: int = 3
    MAX_PHOTO_SIZE_MB: int = 5

    # Real-time notifications
    NOTIFY_RADIUS_KM: float = 5.0

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
