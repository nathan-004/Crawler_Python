from stockage import TXTStockage

import requests
from urllib.parse import urlparse
import re

def remove_extra_whitespaces(text):
    """
    Removes extra whitespaces (more than one) from the input text.
    """
    return re.sub(r'\s{2,}', ' ', text).strip()  # Replace 2 or more spaces with a single space


class WebScrapping():
    def __init__(self, url="", languages=["en", "fr", None]):
        self.url = url
        if url != "":
            self.elements = self.get_html_elements()
        self.file_exceptions = [
            "zip",
            "pdf",
        ]
        self.logs = TXTStockage("logs.txt")

        self.validate_urls = set()
        self.not_validate_urls = set()

        self.languages = set(languages)

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
            response = requests.get(self.url)
        
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

        for idx, char in enumerate(html_text):
            if char == "\n":
                continue
                
            # print(f"Char: {char}, State: {state}, Current Start: {current_start}, Current Content: {current_content}, Current End: {current_end}")

            if state == "outside":
                if char == "<":
                    if html_text[idx+1] == "!":
                        state = "inside_comment"
                    elif html_text[idx+1] == "/":
                        state = "inside_close"
                        current_end = ""
                    else:
                        current_content = ""
                        state = "inside_open"
                else:
                    pass

            elif state == "inside_open":
                if char == ">":
                    stack.push((current_start.split()[0], "".join(current_start.split()[1:]))) # Ajouter la balise à la pile
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
                if char == "<":
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
            response = requests.head(url, timeout=5000, allow_redirects=True) # Timeout de 5 secondes
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
                self.not_validate_urls.add(url)
                print(f"Response: {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            # Prend en charge :
            # - ChunkedEncodingError
            # - ConnectionError, Timeout, TooManyRedirects…
            self.logs.append(f"Error: {url}", timestamp=True)
            return False
        
    def is_valide_url_format(self, url:str):
        """
        Vérifie rapidement si une URL est bien formée (sans requête réseau).
        """
        if url in self.validate_urls:
            return True
        elif url in self.not_validate_urls:
            return False

        parsed = urlparse(url)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return True
        else:
            #self.not_validate_urls.add(url)
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

class Stack():
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self, index=-1):
        if not self.is_empty():
            return self.stack.pop(index)
        else:
            raise Exception("Stack is empty")
        
    def last_balise(self, balise_name):
        # Find the last balise in the stack with the same name
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == balise_name:
                return self.pop(i)
        return None

    def is_empty(self):
        return len(self.stack) == 0
    
    def stack_to_string(self):
        """
        Retourne la pile sous forme de chaîne de caractères
        """
        return "\n".join([str(i) for i in self.stack])
    
    def string_to_stack(self, string):
        """
        Remplit la pile à partir d'une chaîne de caractères
        """
        self.stack = []
        for i in string.split("\n"):
            if i != "":
                try:
                    self.push(eval(i))
                except SyntaxError:
                    self.push(i)

if __name__ == "__main__":
    a = WebScrapping(url="https://webscraper.io/test-sites")

    # print(a.find_balise("a"))

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

# https://webscraper.io/test-sites
# https://www.w3schools.com/html/tryit.asp?filename=tryhtml_intro
