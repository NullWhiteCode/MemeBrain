"""Create, cache, and manage background generation of image thumbnails."""

import hashlib
import threading
from pathlib import Path

from PIL import Image


THUMBNAIL_SIZE = (384, 384)
THUMBNAIL_CACHE_DIR = Path("cache") / "thumbnails"

_thumbnail_thread = None


def get_thumbnail_cache_path(image_path, library_path):
    """Return the deterministic cache path for an image's thumbnail."""
    image_path = Path(image_path)
    library_path = Path(library_path)

    relative_path = image_path.relative_to(library_path)

    cache_filename = hashlib.md5(
        relative_path.as_posix().encode("utf-8")
    ).hexdigest()

    return THUMBNAIL_CACHE_DIR / f"{cache_filename}.webp"


def build_image_thumbnail(image_path, library_path):
    """Return an existing thumbnail or generate and cache a new one.

    Returns None when the source image is missing or cannot be processed.
    """
    image_path = Path(image_path)

    if not image_path.is_file():
        return None

    cache_path = get_thumbnail_cache_path(image_path, library_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if cache_path.exists():
        return cache_path

    try:
        with Image.open(image_path) as image:
            image.thumbnail(THUMBNAIL_SIZE)
            image.save(cache_path, "WEBP")

        return cache_path

    except (OSError, ValueError) as error:
        print(f"Thumbnail failed: {image_path}")
        print(f"Reason: {error}")
        return None


def generate_library_thumbnails(library_index, library_path):
    """Generate any missing thumbnails for all indexed library images."""
    print(f"Generating thumbnails for {len(library_index)} images...")

    for item in library_index:
        build_image_thumbnail(item["path"], library_path)


def start_thumbnail_worker(library_index, library_path):
    """Start one background thumbnail worker unless one is already running."""
    global _thumbnail_thread

    if _thumbnail_thread is not None and _thumbnail_thread.is_alive():
        return _thumbnail_thread

    _thumbnail_thread = threading.Thread(
        target=generate_library_thumbnails,
        args=(library_index, library_path),
        name="thumbnail-worker",
        daemon=True,
    )

    _thumbnail_thread.start()
    return _thumbnail_thread