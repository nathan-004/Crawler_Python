from Searcher import Searcher
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("q")
    print("Requête reçue :", query)
    return jsonify({"Value": 0})

if __name__ == "__main__":
    app.run()