from web import WebScrapping, RobotFileParser, Stack, LoadError
from stockage import get_blacklist
from display import ColorDisplay

from random import shuffle
import sqlite3
import json

current_blacklist = get_blacklist()
BLACKLIST = get_blacklist()

def get_general_frequency(word):
    """Retourne la fréquence d'apparition d'un mot dans des pages normales dans words.db"""

    conn = sqlite3.connect("words.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM words WHERE word=?", (word,))
    line = cursor.fetchone()
    conn.close()

    if line is None: # Mot n'existe pas
        return 0
    else:
        urls = json.loads(line[2])

    with open("parameters.json", "r") as f:
        total_urls = json.load(f)["Index"]

    return len(urls) / total_urls

class Filter:
    """Regarde si un site est considéré comme pornographique à partir d'une blacklist"""
    global_blacklist_content = {}
    blacklist_words_count = 0

    def train(self, blacklist):
        """
        Trouver les mots dont la fréquence est la plus élevée par rapport à des sites normaux

        Parameters
        ----------
        blacklist:list
            Liste de sites pornographiques
        """

        web = WebScrapping("")
        stack = Stack()
        shuffle(blacklist)
        stack.string_to_stack("\n".join(blacklist))
        console = ColorDisplay(True)

        while not stack.is_empty():
            url = stack.pop(0)
            web.url = url
            console.log(f"Visiting : {url}")
            try:
                web.elements = web.get_html_elements()
                web.console.quit()
            except LoadError as l:
                console.error(l)
                continue

            content = web.get_content()

            if content == {}:
                console.warning("Contenu vide")
                continue
            
            total = sum(content.values())
            if total == 1:
                console.warning("1 seul mot")
                continue

            for word in content:
                if get_general_frequency(word) > 0.05:
                    continue

                if not word in self.global_blacklist_content:
                    self.global_blacklist_content[word] = content[word]/total
                else:
                    self.global_blacklist_content[word] += content[word]/total
                self.blacklist_words_count += content[word]
            
            console.validate(sorted(self.global_blacklist_content, key= lambda word : self.global_blacklist_content[word], reverse=True)[:15 if len(self.global_blacklist_content) > 15 else len(self.global_blacklist_content)])

if __name__ == "__main__":
    f = Filter()
    try:
        f.train(current_blacklist)
    except (KeyboardInterrupt) as e:
        print(f.global_blacklist_content)
        print(sorted(f.global_blacklist_content, key= lambda word : f.global_blacklist_content[word], reverse=True))
        print(f.blacklist_words_count)