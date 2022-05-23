import sys
import time
import logging
import argparse
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
def message_handler(message):
    """
    Функция принимает сообщение-словарь,
    проверяет информацию и возвращает сообщение-словарь

    :param message
    :return message
    """

    timestamp = int(time.time())
    account_names = [variables.LISTEN_ACCOUNT_NAME, variables.SENDER_ACCOUNT_NAME]

    try:
        SERVER_LOGGER.debug("Обработка сообщения от клиента")

        if message["action"] == variables.PRESENCE:
            if message["time"] and message["user"]["account_name"] in account_names:
                SERVER_LOGGER.debug("Response 200")
                return {"response": "200",
                        "time": timestamp}

            elif message["time"] and message["user"]["account_name"] not in account_names:
                SERVER_LOGGER.warning("Response 404")
                return {"response": "404",
                        "time": timestamp,
                        "alert": "Пользователь/чат отсутствует на сервере"}

        elif message["action"] == variables.MSG:
            if message["time"] and message["message"] and message["from"] == variables.SENDER_ACCOUNT_NAME \
                    and message["to"] == "#all":
                SERVER_LOGGER.debug("Response 200")
                return message

        else:
            raise KeyError

    except (KeyError, TypeError):
        SERVER_LOGGER.warning("Response 400")
        return {"response": "400",
                "time": timestamp,
                "alert": "Неправильный запрос/JSON-объект"}

    return message


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

    SERVER_LOGGER.debug(f"Запуск сервера c адрессом: {address}, портом: {port}")

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.settimeout(0.5)
    s.listen(variables.MAX_CONNECTIONS)

    all_clients = []
    messages = []

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
                        SERVER_LOGGER.info(f"Получено сообщение от клиента {recv_client.getpeername()}")
                        received_data = recv_client.recv(variables.MAX_PACKAGE_LENGTH)
                        received_msg = decode_data(received_data)
                        print(f"Получил сообщение {received_msg}")
                        messages.append(message_handler(received_msg))
                    except:
                        SERVER_LOGGER.info(f"Клиент {recv_client.getpeername()} отключился")
                        all_clients.remove(recv_client)

            if awaiting_lst and messages:
                message_data = encode_message(messages.pop(0))
                for awaiting_client in awaiting_lst:
                    try:
                        awaiting_client.send(message_data)
                    except:
                        SERVER_LOGGER.info(f"Клиент {awaiting_client.getpeername()} отключился")
                        all_clients.remove(awaiting_client)


if __name__ == "__main__":
    main()
