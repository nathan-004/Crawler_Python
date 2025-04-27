from web import WebScrapping, Stack

class Crawler():
    def __init__(self, start_url):
        self.url = start_url
        self.web = WebScrapping(url=self.url)

    def crawl_dfs(self):
        """
        Parcours en profondeur (DFS) du site web à partir de l'URL de départ.
        """
        stack = Stack()
        stack.push(self.url)
        visited = set()

        while not stack.is_empty():
            url = stack.pop()
            print("Visiting:", url)
            if url not in visited:
                visited.add(url)
                self.web.url = url
                self.web.elements = self.web.get_html_elements()
                balises = self.web.find_balise("a")
                for balise in balises:
                    if not "href" in balise[1]:
                        continue
                    if balise[1]["href"].startswith("#"):
                        continue
                    if balise[1]["href"].startswith("mailto:"):
                        continue
                    
                    new_url = self.web.urljoin(url, balise[1]["href"])
                    if new_url not in visited and self.web.is_valid_url(new_url) and new_url not in stack.stack:
                        stack.push(new_url)
                        #print(len(stack.stack),new_url, sep=" | ")
                    else:
                        #print("URL déjà visitée ou invalide:", new_url)
                        pass
            else:
                #print("URL déjà visitée:", url)
                pass
        print(stack.stack)

    def crawl_bfs(self):
        """
        Parcours en largeur (BFS) du site web à partir de l'URL de départ.
        """
        queue = Stack()
        queue.push(self.url)
        visited = set()

        while not queue.is_empty():
            url = queue.pop(0)
            print("Visiting:", url)
            if url not in visited:
                visited.add(url)
                self.web.url = url
                self.web.elements = self.web.get_html_elements()
                balises = self.web.find_balise("a")
                for balise in balises:
                    if not "href" in balise[1]:
                        continue
                    if balise[1]["href"].startswith("#"):
                        continue
                    if balise[1]["href"].startswith("mailto:"):
                        continue

                    val = True
                    for file_end in self.web.file_exceptions:
                        if balise[1]["href"].endswith(file_end):
                            break
                    else:
                        val = False

                    if val:
                        continue
                    
                    new_url = self.web.urljoin(url, balise[1]["href"])
                    if new_url not in visited and self.web.is_valid_url(new_url) and new_url not in queue.stack:
                        queue.push(new_url)
                        #print(len(queue.stack),new_url, sep=" | ")
                    else:
                        #print("URL déjà visitée ou invalide:", new_url)
                        pass
            else:
                #print("URL déjà visitée:", url)
                pass
        print(queue.stack)

if __name__ == "__main__":
    start_url = "https://webscraper.io/test-sites"
    crawler = Crawler(start_url)
    crawler.crawl_bfs()

# https://webscraper.io/test-sites
# https://www.w3schools.com/html/tryit.asp?filename=tryhtml_intro
