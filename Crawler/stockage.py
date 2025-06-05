import json
import time
import sqlite3

class SQLStockage:
    """Classe de stockage pour les données SQL."""

    N = 50

    def __init__(self, db_name):
        """
        Initialise le stockage avec un nom de base de données.
        :param db_name: Nom de la base de données.
        """
        self.db_name = db_name
        self._init_db()
        self.to_save = []

    def _init_db(self):
        """
        Crée la table si elle n'existe pas.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                domain TEXT,
                title TEXT,
                word_freq TEXT,
                date_scraped DATETIME,
                is_valid BOOLEAN
            );
        ''')
        conn.commit()
        conn.close()

    def save_url(self, url, domain=None, title=None, word_freq=None, is_valid=True, timestamp=None):
        """
        Sauvegarde une URL avec ses métadonnées dans la base.

        Parameters
        ----------
        word_freq:dict
            Dictionnaire sous forme {"mot": occurence}
        """
        date_scraped = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if timestamp is not None else timestamp
        word_freq = json.dumps(word_freq)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO urls (url, domain, title, word_freq, date_scraped, is_valid)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, domain, title, word_freq, date_scraped, is_valid))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'insertion: {e}")
        finally:
            conn.close()

    def append_url(self, url, domain=None, title=None, word_freq=None, is_valid=None):
        """
        Stocke les valeurs dans une liste et tous les 100 urls, sauvegarde tout
        """
        print(len(self.to_save))
        if len(self.to_save) >= self.N:
            for line in self.to_save:
                self.save_url(*line)
            self.to_save.clear()
        else:
            self.to_save.append([url, domain, title, word_freq, is_valid, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())])

    def load_all_urls(self):
        """
        Récupère toutes les URLs stockées.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT url, domain, title, word_freq, date_scraped, is_valid FROM urls")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_urls(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM urls")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

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
            with open(self.filename, 'r', encoding="utf-8") as file:
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
        with open(self.filename, 'w', encoding="utf-8") as file:
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
            with open(self.filename, 'r', encoding="utf-8") as file:
                data = file.read()
            return data
        except FileNotFoundError:
            return ""

    def save(self, data):
        """
        Sauvegarde les données dans le fichier texte.
        :param data: Données à sauvegarder.
        """
        with open(self.filename, 'w', encoding="utf-8") as file:
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