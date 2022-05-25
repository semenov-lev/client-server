"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
import ipaddress

from task_1 import host_ping


def host_range_ping():
    while True:
        ip = input("Введите адрес узла: \n")
        try:
            ip = ipaddress.ip_address(ip)
        except ValueError:
            print(f"{ip} не подходит в качестве адреса!")
            continue
        diapason = input("Введите количество адресов: \n")
        try:
            diapason = int(diapason)
            if diapason < 1:
                print("Диапазон не может быть меньше единицы!")
                continue
        except TypeError as e:
            print(e)
            continue
        last_oct = int(str(ip).split('.')[-1])
        if last_oct + diapason > 255:
            diapason = 256 - last_oct
        host_ping([str(ip + i) for i in range(diapason)])


if __name__ == "__main__":
    host_range_ping()
