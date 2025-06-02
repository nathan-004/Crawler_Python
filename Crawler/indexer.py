from stockage import SQLStockage, JSONStockage

import sqlite3
import json

class Indexer:
    """Stock every word with the websites they are in a database"""
    
    def __init__(self, filename="words.db"):
        self.filename = filename
        self.create_db()
        self.parameters = JSONStockage("parameters.json")
        self.par = self.parameters.load()
        
        if self.par == {}:
            self.parameters.save({"Index": 0})
            self.index = 0
        else:
            self.index = self.par["Index"]
    
    def create_db(self):
        """containers contient les urls qui contiennent ce mot avec la fréquence"""
        conn = sqlite3.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE,
                containers TEXT
            );
        ''')
        conn.commit()
        conn.close()
        
    def index_db(self, db_name="urls.db"):
        """Make the database with every word"""
        sql = SQLStockage(db_name)
        donnees = sql.load_all_urls()[self.index:]
        
        for line in donnees:
            self.index += 1
            url = line[0]
            words = json.loads(line[3])
            total = sum(words.values())
            
            for word in words:
                self.add_word(word, url, words[word])
            
            self.parameters.save({"Index": self.index})
            
        print(len(donnees))
    
    def get_line(self, word):
        """Retourne la ligne contenant le mot"""
        conn = sqlite3.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words WHERE word=?", (word,))
        rows = cursor.fetchone()
        conn.close()
        return rows
    
    def add_word(self, word, url, freq_word):
        """
        Ajoute une ligne pour le mot dans la base de données words.db si il n'existe pas sinon ajoute l'url dans la colonne containers
        
        Parameters
        ----------
        word:string
        url:string
        freq_word:float
            Nombre de mots divisé par le total de mots dans la page
        """
        
        line = self.get_line(word)
        
        if line is None:
            freq_word = json.dumps({url : freq_word})
            conn = sqlite3.connect(self.filename)
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO words (word, containers)
                    VALUES (?, ?)
                ''', (word, freq_word))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Erreur lors de l'insertion: {e}")
            finally:
                conn.close()
        else:
            line = list(line)
            line[2] = json.loads(line[2])
            conn = sqlite3.connect(self.filename)
            cursor = conn.cursor()
            line[2][url] = freq_word
            containers = json.dumps(line[2])
            try:
                cursor.execute('''
                    UPDATE words
                    SET containers = ?
                    WHERE word=?
                ''', (containers, word))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Erreur lors de l'insertion: {e}")
            finally:
                conn.close()
            
if __name__ == "__main__":
    idx = Indexer()
    idx.index_db()