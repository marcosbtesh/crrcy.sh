class Currencies:
    def __init__(self) -> None:
        self.fiat_file = "fiat.txt"
        self.crypto_file = "crypto.txt"
        pass

    def check_which_type_of_currency(self, iso: str):

        currency_type = "UNKOWN"

        with open(self.fiat_file, "r") as fiat:
            for line in fiat:

                if line == iso:
                    currency_type = "FIAT"

        with open(self.crypto_file, "r") as crypto:
            for line in crypto:
                if line == iso:
                    currency_type = "CRYPTO"
