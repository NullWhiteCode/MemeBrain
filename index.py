import sqlite3, time

def setupDatabase():
    con = sqlite3.connect("database/memebrain.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, path TEXT, modified_time REAL,  file_size INTEGER, indexed_time REAL, status TEXT)")

    con.commit()
    con.close()





if __name__ == "__main__":
    setupDatabase()



