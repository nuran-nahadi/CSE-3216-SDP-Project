"""Utilities for applying simple in-memory rate limiting to callables."""

import functools
import inspect
import time
from threading import Lock
from typing import Any, Callable, Dict, List

from fastapi import HTTPException, status


class RateLimiter:
    """Thread-safe in-memory rate limiter."""

    def __init__(self) -> None:
        self._calls: Dict[str, List[float]] = {}
        self._lock = Lock()

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        now = time.time()
        with self._lock:
            timestamps = self._calls.setdefault(key, [])
            # Drop calls outside the window
            timestamps = [ts for ts in timestamps if now - ts < window]
            if len(timestamps) >= limit:
                self._calls[key] = timestamps
                return False

            timestamps.append(now)
            self._calls[key] = timestamps
            return True


_rate_limiter = RateLimiter()


def rate_limit(limit: int = 60, window: int = 60, identifier: str = "user") -> Callable:
    """Rate limit a callable based on the provided identifier scope.

    Args:
        limit: Maximum number of calls allowed within the window.
        window: Window size in seconds.
        identifier: Key used to bucket calls ("user", "ip", or "global").
    """

    def decorator(func: Callable) -> Callable:
        signature = inspect.signature(func)

        def resolve_bucket(args: Any, kwargs: Any) -> str:
            try:
                bound = signature.bind_partial(*args, **kwargs)
                arguments = bound.arguments
            except TypeError:
                arguments = {}

            # Default bucket selection based on identifier type
            if identifier == "user":
                user_obj = arguments.get("current_user") or arguments.get("user")
                if user_obj is not None:
                    user_id = getattr(user_obj, "id", None)
                    if user_id is not None:
                        return f"user:{user_id}"
                if "user_id" in arguments and arguments["user_id"] is not None:
                    return f"user:{arguments['user_id']}"
            elif identifier == "ip":
                request = arguments.get("request")
                client = getattr(request, "client", None)
                host = getattr(client, "host", None) if client else None
                if host:
                    return f"ip:{host}"

            return "global"

        def build_key(args: Any, kwargs: Any) -> str:
            bucket = resolve_bucket(args, kwargs)
            return f"{func.__module__}.{func.__qualname__}:{bucket}"

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            key = build_key(args, kwargs)
            if not _rate_limiter.is_allowed(key, limit, window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                )
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            key = build_key(args, kwargs)
            if not _rate_limiter.is_allowed(key, limit, window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                )
            return func(*args, **kwargs)

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
