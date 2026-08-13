import hashlib
import sqlite3, time
from pathlib import Path

from library import index_library


def setupDatabase():
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, path TEXT UNIQUE, modified_time REAL, file_size INTEGER, indexed_time REAL, status TEXT, file_hash TEXT)")

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


def getStoredFiles():
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM files")

    result = cur.fetchall()
    con.close()

    return result


def pathCompare(library_index):
    stored_files = getStoredFiles()
    stored_paths = []
    current_paths = []

    for row in stored_files:
        stored_paths.append(row[1])

    for item in library_index:
        current_paths.append(str(item["path"]))

    for path in stored_paths:
        if path not in current_paths:
            markFileMissing(path)


def markFileMissing(path):
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()

    cur.execute("""
    UPDATE
        files

    SET
        status = ?

    WHERE
        path = ?

        """,
        (
            "missing",
            str(path),
        )
    )

    con.commit()
    con.close()


def markFileIndexed(path):
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()

    cur.execute("""
    UPDATE
        files

    SET
        status = ?

    WHERE
        path = ?

        """,
        (
            "indexed",
            str(path),
        )
    )

    con.commit()
    con.close()


def insertFile(path):
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()

    stats = path.stat()
    modified_time = stats.st_mtime
    file_size = stats.st_size
    file_path = str(path)
    indexed_time = time.time()
    status = "indexed"
    file_hash = calculate_file_hash(path)

    cur.execute("""
    INSERT INTO files
        (path, modified_time, file_size, indexed_time, status, file_hash)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            file_path,
            modified_time,
            file_size,
            indexed_time,
            status,
            file_hash,
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
    file_hash = calculate_file_hash(path)

    cur.execute("""
    UPDATE 
        files

    SET
        modified_time = ?,
        file_size = ?,
        indexed_time = ?,
        status = ?,
        file_hash = ?

    WHERE
        path = ?
        """,
        (
            stats.st_mtime,
            stats.st_size,
            indexed_time,
            "indexed",
            file_hash,
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

            if row[5] == "missing":
                markFileIndexed(path)


def calculate_file_hash(path):
    
    with path.open("rb") as file:
        hash_result = hashlib.file_digest(
            file, 
            hashlib.sha256,
        ).hexdigest()

    return hash_result


def getDuplicateGroups():
    stored_files = getStoredFiles()
    dict_groups = {}
    duplicate_groups = {}

    for file in stored_files:
        file_hash = file[6]
        file_path = file[1]

        if file_hash not in dict_groups:
            dict_groups[file_hash] = []

        dict_groups[file_hash].append(file_path)

        if len(dict_groups[file_hash]) > 1:
            duplicate_groups[file_hash] = dict_groups[file_hash]

    return duplicate_groups

    



        


def index_folder(library_path):
    library_index = index_library(library_path)
    store_library_index(library_index)


if __name__ == "__main__":
    setupDatabase()

    library = Path(r"F:\User Files\Pictures\Spicy Memes")
    library_index = index_library(library)

    store_library_index(library_index)
    pathCompare(library_index)
    getDuplicateGroups()

    print(getDuplicateGroups())








