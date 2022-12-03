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

sock_lock = threading.Lock()


class UserInteraction(threading.Thread):
    def __init__(self, sock, account_name):
        self.sock = sock
        self.account_name = account_name
        self.contacts = []
        super().__init__()
        self._contacts = 0

    def get_contacts(self):
        timestamp = int(time.time())

        send_message(self.sock,
                     {
                         "action": variables.GET_CONTACTS,
                         "time": timestamp,
                         "user_login": self.account_name
                     })
        try:
            message = recv_message(self.sock)
            self.contacts = message["alert"]

            self._contacts += 1
            print(f"Контакты получены {self._contacts}-й раз")
        except Exception as e:
            print(e, "Ошибка при получении контактов")
        else:
            print(f"Список контактов: {self.contacts}")

    def add_contact(self, username):
        timestamp = int(time.time())

        send_message(self.sock,
                     {
                         "action": variables.ADD_CONTACT,
                         "user_id": username,
                         "time": timestamp,
                         "user_login": self.account_name
                     })

    def delete_contact(self, username):
        timestamp = int(time.time())

        send_message(self.sock,
                     {
                         "action": variables.DEL_CONTACT,
                         "user_id": username,
                         "time": timestamp,
                         "user_login": self.account_name
                     })

    def msg_to_users(self, message, destination):
        timestamp = int(time.time())

        return {
            "action": "msg",
            "time": timestamp,
            "to": destination,
            "from": self.account_name,
            "message": message
        }

    def contacts_menu(self):
        command = ""
        print(f"\n{'–' * 100}\nМеню контактов\n{'–' * 100}")
        with sock_lock:
            self.get_contacts()
        # print(f"Контакты: {self.contacts}")

        operations_lst = ["Список контактов: /list",
                          "Добавить контакт: /add <username>",
                          "Удалить контакт: /del <username>",
                          "Выход: /q"]

        print("\n ".join(operations_lst))
        while command != "/q":
            command = str(input("\n"))
            if command.split()[0] == "/list":
                print(self.contacts)
            elif command.split()[0] == "/add":
                username = command.split()[1]
                self.add_contact(username)
            elif command.split()[0] == "/del":
                username = command.split()[1]
                self.delete_contact(username)
            else:
                print("Некорректный ввод")
        else:
            print(f"\n{'–' * 100}\nВыход в меню\n{'–' * 100}")

    def run(self):
        with sock_lock:
            self.get_contacts()
        print_menu()
        while True:
            print("UserInteractive начал цикл")
            command = str(input("Ввод: "))
            try:
                if command == '/q':
                    send_message(self.sock, {"action": "quit"})
                    break
                elif command in ("/help", "/h"):
                    print_menu()
                elif command == "/c":
                    self.contacts_menu()
                elif command == "/w":
                    destination = str(input("\nВведите имя адресата, или /q, чтобы выйти: "))
                    while destination != "/q":
                        print(f"Начало беседы с {destination}")
                        msg = str(input(f"{self.account_name}: "))
                        if msg != "/q":
                            send_message(self.sock, self.msg_to_users(msg, destination))
                        else:
                            print(f"\n{'–' * 100}\nВыход в меню\n{'–' * 100}")
                            break
                    else:
                        print(f"\n{'–' * 100}\nВыход в меню\n{'–' * 100}")

            except ConnectionAbortedError:
                print("\nСоединение разорвано!")
                CLIENT_LOGGER.warning("\nСоединение разорвано!")
                break
            print("UserInteractive закончил цикл")


class ClientRecv(threading.Thread):
    def __init__(self, sock, account_name):
        self.sock = sock
        self.account_name = account_name
        super().__init__()

    def run(self):
        while True:
            time.sleep(1)
            with sock_lock:
                print("ClientRecv начал цикл")
                try:
                    message = recv_message(self.sock)
                    # Разбор сообщения от пользователя
                    if "action" in message and "to" in message:
                        if message["action"] == "msg":
                            if message["to"] == self.account_name or message["to"] == "#all":
                                print(f"\n{message['from']}: {message['message']}")
                        CLIENT_LOGGER.info(
                            f"Сообщение от пользователя {message['from']} для {message['to']}: {message['message']}")
                    else:
                        # Разбор сообщения от сервера
                        response_handler(message)
                except ConnectionAbortedError:
                    print("\nСоединение разорвано!")
                    CLIENT_LOGGER.warning("Соединение разорвано!")
                    break
                except KeyError:
                    CLIENT_LOGGER.error("Отсутствует необходимый ключ в ответе")
                    print("\nОтсутствует необходимый ключ в ответе")
                    break
                print("ClientRecv закончил цикл")


def response_handler(message):
    code = message["response"]
    if code in ("200", "201", "202"):
        CLIENT_LOGGER.info(f"Cервер: {code}")
    elif code == "400":
        print(f"\nCервер: {code}, {message['alert']}")
        CLIENT_LOGGER.warning(f"Cервер: {code}, {message['alert']}")
    elif code == "404":
        print(f"\nCервер: {code}, {message['alert']}")
        CLIENT_LOGGER.warning(f"Cервер: {code}, {message['alert']}")


@log
def arg_parser():
    """
    Функция-парсер аргументов командной строки
    :return: tuple
    """
    parser = argparse.ArgumentParser(description='Client script')
    parser.add_argument('-a', dest='address', default='')
    parser.add_argument('-p', dest='port', default=variables.DEFAULT_PORT, type=int)
    args = parser.parse_args()
    address = args.address
    port = args.port
    return address, port


def print_menu():
    menu_lst = ["Написать сообщение пользователю: /w",
                "Контакты: /c", "Выход: /q",
                "Список команд: /help /h"]
    print("\n ".join(menu_lst))


def send_message(sock, message):
    """
    Отправляет сообщение на сервер
    :param sock:
    :param message:
    """
    sock.send(encode_message(message))


def recv_message(sock):
    """
    Возвращает сообщение-dict от сервера
    :param sock:
    :return: dict
    """
    print("Получаю сообщение")
    data = sock.recv(variables.MAX_PACKAGE_LENGTH)
    message = decode_data(data)
    print("Получил!")
    return message


@log
def presence_action(sock, account_name):
    CLIENT_LOGGER.info(f"Отправляем сообщение о присутствии")
    action = variables.PRESENCE
    timestamp = int(time.time())
    status = "Я здесь!"

    send_message(sock,
                 {
                     "action": action,
                     "time": timestamp,
                     "type": "status",
                     "user": {
                         "account_name": account_name,
                         "status": status
                     }
                 })

    response_msg = recv_message(sock)

    if response_msg["response"] == "200":
        print("Присутствие: ОК")
    else:
        print("Ошибка")
        sys.exit(1)


def main():
    """
    client.py -a <address> -p [<port>]
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
        transport = socket(AF_INET, SOCK_STREAM)
        account_name = str(input("Логин: "))

        # transport.settimeout(1)

        transport.connect((server_address, server_port))

    except Exception as e:
        print(e)
        CLIENT_LOGGER.critical("Ошибка соединения с сервером!")
        sys.exit(1)

    presence_action(transport, account_name)

    user_interaction = UserInteraction(transport, account_name)
    user_interaction.daemon = True

    client_recv = ClientRecv(transport, account_name)
    client_recv.daemon = True

    user_interaction.start()
    client_recv.start()

    while True:
        time.sleep(1)
        if user_interaction.is_alive() and client_recv.is_alive():
            continue
        break


if __name__ == "__main__":
    main()
