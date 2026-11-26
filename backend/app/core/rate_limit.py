"""In-memory sliding-window rate limiting and request-size guard middleware."""

from collections import defaultdict, deque
import time
from typing import Deque, Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-client sliding-window rate limiter for API endpoints."""

    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = max(10, requests_per_minute)
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api") or path in {"/api/health", "/api/v1/health"}:
            return await call_next(request)

        settings = get_settings()
        if settings.app_env == "test":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = self._hits[client_ip]
        while window and now - window[0] > 60.0:
            window.popleft()

        if len(window) >= self.requests_per_minute:
            retry_after = max(1, int(60.0 - (now - window[0])))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please wait a moment and try again."},
                headers={"Retry-After": str(retry_after)},
            )

        window.append(now)
        return await call_next(request)
