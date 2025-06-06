from Searcher import Searcher
from flask import Flask

app = Flask(__name__)

@app.rout("/")
def get_results():
    pass