import logging
import sys

import settings as sett


logging.basicConfig(
    stream=sys.stderr,
    level=sett.LOG_CONSOLE_LEVEL,
    format=sett.LOG_CONSOLE_FORMAT,
)
