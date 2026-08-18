import sqlite3


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


def insertFile(file_data):
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()

    cur.execute("""
    INSERT INTO files
        (path, modified_time, file_size, indexed_time, status, file_hash)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            file_data["file_path"],
            file_data["modified_time"],
            file_data["file_size"],
            file_data["indexed_time"],
            file_data["status"],
            file_data["file_hash"],
        )
    )

    con.commit()
    con.close()


def updateFile(file_data):
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()

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
            file_data["modified_time"],
            file_data["file_size"],
            file_data["indexed_time"],
            file_data["status"],
            file_data["file_hash"],
            file_data["file_path"],
        )
    )

    con.commit()
    con.close()


