
def graph():
    pass

class Node():
    """Noeud contenant le poids, les liens, ..."""
    
    def __init__(self, url, links:list):
        """
        Parameters
        ----------
        url:str
        links:list
            Listes des liens sur la page
        """

class Graph:
    """Graphe contenant toutes les pages"""
    
    def __init__(self, pages:list):
        """
        Parameters
        ----------
        pages:list
            Liste des pages existantes
        """
        
        self.pages = pages
        
        conn = sqlite3.connect("words.db")
        cursor = conn.cursor()
        self.nodes = []
        for url in pages:
            cursor.execute("SELECT ")
        conn.close()

# https://web.stanford.edu/class/cs54n/handouts/24-GooglePageRankAlgorithm.pdf