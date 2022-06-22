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
        self.contacts = []

    def run(self):
        self.account_name = str(input("Ввести имя аккаунта: "))

        CLIENT_LOGGER.info(f"Отправляем сообщение о присутствии")

        # Отправляем приветствие и разбираем отклик
        self.presence_message()
        # Получаем список контактов из базы данных сервера
        self.get_contacts()

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
        menu_lst = ["Написать сообщение пользователю: /w",
                    "Контакты: /c", "Выход: /q",
                    "Список команд: /help /h"]
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
                    while msg != "/q":
                        msg = str(input())
                        self.server_socket.send(encode_message(self.send_message(msg, destination)))
                    else:
                        print(f"\n{'–' * 100}\nВыход в меню\n{'–' * 100}")
                elif command == "/c":
                    print(f"\n{'–' * 100}\nКонтакты\n{'–' * 100}")
                    self.print_contacts()
                    operations_lst = ["Список контактов: /list",
                                      "Добавить контакт: /add <username>",
                                      "Удалить контакт: /del <username>",
                                      "Выход: /q"]
                    for _ in operations_lst:
                        print("\n", _)
                    operation = ""
                    while operation != "/q":
                        self.get_contacts()
                        operation = str(input("\n"))
                        if operation.split()[0] == "/list":
                            self.print_contacts()
                        if operation.split()[0] == "/add":
                            try:
                                username = operation.split()[1]
                                self.add_contact(username)
                            except IndexError:
                                print("Некорректный ввод")
                        elif operation.split()[0] == "/del":
                            try:
                                username = operation.split()[1]
                                self.delete_contact(username)
                            except IndexError:
                                print("Некорректный ввод")
                    else:
                        print(f"\n{'–' * 100}\nВыход в меню\n{'–' * 100}")

            except ConnectionAbortedError:
                print("\nСоединение разорвано!")
                CLIENT_LOGGER.warning("\nСоединение разорвано!")
                break

    def receive_handler(self):
        while True:
            try:
                message = decode_data(self.server_socket.recv(variables.MAX_PACKAGE_LENGTH))
                # Разбор сообщения от пользователя
                if "action" in message and "to" in message:
                    if message["action"] == "msg":
                        if message["to"] == self.account_name or message["to"] == "#all":
                            print(f"\n{message['from']}: {message['message']}\n")
                    CLIENT_LOGGER.info(
                        f"Сообщение от пользователя {message['from']} для {message['to']}: {message['message']}")
                else:
                    # Разбор сообщения от сервера
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

        self.server_socket.send(encode_message({
            "action": action,
            "time": timestamp,
            "type": "status",
            "user": {
                "account_name": self.account_name,
                "status": status
            }
        }))

        response_data = self.server_socket.recv(variables.MAX_PACKAGE_LENGTH)
        self.response_handler(decode_data(response_data))

    def get_contacts(self):
        action = variables.GET_CONTACTS
        timestamp = int(time.time())

        self.server_socket.send(encode_message({
            "action": action,
            "time": timestamp,
            "user_login": self.account_name
        }))

        response_data = self.server_socket.recv(variables.MAX_PACKAGE_LENGTH)
        self.contacts = (decode_data(response_data))["alert"]

    def print_contacts(self):
        print("\n", '–' * 100)
        print("Список контактов: ", "\n".join(self.contacts))
        print("\n", '–' * 100)

    def add_contact(self, nickname):
        timestamp = int(time.time())

        self.server_socket.send(encode_message({
            "action": variables.ADD_CONTACT,
            "user_id": nickname,
            "time": timestamp,
            "user_login": self.account_name
        }))

    def delete_contact(self, nickname):
        timestamp = int(time.time())

        self.server_socket.send(encode_message({
            "action": variables.DEL_CONTACT,
            "user_id": nickname,
            "time": timestamp,
            "user_login": self.account_name
        }))

    def response_handler(self, response):
        code = response["response"]
        if code in ("200", "201", "202"):
            print(f"\nCервер: {code}")
            CLIENT_LOGGER.info(f"Cервер: {code}")
        elif code == "400":
            print(f"\nCервер: {code}, {response['alert']}")
            CLIENT_LOGGER.warning(f"Cервер: {code}, {response['alert']}")
        elif code == "404":
            print(f"\nCервер: {code}, {response['alert']}")
            CLIENT_LOGGER.warning(f"Cервер: {code}, {response['alert']}")

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
