import inspect
import logging
import sys
from ipaddress import ip_address

module = inspect.stack()[-1].filename.split('\\')[-1]

if module == 'server.py':
    LOGGER = logging.getLogger("server_logger")
else:
    LOGGER = logging.getLogger("client_logger")


class Port:
    def __set__(self, instance, value):
        if 1024 > value or value > 65535:
            LOGGER.critical("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
            print("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
            sys.exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Host:
    def __set__(self, instance, value):
        try:
            ip_address(value)
        except ValueError:
            LOGGER.critical("Некорректно введен адрес")
            print("Некорректно введен адрес!")
            sys.exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
