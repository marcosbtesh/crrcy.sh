import dotenv
from flask import Flask

from crypto import Crypto
from fiat import Fiat

app = Flask(__name__)


crypto = Crypto()
fiat = Fiat()


@app.route("/")
def _home_():
    print("Route home")

    return ""
