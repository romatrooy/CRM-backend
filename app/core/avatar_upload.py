"""
Сохранение аватаров (пользователи, контакты) на локальный диск.
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

_USER_SUBDIR = "avatars"
_CONTACT_SUBDIR = "contact_avatars"


def _avatars_dir() -> Path:
    return Path(settings.UPLOAD_ROOT) / _USER_SUBDIR


def _contact_avatars_dir() -> Path:
    return Path(settings.UPLOAD_ROOT) / _CONTACT_SUBDIR


def local_path_from_avatar_url(avatar_url: Optional[str]) -> Optional[Path]:
    """Путь к локальному файлу аватара, если URL выдан этим сервером."""
    if not avatar_url:
        return None
    prefix = f"{settings.UPLOAD_URL_PREFIX.rstrip('/')}/{_USER_SUBDIR}/"
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


def local_path_from_contact_avatar_url(avatar_url: Optional[str]) -> Optional[Path]:
    """Путь к локальному файлу фото контакта, если URL выдан этим сервером."""
    if not avatar_url:
        return None
    prefix = f"{settings.UPLOAD_URL_PREFIX.rstrip('/')}/{_CONTACT_SUBDIR}/"
    if not avatar_url.startswith(prefix):
        return None
    name = avatar_url[len(prefix) :]
    if not name or "/" in name or ".." in name:
        return None
    path = _contact_avatars_dir() / name
    try:
        path.resolve().relative_to(_contact_avatars_dir().resolve())
    except ValueError:
        return None
    return path


async def _save_image_upload(
    subdir: str,
    base_dir: Path,
    id_prefix: str,
    file: UploadFile,
) -> Tuple[str, int]:
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
    filename = f"{id_prefix}_{uuid.uuid4().hex}{ext}"
    base_dir.mkdir(parents=True, exist_ok=True)
    dest = base_dir / filename

    async with aiofiles.open(dest, "wb") as out:
        await out.write(data)

    public_url = f"{settings.UPLOAD_URL_PREFIX.rstrip('/')}/{subdir}/{filename}"
    return public_url, len(data)


async def save_user_avatar_file(user_id: int, file: UploadFile) -> Tuple[str, int]:
    return await _save_image_upload(
        _USER_SUBDIR, _avatars_dir(), str(user_id), file
    )


async def save_contact_avatar_file(contact_id: int, file: UploadFile) -> Tuple[str, int]:
    return await _save_image_upload(
        _CONTACT_SUBDIR, _contact_avatars_dir(), str(contact_id), file
    )
