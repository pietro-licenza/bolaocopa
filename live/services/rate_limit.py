"""
Rate-limit helpers for the live data sync flow.

The free tiers of the upstream APIs we use have very tight quotas:

* **API-Football**: 100 requests/day on the free plan.
* **football-data.org**: 10 requests/minute on the free plan.

The strategy in ``TASKS.md`` (US-7.3) is to keep a daily counter in the
Django cache and block the "Buscar resultado" button once the combined
total of FDO + API-Football requests approaches the daily cap. We also
track a rolling "requests in the last minute" count for FDO specifically,
so we can surface a friendlier error message when football-data.org rate-
limits us.

The cache backend used is whatever ``CACHES['default']`` is configured to
point at. Django's default (``LocMemCache``) is process-local, which is
fine for the dev server and the ``manage.py runserver`` workflow — for
multi-process production deployments a shared cache (Redis, memcached)
would be required for these counters to be accurate. The helpers are
written against the public ``django.core.cache`` API so swapping the
backend in ``core/settings.py`` is enough.
"""

import time
from datetime import date as date_type
from datetime import datetime as datetime_type

from django.core.cache import cache


# Cache keys are namespaced so they don't collide with anything else in
# the project (which also uses the default cache for other purposes,
# e.g. session storage lives in the DB but the cache is otherwise free).
_DAILY_KEY_FMT = 'api_requests_{date}'
_FDO_MINUTE_KEY_FMT = 'fdo_minute_requests_{minute_ts}'

# Default caps. Documented in TASKS.md / US-7.3.
DEFAULT_DAILY_LIMIT = 95
FDO_MINUTE_LIMIT = 10
FDO_MINUTE_WINDOW_SECONDS = 60


def _today_key():
    """Return the cache key used to track today's request total."""
    return _DAILY_KEY_FMT.format(date=date_type.today().isoformat())


def _current_minute_key():
    """Return the cache key for the current 60-second window."""
    ts = int(time.time() // FDO_MINUTE_WINDOW_SECONDS)
    return _FDO_MINUTE_KEY_FMT.format(minute_ts=ts)


def get_daily_request_count():
    """Return how many requests have been counted today (int).

    Returns ``0`` when no requests have been recorded yet, which is
    indistinguishable from "explicitly counted to zero" — both states
    mean the same thing for rate-limiting purposes.
    """
    value = cache.get(_today_key())
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        # A corrupt cache entry should never block the user; treat it
        # as zero and let the next increment reset things.
        return 0


def increment_daily_request_count(n=1):
    """Bump the daily counter by ``n`` (default 1) and return the new total.

    Uses ``cache.incr`` when the key already exists (atomic on backends
    that support it, e.g. memcached). When the key does not exist yet
    we fall back to ``cache.add`` to seed it, which is a no-op if some
    other process raced us and stored a value first — either way the
    next call to ``incr`` will pick up the right baseline.
    """
    key = _today_key()
    # Expire the counter at the next midnight so we don't keep stale
    # counts around forever. ``end_of_day`` is in UTC since we don't
    # know the user's timezone; the day boundary is close enough for
    # a daily counter.
    now = datetime_type.utcnow()
    end_of_day = datetime_type.combine(
        now.date(), datetime_type.max.time(),
    )
    seconds_left = max(int((end_of_day - now).total_seconds()), 60)

    try:
        return int(cache.incr(key, n))
    except ValueError:
        # Key does not exist yet — seed it.
        added = cache.add(key, n, timeout=seconds_left)
        if added:
            return n
        # Another process seeded it first; try the atomic incr again.
        return int(cache.incr(key, n))


def is_daily_limit_reached(limit=DEFAULT_DAILY_LIMIT):
    """Return ``True`` if the daily counter is at or above ``limit``."""
    return get_daily_request_count() >= limit


def check_fdo_minute_limit():
    """Return ``True`` if the FDO per-minute limit has been reached.

    The "last minute" window is computed in fixed 60-second buckets
    (epoch // 60). When the bucket flips, the key naturally expires and
    the count resets, which is the desired behavior.
    """
    return get_fdo_minute_count() >= FDO_MINUTE_LIMIT


def get_fdo_minute_count():
    """Return the number of FDO requests counted in the current minute."""
    key = _current_minute_key()
    value = cache.get(key)
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def increment_fdo_minute_count(n=1):
    """Bump the per-minute FDO counter by ``n`` and return the new total."""
    key = _current_minute_key()
    try:
        return int(cache.incr(key, n))
    except ValueError:
        added = cache.add(key, n, timeout=FDO_MINUTE_WINDOW_SECONDS)
        if added:
            return n
        return int(cache.incr(key, n))
