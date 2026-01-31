import requests

from cache import get_cache, set_cache


class Fiat:
    def __init__(self) -> None:
        self.CACHE_KEY = "fiat_rates"
        pass

    async def get_rates(self):

        # Firstly we check the cache
        cached_data = get_cache(self.CACHE_KEY)

        if cached_data:
            return cached_data

        response = await requests.get("")

        rates = response["data"]

        set_cache(self.CACHE_KEY, rates)

        return rates

    async def get_latest(self):
        cached_data = get_cache(self.CACHE_KEY)

        if cached_data:
            return cached_data

        response = await requests.get("")
        rates = response["data"]

        set_cache(self.CACHE_KEY, rates)

    async def get_iso_rate(self, iso: str):
        print(f"Getting rates for {iso}")
