"""Tests for the configuration module."""

from pathlib import Path

import pytest

from config import (
    CONFIG_FILE,
    load_config,
    load_current_folder,
    load_library_path,
    save_config,
    save_current_folder,
    save_library_path,
)


class TestConfig:
    """read/write round-trips and edge cases."""

    def test_load_empty_when_no_file(self, tmp_path: Path) -> None:
        path = tmp_path / "config.json"
        assert not path.exists()
        # Patch CONFIG_FILE to use a non-existent path
        import config as cfg
        original = cfg.CONFIG_FILE
        cfg.CONFIG_FILE = path
        try:
            assert load_config() == {}
        finally:
            cfg.CONFIG_FILE = original

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        import config as cfg
        original = cfg.CONFIG_FILE
        cfg.CONFIG_FILE = tmp_path / "roundtrip.json"
        try:
            save_config({"key": "value", "nested": {"a": 1}})
            loaded = load_config()
            assert loaded == {"key": "value", "nested": {"a": 1}}
        finally:
            cfg.CONFIG_FILE = original

    def test_save_library_path(self, tmp_path: Path) -> None:
        import config as cfg
        original = cfg.CONFIG_FILE
        cfg.CONFIG_FILE = tmp_path / "libpath.json"
        try:
            save_library_path("/tmp/images")
            assert load_library_path() == "/tmp/images"
        finally:
            cfg.CONFIG_FILE = original

    def test_load_library_path_none(self, tmp_path: Path) -> None:
        import config as cfg
        original = cfg.CONFIG_FILE
        cfg.CONFIG_FILE = tmp_path / "empty.json"
        try:
            assert load_library_path() is None
        finally:
            cfg.CONFIG_FILE = original

    def test_save_current_folder(self, tmp_path: Path) -> None:
        import config as cfg
        original = cfg.CONFIG_FILE
        cfg.CONFIG_FILE = tmp_path / "folder.json"
        try:
            save_current_folder("memes/funny")
            assert load_current_folder() == "memes/funny"
        finally:
            cfg.CONFIG_FILE = original

    def test_current_folder_default_none(self, tmp_path: Path) -> None:
        import config as cfg
        original = cfg.CONFIG_FILE
        cfg.CONFIG_FILE = tmp_path / "nofolder.json"
        try:
            assert load_current_folder() is None
        finally:
            cfg.CONFIG_FILE = original

    def test_overwrite_previous_values(self, tmp_path: Path) -> None:
        import config as cfg
        original = cfg.CONFIG_FILE
        cfg.CONFIG_FILE = tmp_path / "overwrite.json"
        try:
            save_library_path("/first")
            save_library_path("/second")
            assert load_library_path() == "/second"
        finally:
            cfg.CONFIG_FILE = original

    def test_persists_json_indentation(self, tmp_path: Path) -> None:
        import config as cfg
        original = cfg.CONFIG_FILE
        cfg.CONFIG_FILE = tmp_path / "indent.json"
        try:
            save_library_path("/test")
            raw = cfg.CONFIG_FILE.read_text(encoding="utf-8")
            assert '"library_path"' in raw
            assert '  ' in raw  # two-space indent
        finally:
            cfg.CONFIG_FILE = original
