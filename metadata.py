"""Extract and format metadata for image files."""

import mimetypes
from datetime import datetime
from pathlib import Path

from PIL import Image


ImageMetadata = dict


def _get_creation_time(file_stats: object) -> float | None:
    """Return the file creation time, or None when unavailable.

    macOS provides ``st_birthtime``; Linux does not reliably expose
    creation time, so this returns *st_mtime* as a best-effort fallback.
    """
    try:
        return file_stats.st_birthtime  # type: ignore[attr-defined]
    except AttributeError:
        try:
            return file_stats.st_ctime  # type: ignore[attr-defined]
        except AttributeError:
            return None


def get_image_metadata(image_path: str | Path) -> ImageMetadata | None:
    """Return display-ready metadata for an image, or None if it is missing."""
    image_path = Path(image_path)

    if not image_path.is_file():
        return None

    file_stats = image_path.stat()
    created_ts = _get_creation_time(file_stats)

    with Image.open(image_path) as image:
        return {
            "filename": image_path.name,
            "extension": image_path.suffix.lower(),
            "filesize": format_filesize(file_stats.st_size),
            "modified": format_timestamp(file_stats.st_mtime),
            "created": format_timestamp(created_ts) if created_ts else "Unknown",
            "mime_type": (
                mimetypes.guess_type(str(image_path))[0]
                or "Unknown"
            ),
            "dimensions": f"{image.width} x {image.height}",
            "mode": image.mode,
            "animated": getattr(image, "is_animated", False),
        }


def format_filesize(filesize: int) -> str:
    """Convert a byte count into a human-readable file size."""
    for unit in ("B", "KB", "MB"):
        if filesize < 1024.0:
            return f"{filesize:.2f} {unit}"
        filesize /= 1024.0
    return f"{filesize:.2f} GB"


def format_timestamp(timestamp: float) -> str:
    """Convert a filesystem timestamp into a display-friendly string."""
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%Y-%m-%d %H:%M:%S")
