import dotenv
from flask import Flask

app = Flask(__name__)


@app.route("/")
def _home_():
    print("Route home")

    return ""
