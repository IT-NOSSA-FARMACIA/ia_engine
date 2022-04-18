from split_settings.tools import include

include(
    "config/base.py",
    "config/database.py",
    "config/cache.py",
    "config/logs.py",
    "config/celery.py",
    "config/roles.py",
    "config/notification.py",
    "config/development.py",
)
