import argparse
import sys
import time
import logging
from ipaddress import ip_address
from socket import socket, AF_INET, SOCK_STREAM

import common.variables as variables
from common.utils import encode_message, decode_data
from log import client_log_config
from decorators import log

CLIENT_LOGGER = logging.getLogger("client_logger")


@log
def arg_parser():
    parser = argparse.ArgumentParser(description='Client script')
    parser.add_argument('-a', dest='address', default='')
    parser.add_argument('-p', dest='port', default=variables.DEFAULT_PORT, type=int)
    parser.add_argument('-m', dest='mode', default="listen")
    args = parser.parse_args()
    address = args.address
    mode = args.mode
    port = args.port
    return address, port, mode


@log
def presence_message(account_name):
    action = variables.PRESENCE
    timestamp = int(time.time())
    status = "Я здесь!"

    return {
        "action": action,
        "time": timestamp,
        "type": "status",
        "user": {
            "account_name": account_name,
            "status": status
        }
    }


@log
def message_to_all(message, account_name):
    timestamp = int(time.time())

    return {
        "action": "msg",
        "time": timestamp,
        "to": "#all",
        "from": account_name,
        "message": message
    }


@log
def message_handler(message):
    if "action" in message and message["action"] == "msg":
        print(f"Сообщение от пользователя {message['from']}:\n"
              f"{message['message']}")
        CLIENT_LOGGER.info(f"Сообщение от пользователя {message['from']}: {message['message']}")
    else:
        if message["response"] == "200":
            print(f"Сообщение от сервера: {message}")
            CLIENT_LOGGER.info(f"Response: 200, ОК")
        else:
            print(f"Сообщение от сервера: {message}")
            CLIENT_LOGGER.warning(f"Response: {message}!!!")


def main():
    """
    client.py -a <address> -p [<port>] -m [mode]
    :return:
    """

    server_address, server_port, mode = arg_parser()

    try:
        ip_address(server_address)
    except ValueError:
        CLIENT_LOGGER.critical("Некорректно введен адрес")
        sys.exit(1)

    if 1024 > server_port or server_port > 65535:
        CLIENT_LOGGER.critical("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    if mode not in ('listen', 'sender'):
        CLIENT_LOGGER.critical("Режим может быть только 'listen', или 'sender'")
        sys.exit(1)

    if mode == 'sender':
        ACCOUNT_NAME = variables.SENDER_ACCOUNT_NAME
    else:
        ACCOUNT_NAME = variables.LISTEN_ACCOUNT_NAME

    CLIENT_LOGGER.debug(f"Подключаемся к серверу в режиме '{mode}'")

    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((server_address, server_port))

        CLIENT_LOGGER.info(f"Отправляем сообщение о присутствии")
        presence_data = encode_message(presence_message(ACCOUNT_NAME))
        s.send(presence_data)

        data = s.recv(variables.MAX_PACKAGE_LENGTH)
        message_handler(decode_data(data))

    except:
        CLIENT_LOGGER.critical("Произошла неведомая ошибка")
        sys.exit(1)

    while True:
        if mode == 'sender':
            try:
                msg = input("Ввести сообщение, или '/q' для выхода: ")
                if msg == '/q':
                    s.close()
                    sys.exit(0)

                message_data = encode_message(message_to_all(msg, ACCOUNT_NAME))
                s.send(message_data)
            except:
                CLIENT_LOGGER.debug(f"Соединение закрыто у режима {mode}")
                sys.exit(1)

        if mode == 'listen':
            try:
                receive_message = decode_data(s.recv(variables.MAX_PACKAGE_LENGTH))
                message_handler(receive_message)
            except:
                CLIENT_LOGGER.debug(f"Соединение закрыто у режима {mode}")
                sys.exit(1)


if __name__ == "__main__":
    main()
