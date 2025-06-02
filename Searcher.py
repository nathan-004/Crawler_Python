import math
import sqlite3
import json

class Searcher:
    """Find the most relevant urls from an input"""
    
    def __init__(self):
        pass
    
    def search(self, query:str):
        """
        Search urls that contains the most terms
        
        Parameters
        ----------
        query:str
        """
        words = query.split(" ")
        
        pass
        
    def keyword_searching_algorithm(self, word, url):
        """Use words.db to assign a score to an url with the word"""
        conn = sqlite3.connect("words.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words WHERE word=?", (word,))
        line = cursor.fetchone()
        conn.close()
        
        if line is None:
            return 0
        else:
            urls = json.loads(line[2])
            if not url in urls:
                return 0
            else:
                tf = urls[url]
                df = len(urls)
        conn = sqlite3.connect("urls.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM urls")
        N = len(cursor.fetchall())
        
        conn.close()
        return tf * math.log(N/df)
    
if __name__ == "__main__":
    s = Searcher()
    print(s.keyword_searching_algorithm("le", "https://fr.wikipedia.org/wiki/Test"))