from web import WebScrapping, Stack, RobotFileParser
from stockage import JSONStockage, TXTStockage, SQLStockage, get_domains_list
from indexer import Indexer

import time

class Crawler():
    def __init__(self, start_url=None):
        self.url = start_url
        self.web = WebScrapping(url=self.url)
        self.stack = Stack()  # Déplacer la pile ici
        self.sql_stockage = SQLStockage("urls.db")

    def crawl_bfs(self, debug=False):
        """
        Parcours en largeur (BFS) du site web à partir de l'URL de départ.
        """
        self.stack.string_to_stack(TXTStockage("urls_stack.txt").load())
        if self.stack.is_empty():
            if self.url:
                self.stack.push(self.url)
            else:
                self.stack.stack  = get_domains_list().copy()
        urls = self.sql_stockage.get_urls()
        if urls is None:
            visited = set()
        else:
            visited = set(urls)
        self.json_stockage = JSONStockage("urls.json")

        robot_parser = RobotFileParser()

        while not self.stack.is_empty():
            url = self.stack.pop(0)  # Utiliser self.stack

            if not self.web.is_valid_url(url):
                print(f"Invalid URL : {url}")
                logs.append(f"Invalid URL : {url}", timestamp=True)
                continue

            if url not in visited:
                visited.add(url)

                if debug:
                    start_robot = time.time()

                robot_parser.parse(url)
                if not robot_parser.is_allowed(url):
                    print(f"Blocked by robots.txt: {url}")
                    logs.append(f"Blocked by robots.txt: {url}", timestamp=True)
                    continue
                
                if debug:
                    end_robot = time.time()
                    print(f"Robot file parsed in {end_robot - start_robot:.2f} seconds")
                
                print("Visiting:", url)
                logs.append(f"Visiting : {url}", timestamp=True)
                self.web.url = url

                if debug:
                    start_web_scrap = time.time()
                self.web.elements = self.web.get_html_elements()
                self.sql_stockage.append_url(
                    url = url,
                    domain=self.web.find_domain(url),
                    title=self.web.find_balise("title")[0][2] if self.web.find_balise("title") != [] else "",
                    word_freq=self.web.get_content(),
                    is_valid=True,
                )
                
                # Indexer
                ind = Indexer()
                ind.index_db()
                
                balises = self.web.find_balise("a")
                if debug:
                    end_web_scrap = time.time()
                    print(f"Web scraping done in {end_web_scrap - start_web_scrap:.2f} seconds")

                valid_urls = []

                if debug:
                    start_link = time.time()
                    print("Links found:", len(balises))
                for balise in balises:
                    if not "href" in balise[1]:
                        continue
                    if balise[1]["href"].startswith("#"):
                        continue
                    if balise[1]["href"].startswith("mailto:"):
                        continue
                    
                    if debug:
                        start = time.time()
                    val = True
                    for file_end in self.web.file_exceptions:
                        if balise[1]["href"].endswith(file_end):
                            break
                    else:
                        val = False
                    if debug:  
                        end = time.time()
                        print(f"Link validation done in {end - start:.2f} seconds")

                    if val:
                        continue

                    if debug:
                        start = time.time()
                    new_url = self.web.urljoin(url, balise[1]["href"])
                    if debug:
                        end = time.time()
                        print(f"URL join done in {end - start:.2f} seconds")

                    if debug:
                        start = time.time()
                    if new_url not in visited and self.web.is_valide_url_format(new_url) and new_url not in self.stack.stack:
                        self.stack.push(new_url)  # Utiliser self.stack
                    valid_urls.append(new_url)
                    if debug:
                        end = time.time()
                        print(f"Link added to stack in {end - start:.2f} seconds")

                if debug:
                    end_link = time.time()
                    print(f"Links processed in {end_link - start_link:.2f} seconds")

                # Ajouter les données à sauvegarder
                if debug:
                    start_json = time.time()
                self.json_stockage.data_append(url, valid_urls)
                if debug:
                    end_json = time.time()
                    print(f"Data saved in JSON in {end_json - start_json:.2f} seconds")


if __name__ == "__main__":
    start_url = None #"https://fr.wikipedia.org/wiki/Test"
    logs = TXTStockage("logs.txt")
    logs.append(f"Début du scraping, url de départ : {start_url}", timestamp=True)

    crawler = Crawler(start_url)
    try:
        crawler.crawl_bfs(debug=True)
    except Exception as e:
        print(e)
        text_stockage = TXTStockage("urls_stack.txt")
        print("Sauvegarde de la pile dans le fichier urls_stack.txt")
        text_stockage.save(crawler.stack.stack_to_string())
        print("Sauvegarde des données dans le fichier urls.json")
        crawler.json_stockage.save_stock()
        print("Sauvegarde des données dans la base de données")
        for line in crawler.sql_stockage.to_save:
            crawler.sql_stockage.save_url(*line)
        logs.append("Sauvegarde des données ...", timestamp=True)


# https://webscraper.io/test-sites
# https://www.w3schools.com/html/tryit.asp?filename=tryhtml_intro