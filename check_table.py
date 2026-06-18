import sqlite3

connection = sqlite3.connect("nextflick.db")
cursor = connection.cursor()

cursor.execute("PRAGMA table_info(movies)")

print(cursor.fetchall())

connection.close()