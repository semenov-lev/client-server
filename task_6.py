"""
Задание 6.

Создать  НЕ программно (вручную) текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».

Принудительно программно открыть файл в формате Unicode и вывести его содержимое.
Что это значит? Это значит, что при чтении файла вы должны явно указать кодировку utf-8
и файл должен открыться у ЛЮБОГО!!! человека при запуске вашего скрипта.

При сдаче задания в папке должен лежать текстовый файл!

Это значит вы должны предусмотреть случай, что вы по дефолту записали файл в cp1251,
а прочитать пытаетесь в utf-8.

Преподаватель будет запускать ваш скрипт и ошибок НЕ ДОЛЖНО появиться!

Подсказки:
--- обратите внимание, что заполнять файл вы можете в любой кодировке
но открыть нужно ИМЕННО!!! в формате Unicode (utf-8)
--- обратите внимание на чтение файла в режиме rb
для последующей переконвертации в нужную кодировку

НАРУШЕНИЕ обозначенных условий - задание не выполнено!!!
"""

import chardet

FILE = 'test_file.txt'


def convert_encoding(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
        encoding = chardet.detect(content)['encoding']
        decoded_content = content.decode(encoding)

    with open(file_path, 'wb') as file:
        file.write(decoded_content.encode('utf-8'))
        file.close()


def read_file(file_path):
    convert_encoding(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        print(file.read())


read_file(FILE)
