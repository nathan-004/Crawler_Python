# Moteur de Recherche Python avec Flask

![Python](https://img.shields.io/badge/language-Python-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Last Commit](https://img.shields.io/github/last-commit/nathan-004/search-engine)
![GitHub issues](https://img.shields.io/github/issues/nathan-004/search-engine)
![Status](https://img.shields.io/badge/status-en%20cours-orange)
![Python version](https://img.shields.io/badge/python-3.10-blue)

Ce projet est un **moteur de recherche web** codé en Python. Il permet de crawler les pages web, d'indexer leur contenu dans des bases SQLite, et de rechercher des informations via une interface web en Flask.

---

## Fonctionnalités

- **Crawler** de pages web (respecte les fichiers `robots.txt`)
- **Indexation** des mots avec fréquence (TF-IDF)
- **Recherche** rapide avec système de score
- **Filtrage** des mots vides et mots trop fréquents
- **Interface Web** en HTML/CSS/JavaScript (via Flask)
- **Bases de données SQLite** (20 Mo & 100 Mo)

---

## Structure du projet

```
search-engine-main/
├── Crawler/
│ ├── api.py
│ ├── Searcher.py
│ ├── Crawler.py
│ ├── indexer.py
| ├── web.py
│ └── ...
├── Website/
│ ├── html/
│ │ └── search.html
│ │ └── index.html
│ ├── static/
│ | └── css/
│ | └── js/
└── README.md
```

## Installation

1. Clone ce dépôt :

```bash
git clone https://github.com/ton-utilisateur/search-engine-main.git
cd search-engine-main
```

2. Installe les dépendances Python (idéalement dans un environnement virtuel) :

```bash
pip install flask
```

3. Lance l'application Flask :
```bash
cd Crawler
python api.py
```

4. Accède à l'application web via :
```
http://127.0.0.1:5000
```

## Utilisation

- Entrez un mot-clé dans la barre de recherche.
- Le backend utilise un algorithme TF-IDF pour noter chaque page contenant ces mots.
- Les scores élevés indiquent une plus grande pertinence.

## Limitations

- Beaucoup d'URLs très populaires bloquent le crawl via erreur 403 Forbidden.
- Les mots très fréquents comme "le", "la", etc., sont filtrés ou réduits en score.
- Base de données locale, non adaptée à un usage en production sans adaptation.

## Technologies utilisées

- Python
- Flask
- SQLite
- HTML, CSS, JavaScript
- Jinja2 (templates Flask)

## Ressources

Exemple code : [mwmbl](https://github.com/mwmbl/mwmbl)  
Papier : [Google](http://infolab.stanford.edu/pub/papers/google.pdf)
