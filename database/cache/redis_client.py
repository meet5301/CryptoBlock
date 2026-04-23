from __future__ import annotations

from functools import lru_cache

import redis

from config import REDIS_URL


@lru_cache(maxsize=1)
def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)
