import inspect
import logging

from log import client_log_config, server_log_config

module = inspect.stack()[-1].filename.split('\\')[-1]

if module == 'server.py':
    LOGGER = logging.getLogger("server_logger")
else:
    LOGGER = logging.getLogger("client_logger")


def log(func):
    def decorated(*args, **kwargs):
        LOGGER.debug(f"Функция {func.__name__} "
                     f"вызвана из функции {inspect.getouterframes(inspect.currentframe())[1].function} "
                     f"модуля {module}")
        return func(*args, **kwargs)

    return decorated
