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


@log
def message_handler(message, client, queue, messages, accounts, all_clients):
    """
    Функция принимает и обрабатывает message - словарь,
    регистрирует новых пользователей и добавляет message
    в список messages

    :param message
    :param client
    :param queue:
    :param messages
    :param accounts
    :param all_clients:
    :return
    """

    try:
        SERVER_LOGGER.debug("Обработка сообщения от клиента")
        if message["action"] == 'presence':
            sender = message["user"]["account_name"]

            if sender not in accounts:
                accounts[sender] = client
                client.send(encode_message({"response": "200",
                                            "time": time()}))
                SERVER_LOGGER.debug(f"Регистрация нового пользователя {sender}")

            else:
                client.send(encode_message({"response": "400",
                                            "time": time(),
                                            "alert": f"Пользователь {sender} уже существует!"}))
                SERVER_LOGGER.warning(f"Response 400, Пользователь {sender} уже существует!")

        elif message["action"] == 'quit':
            disconnect_client(client, queue, all_clients, accounts)
            return

        elif message["action"] == 'msg':
            sender = message["from"]
            destination = message["to"]
            if destination not in accounts:
                raise UserWarning
            else:
                SERVER_LOGGER.debug(f"Получено сообщение от {sender} к {destination}")
                messages.append(message)
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


@log
def send_to_address(awaiting_clients, messages, accounts, all_clients):
    message = messages.pop(0)
    destination_name = message["to"]
    try:
        if accounts[destination_name] in awaiting_clients:
            accounts[destination_name].send(encode_message(message))
    except:
        disconnect_client(accounts[destination_name], awaiting_clients, all_clients, accounts)


@log
def disconnect_client(client, queue, all_clients, accounts):
    '''
    Удаляет информацию о пользователе и отключает его от сокета

    :param client:
    :param queue:
    :param all_clients:
    :param accounts:
    :return:
    '''
    client_name = None
    all_clients.remove(client)
    queue.remove(client)
    for k, v in accounts.items():
        if v == client:
            client_name = k
            del accounts[k]
            break
    client.close()
    print(f"Клиент {client_name} покинул чат")
    SERVER_LOGGER.info(f"Клиент {client_name} покинул чат")


def main():
    """

    server.py -a [<address>] -p [<port>]
    :return:
    """

    address, port = arg_parser()

    try:
        ip_address(address)
    except ValueError:
        SERVER_LOGGER.critical("Некорректно введен адрес")
        sys.exit(1)

    if 1024 > port or port > 65535:
        SERVER_LOGGER.critical("Значение <port> должно быть числом, в диапазоне с 1024 по 65535")
        sys.exit(1)

    SERVER_LOGGER.debug(f"Запуск сервера c адресом: {address}, портом: {port}")

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.settimeout(0.5)
    s.listen(variables.MAX_CONNECTIONS)

    all_clients = []
    messages = []
    accounts = {}

    SERVER_LOGGER.info("Сервер запущен!")
    print("Сервер запущен!")
    while True:
        try:
            client, client_address = s.accept()
        except OSError:
            pass
        else:
            all_clients.append(client)
            SERVER_LOGGER.info(f"Клиент {client.getpeername()} подключился")
        finally:
            wait = 0
            receive_lst = []
            awaiting_lst = []

            try:
                if all_clients:
                    receive_lst, awaiting_lst, errors = select(all_clients, all_clients, [], wait)
            except OSError:
                pass

            if receive_lst:
                for recv_client in receive_lst:
                    try:
                        peername = recv_client.getpeername()
                        SERVER_LOGGER.info(f"Получено сообщение от клиента {peername}")
                        received_data = recv_client.recv(variables.MAX_PACKAGE_LENGTH)
                        received_msg = decode_data(received_data)
                        message_handler(received_msg, recv_client, receive_lst, messages, accounts, all_clients)
                    except:
                        disconnect_client(recv_client, receive_lst, all_clients, accounts)

            if awaiting_lst and messages:
                send_to_address(awaiting_lst, messages, accounts, all_clients)


if __name__ == "__main__":
    main()
