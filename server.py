import sys
import time
from ipaddress import ip_address
from socket import socket, AF_INET, SOCK_STREAM

import common.variables as variables
from common.utils import encode_message, decode_message


def message_handler(message):
    action = variables.PRESENCE
    account_name = variables.ACCOUNT_NAME
    timestamp = int(time.time())

    try:

        if message["action"] == action and message["time"] and message["user"]["account_name"] == account_name:

            message = {"response": "200",
                       "time": timestamp}

        elif message["action"] == action and message["time"] and message["user"]["account_name"] != account_name:

            message = {"response": "404",
                       "time": timestamp,
                       "alert": "Пользователь/чат отсутствует на сервере"}
        else:
            raise KeyError

    except KeyError:
        message = {"response": "400",
                   "time": timestamp,
                   "alert": "Неправильный запрос/JSON-объект"}

    return encode_message(message)


def main():
    """
    server.py -a [<address>] -p [<port>]
    :return:
    """

    try:
        if "-a" in sys.argv:
            address = str(ip_address(sys.argv[sys.argv.index("-a") + 1]))
        else:
            address = ''
    except ValueError:
        print("Некорректно введен адрес")
        sys.exit(1)

    try:
        if "-p" in sys.argv:
            port = int(sys.argv[sys.argv.index("-p") + 1])
            if 1024 > port > 65535:
                raise ValueError
        else:
            port = variables.DEFAULT_PORT
    except ValueError:
        print("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.listen(variables.MAX_CONNECTIONS)

    while True:
        client, client_address = s.accept()

        received_data = client.recv(variables.MAX_PACKAGE_LENGTH)

        received_message = decode_message(received_data)

        print(f"Сообщение от клиента: {received_message}")

        response_data = message_handler(received_message)

        client.send(response_data)

        client.close()


if __name__ == "__main__":
    main()
