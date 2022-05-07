import sys
import time
import logging
from ipaddress import ip_address
from socket import socket, AF_INET, SOCK_STREAM

import common.variables as variables
from common.utils import encode_message, decode_data
from log import client_log_config

CLIENT_LOGGER = logging.getLogger("client_logger")


def presence_message():
    action = variables.PRESENCE
    timestamp = int(time.time())
    status = "Я здесь!"
    account_name = "test_account"

    message = {
        "action": action,
        "time": timestamp,
        "type": "status",
        "user": {
            "account_name": account_name,
            "status": status
        }
    }

    return message


def main():
    """
    client.py -a <address> -p [<port>]
    :return:
    """

    try:
        if "-a" not in sys.argv:
            raise KeyError
        server_address = str(ip_address(sys.argv[sys.argv.index("-a") + 1]))
    except KeyError:
        CLIENT_LOGGER.error("Должен быть указан адрес: -a <address>")
        sys.exit(1)
    except ValueError:
        CLIENT_LOGGER.error("Некорректно введен адрес")
        sys.exit(1)

    try:
        if "-p" in sys.argv:
            server_port = int(sys.argv[sys.argv.index("-p") + 1])
            if 1024 > server_port > 65535:
                raise ValueError
        else:
            server_port = variables.DEFAULT_PORT
    except ValueError:
        CLIENT_LOGGER.error("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    CLIENT_LOGGER.debug("Подключаемся к серверу")
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((server_address, server_port))

    request_message = presence_message()
    request_data = encode_message(request_message)

    s.send(request_data)
    CLIENT_LOGGER.info(f"Отправляем сообщение на сервер")

    data = s.recv(variables.MAX_PACKAGE_LENGTH)

    CLIENT_LOGGER.info(f"Код ответа сервера: {decode_data(data)['response']}")

    s.close()

    CLIENT_LOGGER.debug("Соединение закрыто")


if __name__ == "__main__":
    main()
