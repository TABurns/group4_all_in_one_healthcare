# logger_config.py


import sys

from loguru import logger

from ui.config.paths import LOG_FILE

logger.remove()


if getattr(sys, "frozen", False):
    logger.add(sink=LOG_FILE, format="{time:YYYY-MM-DD HH:mm} | {level}    | {message}", rotation="500KB")


else:
    logger.add(sink=sys.stdout)
