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

        self.liens_entrant = []

    def distribute(self, graph, d):
        """
        Distribue la valeur de PageRank vers les liens de cette page
        :d float: nombre entre 0 et 1 -> probabilité que l'utilisateur continue sur un lien de la page
        """
        pass

    def page_rank_value(self, graph, d):
        """Modifie la valeur du noeud"""
        self.value = (1-d)/N + d * sum([graph[page].value/len(graph[page].links) for page in self.liens_entrant])

def page_rank(graph, i, d=0.85):
    for _ in range(i):
        for url in graph:
            graph[url].page_rank_value(graph, d)
    
    return sorted(graph, key=lambda url : graph[url].value, reverse=False)[:200]

if __name__ == "__main__":
    console.log(f"Création du graphe | {len(URLS)} urls")
    graph = {url: Node(url, N) for url in URLS}
    console.log("Création des liens entrants...")
    for url, node in graph.items():
        for link in node.links:
            if link in graph:
                graph[link].liens_entrant.append(url)
    console.quit()
    console.validate("Graphe terminé")

    console.log("PageRank...")
    sorted_urls = page_rank(graph, 50)
    console.validate("Classement des pages terminés...")

    for url in sorted_urls:
        print(url, "liens sortants:", len(graph[url].links), "liens entrants:", len(graph[url].liens_entrant))

# https://web.stanford.edu/class/cs54n/handouts/24-GooglePageRankAlgorithm.pdf