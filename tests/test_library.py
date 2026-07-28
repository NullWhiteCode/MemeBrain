"""Tests for the library module — indexing, searching, gallery building."""

from pathlib import Path

import pytest

from library import (
    SUPPORTED_EXTENSIONS,
    build_gallery,
    get_folder_contents,
    get_indexed_folder_items,
    index_library,
    search_library_index,
    split_path_parts,
)


class TestGetFolderContents:
    """get_folder_contents returns supported files and subdirectories."""

    def test_empty_directory(self, tmp_path: Path) -> None:
        files, dirs = get_folder_contents(tmp_path)
        assert files == []
        assert dirs == []

    def test_supported_images(self, tmp_path: Path) -> None:
        (tmp_path / "a.png").write_text("")
        (tmp_path / "b.jpg").write_text("")
        (tmp_path / "c.jpeg").write_text("")
        (tmp_path / "d.webp").write_text("")
        (tmp_path / "e.bmp").write_text("")
        (tmp_path / "f.gif").write_text("")

        files, dirs = get_folder_contents(tmp_path)
        assert len(files) == 6
        assert set(files) == {"a.png", "b.jpg", "c.jpeg", "d.webp", "e.bmp", "f.gif"}
        assert dirs == []

    def test_unsupported_extensions_skipped(self, tmp_path: Path) -> None:
        (tmp_path / "readme.txt").write_text("hello")
        (tmp_path / "data.csv").write_text("a,b,c")
        files, dirs = get_folder_contents(tmp_path)
        assert files == []
        assert dirs == []

    def test_mixed_files_and_directories(self, tmp_path: Path) -> None:
        (tmp_path / "photo.png").write_text("")
        (tmp_path / "docs").mkdir()
        (tmp_path / "videos").mkdir()
        (tmp_path / "notes.txt").write_text("")

        files, dirs = get_folder_contents(tmp_path)
        assert files == ["photo.png"]
        assert sorted(dirs) == ["docs", "videos"]

    def test_case_insensitive_extensions(self, tmp_path: Path) -> None:
        (tmp_path / "PHOTO.PNG").write_text("")
        (tmp_path / "Image.JPG").write_text("")
        (tmp_path / "Snake.WEBP").write_text("")
        files, dirs = get_folder_contents(tmp_path)
        assert len(files) == 3

    def test_non_existent_path(self) -> None:
        files, dirs = get_folder_contents("/nonexistent/path")
        assert files == []
        assert dirs == []

    def test_folder_with_mixed_nested(self, tmp_path: Path) -> None:
        (tmp_path / "root.png").write_text("")
        nested = tmp_path / "sub"
        nested.mkdir()
        (nested / "nested.jpg").write_text("")
        # get_folder_contents only looks one level deep
        files, dirs = get_folder_contents(tmp_path)
        assert files == ["root.png"]
        assert dirs == ["sub"]


class TestIndexLibrary:
    """index_library recursively finds all supported images."""

    def test_empty_library(self, tmp_path: Path) -> None:
        assert index_library(tmp_path) == []

    def test_recursive_indexing(self, tmp_path: Path) -> None:
        (tmp_path / "a.png").write_text("")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.jpg").write_text("")
        deep = sub / "deep"
        deep.mkdir()
        (deep / "c.gif").write_text("")

        index = index_library(tmp_path)
        assert len(index) == 3
        filenames = {item["filename"] for item in index}
        assert filenames == {"a.png", "b.jpg", "c.gif"}

    def test_skips_unsupported(self, tmp_path: Path) -> None:
        (tmp_path / "doc.txt").write_text("")
        (tmp_path / "script.py").write_text("")
        assert index_library(tmp_path) == []

    def test_index_items_have_expected_keys(self, tmp_path: Path) -> None:
        (tmp_path / "test.png").write_text("")
        index = index_library(tmp_path)
        assert len(index) == 1
        item = index[0]
        assert "filename" in item
        assert "path" in item
        assert "relative_path" in item
        assert "folder" in item

    def test_relative_paths_correct(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "img.png").write_text("")
        index = index_library(tmp_path)
        assert str(index[0]["relative_path"]) == "sub/img.png"
        assert str(index[0]["folder"]) == "sub"

    def test_no_library(self) -> None:
        assert index_library("/nonexistent") == []


