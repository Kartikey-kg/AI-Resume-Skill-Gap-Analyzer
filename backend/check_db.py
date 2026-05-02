import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

for row in cursor.execute("SELECT * FROM analysis_results"):
    print(row)

conn.close()
