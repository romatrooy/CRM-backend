"""
Сохранение аватара пользователя на локальный диск.
"""
import uuid
from pathlib import Path
from typing import Optional, Tuple

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_AVATAR_TYPES = frozenset({"image/jpeg", "image/png", "image/webp", "image/gif"})
_TYPE_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _avatars_dir() -> Path:
    return Path(settings.UPLOAD_ROOT) / "avatars"


def local_path_from_avatar_url(avatar_url: Optional[str]) -> Optional[Path]:
    """Путь к локальному файлу аватара, если URL выдан этим сервером."""
    if not avatar_url:
        return None
    prefix = f"{settings.UPLOAD_URL_PREFIX.rstrip('/')}/avatars/"
    if not avatar_url.startswith(prefix):
        return None
    name = avatar_url[len(prefix) :]
    if not name or "/" in name or ".." in name:
        return None
    path = _avatars_dir() / name
    try:
        path.resolve().relative_to(_avatars_dir().resolve())
    except ValueError:
        return None
    return path


async def save_user_avatar_file(user_id: int, file: UploadFile) -> Tuple[str, int]:
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допустимы только изображения: JPEG, PNG, WebP, GIF",
        )
    data = await file.read()
    if len(data) > settings.AVATAR_MAX_SIZE_BYTES:
        mb = settings.AVATAR_MAX_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл слишком большой (максимум {mb} МБ)",
        )
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пустой файл",
        )

    ext = _TYPE_TO_EXT[content_type]
    filename = f"{user_id}_{uuid.uuid4().hex}{ext}"
    av_dir = _avatars_dir()
    av_dir.mkdir(parents=True, exist_ok=True)
    dest = av_dir / filename

    async with aiofiles.open(dest, "wb") as out:
        await out.write(data)

    public_url = f"{settings.UPLOAD_URL_PREFIX.rstrip('/')}/avatars/{filename}"
    return public_url, len(data)
