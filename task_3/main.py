"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""

import yaml

data_to_yaml = {
    "items": ["computer", "printer", "keyboard", "mouse"],
    "items_quantity": 4,
    "items_price": {
        "computer": "200€-1000€",
        "keyboard": "5€-50€",
        "mouse": "4€-7€",
        "printer": "100€-300€"
    }
}

with open("file.yaml", "w", encoding="utf-8") as f_n:
    yaml.dump(data_to_yaml, f_n, default_flow_style=False, allow_unicode=True)

with open("file.yaml", "r", encoding="utf-8") as f_n:
    data = yaml.safe_load(f_n)

assert data == data_to_yaml, "Где-то напортачил"
