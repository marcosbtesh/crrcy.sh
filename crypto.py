import os

from coingecko_sdk import Coingecko
from dotenv import load_dotenv

load_dotenv()


class Crypto:
    def __init__(self) -> None:
        self.CACHE_KEY = "crypto_rates"
        self.client = Coingecko(
            pro_api_key=os.getenv("FIAT_FREE_CURRENCY_API_KEY"), environment="demo"
        )
        pass
