import os


class Currencies:
    def __init__(self) -> None:
        self.fiat_file = "Currencies/fiat.txt"
        self.crypto_file = "Currencies/crypto.txt"

        self.fiat_list = set()
        self.crypto_list = set()

        if os.path.exists(self.fiat_file):
            with open(self.fiat_file, "r") as f:
                self.fiat_list = {line.strip().upper() for line in f if line.strip()}

        if os.path.exists(self.crypto_file):
            with open(self.crypto_file, "r") as c:
                self.crypto_list = {line.strip().upper() for line in c if line.strip()}

    def check_which_type_of_currency(self, iso: str) -> str:

        iso = iso.strip().upper()

        if iso in self.fiat_list:
            return "FIAT"

        if iso in self.crypto_list:
            return "CRYPTO"

        return "UNKNOWN"
