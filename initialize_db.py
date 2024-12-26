import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE notams(
                notam_db_id INTEGER PRIMARY KEY,
                notam_id TEXT,
                notam_text TEXT UNIQUE,
                created_at TEXT,
                is_sent INTEGER
               )""")

cursor.execute("""CREATE TABLE coordinates(
                id INTEGER PRIMARY KEY,
                latitude REAL,
                longitude REAL,
                radius REAL,
                notam_db_id INTEGER,
                FOREIGN KEY (notam_db_id) REFERENCES notams (notam_db_id) ON DELETE CASCADE
               )""")

cursor.execute("""CREATE TABLE db_variables(
                name TEXT PRIMARY KEY,
                value TEXT)
                """)

conn.commit()
conn.close()