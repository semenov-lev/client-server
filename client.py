import argparse
import sys
import time
import logging
import threading
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
    args = parser.parse_args()
    address = args.address
    port = args.port
    return address, port


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
def response_handler(response):
    if response["response"] == "200":
        print(f"Сообщение от сервера: {response}")
        CLIENT_LOGGER.info(f"Response: 200, ОК")
    else:
        print(f"Сообщение от сервера: {response}")
        CLIENT_LOGGER.warning(f"Response: {response}!!!")


@log
def user_interaction(sock, account_name):
    while True:
        dest = str(input("Имя получателя, или '/q' для выхода: "))
        if dest == '/q':
            sock.close()
            sys.exit(0)
        msg = str(input(f"Cообщение для {dest}: "))

        message_data = encode_message(send_message(msg, account_name, dest))
        sock.send(message_data)


@log
def send_message(message, account_name, dest):
    timestamp = int(time.time())

    return {
        "action": "msg",
        "time": timestamp,
        "to": dest,
        "from": account_name,
        "message": message
    }


@log
def receive_handler(sock, account_name):
    while True:
        message = decode_data(sock.recv(variables.MAX_PACKAGE_LENGTH))

        try:
            # Сообщения пользователей
            if "action" in message and "to" in message:
                if message["action"] == "msg":
                    if message["to"] == account_name or message["to"] == "#all":
                        print(f"{message['from']}: {message['message']}")
                CLIENT_LOGGER.info(f"Сообщение от пользователя {message['from']} для {message['to']}: {message['message']}")
            else:
                # Сообщение от сервера
                response_handler(message)
        except KeyError:
            print("receive_handler не распознал ключ в ответе")


def main():
    """
    client.py -a <address> -p [<port>]
    :return:
    """

    server_address, server_port = arg_parser()

    try:
        ip_address(server_address)
    except ValueError:
        CLIENT_LOGGER.critical("Некорректно введен адресc!")
        sys.exit(1)

    if 1024 > server_port or server_port > 65535:
        CLIENT_LOGGER.critical("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    CLIENT_LOGGER.debug(f"Подключаемся к серверу...")

    try:
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.connect((server_address, server_port))

        CLIENT_LOGGER.info(f"Отправляем сообщение о присутствии")

        ACCOUNT_NAME = str(input("Ввести имя аккаунта: "))

        # Отправляем приветствие и разбираем отклик
        presence_data = encode_message(presence_message(ACCOUNT_NAME))
        server_socket.send(presence_data)

        response_data = server_socket.recv(variables.MAX_PACKAGE_LENGTH)
        response_handler(decode_data(response_data))

    except:
        CLIENT_LOGGER.critical("Ошибка соединения с сервером!")
        sys.exit(1)

    # try:
    # Ввод
    ui = threading.Thread(target=user_interaction, args=(server_socket, ACCOUNT_NAME))
    ui.daemon = True
    ui.start()

    # Вывод

    recv = threading.Thread(target=receive_handler, args=(server_socket, ACCOUNT_NAME))
    recv.daemon = True
    recv.start()
    # except:
    #     CLIENT_LOGGER.debug(f"Соединение прервано")
    #     sys.exit(1)

    while True:
        if ui.is_alive() and recv.is_alive():
            continue
        break


if __name__ == "__main__":
    main()
