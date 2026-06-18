import sqlite3
connection=sqlite3.connect("nextflick.db")
cursor=connection.cursor()

cursor.execute(""" create table if not exists movies(id integer primary key autoincrement,movie_name text,rating integer,genre text)""")

connection.commit()
connection.close()
print("Movies table created successfully")