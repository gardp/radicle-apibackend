import redis
from django.conf import settings
from datetime import datetime, timedelta

def get_redis_client():
    """Get Redis client using Celery broker URL."""
    redis_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
    return redis.from_url(redis_url, decode_responses=True)

def check_rate_limit(ip_address, limit=5, window_hours=1):
    """
    Check if IP has exceeded rate limit.
    Returns (allowed, remaining, reset_time)
    """
    client = get_redis_client()
    now = datetime.utcnow()
    hour_bucket = now.replace(minute=0, second=0, microsecond=0)
    key = f"contact_us:{ip_address}:{hour_bucket.strftime('%Y%m%d%H')}"

    try:
        current = client.incr(key)
        client.expire(key, (window_hours + 1) * 3600)  # +1 hour buffer
        remaining = max(0, limit - current)
        allowed = current <= limit
        reset_time = hour_bucket + timedelta(hours=window_hours)
        return allowed, remaining, reset_time
    except Exception:
        # If Redis fails, allow the request (fail open)
        return True, limit, now + timedelta(hours=window_hours)