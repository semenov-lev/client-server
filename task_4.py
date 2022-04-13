"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""

words_str = ['разработка', 'администрирование', 'protocol', 'standard']

for word in words_str:
    word_encoded = word.encode('utf-8')
    word_decoded = word_encoded.decode('utf-8')
    print(f'Байтовое представление: {word_encoded}'
          f'\nСтроковое представление: {word_decoded}\n')
