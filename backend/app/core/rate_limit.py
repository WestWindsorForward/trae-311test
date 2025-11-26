import time
from fastapi import Request, HTTPException, status
import redis
from .config import settings

class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    async def __call__(self, request: Request):
        ip = request.headers.get("x-forwarded-for") or request.client.host
        key = f"rl:{ip}:{request.url.path}:{int(time.time()//self.window)}"
        try:
            count = self.client.incr(key)
            if count == 1:
                self.client.expire(key, self.window)
            if count > self.limit:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        except Exception:
            return
