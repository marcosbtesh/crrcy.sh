import os

import freecurrencyapi
from dotenv import load_dotenv

from cache import get_cache_batch, set_cache_batch

load_dotenv()


class Fiat:
    def __init__(self) -> None:
        self.CACHE_PREFIX = "fiat"
        self.client = freecurrencyapi.Client(os.getenv("FIAT_FREE_CURRENCY_API_KEY"))

    async def get_latest(self):
        response = self.client.latest()
        rates = response.get("data", {})

        set_cache_batch(rates, prefix=self.CACHE_PREFIX)

        return rates

    async def get_iso_rate(self, isos: list[str]):
        print(f"Getting rates for {isos}")

        cached_batch = get_cache_batch(isos, prefix=self.CACHE_PREFIX)

        missing_isos = [iso for iso, val in cached_batch.items() if val is None]

        if not missing_isos:
            return cached_batch

        print(f"Fetching missing from API: {missing_isos}")
        try:
            response = self.client.latest(currencies=missing_isos)
            new_rates = response.get("data", {})

            set_cache_batch(new_rates, prefix=self.CACHE_PREFIX)

            cached_batch.update(new_rates)
        except Exception as e:
            print(f"API Error: {e}")
            pass

        return cached_batch

    async def get_rates(self):
        return await self.get_latest()
