from web import WEB_SCRAPPING
import random
import json

class Crawler():

    def __init__(self, url):
        self.url = url
        self.web = WEB_SCRAPPING(url)
        self.queue = Queue()
        self.database = DATABASE("database.json", True) # Database containing all the urls
        self.visited = self.database.get_JSON()

        # Database architecture
        # "url_example" : {"pointers": 0, "contents": {"champignon": Score donné pour un sujet dépendant du type de balise utilisée}}

    def launch(self, iterations, url=None):
        """
        Launch the bot on the given url

        Inputs
        ------
        url:str
            url of the first website
        iterations:int
            number of times the bot will run

        Returns
        -------
        None

        1. Look at the page
        2. Get the links
        3. Put them in a queue file
        4. Take a link in the queue
        5. Repeat
        """

        done = []

        if url is None:
            url = self.url

        for i in range(iterations):
            while url in done:
                url = self.queue.get()
            urls = self.get_links(url)

            for a in urls:
                if a in self.visited:
                    self.visited[a]["pointers"] += 1
                else:
                    self.visited[a] = {"pointers" : 1, "contents": {}}

                if not self.queue.is_element(a) and not (a in done):
                    self.queue.add(a)

            print(i, len(done), len(urls), "liens", "|", url, sep=" ")

            if url in self.visited:
                pass
            else:
                self.visited[url] = {"pointeurs": 1, "contents": {}}

            done.append(url)
            url = self.queue.get()

        self.database.add_JSON(self.visited)

    def get_links(self, url=None):
        """
        Given an url, return a list of all the url in the page

        Inputs
        ------
        url:str
            url of the website

        Returns
        -------
        list
            list of all the url in the page
        """

        if url is None:
            url = self.url

        self.web.elements = self.web.ELEMENTS(url)
        links = self.web.find("a")
        urls = []

        for el in links:
            for arg in el["arg"]:
                if arg[:4] == "href":
                    a = arg[6:-1]
                    if a[:8] != "https://":
                        a = url + a
                    if a in self.visited:
                        continue
                    urls.append(a)

        return urls


class Queue():

    def __init__(self, queue = []):
        self.queue = queue
        self.save_url = "https://jeunes.nouvelle-aquitaine.fr/formation/au-lycee/lycee-connecte"

    def is_element(self, element):
        """
        Return True if the element is in the queue else False

        Inputs
        ------
        element
            Element to look at

        Returns
        -------
        bool
            True if element else False
        """

        for el in self.queue:
            if el == element:
                return True
            else:
                return False

    def add(self, element):
        """
        Add an element to the queue
        """

        self.queue.append(element)

    def get(self, index=0):
        """
        Get and delete an element of the queue
        """
        try:
            return self.queue.pop(index)
        except IndexError:
            return self.save_url


class DATABASE():

    def __init__(self, file, empty=False):
        """
        Inputs
        ------
        file:str
            name of the file
        empty:bool
            if true : resets the file
        """

        self.file = file

        if empty:
            with open(file, 'w') as json_file:
                json.dump(dict(), json_file)


    def get_JSON(self, file=None):
        """
        Returns the values in a JSON file

        Returns
        -------
        dict
            Values in the JSON file
        """

        if file is None:
            file = self.file

        with open(file, "r") as file:
            data = json.load(file)

        return data

    def add_JSON(self, values, file=None):
        """
        Add content to a JSON file

        Inputs
        ------
        value:dict
            dict of values
        file:str
            name of the file
        """

        if file is None:
            file = self.file

        res = self.get_JSON()

        with open(file, 'w') as json_file:
            # json.dump(dict(list(res.items()) + list(values.items())), json_file)
            json.dump(values, json_file, indent = 4)




bot = Crawler("https://www.youtube.com/")
bot.launch(200)
print(bot.visited)

"""
test -> https://www.google.com/
        https://jeunes.nouvelle-aquitaine.fr/formation/au-lycee/lycee-connecte
"""