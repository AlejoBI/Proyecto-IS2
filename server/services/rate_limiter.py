from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from time import time


class InMemoryRateLimiter:
    """Small process-local limiter for a single demo instance.

    A distributed deployment should replace this with Redis or the provider's
    native rate limiter. This limiter still protects the API from accidental
    bursts and is deliberately independent from user-provided API keys.
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = monotonic()
        with self._lock:
            requests = self._requests[key]
            while requests and now - requests[0] >= self.window_seconds:
                requests.popleft()
            if len(requests) >= self.max_requests:
                return False
            requests.append(now)
            return True

    def cleanup(self) -> None:
        now = monotonic()
        with self._lock:
            expired = [
                key for key, requests in self._requests.items()
                if not requests or now - requests[-1] >= self.window_seconds
            ]
            for key in expired:
                self._requests.pop(key, None)


class RedisRateLimiter:
    """Distributed fixed-window limiter for multi-replica deployments."""

    def __init__(self, url: str, max_requests: int, window_seconds: int,
                 prefix: str = "proyecto-is2:rate") -> None:
        import redis

        self.client = redis.Redis.from_url(url, decode_responses=True)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.prefix = prefix

    def allow(self, key: str) -> bool:
        bucket = int(time() // self.window_seconds)
        redis_key = f"{self.prefix}:{key}:{bucket}"
        with self.client.pipeline() as pipeline:
            pipeline.incr(redis_key)
            pipeline.expire(redis_key, self.window_seconds + 1)
            count, _ = pipeline.execute()
        return int(count) <= self.max_requests
