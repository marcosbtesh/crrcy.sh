import os

from coingecko_sdk import Coingecko
from dotenv import load_dotenv

from cache import get_cache, set_cache

load_dotenv()


class Crypto:
    def __init__(self) -> None:
        self.CACHE_KEY = "crypto_rates"
        self.client = Coingecko(
            demo_api_key=os.getenv("COINGECKO_API_KEY"),
            environment="demo",
        )

    def get_prices(self, coins: list[str], vs_currency: str = "usd"):

        key = f"{self.CACHE_KEY}_{'_'.join(coins)}_{vs_currency}"

        cached_data = get_cache(key)
        if cached_data:
            return cached_data

        try:
            response = self.client.simple.price.get(
                ids=",".join(coins), vs_currencies=vs_currency
            )

            set_cache(key, response)
            return response

        except Exception as e:
            print(f"Error fetching crypto: {e}")
            return {"error": str(e)}
