import requests

class WebScrapping():
    def __init__(self, url=""):
        self.url = url
        self.elements = self.get_html_elements()
        self.file_exceptions = [
            "zip",
            "pdf",
        ]

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
                        print(f"Error: {e}, Current character : {idx}, Current page : {url}, Stack: {stack.stack}")
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
                    elements.append((("comment", ""), comment))
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
        if requests.get(url).status_code == 200:
            return True
        else:
            return False

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

if __name__ == "__main__":
    a = WebScrapping(url="https://webscraper.io/test-sites")

    # print(a.find_balise("a"))

    print(a.urljoin("https://webscraper.io/test-sites/test2", "/test-sites3"))
    print(a.urljoin("https://webscraper.io/test-sites", "../test-sites"))
    print(a.urljoin("https://webscraper.io/test-sites", "https://test-sites/test-sites"))


# https://webscraper.io/test-sites
# https://www.w3schools.com/html/tryit.asp?filename=tryhtml_intro
