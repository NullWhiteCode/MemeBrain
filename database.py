import sqlite3


def setupConnection():
    con = sqlite3.connect("database/memebrain.db")
    con.execute("PRAGMA foreign_keys = ON")
    return con


def setupDatabase():
    con = setupConnection()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY, 
            path TEXT UNIQUE, 
            modified_time REAL, 
            file_size INTEGER, 
            indexed_time REAL, 
            status TEXT, 
            file_hash TEXT
        )
    """)

    con.commit()
    con.close()
    
    setupOCRDatabase()
    
    
def setupOCRDatabase():
    con = setupConnection()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ocr (
            id INTEGER PRIMARY KEY,
            file_id INTEGER UNIQUE,
            text TEXT,
            ocr_time REAL,
            engine TEXT,
            engine_version TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)

    con.commit()
    con.close()
    
    
def ocrRowLookup(image_path):
    file = fileLookup(image_path)
    file_id = file[0]
    
    con = setupConnection()
    cur = con.cursor()
    
    cur.execute("SELECT * FROM ocr WHERE file_id = ?",
                (file_id,)
                )
    
    result = cur.fetchone()
    con.close()
    
    return result
    

def fileLookup(path):
    con = setupConnection()
    cur = con.cursor()
    pathString = (str(path),)

    cur.execute("SELECT * FROM files WHERE path = ?", 
                pathString,
                )

    result = cur.fetchone()
    con.close()

    return result


def getStoredFiles():
    con = setupConnection()
    cur = con.cursor()

    cur.execute("SELECT * FROM files")

    result = cur.fetchall()
    con.close()

    return result


def markFileMissing(path):
    con = setupConnection()
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
    con = setupConnection()
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
    con = setupConnection()
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
    
    
def insertOCRData(ocr_data):
    con = setupConnection()
    cur = con.cursor()
    
    cur.execute("""
    INSERT INTO ocr
        (file_id, text, ocr_time, engine, engine_version)
        
    VALUES (?, ?, ?, ?, ?)
    
    ON CONFLICT(file_id) DO UPDATE SET
        text = excluded.text,
        ocr_time = excluded.ocr_time,
        engine = excluded.engine,
        engine_version = excluded.engine_version
    
        """, (
            ocr_data["file_id"],
            ocr_data["text"],
            ocr_data["ocr_time"],
            ocr_data["engine"],
            ocr_data["engine_version"],
        )
    )
    
    con.commit()
    con.close()
    

def updateFile(file_data):
    con = setupConnection()
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



    

        