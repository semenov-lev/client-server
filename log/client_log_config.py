import logging
import os


FORMAT = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s")

FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client.log")

LOGGER_HANDLER = logging.FileHandler(FILE_PATH, encoding='utf-8')
LOGGER_HANDLER.setFormatter(FORMAT)

LOGGER = logging.getLogger("client_logger")
LOGGER.addHandler(LOGGER_HANDLER)
LOGGER.setLevel(logging.DEBUG)

if __name__ == "__main__":
    LOGGER.debug('test-message')
    LOGGER.critical('test-message')
