from web import WebScrapping, Stack

class Crawler():
    def __init__(self, start_url):
        self.url = start_url
        self.web = WebScrapping(url=self.url)

    def crawl_bfs(self):
        """
        Parcours en largeur (BFS) de la page web
        """
        stack = Stack()
        stack.push(self.url)
        visited = set()

        while not stack.is_empty():
            url = stack.pop(0)
            if url not in visited:
                visited.add(url)
                self.web.url = url
                balises = self.web.find_balise("a")
                for balise in balises:
                    if not "href" in balise[1]:
                        continue
                    if balise[1]["href"].startswith("#"):
                        continue
                    
                    new_url = self.web.urljoin(url, balise[1]["href"])
                    if new_url not in visited:
                        stack.push(new_url)
                        print(new_url)

if __name__ == "__main__":
    start_url = "https://webscraper.io/test-sites"
    crawler = Crawler(start_url)
    crawler.crawl_bfs()

# https://webscraper.io/test-sites
# https://www.w3schools.com/html/tryit.asp?filename=tryhtml_intro
