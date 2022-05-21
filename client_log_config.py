import logging
import logging.handlers

import settings as sett
import log_config               # Default logger config

log = logging.getLogger(sett.CLIENT_LOG_NAME)
log.propagate = True            # Propagate to the main logger to write to stderr
log.setLevel(sett.CLIENT_LOG_FILE_LEVEL)
log_handler = logging.FileHandler(sett.CLIENT_LOG_FILENAME)
log_handler.setFormatter(logging.Formatter(sett.CLIENT_LOG_FORMAT))
log.addHandler(log_handler)
