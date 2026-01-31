import os

from coingecko_sdk import Coingecko
from dotenv import load_dotenv

from cache import get_cache_batch, set_cache_batch

load_dotenv()


class Crypto:
    def __init__(self) -> None:
        self.CACHE_PREFIX = "crypto"
        self.client = Coingecko(
            demo_api_key=os.getenv("COINGECKO_API_KEY"),
            environment="demo",
        )

    def get_prices(self, coins: list[str], vs_currency: str = "usd"):
        prefix = f"{self.CACHE_PREFIX}_{vs_currency}"

        cached_batch = get_cache_batch(coins, prefix=prefix)

        missing_coins = [coin for coin, val in cached_batch.items() if val is None]

        if not missing_coins:
            return cached_batch

        try:
            response = self.client.simple.price.get(
                ids=",".join(missing_coins), vs_currencies=vs_currency
            )

            set_cache_batch(response, prefix=prefix)

            cached_batch.update(response)
            return cached_batch

        except Exception as e:
            print(f"Error fetching crypto: {e}")
            if any(cached_batch.values()):
                return cached_batch
            return {"error": str(e)}
