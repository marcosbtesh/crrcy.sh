import os
import currencyapicom
from dotenv import load_dotenv
from cache import get_cache_batch, set_cache_batch
from currencies import Currencies

load_dotenv()


class Currency:
    def __init__(self) -> None:
        self.CACHE_PREFIX = "currency"
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
            response = self.client.latest(currencies=missing, base_currency=base)
            raw_rates = response.get("data", {})

            should_invert_crypto = not is_crypto_base and any(
                self.checker.check_which_type_of_currency(s) == "CRYPTO"
                for s in missing
            )

            new_rates = {}
            for iso, val in self._normalize_rates(raw_rates, invert=False).items():
                if (
                    should_invert_crypto
                    and self.checker.check_which_type_of_currency(iso) == "CRYPTO"
                ):
                    new_rates[iso] = 1 / val if val != 0 else val
                else:
                    new_rates[iso] = val

            set_cache_batch(new_rates, prefix=prefix, expire_hours=cache_expire_hours)
            cached_batch.update(new_rates)

        except Exception as e:
            print(f"API Error: {e}")

        return cached_batch
