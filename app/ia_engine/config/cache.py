"""
    Cache config.
"""

MEMCACHE_URL = env.str("CACHE_URL", default="")

if MEMCACHE_URL:
    BACKEND_CACHE = "django.core.cache.backends.memcached.MemcachedCache"
else:
    BACKEND_CACHE = "django.core.cache.backends.filebased.FileBasedCache"

CACHES = {
    "default": {
        "BACKEND": BACKEND_CACHE,
        "LOCATION": MEMCACHE_URL or os.path.join(BASE_DIR, "ia_engine.cache"),
    }
}
