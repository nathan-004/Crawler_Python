from Searcher import Searcher
from flask import Flask, request, render_template

app = Flask(__name__, template_folder="../Website/html", static_folder="../Website/static")
s = Searcher()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    urls = []
    query = request.args.get("q")
    results = s.search(query)

    for url in results:
        if results[url] != 0:
            urls.append(url)
    
    return render_template("search.html", results=urls)

if __name__ == "__main__":
    app.run()