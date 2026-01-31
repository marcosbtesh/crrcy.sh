# ttps://github.com/crypti/cryptocurrencies/blob/master/cryptocurrencies.json

import json

with open("crypto.json", "r") as file:
    data = json.load(file)

with open("symbols.txt", "w") as f:
    for symbol in data.keys():
        f.write(f"{symbol}\n")
