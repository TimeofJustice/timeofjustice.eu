from django.core.cache import cache


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")

    return forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")


def rate_limited(request, scope, limit, window):
    """
    True once `limit` requests from one address are seen within `window` seconds.

    Deliberately lightweight: it exists to stop pointless hammering, not a
    determined attacker, who could simply vary the forwarded address.
    """
    key = f"throttle:{scope}:{client_ip(request)}"

    cache.add(key, 0, window)

    try:
        attempts = cache.incr(key)
    except ValueError:
        # The entry expired between add and incr.
        cache.set(key, 1, window)
        attempts = 1

    return attempts > limit
