from collections import defaultdict
import itertools

# Функция, которая проверяет, удовлетворяет ли вход на турнир entry всем выставленным фильтрам
def myFilter(filters, entry):
    try:
            # Условие выполняется только если в колоде найдется каждая карта из списка cardlist
            return (any(color == entry['colorID'] for color in filters.colors) or (filters.colors == {})
                    and ((entry['dateCreated'] >= filters.initialTime) or (filters.initialTime == 0))
                    and ((entry['dateCreated'] <= filters.finalTime) or (filters.finalTime == 0))
                    and (any((commander == entry['commander']) for commander in filters.includeCommanders) or filters.includeCommanders == set())
                    and (any((commander != entry['commander']) for commander in filters.excludeCommanders) or filters.excludeCommanders == set())
                    and all((card in set(entry['truedecklist']) for card in filters.includeCardList))
                    and not any((card in set(entry['truedecklist']) for card in filters.excludeCardList)))
    except Exception:
        return False

# Функция, которая считает погрешность измерения винрейта на основе количества игр в выборке
def calculateInaccuracy(games):
    return games**(-0.61)

# Функция, которая подсчитывает средний винрейт всех колод в data, удовлетворяющих всем выставленным фильтрам
def calculateWinrate(filters, data):
    wins = 0
    games = 0

    for entry in data:
        if myFilter(filters, entry):
            wins += entry['wins']
            games += entry['wins'] + entry['losses']

    if games >= 25:
        winrate = round((wins / games) * 100, 2)
    else:
        winrate = 0

    return winrate

# Функция, которая оценивает вклад карт из cardList на основе разницы винрейта с ними и без них для колод, удовлетворяющих выставленным фильтрам
def calculateImpact(filters, cardList: set, data):
    winsWith = 0
    winsWithout = 0
    gamesWith = 0
    gamesWithout = 0
    impact = 0
    for entry in data:
        if myFilter(filters, entry):
            try:
                if all((card in set(entry['truedecklist']) for card in cardList)):
                    winsWith += entry['wins']
                    gamesWith += entry['wins'] + entry['losses']
                else:
                    winsWithout += entry['wins']
                    gamesWithout += entry['wins'] + entry['losses']
            except:
                continue
    if gamesWith != 0 and gamesWithout != 0:
        winrateWith = winsWith/gamesWith
        winrateWithout = winsWithout/gamesWithout
        impact = winrateWith - winrateWithout
        inaccury = (calculateInaccuracy(gamesWith)**2 + calculateInaccuracy(gamesWithout)**2)**0.5
        return [impact, inaccury]
    else:
        return [0, 0]

# Функция, которая составляет список рекомендаций среди карт из списка stapleList для колоды includeCardList на основе колод из data, удовлетворяющих выставленным фильтрам
def calculateIncludeRecomendations(filters, stapleList, data):
    combinations = [(card, staple) for card in filters.includeCardList for staple in stapleList if not staple in filters.includeCardList]

    winsWith = defaultdict(int)
    winsWithout = defaultdict(int)
    gamesWith = defaultdict(int)
    gamesWithout = defaultdict(int)
    synergies = defaultdict(int)
    inaccuracy = defaultdict(int)

    #этот фильтр отличается от оригинального тем, что не обязывает колоды включать в себя какие-то определенные карты
    newFilter = filters
    newFilter.includeCardList = set()

    for entry in data:
        try:
            if myFilter(newFilter, entry):
                decklist = set(entry['truedecklist'])
                for combination in combinations:
                    if combination[0] in decklist:
                        if combination[1] in decklist:
                            winsWith[combination] += entry['wins']
                            gamesWith[combination] += entry['wins'] + entry['losses']
                        else:
                            winsWithout[combination] += entry['wins']
                            gamesWithout[combination] += entry['wins'] + entry['losses']
        except Exception:
            continue

    for combination in combinations:
        if gamesWith[combination] and gamesWithout[combination]:
            synergies[combination[1]] = round(((winsWith[combination]/gamesWith[combination]) - (winsWithout[combination]/gamesWithout[combination]))*100, 2)
            inaccuracy[combination[1]] = round(((calculateInaccuracy(gamesWith[combination])**2 + calculateInaccuracy(gamesWithout[combination])**2)**0.5)*100, 2)

    sorted_synergies = {k: v for k, v in sorted(synergies.items(), key=lambda item: item[1], reverse=True)}
    result = dict()
    for k, v in sorted_synergies.items():
        result[k] = [v, inaccuracy[k]]
    return result

# Функция, которая составляет список рекомендаций среди карт из списка stapleList для колоды includeCardList на основе колод из data, удовлетворяющих выставленным фильтрам
def calculateExcludeRecomendations(filters, data):
    combinations = set(itertools.combinations(filters[5], 2))

    # В этих словарях ключом является комбинация карт, значением является список из побед/игр/винрейтов первой карты из комбинации без второй,
    # второй карты из комбинации без первой, и самой комбинации
    combinationWins = {}
    combinationGames = {}
    combinationWinrates = {}
    combinationSynergies = {}
    synergies = {}
    for card in filters[5]:
        synergies[card] = 0

    for combination in combinations:
        combinationWins[combination] = [0, 0, 0]
        combinationGames[combination] = [0, 0, 0]
        combinationWinrates[combination] = 0
        combinationSynergies[combination] = 0


    for entry in data:
        try:
            if myFilter([filters[0], filters[1], filters[2], filters[3], filters[4], [], filters[6]], entry):
                decklist = set(entry['truedecklist'])
                for combination in combinations:
                    if combination[0] in decklist and combination[1] in decklist:
                        combinationWins[combination][2] += entry['wins']
                        combinationGames[combination][2] += entry['wins'] + entry['losses']
                    elif combination[0] in decklist:
                        combinationWins[combination][0] += entry['wins']
                        combinationGames[combination][0] += entry['wins'] + entry['losses']
                    elif combination[1] in decklist:
                        combinationWins[combination][1] += entry['wins']
                        combinationGames[combination][1] += entry['wins'] + entry['losses']
        except Exception:
            continue

    for combination in combinations:
        if all(games > 0 for games in combinationGames[combination]):
            combinationSynergies[combination] = round(((combinationWins[combination][0]/combinationGames[combination][0]) - (combinationWins[combination][1]/combinationGames[combination][1]))*100,2)
    
    for card in filters[5]:
        for combination in combinations:
            if(combinationGames[combination][2] <= 20):
                continue
            if combination[0] == card and (combinationGames[combination][1] >= 20):
                synergies[card] += (combinationWins[combination][2]/combinationGames[combination][2]) - (combinationWins[combination][1]/combinationGames[combination][1])
            elif combination[1] == card and (combinationGames[combination][0] >= 20):
                synergies[card] += (combinationWins[combination][2]/combinationGames[combination][2]) - (combinationWins[combination][0]/combinationGames[combination][0])

    sorted_synergies = {k: v for k, v in sorted(synergies.items(), key=lambda item: item[1], reverse=False)[:10]}
    return sorted_synergies

# Функция, считающая количество колод с выставленными фильтрами
def calculatePopularity(filters, data):
    return 0

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