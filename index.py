import sqlite3, time


def createDatabase(path):
    stats = path.stat()
    modified_time = stats.st_mtime
    file_size = stats.st_size
    filePath = str(path)
    indexed_time = time.time()

    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, path TEXT, modified_time REAL,  file_size INTEGER, indexed_time REAL, status TEXT)")

    cur.execute("""
    INSERT INTO files
        (path, modified_time, file_size, indexed_time, status)
    VALUES (?, ?, ?, ?, ?)
""", (
    filePath,
    modified_time,
    file_size,
    indexed_time,
    "Indexed"
))
    con.commit()

    res = cur.execute("SELECT * FROM files")
    for row in res.fetchall():
        print(row)

    con.close()


from pathlib import Path

if __name__ == "__main__":
    test_path = Path(r"E:\Null\Pictures\Personal\Screenshot 2026-03-kkk31 005104.png")
    createDatabase(test_path)

