"""Extract and format metadata for image files."""

import mimetypes
from datetime import datetime
from pathlib import Path

from PIL import Image


def get_image_metadata(image_path):
    """Return display-ready metadata for an image, or None if it is missing."""
    image_path = Path(image_path)

    if not image_path.is_file():
        return None

    file_stats = image_path.stat()

    with Image.open(image_path) as image:
        return {
            "filename": image_path.name,
            "extension": image_path.suffix.lower(),
            "filesize": format_filesize(file_stats.st_size),
            "modified": format_timestamp(file_stats.st_mtime),
            "created": format_timestamp(file_stats.st_birthtime),
            "mime_type": (
                mimetypes.guess_type(str(image_path))[0]
                or "Unknown"
            ),
            "dimensions": f"{image.width} × {image.height}",
            "mode": image.mode,
            "animated": getattr(image, "is_animated", False),
        }


def format_filesize(filesize):
    """Convert a byte count into a human-readable file size."""
    for unit in ("B", "KB", "MB"):
        if filesize < 1024.0:
            return f"{filesize:.2f} {unit}"

        filesize /= 1024.0

    return f"{filesize:.2f} GB"


def format_timestamp(timestamp):
    """Convert a filesystem timestamp into a display-friendly string."""
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%Y-%m-%d %H:%M:%S")