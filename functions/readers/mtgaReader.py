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