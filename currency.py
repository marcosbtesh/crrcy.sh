import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

import currencyapicom
from dotenv import load_dotenv

from cache import get_cache, get_cache_batch, set_cache, set_cache_batch
from currencies import Currencies

load_dotenv()


class Currency:
    def __init__(self) -> None:
        self.CACHE_PREFIX = "currency"
        self.CACHE_PREFIX_HISTORICAL = "historical"
        self.CACHE_PREFIX_LATEST = "latest"
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

    async def get_timeseries_data(
        self,
        base: str,
        targets: list[str],
        start_date: datetime,
        end_date: datetime,
        step: int = 1,
    ) -> Dict[str, Any]:
        base = base.upper()
        targets = [t.upper() for t in targets]

        date_list = []
        curr = start_date
        while curr <= end_date:
            date_list.append(curr.strftime("%Y-%m-%d"))
            curr += timedelta(days=step)

        today_str = datetime.now().strftime("%Y-%m-%d")

        combined_results = {t: {} for t in targets}

        for target in targets:
            cache_keys = []
            for d in date_list:
                if d == today_str:
                    cache_keys.append(f"{self.CACHE_PREFIX_LATEST}:{base}:{target}")
                else:
                    cache_keys.append(
                        f"{self.CACHE_PREFIX_HISTORICAL}:{d}:{base}:['{target}']"
                    )

            cached_values = get_cache_batch(keys=cache_keys, prefix="")

            missing_dates = []
            for i, date_str in enumerate(date_list):
                key = cache_keys[i]
                data = cached_values.get(key)
                if data and "data" in data and target in data["data"]:
                    combined_results[target][date_str] = {
                        "value": data["data"][target]["value"]
                    }
                else:
                    missing_dates.append(date_str)

            for d_str in missing_dates:
                try:
                    if d_str == today_str:
                        api_data = await self.client.latest(
                            base_currency=base, currencies=[target]
                        )
                        set_cache(
                            f"{self.CACHE_PREFIX_LATEST}:{base}:{target}",
                            api_data,
                            expire_hours=1,
                        )
                    else:
                        api_data = await self.client.historical(
                            base_currency=base, currencies=[target], date=d_str
                        )
                        set_cache(
                            f"{self.CACHE_PREFIX_HISTORICAL}:{d_str}:{base}:['{target}']",
                            api_data,
                            expire_hours=48,
                        )

                    combined_results[target][d_str] = {
                        "value": api_data["data"][target]["value"]
                    }
                except Exception:
                    continue

        return {
            "meta": {"base": base, "targets": targets, "step": step},
            "series": combined_results,
        }

    # @deprectated
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
