import sqlite3, time
from pathlib import Path

from library import index_library


def setupDatabase():
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, path TEXT UNIQUE, modified_time REAL, file_size INTEGER, indexed_time REAL, status TEXT)")

    con.commit()
    con.close()


def fileLookup(path):
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()
    pathString = (str(path),)

    cur.execute("SELECT * FROM files WHERE path = ?", 
                pathString,
                )

    result = cur.fetchone()
    con.close()

    return result


def insertFile(path):
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()

    stats = path.stat()
    modified_time = stats.st_mtime
    file_size = stats.st_size
    file_path = str(path)
    indexed_time = time.time()
    status = "indexed"

    cur.execute("""
    INSERT INTO files
        (path, modified_time, file_size, indexed_time, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            file_path,
            modified_time,
            file_size,
            indexed_time,
            status,
        )
        )

    con.commit()
    con.close()


def file_changed(path, row):
    stats = path.stat()
    modified_time = stats.st_mtime
    file_size = stats.st_size

    if modified_time != row[2] or file_size != row[3]:
        return True
    return False


def updateFile(path):
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()

    stats = path.stat()
    indexed_time = time.time()

    cur.execute("""
    UPDATE 
        files

    SET
        modified_time = ?,
        file_size = ?,
        indexed_time = ?,
        status = ?

    WHERE
        path = ?
        """,
        (
            stats.st_mtime,
            stats.st_size,
            indexed_time,
            "indexed",
            str(path),
        )
    )

    con.commit()
    con.close()


def store_library_index(library_index):
    for item in library_index:
        path = item["path"]
        row = fileLookup(path)

        if row is None:
            insertFile(path)

        else:
            if file_changed(path, row):
                updateFile(path)


def index_folder(library_path):
    library_index = index_library(library_path)
    store_library_index(library_index)


if __name__ == "__main__":
    setupDatabase()

    library = Path(r"E:\Null\Pictures\Spicy Memes")
    index_folder(library)



