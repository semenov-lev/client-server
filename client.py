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
from metaclasses import ClientVerifier

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


class Client(metaclass=ClientVerifier):
    def __init__(self, server_socket):
        self.server_socket = server_socket
        self.account_name = ""

    def run(self):
        self.account_name = str(input("Ввести имя аккаунта: "))

        CLIENT_LOGGER.info(f"Отправляем сообщение о присутствии")

        # Отправляем приветствие и разбираем отклик
        presence_data = encode_message(self.presence_message())
        self.server_socket.send(presence_data)

        response_data = self.server_socket.recv(variables.MAX_PACKAGE_LENGTH)
        self.response_handler(decode_data(response_data))

        ui = threading.Thread(target=self.user_interaction)
        ui.daemon = True
        ui.start()

        recv = threading.Thread(target=self.receive_handler)
        recv.daemon = True
        recv.start()

        while True:
            # time.sleep(0.5)
            if ui.is_alive() and recv.is_alive():
                continue
            break

    def get_menu(self):
        menu_lst = ["Написать сообщение пользователю: /w", "Контакты: /c", "Выход: /q", "Список команд: /help /h"]
        for _ in menu_lst:
            print("\n", _)

    def user_interaction(self):
        self.get_menu()
        while True:
            msg = ""
            time.sleep(0.5)
            command = str(input("\n"))
            try:
                if command == '/q':
                    self.server_socket.send(encode_message({"action": "quit"}))
                    break
                elif command in ("/help", "/h"):
                    self.get_menu()
                elif command == "/w":
                    destination = str(input("\nВведите имя адресата, или /q, чтобы выйти: "))
                    print(f"\n{'–' * 100}\nЧат с пользователем '{destination}'\n{'–' * 100}")
                    while msg != "/q":
                        msg = str(input())
                        message_data = encode_message(self.send_message(msg, destination))
                        self.server_socket.send(message_data)
                    else:
                        print(f"\n{'–' * 100}\nВыход в меню\n{'–' * 100}")
                elif command == "/c":
                    self.get_contacts()
            except ConnectionAbortedError:
                print("\nСоединение разорвано!")
                CLIENT_LOGGER.warning("\nСоединение разорвано!")
                break

    def receive_handler(self):
        while True:
            try:
                message = decode_data(self.server_socket.recv(variables.MAX_PACKAGE_LENGTH))
                # Сообщения пользователей
                if "action" in message and "to" in message:
                    if message["action"] == "msg":
                        if message["to"] == self.account_name or message["to"] == "#all":
                            print(f"\n{message['from']}: {message['message']}\n")
                    CLIENT_LOGGER.info(
                        f"Сообщение от пользователя {message['from']} для {message['to']}: {message['message']}")
                else:
                    # Сообщение от сервера
                    self.response_handler(message)
            except ConnectionAbortedError:
                print("\nСоединение разорвано!")
                CLIENT_LOGGER.warning("Соединение разорвано!")
                break
            except KeyError:
                CLIENT_LOGGER.error("Отсутствует необходимый ключ в ответе")
                print("\nОтсутствует необходимый ключ в ответе")
                break

    def presence_message(self):
        action = variables.PRESENCE
        timestamp = int(time.time())
        status = "Я здесь!"

        return {
            "action": action,
            "time": timestamp,
            "type": "status",
            "user": {
                "account_name": self.account_name,
                "status": status
            }
        }

    def get_contacts(self):
        action = variables.GET_CONTACTS
        timestamp = int(time.time())

        return {
            "action": action,
            "time": timestamp,
            "user_login": self.account_name
        }

    def response_handler(self, response):
        code = response["response"]
        if code == "200":
            print(f"\nCервер: {code}, OK")
            CLIENT_LOGGER.info(f"Cервер: {code}, OK")
        elif code == "400":
            print(f"\nCервер: {code}, {response['alert']}")
            CLIENT_LOGGER.warning(f"Cервер: {code}, {response['alert']}")
        elif code == "404":
            print(f"\nCервер: {code}, {response['alert']}")
            CLIENT_LOGGER.warning(f"Cервер: {code}, {response['alert']}")

    @log
    def send_message(self, message, dest):
        timestamp = int(time.time())

        return {
            "action": "msg",
            "time": timestamp,
            "to": dest,
            "from": self.account_name,
            "message": message
        }


def main():
    """
    client.py -a <address> -p [<port>]
    :return:
    """

    server_address, server_port = arg_parser()

    CLIENT_LOGGER.debug(f"Подключаемся к серверу c адресом {server_address}, портом {server_port}...")

    try:
        ip_address(server_address)
    except ValueError:
        CLIENT_LOGGER.critical("Некорректно введен адресc!")
        sys.exit(1)

    if 1024 > server_port or server_port > 65535:
        CLIENT_LOGGER.critical("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    try:
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.connect((server_address, server_port))

    except Exception as e:
        print(e)
        CLIENT_LOGGER.critical("Ошибка соединения с сервером!")
        sys.exit(1)

    client = Client(server_socket)

    client.run()


if __name__ == "__main__":
    main()
