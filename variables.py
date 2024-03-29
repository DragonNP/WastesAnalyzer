import logging
import os

PATH_TO_USERS_DATA_BASE = './data/users.json'
PATH_TO_RESULT_POLL_DATA_BASE = './data/result_poll.json'
PATH_TO_LOG = './data/logger.log'
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_API', None)
GLOBAL_LOGGER_LEVEL = os.environ.get('LOGGER_LEVEL', logging.INFO)
USER_ID_ADMIN = 576476322
