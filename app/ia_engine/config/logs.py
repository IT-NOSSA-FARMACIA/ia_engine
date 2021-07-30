if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"level": "INFO", "handlers": ["file"]},
        "handlers": {
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",  # 'logging.handlers.RotatingFileHandler',
                "filename": "/var/log/ia_engine/django_request.log",
                #'maxBytes': 1024*1024*5, # 5 MB
                #'backupCount': 5,
                "formatter": "app",
            },
        },
        "loggers": {
            "django": {"handlers": ["file"], "level": "INFO", "propagate": True},
        },
        "formatters": {
            "app": {
                "format": (
                    u"%(asctime)s [%(levelname)-8s] "
                    "(%(module)s.%(funcName)s) %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
    }
