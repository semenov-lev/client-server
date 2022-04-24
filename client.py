import sys
import time
from ipaddress import ip_address
from socket import socket, AF_INET, SOCK_STREAM

import common.variables as variables
from common.utils import encode_message, decode_data


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

    return encode_message(message)


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
        print("Должен быть указан адрес: -a <address>")
        sys.exit(1)
    except ValueError:
        print("Некорректно введен адрес")
        sys.exit(1)

    try:
        if "-p" in sys.argv:
            server_port = int(sys.argv[sys.argv.index("-p") + 1])
            if 1024 > server_port > 65535:
                raise ValueError
        else:
            server_port = variables.DEFAULT_PORT
    except ValueError:
        print("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((server_address, server_port))

    s.send(presence_message())

    data = s.recv(variables.MAX_PACKAGE_LENGTH)

    print(f"Полученное сообщение от сервера: {decode_data(data)}")

    s.close()


if __name__ == "__main__":
    main()
