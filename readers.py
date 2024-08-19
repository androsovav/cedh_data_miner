# Функция, читающая деклист с сайта mtggoldfish в формате для MTGA
def mtgaReader(file_name):
    commander_cards = []
    deck_cards = []
    in_deck_section = False
    in_commander_section = False
    
    with open(file_name, 'r') as file:
        for line in file:
            line = line.strip()
            
            if line == 'Commander':
                in_commander_section = True
                in_deck_section = False
                continue
            elif line == 'Deck':
                in_commander_section = False
                in_deck_section = True
                continue
            
            if in_commander_section and line:
                cmdr_card = line.split(' ', 1)[-1]
                commander_cards.append(cmdr_card)
                deck_cards.append(cmdr_card)  # Добавляем командира в список карт
            elif in_deck_section and line:
                card = line.split(' ', 1)[-1]
                deck_cards.append(card)
    return [' / '.join(commander_cards), deck_cards]

# Функция, читающая деклист с сайта moxfield в формате для moxfield
def moxfieldReader(file_name):
    card_names = set()  # Инициализация пустого набора set()
    
    with open(file_name, 'r') as file:
        for line in file:
            card_info = line.split('(')[0].split(' ', 2)
            if len(card_info) > 1:
                card_name = ' '.join(card_info[1:]).strip()  # Объединяем слова, начиная с второго и удаляем лишние пробелы
                card_names.add(card_name)
    
    return card_names

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