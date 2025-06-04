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
        """Make the database with every word, commit every 50 urls"""
        sql = SQLStockage(db_name)
        donnees = sql.load_all_urls()[self.index:]
        buffer = []

        for line in donnees:
            self.index += 1
            url = line[0]
            words = json.loads(line[3])
            total = sum(words.values())
            buffer.append((url, words))

            if len(buffer) == 50:
                self._commit_buffer(buffer)
                buffer = []
                print(self.index)
            
            self.parameters.save({"Index": self.index})

        # Commit any remaining urls in buffer
        if buffer:
            self._commit_buffer(buffer)
            self.parameters.save({"Index": self.index})

        print(len(donnees))

    def _commit_buffer(self, buffer):
        """Ajoute les mots de 50 urls à la base de données en une fois (optimisé)"""
        conn = sqlite3.connect(self.filename)
        cursor = conn.cursor()
        try:
            for url, words in buffer:
                for word, freq_word in words.items():
                    cursor.execute("SELECT containers FROM words WHERE word=?", (word,))
                    row = cursor.fetchone()
                    if row is None:
                        containers = json.dumps({url: freq_word})
                        cursor.execute(
                            "INSERT INTO words (word, containers) VALUES (?, ?)",
                            (word, containers)
                        )
                    else:
                        containers = json.loads(row[0])
                        containers[url] = freq_word
                        cursor.execute(
                            "UPDATE words SET containers=? WHERE word=?",
                            (json.dumps(containers), word)
                        )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'insertion en lot: {e}")
        finally:
            conn.close()
    
    def get_line(self, word):
        """Retourne la ligne contenant le mot"""
        conn = sqlite3.connect(self.filename)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words WHERE word=?", (word,))
        rows = cursor.fetchone()
        conn.close()
        return rows
            
if __name__ == "__main__":
    idx = Indexer()
    idx.index_db()