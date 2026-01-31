import os


class Currencies:
    def __init__(self) -> None:
        self.fiat_file = "Currencies/fiat.txt"
        self.crypto_file = "Currencies/crypto.txt"
        pass

    def check_which_type_of_currency(self, iso: str):

        currency_type = "UNKOWN"

        if not os.path.exists(self.fiat_file):
            print("Fiat file does not exist")
            return currency_type

        if not os.path.exists(self.crypto_file):
            print("Crypto file does not exist")
            return currency_type

        with open(self.fiat_file, "r") as fiat:
            for line in fiat:

                if line == iso:
                    currency_type = "FIAT"

        with open(self.crypto_file, "r") as crypto:
            for line in crypto:
                if line == iso:
                    currency_type = "CRYPTO"

            # if currency_type == "FIAT":
            #     currency_type = "UNKOWN"
