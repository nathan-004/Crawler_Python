from stockage import SQLStockage
from web import WebScrapping as ws
from display import ColorDisplay

import sqlite3
import json
from random import random

URLS = SQLStockage("urls.db").get_urls()
N = len(URLS)
console = ColorDisplay(debug=False)


class Node:
    """Représente une page"""

    def __init__(self, name, N):
        self.name = name
        conn = sqlite3.connect("urls.db")
        cursor = conn.cursor()
        cursor.execute("SELECT links FROM urls WHERE url = ?", (name,))
        self.links = []
        for balise in json.loads(cursor.fetchone()[0]): # ["a", {"href": "Lien relatif"}, "Contenu du lien"]
            try:
                self.links.append(ws.urljoin(ws, name, balise[1]["href"]))
            except Exception as e:
                console.warning(e)
        conn.close()

        self.value = 1/N

    def distribute(self, graph, d):
        """
        Distribue la valeur de PageRank vers les liens de cette page
        :d float: nombre entre 0 et 1 -> probabilité que l'utilisateur continue sur un lien de la page
        """
        pass

if __name__ == "__main__":
    console.log(f"Création du graphe | {len(URLS)} urls")
    graph = {url: Node(url, N) for url in URLS}
    console.quit()
    console.validate("Graphe terminé")

# https://web.stanford.edu/class/cs54n/handouts/24-GooglePageRankAlgorithm.pdf