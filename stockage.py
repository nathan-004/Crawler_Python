import json
import time
import sqlite3

class SQLStockage:
    """
    Classe de stockage pour les données SQL.
    """

    def __init__(self, db_name):
        """
        Initialise le stockage avec un nom de base de données.
        :param db_name: Nom de la base de données.
        """
        self.db_name = db_name
        self.data = self.load()

    def load(self):
        """
        Charge les données depuis la base de données SQL.
        :return: Données chargées.
        """
        # Implémentation spécifique à la base de données SQL
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM urls")
        data = cursor.fetchall()
        conn.close()
        return data

    def save(self, data):
        """
        Sauvegarde les données dans la base de données SQL.
        :param data: Données à sauvegarder.
        """
        # Implémentation spécifique à la base de données SQL
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS urls (url TEXT, links TEXT, timestamp TEXT)")
        cursor.execute("INSERT INTO urls (url, links, timestamp) VALUES (?, ?, ?)", (data['url'], json.dumps(data['links']), data['timestamp']))
        conn.commit()
        conn.close()

class JSONStockage:
    """
    Classe de stockage pour les données JSON.
    """

    def __init__(self, filename):
        """
        Initialise le stockage avec un nom de fichier.
        :param filename: Nom du fichier de stockage.
        """
        self.filename = filename
        self.data = self.load()

    def load(self):
        """
        Charge les données depuis le fichier JSON.
        :return: Données chargées.
        """
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return {}
        
    def save(self, data):
        """
        Sauvegarde les données dans le fichier JSON.
        :param data -> dict: Données à sauvegarder.
        Ajout d'un timestamp à chaque sauvegarde.
        """
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)

    def append(self, url, links):
        """
        Ajoute des données à la fin du fichier JSON.
        :param url: URL à ajouter.
        :param links: Liens associés à l'URL.
        :param elements: Éléments associés à l'URL.
        """
        data = self.load()
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        if url not in data:
            data[url] = {
                "links": links,
                "timestamp": timestamp,
            }
        else:
            data[url]["links"].extend(links)
            data[url]["timestamp"] = timestamp

        self.save(data)

    def data_append(self, url, links):
        """
        Ajoute des données au dictionnaire de données sans les sauvegarder dans le fichier.
        :param url: URL à ajouter + liens associés + éléments associés."""


        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if url not in self.data:
            self.data[url] = {
                "links": links,
                "timestamp": timestamp,
            }
        else:
            self.data[url]["links"].extend(links)
            self.data[url]["timestamp"] = timestamp

    def save_stock(self):
        """
        Sauvegarde les données dans le fichier JSON.
        """
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def reset(self):
        """
        Réinitialise le fichier JSON en le vidant.
        """
        with open(self.filename, 'w') as file:
            json.dump({}, file, indent=4)


class TXTStockage:
    """
    Classe de stockage pour les données texte.
    """

    def __init__(self, filename="urls_stack.txt"):
        """
        Initialise le stockage avec un nom de fichier.
        :param filename: Nom du fichier de stockage.
        """
        self.filename = filename

    def load(self):
        """
        Charge les données depuis le fichier texte.
        :return: Données chargées.
        """
        try:
            with open(self.filename, 'r') as file:
                data = file.read()
            return data
        except FileNotFoundError:
            return ""

    def save(self, data):
        """
        Sauvegarde les données dans le fichier texte.
        :param data: Données à sauvegarder.
        """
        with open(self.filename, 'w') as file:
            file.write(data)

    def append(self, data, timestamp=None):
        """
        Ajoute des données à la fin du fichier texte.
        :param data: Données à ajouter.
        """
        if timestamp:
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            data = f"{timestamp} - {data}"

        with open(self.filename, 'a') as file:
            file.write(data + "\n")

    def reset(self):
        """
        Réinitialise le fichier texte en le vidant.
        """
        with open(self.filename, 'w') as file:
            file.write("")



if __name__ == "__main__":
    JSONStockage("urls.json").reset()
    TXTStockage("urls_stack.txt").reset()
    TXTStockage("logs.txt").reset()