import json
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
        cache_expire_hours = 1 if is_crypto_base else 12
        # cache_expire_hours = 24 if is_crypto_base else 24

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

            missing_known = [
                s
                for s in missing
                if self.checker.check_which_type_of_currency(s) in ["FIAT", "CRYPTO"]
            ]

            if not missing_known:
                return cached_batch

            missing_crypto = [
                s
                for s in missing_known
                if self.checker.check_which_type_of_currency(s) == "CRYPTO"
            ]
            missing_fiat = [
                s
                for s in missing_known
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

        end_date_str = end_date.strftime("%Y-%m-%d")
        if not date_list or date_list[-1] != end_date_str:
            date_list.append(end_date_str)
        combined_results = {t: {} for t in targets}
        last_updated_at = None

        for target in targets:

            ctype = self.checker.check_which_type_of_currency(target)
            if ctype == "UNKNOWN":
                continue

            is_symbol_crypto = (
                self.checker.check_which_type_of_currency(target) == "CRYPTO"
            )

            for date_str in date_list:
                if date_str == today_str:
                    cache_key = f"{self.CACHE_PREFIX_LATEST}:{base}:{target}"
                else:
                    cache_key = (
                        f"{self.CACHE_PREFIX_HISTORICAL}:{date_str}:{base}:{target}"
                    )

                cached_data = get_cache(cache_key)

                if cached_data:
                    try:
                        data_dict = (
                            json.loads(cached_data)
                            if isinstance(cached_data, str)
                            else cached_data
                        )
                        if isinstance(data_dict, dict) and "data" in data_dict:
                            if target in data_dict["data"]:
                                value = data_dict["data"][target]["value"]
                                if (
                                    is_symbol_crypto
                                    and isinstance(value, (int, float))
                                    and value != 0
                                ):
                                    value = 1 / value
                                combined_results[target][date_str] = {"value": value}
                                if not last_updated_at and "meta" in data_dict:
                                    last_updated_at = data_dict["meta"].get(
                                        "last_updated_at"
                                    )
                                continue
                    except Exception:
                        pass

                try:
                    if date_str == today_str:
                        api_data = self.client.latest(
                            base_currency=base, currencies=[target]
                        )
                        set_cache(
                            cache_key,
                            api_data,
                            expire_hours=1,
                        )
                    else:
                        api_data = self.client.historical(
                            base_currency=base, currencies=[target], date=date_str
                        )
                        set_cache(
                            cache_key,
                            api_data,
                            expire_hours=None,
                        )

                    if "data" in api_data and target in api_data["data"]:
                        value = api_data["data"][target]["value"]
                        if (
                            is_symbol_crypto
                            and isinstance(value, (int, float))
                            and value != 0
                        ):
                            value = 1 / value
                        combined_results[target][date_str] = {"value": value}
                        if not last_updated_at and "meta" in api_data:
                            last_updated_at = api_data["meta"].get("last_updated_at")
                except Exception as e:
                    continue

        return {
            "meta": {
                "base": base,
                "targets": targets,
                "step": step,
                "last_updated_at": last_updated_at or "Unknown",
            },
            "data": combined_results,
        }
