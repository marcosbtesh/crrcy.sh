import datetime
import os

import currencyapicom
from dotenv import load_dotenv

from cache import get_cache, get_cache_batch, set_cache, set_cache_batch
from currencies import Currencies

load_dotenv()


class Currency:
    def __init__(self) -> None:
        self.CACHE_PREFIX = "currency"
        self.CACHE_PREFIX_HISTORICAL = "historical"
        self.client = currencyapicom.Client(os.getenv("FIAT_FREE_CURRENCY_API_KEY"))
        self.checker = Currencies()

    def _normalize_rates(self, raw_data: dict, invert: bool = False) -> dict:
        clean_rates = {}
        for iso, data in raw_data.items():
            val = data["value"] if isinstance(data, dict) and "value" in data else data
            if invert and isinstance(val, (int, float)) and val != 0:
                clean_rates[iso] = 1 / val
            else:
                clean_rates[iso] = val
        return clean_rates

    async def get_rates(self, symbols: list[str] | None = None, base: str = "USD"):
        base = base.upper()
        is_crypto_base = self.checker.check_which_type_of_currency(base) == "CRYPTO"
        cache_expire_hours = 2 if is_crypto_base else 6
        cache_expire_hours = 24 if is_crypto_base else 24

        prefix = f"{self.CACHE_PREFIX}:{base}"

        if not symbols or "LATEST" in [s.upper() for s in symbols]:
            api_base = "USD" if is_crypto_base else base
            response = self.client.latest(base_currency=api_base)
            raw_rates = response.get("data", {})
            rates = self._normalize_rates(raw_rates, invert=is_crypto_base)
            set_cache_batch(rates, prefix=prefix, expire_hours=cache_expire_hours)
            return rates

        cached_batch = get_cache_batch(symbols, prefix=prefix)
        missing = [s for s, v in cached_batch.items() if v is None]

        if not missing:
            return cached_batch

        try:
            missing_crypto = [
                s
                for s in missing
                if self.checker.check_which_type_of_currency(s) == "CRYPTO"
            ]
            missing_fiat = [
                s
                for s in missing
                if self.checker.check_which_type_of_currency(s) == "FIAT"
            ]

            new_rates = {}

            if missing_crypto:
                response = self.client.latest(
                    currencies=missing_crypto, base_currency=base
                )
                raw_rates = response.get("data", {})

                for iso, val in self._normalize_rates(raw_rates, invert=False).items():
                    if not is_crypto_base:
                        new_rates[iso] = 1 / val if val != 0 else val
                    else:
                        new_rates[iso] = val

            if missing_fiat:
                response = self.client.latest(
                    currencies=missing_fiat, base_currency=base
                )
                raw_rates = response.get("data", {})

                for iso, val in self._normalize_rates(raw_rates, invert=False).items():
                    if is_crypto_base:
                        new_rates[iso] = 1 / val if val != 0 else val
                    else:
                        new_rates[iso] = val

            set_cache_batch(new_rates, prefix=prefix, expire_hours=cache_expire_hours)
            cached_batch.update(new_rates)

        except Exception as e:
            print(f"API Error: {e}")

        return cached_batch

    async def get_historical_rates(self, base: str, symbols: list[str], date: str):
        base = base.upper()

        key = f"{self.CACHE_PREFIX_HISTORICAL}:{date}:{base}:{symbols}"

        cached_batch = get_cache(key=key)

        if cached_batch:
            return cached_batch

        try:

            historical_rates = self.client.historical(
                base_currency=base, currencies=symbols, date=date
            )

            set_cache(key, historical_rates, expire_hours=48)

            return historical_rates
        except Exception as e:
            print(f"API Error: {str(e)}")
