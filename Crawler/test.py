import json
import sqlite3
from colorama import *

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

with open("urls_stack.txt", 'r', encoding="utf-8") as file:
    data = file.read()

print("Nombre d'urls en attentes : ", len(data))