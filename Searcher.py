
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