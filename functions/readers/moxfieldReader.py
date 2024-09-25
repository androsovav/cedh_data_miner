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