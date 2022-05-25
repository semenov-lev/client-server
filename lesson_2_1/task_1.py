"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
import ipaddress
import subprocess
import socket


def host_ping(nodes: list):
    results = {"Reachable": [],
               "Unreachable": []}
    for node in nodes:
        try:
            address = ipaddress.ip_address(node)
        except ValueError:
            try:
                address = socket.gethostbyname(node)
            except socket.gaierror:
                print(f"'{node}' не является именем хоста, или ip-адресом!")
                results["Unreachable"].append(str(node))
                continue
        process = subprocess.Popen(f"ping {address}", shell=False, stdout=subprocess.PIPE)
        process.wait()
        if process.returncode == 0:
            results["Reachable"].append(str(node))
        else:
            results["Unreachable"].append(str(node))

    print(f"Доступные адреса: {results['Reachable']}\nНедоступные адреса: {results['Unreachable']}")


if __name__ == "__main__":
    addresses = ['yandex.ru', 'google.com', '127.0.0.1', 'asdasdasdasudih']

    host_ping(addresses)
