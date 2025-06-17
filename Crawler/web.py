from stockage import TXTStockage

import requests
from urllib.parse import urlparse
import re

def remove_extra_whitespaces(text):
    """
    Removes extra whitespaces (more than one) from the input text.
    """
    return re.sub(r'\s{2,}', ' ', text).strip()  # Replace 2 or more spaces with a single space

def get_headers():
    return {
        'User-Agent': "SeekrBot/1.0 (https://github.com/nathan-004/search-engine)",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

class WebScrapping():

    TIMEOUT = 5 # En secondes
    ERROR_CODES = {
        403: "Forbidden",
        405: "Method Not Allowed",
        429: "Too Many Requests",
        404: "Not Found",
        501: "Not Implemented",
        503: "Service Unavailable",
        440: "Login Time-out",
        418: "I'm a teapot",
    }

    BALISES_EXCEPTIONS = set([
        "script",
        "style"
    ])

    def __init__(self, url="", languages=["en", "fr", None]):
        self.url = url
        self.file_exceptions = [
            "zip",
            "pdf",
        ]
        self.logs = TXTStockage("logs.txt")

        self.validate_urls = set()
        self.not_validate_urls = set()

        self.languages = set(languages)

        if url != "" and url is not None:
            self.elements = self.get_html_elements()

    def get_html_elements(self, url=None, html_text=None):
        """
        Définir dans que état le programme est à chaque moment : 
            outside -> Tu lis du texte normal.
            inside_open -> Tu lis le nom et les attributs d'une balise ouverte <div class="...">.
            inside_close -> Tu lis une balise fermante </div>.
            inside_content -> Tu lis le contenu entre <div> ... </div>.
            inside_comment -> Tu lis un commentaire <!-- ... -->.
        Détecter les balises autofermantes :
            Détecter />
        Lire les atributs d'une balise :
            <div class="..."> -> class="..."
        Utiliser une pile pour stocker les balises
        """

        if url is None:
            url = self.url

        if url != "":
            response = requests.get(self.url, headers=get_headers())
        
            if response.status_code != 200:
                raise Exception(f"Failed to load page: {response.status_code}")
        
        if html_text is None:
            html_text = response.text

        state = "outside"
        elements = []
        current_start = "" # Nom de la balise + attributs
        current_content = ""
        current_end = "" # Nom de la balise fermante
        stack = Stack()
        comment = ""
        current_balise = ""

        for idx, char in enumerate(html_text):
            if char == "\n":
                continue
                
            # print(f"Char: {char}, State: {state}, Current Start: {current_start}, Current Content: {current_content}, Current End: {current_end}")

            if state == "outside":
                if char == "<":
                    if html_text[idx+1] == "!":
                        state = "inside_comment"
                    elif html_text[idx+1] == "/":
                        print(idx, html_text[idx-10:idx+10])
                        state = "inside_close"
                        current_end = ""
                    else:
                        current_content = ""
                        state = "inside_open"
                else:
                    pass

            elif state == "inside_open":
                if char == ">":
                    if current_start and current_start.strip():
                        parts = current_start.strip().split()
                        tag_name = parts[0]
                        tag_attrs = "".join(parts[1:]) if len(parts) > 1 else ""
                        stack.push((tag_name, tag_attrs))
                        current_balise = tag_name
                    else:
                        print(f"Erreur, Current start n'est pas présent")
                    state = "inside_content"
                    current_start = ""
                else:
                    current_start += char

            elif state == "inside_close":
                if char == ">":
                    try:
                        elements.append((*self.get_arguments(stack.last_balise(current_end)), current_content))
                    except TypeError as e:
                        print(f"Error: {e}, Current character : {idx}, Current page : {url}, Current start: {current_start}, Current end: {current_end}")
                        self.logs.append(f"Error: {e}, Current character : {idx}, Current page : {url}, Current start: {current_start}, Current end: {current_end}", timestamp=True)
                        pass
                    state = "outside"
                    current_start = ""
                    current_content = ""
                    current_end = ""
                else:
                    if char != "/":
                        current_end += char

            elif state == "inside_content":
                if current_balise in self.BALISES_EXCEPTIONS: # Gérer les balises comme script ou style
                    if char == "<":
                        if html_text[idx+2:idx+2+len(current_balise)] == current_balise:
                            state = "inside_close"
                elif char == "<":
                    if html_text[idx+1] == "/":
                        state = "inside_close"
                    elif html_text[idx+1] == "!":
                        state = "inside_comment"
                    else:
                        state = "inside_open"
                        current_content = ""
                else:
                    current_content += char
            
            elif state == "inside_comment":
                if char == ">":
                    elements.append(("comment", {}, comment))
                    comment = ""
                    state = "outside"
                else:
                    comment += char

        return elements
    
    def get_arguments(self, arguments):
        """
        Parametres
        ---------
        arguments:tuple
            Nom de la balise,
            Arguments de la balise -> "class="container" id="main",

        Retourne
        -------
        tuple
            (nom_balise:str, arguments:dict)
        """

        balise_name = arguments[0]

        current_arg_name = ""
        current_arg_value = ""
        name = True
        value = False

        arguments_ = {}

        for i in range(len(arguments[1])):
            #print(f"Char: {arguments[1][i]}, Name: {name}, Value: {value}, Current Arg Name: {current_arg_name}, Current Arg Value: {current_arg_value}")
            if arguments[1][i] == "=":
                value = True
                name = False
                continue
            elif arguments[1][i] == " ":
                if name:
                    continue
            elif arguments[1][i] == '"':
                if value:
                    if current_arg_value != "":
                        arguments_[current_arg_name] = current_arg_value
                        current_arg_name = ""
                        current_arg_value = ""
                        value = False
                        name = True
                    continue
                else:
                    if current_arg_name == "":
                        continue
                    name = True
                    value = False
                    continue
            
            if name:
                current_arg_name += arguments[1][i]
            if value:
                current_arg_value += arguments[1][i]
        
        return (balise_name, arguments_)
    
    def find_balise(self, balise_name):
        """
        Parametres
        ---------
        balise_name:str
            Nom de la balise à trouver

        Retourne
        -------
        tuple
            (nom_balise:str, arguments:dict, content:str)
        """
        balises = []

        for element in self.elements:
            if element[0] == balise_name:
                balises.append(element)
        return balises
    
    def urljoin(self, url_base, url:str):
        """
        Parametres
        ---------
        url_base:str
            URL de la page courante
        url:str
            URL à joindre à l'URL de la page courante

        Retourne
        -------
        str
            URL jointe
        """
        if not url:
            return url_base
        if url.startswith("http"):
            return url
        elif url.startswith("../"):
            url_base = url_base.split("/")
            url_base = url_base[:-1]
            url_base = "/".join(url_base)
            return url_base + url[2:]
        elif url.startswith("/"):
            url_base = url_base.split("//")
            domain = url_base[1].split("/")[0]
            url_base = url_base[0] + "//" + domain
            return url_base + url
        elif url.startswith("./"):
            if not url_base.endswith("/"):
                url_base += "/"
            return "/".join(url_base.split("/")[:-1]) + url[2:]  # Supprime "./" et concatène avec le répertoire courant
        else:
            sep = "/" if url_base[-1] != "/" and url[0] != "/" else ""
            return url_base + sep + url
        
    def is_valid_url(self, url:str):
        """
        Parametres
        ---------
        url:str
            URL à vérifier

        Retourne
        -------
        bool
            True si l'URL est valide, False sinon
        """
        if url in self.validate_urls:
            return True
        elif url in self.not_validate_urls:
            return False

        try:
            response = requests.head(url, timeout=self.TIMEOUT, allow_redirects=True, headers=get_headers()) # Timeout de 5 secondes
            lang = response.headers['Content-language'] if 'Content-language' in response.headers else None

            if response.status_code == 200:
                if lang in self.languages:
                    self.validate_urls.add(url)
                    return True
                else:
                    print(f"Language : {lang}")
                    self.not_validate_urls.add(url)
                    return False
            else:
                if response.status_code not in [429]:
                    self.not_validate_urls.add(url)
                print(f"Response: {response.status_code} {self.ERROR_CODES[response.status_code] if response.status_code in self.ERROR_CODES else None} | URL : {url}")
                return False
        except requests.exceptions.RequestException as e:
            # Prend en charge :
            # - ChunkedEncodingError
            # - ConnectionError, Timeout, TooManyRedirects…
            self.logs.append(f"Error: {url}", timestamp=True)
            print(e)
            return False
        
    def is_valide_url_format(self, url:str):
        """
        Vérifie rapidement si une URL est bien formée (sans requête réseau).
        """
        if url in self.validate_urls:
            return True
        elif url in self.not_validate_urls:
            return False

        if url.startswith("http") or url.startswith("https"):
            return True
        else:
            self.not_validate_urls.add(url)
            return False
        
    def find_domain(self, url:str):
        """
        Parametres
        ---------
        url:str
            URL à vérifier

        Retourne
        -------
        str
            Domaine de l'URL
        """
        if url.startswith("http"):
            url = url.split("//")
            return url[0] + "//" + url[1].split("/")[0]
        else:
            return url.split("/")[0]
        
    def find_path(self, url:str):
        """
        Parametres
        ---------
        url:str
            URL à vérifier

        Retourne
        -------
        str
            Chemin de l'URL
        """

        if url.startswith("http"):
            url = url.split("//")
            return "/" + "/".join(url[1].split("/")[1:])
        else:
            return "/" + "/".join(url.split("/")[1:])
        
    def get_content(self):
        """
        Retourne
        -------
        dict
            Le contenu de la page sous forme {"mot": occurences}
        """

        content = {}
        exceptions = set(["comment", "script", "style", "link", "meta", "head"])

        for element in self.elements:
            if element[0] in exceptions:
                continue
            
            for word in element[2].split():
                if word.lower() not in content:
                    content[word.lower()] = 0
                content[word.lower()] += 1
        
        return content    
        
class RobotFileParser():
    def __init__(self):
        self.disallowed = set()
        self.visited = set()
        self.crawler_name = "*"
        self.allowed = set()

    def parse(self, url):
        """
        Parse le fichier robots.txt à partir de l'URL donnée.
        :param url: URL du fichier robots.txt.
        """
        url = WebScrapping().find_domain(url)
        url_robot = url + "/robots.txt"

        if url in self.visited:
            return

        response = requests.get(url_robot)
        if response.status_code == 200:
            lines = response.text.splitlines()
            user_agent_block = False
            user_agent_used = False
            for line in lines:
                line = line.strip()
                if line.lower().startswith("user-agent:"):
                    user_agent = line.split(":")[1].strip()
                    user_agent_block = (user_agent == self.crawler_name or user_agent == "*" or not user_agent_used)
                elif user_agent_block and line.lower().startswith("disallow:"):
                    path = line.split(":")[1].strip()
                    self.disallowed.add(WebScrapping().urljoin(url_robot, path))
                    user_agent_used = True
                elif user_agent_block and line.lower().startswith("allow:"):
                    path = line.split(":")[1].strip()
                    self.allowed.add(WebScrapping().urljoin(url_robot, path))
                    user_agent_used = True
                else:
                    user_agent_used = True

        self.visited.add(url_robot)
    
    def is_allowed(self, url:str):
        """
        Vérifie si l'URL est autorisée par le fichier robots.txt.
        :param url: URL à vérifier.
        :return: True si l'URL est autorisée, False sinon.
        """
        if url in self.allowed:
            return True

        path = WebScrapping().find_path(url)
        domain = WebScrapping().find_domain(url)

        for disallowed_path in self.disallowed:
            if WebScrapping().find_domain(disallowed_path) == domain:
                if disallowed_path and path.startswith(WebScrapping().find_path(disallowed_path)):
                    return False
        return True

class Stack(list):

    def __init__(self):
        super().__init__()
        self.set = set()

    def push(self, item):
        if isinstance(item, list):
            for i in item:
                self.append_unique(i)
        else:
            self.append_unique(item)

    def append_unique(self, item):
        if item not in self.set:
            self.append(item)
            self.set.add(item)

    def pop(self, index=-1):
        if not self.is_empty():
            item = super().pop(index)
            self.set.discard(item)
            return item
        else:
            raise Exception("Stack is empty")

    def is_empty(self):
        return len(self) == 0

    def stack_to_string(self):
        return "\n".join([str(i) for i in self])

    def string_to_stack(self, string):
        self.clear()
        self.set.clear()
        for i in string.split("\n"):
            if i != "":
                try:
                    self.push(eval(i))
                except (SyntaxError, NameError):
                    self.push(i)

    def last_balise(self, balise_name):
        # Trouve et retire la dernière balise du nom donné
        for i in range(len(self)-1, -1, -1):
            if self[i][0] == balise_name:
                return super().pop(i)
        return None

if __name__ == "__main__":
    a = WebScrapping(url="https://bloomberg.com")

    

    """
    print(a.urljoin("https://webscraper.io/test-sites/test2", "/test-sites3"))
    print(a.urljoin("https://webscraper.io/test-sites", "../test-sites"))
    print(a.urljoin("https://webscraper.io/test-sites", "https://test-sites/test-sites"))

    print(a.find_domain("https://webscraper.io/test-sites/test2"))
    print(a.find_domain("https://test-sites/test-sites"))

    print(a.find_path("https://webscraper.io/test-sites/test2"))
    print(a.find_path("https://test-sites/test-sites"))

    print(a.get_content())

    print(a.is_valide_url_format("https://test.test2.com/"))

    print("-" * 50)
    a = WebScrapping(url="https://fr.wikipedia.org/wiki/Portail:Programmation_informatique")
    print(a.get_content())
    print(a.find_balise("a"))

    print(a.is_valid_url("https://indeed.com"))
    """

# https://webscraper.io/test-sites
# https://www.w3schools.com/html/tryit.asp?filename=tryhtml_intro
