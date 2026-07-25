import sqlite3

connection = sqlite3.connect("users.db")
with open("schema.sql") as file:
    schema = file.read()
connection.executescript(schema)
connection.commit()
connection.close()