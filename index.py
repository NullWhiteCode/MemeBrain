"""SQLite-backed persistence for indexed library files."""

import sqlite3
import time
from pathlib import Path

from library import index_library


DATABASE_PATH = Path("database") / "memebrain.db"


class LibraryItem(dict):
    """Typed dict for indexed library items."""
    filename: str
    path: Path
    relative_path: Path
    folder: Path


def _get_connection() -> sqlite3.Connection:
    """Return a connection to the local database."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DATABASE_PATH))


def setup_database() -> None:
    """Create the files table if it does not already exist."""
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS files("
            "id INTEGER PRIMARY KEY, "
            "path TEXT UNIQUE, "
            "modified_time REAL, "
            "file_size INTEGER, "
            "indexed_time REAL, "
            "status TEXT"
            ")"
        )
        con.commit()
    finally:
        con.close()


def file_lookup(path: Path) -> tuple | None:
    """Return the database row for *path*, or None if it is not indexed."""
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM files WHERE path = ?",
            (str(path),),
        )
        return cur.fetchone()
    finally:
        con.close()


def insert_file(path: Path) -> None:
    """Insert a new file entry into the index database."""
    stats = path.stat()
    con = _get_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO files
                (path, modified_time, file_size, indexed_time, status)
                VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(path),
                stats.st_mtime,
                stats.st_size,
                time.time(),
                "indexed",
            ),
        )
        con.commit()
    finally:
        con.close()


def store_library_index(library_index: list[dict]) -> None:
    """Insert any indexed files that are not yet in the database."""
    for item in library_index:
        path = item["path"]
        if file_lookup(path) is None:
            insert_file(path)


def index_folder(library_path: str | Path) -> None:
    """Index every supported image under *library_path* into the database."""
    library_index = index_library(library_path)
    store_library_index(library_index)


def set_database_path(path: str | Path) -> None:
    """Override the default database path (useful for testing)."""
    global DATABASE_PATH
    DATABASE_PATH = Path(path)


if __name__ == "__main__":
    setup_database()
    library = Path(r"E:\Null\Pictures\Spicy Memes")
    index_folder(library)
