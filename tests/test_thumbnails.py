"""Tests for thumbnail generation and caching."""

from pathlib import Path

from PIL import Image

from thumbnails import (
    THUMBNAIL_SIZE,
    build_image_thumbnail,
    get_thumbnail_cache_path,
    THUMBNAIL_CACHE_DIR,
)


class TestGetThumbnailCachePath:
    """Deterministic path generation based on relative image path."""

    def test_returns_path_in_cache_dir(self, tmp_path: Path) -> None:
        library = tmp_path / "library"
        library.mkdir()
        img = library / "photo.png"
        img.write_text("")

        cache_path = get_thumbnail_cache_path(img, library)
        # The cache path should be under {THUMBNAIL_CACHE_DIR}/{hash}.webp
        relative_str = str(cache_path)
        assert "cache/thumbnails" in relative_str or "cache\\thumbnails" in relative_str
        assert cache_path.suffix == ".webp"

    def test_deterministic_output(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        img = library / "img.png"
        img.write_text("")

        p1 = get_thumbnail_cache_path(img, library)
        p2 = get_thumbnail_cache_path(img, library)
        assert p1 == p2

    def test_different_images_different_paths(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        a = library / "a.png"
        b = library / "b.png"
        a.write_text("")
        b.write_text("")

        p1 = get_thumbnail_cache_path(a, library)
        p2 = get_thumbnail_cache_path(b, library)
        assert p1 != p2

    def test_relative_path_based_hash(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        nested = library / "sub"
        nested.mkdir()
        img = nested / "photo.jpg"
        img.write_text("")

        cache_path = get_thumbnail_cache_path(img, library)
        assert cache_path.suffix == ".webp"
        # 32-character hex digest filename
        assert len(cache_path.stem) == 32


class TestBuildImageThumbnail:
    """Generation and caching of individual thumbnails."""

    def test_generates_thumbnail(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        img_path = library / "test.png"
        img = Image.new("RGB", (1000, 800))
        img.save(img_path)

        thumb = build_image_thumbnail(img_path, library)
        assert thumb is not None
        assert thumb.exists()
        assert thumb.suffix == ".webp"

        # Verify thumbnail respects size constraints
        with Image.open(thumb) as t:
            assert t.width <= THUMBNAIL_SIZE[0]
            assert t.height <= THUMBNAIL_SIZE[1]

    def test_returns_none_for_missing_source(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        result = build_image_thumbnail(
            library / "missing.png", library
        )
        assert result is None

    def test_uses_cached_thumbnail(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        img_path = library / "test.png"
        img = Image.new("RGB", (100, 100))
        img.save(img_path)

        first = build_image_thumbnail(img_path, library)
        assert first is not None

        # Delete source image but cache exists — should still return cached
        img_path.unlink()
        cached = build_image_thumbnail(img_path, library)
        assert cached is not None
        assert cached == first

    def test_thumbnail_downscales_large_images(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        img_path = library / "large.png"
        img = Image.new("RGB", (4000, 3000))
        img.save(img_path)

        thumb = build_image_thumbnail(img_path, library)
        assert thumb is not None

        with Image.open(thumb) as t:
            assert t.width <= THUMBNAIL_SIZE[0]
            assert t.height <= THUMBNAIL_SIZE[1]

    def test_thumbnail_downscales_portrait(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        img_path = library / "portrait.png"
        img = Image.new("RGB", (200, 2000))
        img.save(img_path)

        thumb = build_image_thumbnail(img_path, library)
        assert thumb is not None

        with Image.open(thumb) as t:
            assert t.width <= THUMBNAIL_SIZE[0]
            assert t.height <= THUMBNAIL_SIZE[1]

    def test_preserves_aspect_ratio(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        img_path = library / "wide.png"
        img = Image.new("RGB", (1920, 1080))
        img.save(img_path)

        thumb = build_image_thumbnail(img_path, library)
        assert thumb is not None

        with Image.open(thumb) as t:
            w, h = t.size
            # Both dimensions should be <= THUMBNAIL_SIZE
            assert w <= THUMBNAIL_SIZE[0]
            assert h <= THUMBNAIL_SIZE[1]

    def test_thumbnail_cache_directory_created(self, tmp_path: Path) -> None:
        library = tmp_path / "lib"
        library.mkdir()
        img_path = library / "test.png"
        img = Image.new("RGB", (50, 50))
        img.save(img_path)

        build_image_thumbnail(img_path, library)
        # Cache directory should have been created
        cache_path = get_thumbnail_cache_path(img_path, library)
        assert cache_path.parent.exists()
