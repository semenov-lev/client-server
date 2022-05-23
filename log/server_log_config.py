import logging.handlers
import os


FORMAT = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s")

FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.log")

LOGGER_HANDLER = logging.handlers.TimedRotatingFileHandler(FILE_PATH, "D", 1, encoding='utf-8')
LOGGER_HANDLER.setFormatter(FORMAT)

LOGGER = logging.getLogger("server_logger")
LOGGER.addHandler(LOGGER_HANDLER)
LOGGER.setLevel(logging.DEBUG)

if __name__ == "__main__":
    LOGGER.debug('test-message')
    LOGGER.critical('test-message')
