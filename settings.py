import logging

DEFAULT_PORT = 7777
DEFAULT_LISTEN_ADDRESS = ''
DEFAULT_SERVER_ADDRESS = '127.0.0.1'
DEFAULT_ENCODING = 'UTF-8'
MAX_DATA_LEN = 4096             # Maximum data size of the JIM message
CONNECTION_TIMEOUT = 60         # Connection timeout in seconds
SERVER_SOCKET_TIMEOUT = 0.2     # Server socket timeout in seconds
SERVER_SELECT_TIMEOUT = 1.0     # Server timeout for select.select() function waiting for clients
SERVER_MAX_CONNECTIONS = 100    # Maximum number of server connections
CLIENT_SELECT_TIMEOUT = 60.0     # Client timeout for select.select() function waiting for data

DIRECTORY_SEPARATOR = '/'

# *** Logging config
# Common settings
LOG_DIRECTORY = 'log'
# Console log - common for client and server
LOG_CONSOLE_LEVEL = logging.NOTSET
LOG_CONSOLE_FORMAT = "%(asctime)s %(levelname)-10s %(module)s %(message)s"
# Server log
SERVER_LOG_NAME = 'app.server'
SERVER_LOG_FILENAME = DIRECTORY_SEPARATOR.join((LOG_DIRECTORY, 'server.log'))
SERVER_LOG_BACKUP_DAYS_COUNT = 10       # Log backup days for daily logs
SERVER_LOG_FILE_LEVEL = logging.NOTSET
SERVER_LOG_FORMAT = "%(asctime)s %(levelname)-10s %(module)s %(message)s"
# Client log
CLIENT_LOG_NAME = 'app.client'
CLIENT_LOG_FILENAME = DIRECTORY_SEPARATOR.join((LOG_DIRECTORY, 'client.log'))
CLIENT_LOG_FILE_LEVEL = logging.NOTSET
CLIENT_LOG_FORMAT = "%(asctime)s %(levelname)-10s %(module)s %(message)s"
