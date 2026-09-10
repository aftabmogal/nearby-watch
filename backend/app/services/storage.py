import os
import uuid

from fastapi import UploadFile

from app.config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _validate_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    return ext


async def save_file(file: UploadFile) -> str:
    """Saves an uploaded photo and returns its public URL.

    This is the ONLY function post-creation code calls. Swapping
    STORAGE_BACKEND to 's3'/'cloudinary' later means changing what happens
    inside this function (and delete_file below) — nothing in routers/posts.py
    needs to change.
    """
    if settings.STORAGE_BACKEND != "local":
        raise NotImplementedError(
            f"Storage backend '{settings.STORAGE_BACKEND}' is not implemented yet. "
            "Add the branch here when you're ready to move to S3/Cloudinary."
        )

    ext = _validate_extension(file.filename or "")
    contents = await file.read()
    max_bytes = settings.MAX_PHOTO_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise ValueError(f"File too large (max {settings.MAX_PHOTO_SIZE_MB}MB)")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(contents)

    return f"/uploads/posts/{filename}"


def delete_file(url: str) -> None:
    if settings.STORAGE_BACKEND != "local":
        return
    filename = os.path.basename(url)
    path = os.path.join(settings.UPLOAD_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
