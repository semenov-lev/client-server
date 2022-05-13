import sys
import time
import logging
from ipaddress import ip_address
from socket import socket, AF_INET, SOCK_STREAM

import common.variables as variables
from common.utils import encode_message, decode_data
from log import server_log_config
from decorators import log

SERVER_LOGGER = logging.getLogger("server_logger")


@log
def message_handler(message):
    action = variables.PRESENCE
    account_name = variables.ACCOUNT_NAME
    timestamp = int(time.time())

    try:
        SERVER_LOGGER.debug("Обработка сообщения от клиента")
        if message["action"] == action and message["time"] and message["user"]["account_name"] == account_name:
            SERVER_LOGGER.debug("Response 200")
            message = {"response": "200",
                       "time": timestamp}

        elif message["action"] == action and message["time"] and message["user"]["account_name"] != account_name:
            SERVER_LOGGER.warning("Response 404")
            message = {"response": "404",
                       "time": timestamp,
                       "alert": "Пользователь/чат отсутствует на сервере"}
        else:
            raise KeyError

    except (KeyError, TypeError):
        SERVER_LOGGER.warning("Некорректный запрос от клиента, код 400")
        message = {"response": "400",
                   "time": timestamp,
                   "alert": "Неправильный запрос/JSON-объект"}

    return message


def main():
    """
    server.py -a [<address>] -p [<port>]
    :return:
    """

    SERVER_LOGGER.debug(f"Запуск сервера")

    try:
        if "-a" in sys.argv:
            address = str(ip_address(sys.argv[sys.argv.index("-a") + 1]))
        else:
            address = ''
    except ValueError:
        SERVER_LOGGER.error("Некорректно введен адрес")
        sys.exit(1)

    try:
        if "-p" in sys.argv:
            port = int(sys.argv[sys.argv.index("-p") + 1])
            if 1024 > port > 65535:
                raise ValueError
        else:
            port = variables.DEFAULT_PORT
    except ValueError:
        SERVER_LOGGER.error("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.listen(variables.MAX_CONNECTIONS)

    while True:
        SERVER_LOGGER.debug("Ожидание клиента")

        client, client_address = s.accept()

        received_data = client.recv(variables.MAX_PACKAGE_LENGTH)

        received_message = decode_data(received_data)

        SERVER_LOGGER.info(f"Получено сообщение от клиента {client_address}")

        response_message = message_handler(received_message)
        response_data = encode_message(response_message)

        SERVER_LOGGER.info(f"Ответ клиенту {client_address}")

        client.send(response_data)

        client.close()


if __name__ == "__main__":
    main()
