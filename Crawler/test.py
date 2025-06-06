import json
import sqlite3



conn = sqlite3.connect("urls.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM urls")
lines = cursor.fetchall()
conn.close()

print("Nombre d'urls total", len(lines), sep=" : ")

conn = sqlite3.connect("words.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM words")
lines = cursor.fetchall()
conn.close()

print("Nombre de mots", len(lines), sep=" : ")