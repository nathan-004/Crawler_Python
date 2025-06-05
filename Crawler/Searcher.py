import math
import sqlite3
import json


def prod(liste):
    res = liste[0]
    
    for n in liste[1:]:
        if n == 0:
            n = 0.1
        res = res * n
    
    return res

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
        words = query.lower().split(" ")
        
        conn = sqlite3.connect("words.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words WHERE word=?", (words[-1],))
        print(cursor.fetchall())
        cursor.execute('SELECT * FROM words')
        print(len(cursor.fetchall()))
        conn.close() 
        
        url_scores = {}
        
        for word in words:
            conn = sqlite3.connect("words.db")
            cursor = conn.cursor()
            cursor.execute("SELECT containers FROM words WHERE word=?", (word,))
            
            urls = json.loads(cursor.fetchone()[0])
            for url in urls:
                score = prod([self.keyword_searching_algorithm(w, url) for w in words])
                url_scores[url] = score
            conn.close()
        
        sorted_scores = dict(sorted(url_scores.items(), key=lambda item: item[1], reverse=False))

        return sorted_scores

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
        
        with open("parameters.json", "r") as f:
            N = json.load(f)["Index"]
        
        if df / N > 0.7:
            return 0
        
        return tf * math.log(N / df) if df != 0 else 0

if __name__ == "__main__":
    s = Searcher()
    results = s.search("")

    for url, score in results.items():
        print(f"{url} → score: {score}")
