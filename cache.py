import json
import os

import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))


client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)


def get_cache(key):
    data = client.get(key)

    if data:
        return data

    return None


def set_cache(key, data, expire_hours=6):
    client.set(key, json.dumps(data), ex=expire_hours)
