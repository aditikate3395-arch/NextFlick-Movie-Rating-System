import sqlite3

connection = sqlite3.connect("nextflick.db")
cursor = connection.cursor()

cursor.execute("""
ALTER TABLE movies
ADD COLUMN genre TEXT
""")

connection.commit()
connection.close()

print("Category column added successfully")