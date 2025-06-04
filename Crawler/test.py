import json
import sqlite3

with open("urls.json", "r") as f:
    a = json.load(f)

print(list(a.keys())[200])

conn = sqlite3.connect("urls.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM urls")
lines = cursor.fetchall()
conn.close()

print(len(lines))