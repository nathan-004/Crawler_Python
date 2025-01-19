import requests

class WEB_SCRAPPING():

    def __init__(self, url):
        self.url = url
        self.elements = self.ELEMENTS()

    def ELEMENTS(self, url=None):
        """
        Return a list of all the elements in the page

        Inputs
        -------
        url:str
            Url of the page

        Returns
        -------
        list
            All the elements in the page

        1. Get the html code of the page
        2. For every character :
            3. Find its type of element (<a>)
            4. Find its arguments (<a url="">)
            5. Find its content (<a>test</a>)
        """

        html_text = requests.get(self.url).text # Get the html code of the page

        # Init varialbes
        current = html_text[0]
        end = False
        start = False
        arguments = ""
        elements = []

        for char in html_text:
            # Check if it's the type of the element

            if current[-1] == "<" and char != "/": # It"s the start of an element
                start = True
            elif start and char == ">": # It"s the end of an opened element -> current is the arguments
                start = False
                arguments = current
                current = ""
            elif char == "/" and current[-1] == "<": # Check if it"s the start of the end
                end = True
            elif end and char == ">": # It's the end of the end
                res = self.get_arguments(arguments, current)
                elements.append({"type": res[0],"arg": res[1], "content": res[2]})
                current = ""
            current += char

        return elements

    def get_arguments(self, arguments, current):
        """
        Return the type of element, its arguments and its content

        Inputs
        ------
        arguments:str
            start of the element -> " <a class=gb1 href="https://mail.google.com/mail/?tab=wm"
        current:str
            content of the element -> ">Gmail</a"

        Returns
        -------
        tuple
            (element:str, arguments:list, content:str)
        """

        type_ = ""
        content = ""
        start = False
        end = False

        # Get the type of element
        for index, char in enumerate(arguments):
            if char == "<" and not start: # The start of the html element
                start = True
                continue

            if start and not end:
                if char == " ":
                    end = True
                    continue
                type_ += char

            if end:
                break

        argument = arguments[index:].split(" ")[1:]

        content = current.split("<")[0][1:]

        return (type_, argument, content)

    def find(self, type_):
        """
        Returns a list of all the elements `type_` in the page

        Inputs
        ------
        type:str
            The type of elements to find

        Returns
        -------
        list
            All the element in the page
        """

        found = []

        for el in self.elements:
            if el["type"] == type_:
                found.append(el)

        return found

    def get_contents(self, url=None):
        """
        Return a dict of all the contents in the page : for example - "test" and a score

        Returns
        -------
        dict
            {"keyword" : score}
        """

        # Define the lists of important balises : title, strong, ...
balises = {
    "h1": 10,  # Titre principal, très important
    "h2": 9,   # Sous-titre principal
    "h3": 8,   # Niveau inférieur de titre
    "strong": 7,  # Texte fortement accentué
    "b": 6,       # Texte en gras
    "em": 6,      # Texte mis en emphase
    "mark": 5,    # Texte surligné
    "u": 4,       # Texte souligné
    "i": 3,       # Texte en italique
    "small": 2    # Texte en plus petit
}
