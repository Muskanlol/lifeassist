import asyncio
import time


class RateLimiter:
    def __init__(self, min_interval: float = 1.1):
        self.min_interval = min_interval
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self):
        async with self._lock:
            now = time.monotonic()
            delay = self.min_interval - (now - self._last)
            if delay > 0:
                await asyncio.sleep(delay)
            self._last = time.monotonic()


nominatim_limiter = RateLimiter(1.1)
overpass_limiter = RateLimiter(1.1)
osrm_limiter = RateLimiter(0.6)
