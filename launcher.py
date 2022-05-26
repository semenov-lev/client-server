"""Скрипт создавался под Windows"""
import subprocess
import argparse
import time


def arg_parser():
    parser = argparse.ArgumentParser(description='Run application')
    parser.add_argument("-c", dest="count", default=2, type=int)
    args = parser.parse_args()
    count = args.count
    return count


def kill_processes(processes):
    if processes:
        for i in processes:
            i.kill()
        processes.clear()


def main():
    clients_count = arg_parser()

    processes = []

    while True:
        print(f"Действия:\n/q – выход;\n/s – запуск сервера и ({clients_count}) клиент-окон\n")
        action = input(": ")

        if action == "/s":
            kill_processes(processes)
            processes.append(
                subprocess.Popen("python server.py", creationflags=subprocess.CREATE_NEW_CONSOLE))
            time.sleep(0.5)
            print("Сервер запущен!")

            for i in range(clients_count):
                processes.append(
                    subprocess.Popen("python client.py -a 127.0.0.1", creationflags=subprocess.CREATE_NEW_CONSOLE))

        elif action == "/q":
            kill_processes(processes)
            break

        else:
            print("Некорректный ввод!\n")
            continue


if __name__ == "__main__":
    main()
