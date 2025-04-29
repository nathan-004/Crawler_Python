from web import WebScrapping, Stack, RobotFileParser
from stockage import JSONStockage, TXTStockage


class Crawler():
    def __init__(self, start_url):
        self.url = start_url
        self.web = WebScrapping(url=self.url)
        self.stack = Stack()  # Déplacer la pile ici

    def crawl_bfs(self):
        """
        Parcours en largeur (BFS) du site web à partir de l'URL de départ.
        """
        self.stack.string_to_stack(TXTStockage("urls_stack.txt").load())
        if self.stack.is_empty():
            self.stack.push(self.url)
        self.stack.push(self.url)  # Utiliser self.stack
        visited = set()
        self.json_stockage = JSONStockage("urls.json")

        robot_parser = RobotFileParser()

        while not self.stack.is_empty():
            url = self.stack.pop(0)  # Utiliser self.stack
            if url not in visited:
                visited.add(url)

                robot_parser.parse(url)
                if not robot_parser.is_allowed(url):
                    print(f"Blocked by robots.txt: {url}")
                    logs.append(f"Blocked by robots.txt: {url}", timestamp=True)
                    continue
                
                print("Visiting:", url)
                logs.append(f"Visiting : {url}", timestamp=True)
                self.web.url = url
                self.web.elements = self.web.get_html_elements()
                balises = self.web.find_balise("a")
                valid_urls = []

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
                    if new_url not in visited and self.web.is_valid_url(new_url) and new_url not in self.stack.stack:
                        self.stack.push(new_url)  # Utiliser self.stack
                    valid_urls.append(new_url)
            
                # Ajouter les données à sauvegarder
                self.json_stockage.data_append(url, valid_urls)

if __name__ == "__main__":
    start_url = "https://www.google.com/"
    logs = TXTStockage("logs.txt")
    logs.append(f"Début du scraping, url de départ : {start_url}", timestamp=True)

    crawler = Crawler(start_url)
    try:
        crawler.crawl_bfs()
    except KeyboardInterrupt:
        text_stockage = TXTStockage("urls_stack.txt")
        print("Sauvegarde de la pile dans le fichier urls_stack.txt")
        text_stockage.save(crawler.stack.stack_to_string())
        print("Sauvegarde des données dans le fichier urls.json")
        crawler.json_stockage.save_stock()
        logs.append("Sauvegarde des données ...", timestamp=True)


# https://webscraper.io/test-sites
# https://www.w3schools.com/html/tryit.asp?filename=tryhtml_intro