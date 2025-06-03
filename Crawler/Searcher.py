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
        words = query.lower().split(" ")

        max_score = 0
        max_url = ""
        
        conn = sqlite3.connect("words.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words WHERE word='film'")
        print(cursor.fetchall())
        #print([line[1] for line in cursor.fetchall()])
        conn.close() 
        
        
        for word in words:
            conn = sqlite3.connect("words.db")
            cursor = conn.cursor()
            cursor.execute("SELECT containers FROM words WHERE word=?", (word,))
            urls = json.loads(cursor.fetchone()[0])
            for url in urls:
                score = sum([self.keyword_searching_algorithm(w, url) for w in word])
                if score >= max_score:
                    max_score = score
                    max_url = url
            conn.close()

        return max_url

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
    print(s.search("film"))