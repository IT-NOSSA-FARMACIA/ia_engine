"""
    Celery Settings.
"""

from datetime import timedelta

CELERY_BEAT_SCHEDULE = {}

CELERY_BEAT_SCHEDULE["task-search-new-schedule"] = {
    "task": "sync.tasks.search_new_schedule",
    "schedule": timedelta(seconds=30),
    "kwargs": {},
}

CELERY_TASK_ROUTES = {
    "task_engine.tasks.search_new_schedule": {"queue": "search-new-schedule"},
}

BROKER_URL = env.str("CELERY_BROKER_URL", default="amqp://guest:guest@rabbitmq:5672/")
CELERY_BROKER_URL = BROKER_URL
CELERY_RESULT_BACKEND = "django-cache"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_IGNORE_RESULT = False
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = TIME_ZONE
CELERY_IMPORTS = [
    "task_engine.tasks",
]
CELERY_TASK_CREATE_MISSING_QUEUES = True