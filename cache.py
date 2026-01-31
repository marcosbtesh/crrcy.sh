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
