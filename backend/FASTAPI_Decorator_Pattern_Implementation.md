# Decorator Pattern Implementation (Backend)

This document explains the Decorator pattern in general and how it’s applied in this backend to add cross‑cutting behavior (rate limiting) to FastAPI endpoints without changing their core logic.

## Overview

- Goal: Attach reusable behaviors to functions/endpoints declaratively, keeping business logic clean and focused.
- Pattern: The Decorator pattern wraps a target function with pre/post logic while preserving its signature and return type.
- Scope in this project: A production‑ready, thread‑safe rate‑limiting decorator that works for both sync and async callables and supports multiple scoping strategies (per user, per IP, or global).

## Files and Responsibilities

- `app/decorators/rate_limit.py`
  - Implements the rate limiting infrastructure:
    - `RateLimiter`: thread‑safe in‑memory sliding‑window limiter
    - `rate_limit(...)`: the actual decorator that wraps endpoints
- `app/decorators/__init__.py`
  - Re‑exports `rate_limit` for ergonomics: `from app.decorators import rate_limit`
- Usage in routers (examples):
  - `app/routers/expenses.py`
  - `app/routers/events.py`
  - `app/routers/tasks.py`

## Core Implementation Details

### RateLimiter (thread‑safe, in‑memory)

- Data structure: `Dict[str, List[float]]` mapping a bucket key to a list of call timestamps (seconds since epoch).
- Concurrency: protected by a process‑wide `threading.Lock` so multiple workers/requests update safely.
- Sliding window algorithm:
  - On each call, drop timestamps older than `window` seconds.
  - If remaining count ≥ `limit`, deny; otherwise append `now` and allow.
- API:
  - `is_allowed(key: str, limit: int, window: int) -> bool`

### Decorator factory: `rate_limit(limit=60, window=60, identifier="user")`

- Parameters:
  - `limit`: max allowed calls in the given `window` per bucket.
  - `window`: time window in seconds.
  - `identifier`: how to bucket requests. Supported values:
    - `"user"` (default): group by authenticated user id
    - `"ip"`: group by `request.client.host`
    - `"global"`: a single shared bucket for all callers

- Bucket resolution logic (per call):
  - Binds provided `*args, **kwargs` to the wrapped function’s signature using `inspect.signature(...).bind_partial(...)`.
  - If `identifier == "user"`:
    - Tries `current_user` or `user` parameter; if present, uses `user.id`.
    - Else, uses an explicit `user_id` parameter if provided.
    - Else, falls back to global bucket.
  - If `identifier == "ip"`:
    - Looks for a `request` parameter and derives `request.client.host`.
    - Falls back to global if not available.
  - Always constructs a stable key as: `f"{func.__module__}.{func.__qualname__}:{bucket}"`.

- Sync vs. Async detection:
  - Uses `inspect.iscoroutinefunction(func)` to choose the correct wrapper so both synchronous and asynchronous endpoints are supported transparently.

- Error handling:
  - If a bucket exceeds its limit, raises `fastapi.HTTPException` with status `429 Too Many Requests` and a clear message.

### Why this is a Decorator

- The decorator composes behavior around the original function without modifying it:
  - Pre‑logic: evaluate rate limit and possibly short‑circuit with HTTP 429.
  - Call original function if allowed.
  - Return value and signature are preserved using `functools.wraps`.

## Example Usage in Routers

The decorator is applied directly on endpoints where throttling is needed, especially AI‑powered routes which are resource‑intensive.

- Expenses (`app/routers/expenses.py`):
  - `@rate_limit(limit=30, window=60)` on `/ai/parse-text`
  - `@rate_limit(limit=15, window=120)` on `/ai/parse-receipt`
  - `@rate_limit(limit=10, window=300)` on `/ai/parse-voice`
  - `@rate_limit(limit=20, window=300)` on `/ai/insights`

- Events (`app/routers/events.py`):
  - `@rate_limit(limit=30, window=60)` on `/ai/parse-text`
  - `@rate_limit(limit=10, window=300)` on `/ai/parse-voice`

- Tasks (`app/routers/tasks.py`):
  - `@rate_limit(limit=30, window=60)` on `/ai/parse-text`
  - `@rate_limit(limit=10, window=300)` on `/ai/parse-voice`
  - `@rate_limit(limit=20, window=300)` on `/ai/insights`

To import and use:

```python
from app.decorators import rate_limit

@rate_limit(limit=30, window=60)  # default identifier="user"
async def some_endpoint(...):
    ...
```

You can scope by IP if needed:

```python
@rate_limit(limit=100, window=60, identifier="ip")
async def public_endpoint(request: Request, ...):
    ...
```

## Design Choices and Trade‑offs

- In‑memory store:
  - Pros: simple, fast, zero external dependencies.
  - Cons: per‑process only. In multi‑process or multi‑instance deployments, limits aren’t shared. Restart clears counters.
- Thread safety: a per‑process `Lock` ensures consistent updates; suitable for typical ASGI workers running multiple threads.
- Sliding window lists may grow up to the limit per bucket within the window; pruning keeps memory bounded to recent calls.
- Identifier flexibility keeps endpoints independent of a specific auth or network layer, but requires conventional parameter names (`current_user`, `user`, `user_id`, or `request`).

## Extending for Production (Distributed Rate Limiting)

For horizontally scaled deployments, replace the in‑memory map with a shared backend (e.g., Redis):

- Keep the same decorator interface.
- Implement `RateLimiter.is_allowed(...)` using Redis with atomic LUA scripts or sorted sets for sliding window.
- Optionally add headers (e.g., `X-RateLimit-Remaining`) to improve client UX.

## Edge Cases and Recommendations

- Unauthenticated routes: use `identifier="ip"` or `"global"` to avoid collapsing all requests into one user bucket.
- Background tasks: if decorated functions are invoked outside HTTP (no `request` or `current_user`), the decorator gracefully falls back to the global bucket.
- Burst control vs. sustained rate: tune `limit` and `window` per route based on cost (e.g., AI OCR vs. text parsing).
- Testing: to assert rate limiting, call an endpoint `limit + 1` times within `window` and verify the last call returns HTTP 429.

## Quick Reference

- Module: `app/decorators/rate_limit.py`
- Decorator: `rate_limit(limit: int = 60, window: int = 60, identifier: str = "user")`
- Exceptions: raises `HTTPException(429)` when the limit is exceeded
- Works with: both async and sync callables; FastAPI endpoints or internal functions

---

Last updated: 2025-11-03
