import os

print(os.getcwd())
import json

# Открываем файл и читаем его содержимое
with open('sources/decklists/stapleListMardu.txt', 'r') as file:
    lines = file.readlines()

# Извлекаем названия карт и создаем список
card_names = []
for line in lines:
    # Разбиваем строку на части
    parts = line.split()
    # Сбор названий карт до первого элемента, который начинается с цифры
    card_name = []
    for part in parts:
        if part[0].isdigit():  # Если первый символ - цифра, прерываем
            break
        card_name.append(part)  # Иначе добавляем в название карты
    card_names.append(' '.join(card_name))  # Объединяем название в строку

# Выводим полученный список
print(card_names)