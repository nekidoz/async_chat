import logging
import logging.handlers

import settings as sett
import log_config               # Default logger config

log = logging.getLogger(sett.SERVER_LOG_NAME)
log.propagate = True            # Propagate to the main logger to write to stderr
log.setLevel(sett.SERVER_LOG_FILE_LEVEL)
log_handler = logging.handlers.TimedRotatingFileHandler(
    sett.SERVER_LOG_FILENAME,
    when='D',
    interval=1,
    backupCount=sett.SERVER_LOG_BACKUP_DAYS_COUNT)
log_handler.setFormatter(logging.Formatter(sett.SERVER_LOG_FORMAT))
log.addHandler(log_handler)
