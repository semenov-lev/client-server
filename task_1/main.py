"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""

import os
import re
import csv

data_files = [file_name for file_name in os.listdir('.') if file_name.find('info_') == 0]


def get_data():
    main_data = [["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]]
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []

    columns_data = [list(os_prod_list), os_name_list, os_code_list, os_type_list]

    for file_name in data_files:
        with open(file_name, 'r', encoding='utf-8') as f_n:
            for line in f_n:
                for i, column_name in enumerate(main_data[0]):
                    if re.search(column_name, line):
                        columns_data[i].append(line.split(":")[1].strip())

    for i in range(len(data_files)):
        row = [column[i] for column in columns_data]
        """
        В условии предлагают добавлять к каждой строке нумерацию: "1,LENOVO,Win..."
        При этом, не добавляют ее в шапку столбцов. В результате, количество строк в шапке
        и в теле таблицы, не сходится
        """
        # row.insert(0, i + 1)
        main_data.append(row)

    return main_data


def write_to_csv():
    file_name = input("Введите имя файла, в текущей директории: ")
    data = get_data()

    with open(file_name, 'w', encoding='utf-8') as f_n:
        f_n_writer = csv.writer(f_n)
        for row in data:
            f_n_writer.writerow(row)


write_to_csv()
