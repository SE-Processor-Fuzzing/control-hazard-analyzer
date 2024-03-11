import logging.config


def apply() -> None:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "std_out": {
                "format": "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
                "datefmt": "%d-%m-%YT%I:%M:%SZ",
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "std_out",
            }
        },
        "loggers": {"": {"handlers": ["stdout"], "level": "WARNING"}},
    }

    logging.config.dictConfig(LOGGING)
