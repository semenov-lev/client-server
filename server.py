import sys
import logging
import argparse
from time import time
from select import select
from ipaddress import ip_address
from socket import socket, AF_INET, SOCK_STREAM

import common.variables as variables
from common.utils import encode_message, decode_data
from log import server_log_config
from decorators import log
from metaclasses import ServerControl

SERVER_LOGGER = logging.getLogger("server_logger")


@log
def arg_parser():
    parser = argparse.ArgumentParser(description='Server script')
    parser.add_argument('-a', dest='address', default=variables.DEFAULT_IP_ADDRESS)
    parser.add_argument('-p', dest='port', default=variables.DEFAULT_PORT, type=int)
    args = parser.parse_args()
    address = args.address
    port = args.port
    return address, port


class Server(metaclass=ServerControl):
    test_sock = socket(AF_INET, SOCK_STREAM)

    def __init__(self, address, port):
        self.all_clients = []
        self.receive_lst = []
        self.awaiting_lst = []
        self.messages = []
        self.accounts = {}
        self.address = address
        self.port = port
        try:
            ip_address(self.address)
        except ValueError:
            SERVER_LOGGER.critical("Некорректно введен адрес")
            sys.exit(1)
        self.sock = socket(AF_INET, SOCK_STREAM)

        if 1024 > self.port or self.port > 65535:
            SERVER_LOGGER.critical("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
            sys.exit(1)

    def run(self):
        SERVER_LOGGER.debug(f"Запуск сервера c адресом: {self.address}, портом: {self.port}")
        self.sock.bind((self.address, self.port))
        self.sock.settimeout(0.5)
        self.sock.listen(variables.MAX_CONNECTIONS)

        SERVER_LOGGER.info("Сервер запущен!")
        print("Сервер запущен!")

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                self.all_clients.append(client)
                SERVER_LOGGER.info(f"Клиент {client.getpeername()} подключился")
            finally:
                wait = 0
                try:
                    if self.all_clients:
                        self.receive_lst, self.awaiting_lst, errors = select(self.all_clients,
                                                                             self.all_clients,
                                                                             [], wait)
                except OSError:
                    pass

                if self.receive_lst:
                    for recv_client in self.receive_lst:
                        try:
                            peername = recv_client.getpeername()
                            SERVER_LOGGER.info(f"Получено сообщение от клиента {peername}")
                            received_data = recv_client.recv(variables.MAX_PACKAGE_LENGTH)
                            received_msg = decode_data(received_data)
                            self.message_handler(received_msg, recv_client)
                        except Exception as e:
                            print(e)
                            self.disconnect_client(recv_client)
                while self.awaiting_lst and self.messages:  # Лучше будет while self.awaiting_lst ...
                    self.send_to_address()

    @log
    def send_to_address(self):
        message = self.messages.pop(0)
        destination_name = message["to"]
        try:
            if self.accounts[destination_name] in self.awaiting_lst:
                self.accounts[destination_name].send(encode_message(message))
        except Exception as e:
            print(e)
            self.disconnect_client(self.accounts[destination_name])

    @log
    def disconnect_client(self, client):
        """
        Удаляет информацию о пользователе и отключает его от сокета

        :param client:
        :return:
        """
        client_name = None
        self.all_clients.remove(client)
        if client in self.receive_lst:
            self.receive_lst.remove(client)
        if client in self.awaiting_lst:
            self.awaiting_lst.remove(client)
        for k, v in self.accounts.items():
            if v == client:
                client_name = k
                del self.accounts[k]
                break
        client.close()
        print(f"Клиент {client_name} покинул чат")
        SERVER_LOGGER.info(f"Клиент {client_name} покинул чат")

    @log
    def message_handler(self, message, client):
        """
        Функция принимает и обрабатывает message - словарь,
        регистрирует новых пользователей и добавляет message
        в список messages

        :param message
        :param client
        :return
        """

        try:
            SERVER_LOGGER.debug("Обработка сообщения от клиента")
            if message["action"] == 'presence':
                sender = message["user"]["account_name"]

                if sender not in self.accounts:
                    self.accounts[sender] = client
                    client.send(encode_message({"response": "200",
                                                "time": time()}))
                    SERVER_LOGGER.debug(f"Регистрация нового пользователя {sender}")

                else:
                    client.send(encode_message({"response": "400",
                                                "time": time(),
                                                "alert": f"Пользователь {sender} уже существует!"}))
                    SERVER_LOGGER.warning(f"Response 400, Пользователь {sender} уже существует!")

            elif message["action"] == 'quit':
                self.disconnect_client(client)
                return

            elif message["action"] == 'msg':
                sender = message["from"]
                destination = message["to"]
                if destination not in self.accounts:
                    raise UserWarning
                else:
                    SERVER_LOGGER.debug(f"Получено сообщение от {sender} к {destination}")
                    self.messages.append(message)
            else:
                raise KeyError

        except UserWarning:
            SERVER_LOGGER.warning("Response 404")
            client.send(encode_message({"response": "404",
                                        "time": time(),
                                        "alert": "Получатель не в сети, или не зарегистрирован!"}))
        except (KeyError, TypeError):
            SERVER_LOGGER.warning("Response 400")
            client.send(encode_message({"response": "400",
                                        "time": time(),
                                        "alert": "Неправильный запрос/JSON-объект"}))
        return


def main():
    """
    server.py -a [<address>] -p [<port>]
    :return:
    """

    address, port = arg_parser()
    server = Server(address, port)
    server.run()


if __name__ == "__main__":
    main()
