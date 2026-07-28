"""Tests for image metadata extraction."""

from pathlib import Path

from PIL import Image

from metadata import format_filesize, format_timestamp, get_image_metadata


class TestFormatFilesize:
    """format_filesize produces human-readable sizes."""

    def test_bytes(self) -> None:
        assert format_filesize(512) == "512.00 B"

    def test_kilobytes(self) -> None:
        assert format_filesize(2048) == "2.00 KB"

    def test_megabytes(self) -> None:
        assert format_filesize(2 * 1024 * 1024) == "2.00 MB"

    def test_gigabytes(self) -> None:
        gb_val = 3 * 1024 * 1024 * 1024
        result = format_filesize(gb_val)
        assert result.endswith(" GB")

    def test_exact_boundaries(self) -> None:
        assert format_filesize(0) == "0.00 B"
        assert format_filesize(1) == "1.00 B"
        assert format_filesize(1023) == "1023.00 B"


class TestFormatTimestamp:
    """format_timestamp produces ISO-like date strings."""

    def test_known_timestamp(self) -> None:
        # 2024-01-15 10:30:00 UTC = 1705312200.0
        result = format_timestamp(1705312200.0)
        # The exact output depends on locale/timezone, so check the format pattern
        assert "2024" in result
        assert "-01-15" in result or "-01-" in result
        assert ":" in result


class TestGetImageMetadata:
    """get_image_metadata for real image files."""

    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        assert get_image_metadata(tmp_path / "nonexistent.png") is None

    def test_basic_metadata(self, tmp_path: Path) -> None:
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 200), color="red")
        img.save(img_path)

        meta = get_image_metadata(img_path)
        assert meta is not None
        assert meta["filename"] == "test.png"
        assert meta["extension"] == ".png"
        assert "100 x 200" in meta["dimensions"]
        assert meta["mode"] == "RGB"
        assert meta["animated"] is False
        assert meta["mime_type"] == "image/png"

    def test_filesize_in_metadata(self, tmp_path: Path) -> None:
        img_path = tmp_path / "size.png"
        img = Image.new("RGB", (10, 10))
        img.save(img_path)
        meta = get_image_metadata(img_path)
        assert meta is not None
        assert "B" in meta["filesize"]

    def test_rgba_mode(self, tmp_path: Path) -> None:
        img_path = tmp_path / "rgba.png"
        img = Image.new("RGBA", (50, 50), color=(255, 0, 0, 128))
        img.save(img_path)
        meta = get_image_metadata(img_path)
        assert meta is not None
        assert meta["mode"] == "RGBA"

    def test_jpeg_metadata(self, tmp_path: Path) -> None:
        img_path = tmp_path / "test.jpg"
        img = Image.new("RGB", (640, 480), color="blue")
        img.save(img_path, "JPEG")
        meta = get_image_metadata(img_path)
        assert meta is not None
        assert meta["extension"] == ".jpg"
        assert "640 x 480" in meta["dimensions"]
        assert meta["mime_type"] in ("image/jpeg",)