class TestGetIndexedFolderItems:
    """get_indexed_folder_items filters index to a specific folder."""

    def test_matches_direct_children(self, tmp_path: Path) -> None:
        (tmp_path / "root.png").write_text("")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.png").write_text("")

        index = index_library(tmp_path)
        root_items = get_indexed_folder_items(index, tmp_path)
        sub_items = get_indexed_folder_items(index, sub)

        assert len(root_items) == 1
        assert root_items[0]["filename"] == "root.png"
        assert len(sub_items) == 1
        assert sub_items[0]["filename"] == "nested.png"

    def test_empty_folder(self, tmp_path: Path) -> None:
        (tmp_path / "img.png").write_text("")
        empty = tmp_path / "empty"
        empty.mkdir()
        index = index_library(tmp_path)
        items = get_indexed_folder_items(index, empty)
        assert items == []


class TestSearchLibraryIndex:
    """search_library_index filters by filename substring."""

    def test_case_insensitive(self) -> None:
        index = [
            {"filename": "Sunset.png"},
            {"filename": "sunrise.jpg"},
            {"filename": "Moon.gif"},
        ]
        result = search_library_index(index, "sun")
        assert len(result) == 2
        assert {r["filename"] for r in result} == {"Sunset.png", "sunrise.jpg"}

    def test_empty_pattern_returns_all(self) -> None:
        index = [{"filename": "a.png"}, {"filename": "b.jpg"}]
        result = search_library_index(index, "")
        assert len(result) == 2

    def test_no_matches(self) -> None:
        index = [{"filename": "cat.png"}, {"filename": "dog.jpg"}]
        assert search_library_index(index, "zebra") == []

    def test_partial_match(self) -> None:
        index = [{"filename": "vacation_2024.png"}, {"filename": "vacation_2025.jpg"}]
        result = search_library_index(index, "2024")
        assert len(result) == 1
        assert result[0]["filename"] == "vacation_2024.png"


class TestSplitPathParts:
    """split_path_parts builds breadcrumb data."""

    def test_root_path(self) -> None:
        assert split_path_parts("") == []

    def test_single_folder(self) -> None:
        result = split_path_parts("memes")
        assert len(result) == 1
        assert result[0] == {"display": "memes", "link": "memes"}

    def test_nested_folders(self) -> None:
        result = split_path_parts("memes/funny/cats")
        assert len(result) == 3
        assert result[0] == {"display": "memes", "link": "memes"}
        assert result[1] == {"display": "funny", "link": "memes/funny"}
        assert result[2] == {"display": "cats", "link": "memes/funny/cats"}

    def test_windows_separators_not_used(self) -> None:
        # Path normalises forward slashes regardless of platform
        result = split_path_parts("a/b/c")
        assert len(result) == 3

    def test_trailing_slash(self) -> None:
        result = split_path_parts("memes/")
        assert len(result) == 1
        assert result[0]["display"] == "memes"


class TestBuildGallery:
    """build_gallery creates template-ready entries."""

    def test_basic_gallery(self, tmp_path: Path) -> None:
        (tmp_path / "img.png").write_text("")
        index = index_library(tmp_path)
        gallery = build_gallery(tmp_path, index)
        assert len(gallery) == 1
        entry = gallery[0]
        assert entry["filename"] == "img.png"
        assert entry["relative_path"] == "img.png"
        assert entry["thumbnail"].endswith(".webp")
        assert entry["thumbnail_exists"] is False

    def test_empty_index(self, tmp_path: Path) -> None:
        assert build_gallery(tmp_path, []) == []

    def test_multiple_items(self, tmp_path: Path) -> None:
        (tmp_path / "a.png").write_text("")
        (tmp_path / "b.jpg").write_text("")
        index = index_library(tmp_path)
        gallery = build_gallery(tmp_path, index)
        assert len(gallery) == 2
        filenames = {g["filename"] for g in gallery}
        assert filenames == {"a.png", "b.jpg"}


class TestSupportedExtensions:
    """SUPPORTED_EXTENSIONS covers common image formats."""

    def test_contains_common_formats(self) -> None:
        expected = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
        for ext in expected:
            assert ext in SUPPORTED_EXTENSIONS, f"Missing: {ext}"
