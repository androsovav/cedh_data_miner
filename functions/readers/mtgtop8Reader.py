# Функция, читающая деклист скопированный мной вручную с сайта mtgtop8
def mtgtop8Reader(file_name):
    # Открываем файл и читаем его содержимое
    with open(file_name, 'r') as file:
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
    return card_names