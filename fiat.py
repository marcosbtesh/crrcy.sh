import os

import freecurrencyapi
import requests
from dotenv import load_dotenv

from cache import get_cache, set_cache

load_dotenv()


class Fiat:
    def __init__(self) -> None:
        self.CACHE_KEY = "fiat_rates"
        self.client = freecurrencyapi.Client(os.getenv("FIAT_FREE_CURRENCY_API_KEY"))
        pass

    async def get_rates(self):

        # Firstly we check the cache
        cached_data = get_cache(self.CACHE_KEY)

        if cached_data:
            return cached_data

        response = self.client.currencies()

        rates = response["data"]

        set_cache(self.CACHE_KEY, rates)

        return rates

    async def get_latest(self):
        cached_data = get_cache(self.CACHE_KEY)

        if cached_data:
            return cached_data

        response = self.client.latest()

        rates = response["data"]

        set_cache(self.CACHE_KEY, rates)

        return rates

    async def get_iso_rate(self, isos: list[str]):
        print(f"Getting rates for {isos}")

        cached_data = get_cache(self.CACHE_KEY)

        if cached_data:
            return cached_data

        response = self.client.currencies(currencies=[isos])

        rates = response["data"]

        set_cache(self.CACHE_KEY, rates)

        return rates
