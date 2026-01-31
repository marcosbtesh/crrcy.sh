import os


class Currencies:
    def __init__(self) -> None:
        self.fiat_file = "Currencies/fiat.txt"
        self.crypto_file = "Currencies/crypto.txt"

    def check_which_type_of_currency(self, iso: str):
        currency_type = "UNKNOWN"
        iso = iso.strip().upper()

        if not os.path.exists(self.fiat_file) or not os.path.exists(self.crypto_file):
            return currency_type

        with open(self.fiat_file, "r") as f:
            fiat_list = [line.strip().upper() for line in f]
            if iso in fiat_list:
                return "FIAT"

        with open(self.crypto_file, "r") as c:
            crypto_list = [line.strip().upper() for line in c]
            if iso in crypto_list:
                return "CRYPTO"

        return currency_type
