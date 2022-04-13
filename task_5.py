"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""

import subprocess
import chardet

resources = [['ping', 'yandex.ru'],
             ['ping', 'youtube.com']]

for args in resources:
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        encoding = chardet.detect(line)['encoding']
        decoded_line = line.decode(encoding)
        encoded_line = decoded_line.encode('utf-8')
        print(encoded_line.decode('utf-8'))
    print('–' * 100)
