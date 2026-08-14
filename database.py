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