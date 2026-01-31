import json
import os
from typing import Any, List, cast

import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)


def get_cache_batch(keys: list, prefix: str):
    if not keys:
        return {}

    full_keys = [f"{prefix}:{k}" for k in keys]

    values = cast(List[Any], client.mget(full_keys))

    result = {}
    for k, v in zip(keys, values):
        if v is not None:
            try:
                result[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                result[k] = v
        else:
            result[k] = None

    return result


def set_cache_batch(data: dict, prefix: str, expire_hours=6):
    if not data:
        return

    pipe = client.pipeline()
    expiry_seconds = expire_hours * 3600

    for k, v in data.items():
        key = f"{prefix}:{k}"
        pipe.set(key, json.dumps(v), ex=expiry_seconds)

    pipe.execute()


def get_cache(key):
    data = client.get(key)
    return data if data else None


def set_cache(key, data, expire_hours: int | None = 6):
    if expire_hours is None:
        client.set(key, json.dumps(data))
    else:
        client.set(key, json.dumps(data), ex=expire_hours * 3600)


RATE_LIMIT_PREFIX = "rate_limit"
BLOCKED_IPS_PREFIX = "blocked_ip"


def is_ip_blocked(ip_address: str) -> bool:
    """Check if an IP address is currently blocked."""
    blocked_key = f"{BLOCKED_IPS_PREFIX}:{ip_address}"
    return bool(client.exists(blocked_key))


def get_key_expiration(key):
    expiration = client.getex(key)

    print(expiration)
    return expiration


def block_ip(ip_address: str, duration_minutes: int = 60) -> None:
    """Block an IP address for a specified duration."""
    blocked_key = f"{BLOCKED_IPS_PREFIX}:{ip_address}"
    client.setex(blocked_key, duration_minutes * 60, "1")


def increment_request_count(ip_address: str, window_minutes: int = 1) -> int:
    """
    Increment request count for an IP address.
    Returns the current request count in the time window.
    """
    rate_key = f"{RATE_LIMIT_PREFIX}:{ip_address}"
    count = cast(int, client.incr(rate_key))

    if count == 1:
        client.expire(rate_key, window_minutes * 60)

    return count


def check_rate_limit(
    ip_address: str,
    max_requests: int = 100,
    window_minutes: int = 1,
    block_duration_minutes: int = 60,
) -> dict:
    """
    Check if an IP has exceeded rate limits.

    Returns a dict with:
    - allowed: bool - Whether the request is allowed
    - count: int - Current request count in window
    - limit: int - The limit
    - blocked: bool - Whether the IP is blocked
    - message: str - Reason if blocked
    """

    if is_ip_blocked(ip_address):
        return {
            "allowed": False,
            "blocked": True,
            "message": "IP address is temporarily blocked due to rate limit violation",
        }

    current_count = increment_request_count(ip_address, window_minutes)

    if current_count > max_requests:
        block_ip(ip_address, block_duration_minutes)
        return {
            "allowed": False,
            "count": current_count,
            "limit": max_requests,
            "blocked": True,
            "message": f"Rate limit exceeded ({current_count} > {max_requests} requests per {window_minutes} minute(s)). IP blocked for {block_duration_minutes} minutes",
        }

    return {
        "allowed": True,
        "count": current_count,
        "limit": max_requests,
        "blocked": False,
        "message": None,
    }


def reset_ip_rate_limit(ip_address: str) -> None:
    """Reset rate limit counter for a specific IP."""
    rate_key = f"{RATE_LIMIT_PREFIX}:{ip_address}"
    client.delete(rate_key)


def unblock_ip(ip_address: str) -> None:
    """Immediately unblock an IP address."""
    blocked_key = f"{BLOCKED_IPS_PREFIX}:{ip_address}"
    client.delete(blocked_key)
