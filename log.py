""" Docstring for the log.py file.

"""
import logging
import logging.config
import os
from datetime import datetime

CONFIG_DIR = "./config"
LOG_DIR = "./logs"
STAGE = os.getenv('STAGE', 'dev')


def setup_logging() -> None:
    """
    Load logging configuration
    """
    log_configs = {"dev": "logging.dev.ini", "prod": "logging.prod.ini"}
    config = log_configs.get(STAGE, "logging.dev.ini")
    config_path = "/".join([CONFIG_DIR, config])

    timestamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename": f"{LOG_DIR}/{timestamp}.log"},
    )
