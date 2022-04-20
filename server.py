import socket
import sys
from socket import socket, AF_INET, SOCK_STREAM
import ipaddress
import yaml
import json


def get_variables():
    with open("common/settings.yaml", "r") as f_n:
        return yaml.safe_load(f_n)


def main():
    """
    server.py -a [<address>] -p [<port>]
    :return:
    """

    VARIABLES = get_variables()

    try:
        if "-a" in sys.argv:
            address = ipaddress.ip_address(sys.argv[sys.argv.index("-a") + 1])
        else:
            address = ''
    except ValueError:
        print(f'Некорректно введен адрес')
        sys.exit(1)

    try:
        if "-p" in sys.argv:
            port = int(sys.argv[sys.argv.index("-p") + 1])
            if 1024 > port > 65535:
                raise ValueError
        else:
            port = VARIABLES["DEFAULT_PORT"]
    except ValueError:
        print("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.listen(VARIABLES["MAX_CONNECTIONS"])

    while True:
        client, client_address = s.accept()
        data = client.recv(VARIABLES["MAX_PACKAGE_LENGTH"])


if __name__ == "__main__":
    main()
