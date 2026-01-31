import os
import currencyapicom
from dotenv import load_dotenv
from cache import get_cache_batch, set_cache_batch

load_dotenv()


class Currency:
    def __init__(self) -> None:
        self.CACHE_PREFIX = "currency"
        self.client = currencyapicom.Client(os.getenv("FIAT_FREE_CURRENCY_API_KEY"))

    def _normalize_rates(self, raw_data: dict) -> dict:
        clean_rates = {}
        for iso, data in raw_data.items():
            if isinstance(data, dict) and "value" in data:
                clean_rates[iso] = data["value"]
            else:
                clean_rates[iso] = data
        return clean_rates

    async def get_rates(self, symbols: list[str] | None = None, base: str = "USD"):
        prefix = f"{self.CACHE_PREFIX}:{base.upper()}"

        if not symbols or "LATEST" in [s.upper() for s in symbols]:
            response = self.client.latest(base_currency=base)
            raw_rates = response.get("data", {})
            rates = self._normalize_rates(raw_rates)
            set_cache_batch(rates, prefix=prefix)
            return rates

        cached_batch = get_cache_batch(symbols, prefix=prefix)
        missing = [s for s, v in cached_batch.items() if v is None]

        if not missing:
            return cached_batch

        try:
            response = self.client.latest(currencies=missing, base_currency=base)
            raw_rates = response.get("data", {})
            new_rates = self._normalize_rates(raw_rates)

            set_cache_batch(new_rates, prefix=prefix)
            cached_batch.update(new_rates)
        except Exception as e:
            print(f"API Error: {e}")
            pass

        return cached_batch
