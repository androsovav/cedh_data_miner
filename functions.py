from collections import defaultdict
import classes
import itertools
import json
import requests
import time
import mtg_parser
import os
import ijson

# Функция, которая проверяет, удовлетворяет ли вход на турнир entry всем выставленным фильтрам
def myFilter(filters: classes.Filters, entry):
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

#   Основная функция парсинга базы данных. Принимает на вход фильтры и список из деклистов,
#   возвращает количество побед, игр, винрейт и погрешность вычисления винрейта для
#   каждого деклиста в списке.
def parse(filters: classes.Filters, listOfCardlists: list, dataFile: str):

    #   Инициализируем словарь-результат и словарь, запоминающий присутствие
    #   интересующих карт в деклисте
    res = dict()
    presence = dict()
    for card in filters.includeCardList:
        presence.update({card: False})
    for card in filters.excludeCardList:
        presence.update({card: False})
    for i in range(len(listOfCardlists)):
        res.update({i: {"wins": 0, "games": 0, "winrate": 0, "inaccuracy": 0}})
        for card in listOfCardlists[i].including:
            presence.update({card: False})
        for card in listOfCardlists[i].excluding:
            presence.update({card: False})

    with open(dataFile, 'r') as file:
        data = ijson.parse(file)
        wins = 0
        games = 0
        colorID = ""
        commander = ""
        date = 0
        for prefix, event, value in data:

            #   Встречая оглавление нового деклиста проверяем, соответствовал ли последний
            #   просмотренный всем требованиям. Если соответствовал, то учитываем его
            #   количество побед и игр. Затем в любом случае обнуляем presenceDict
            if event == "start_map":
                if (any(color == colorID for color in filters.colors) or (filters.colors == {})
                    and ((date >= filters.initialTime) or (filters.initialTime == 0))
                    and ((date <= filters.finalTime) or (filters.finalTime == 0))
                    and (any((card == commander) for card in filters.includeCommanders) or filters.includeCommanders == set())
                    and (any((card != commander) for card in filters.excludeCommanders) or filters.excludeCommanders == set())
                    and all((presence[card] for card in filters.includeCardList))
                    and not any((presence[card] for card in filters.excludeCardList))):
                        for i in range(len(listOfCardlists)):
                            if (all(presence[card] for card in listOfCardlists[i].including)
                            and not any(presence[card] for card in listOfCardlists[i].excluding)):
                                res[i].update({"wins": res[i]["wins"]+wins})
                                res[i].update({"games": res[i]["games"]+games})
                for card in presence:
                    presence.update({card: False})
                continue
            if prefix.endswith('.wins'):
                wins = value
            elif prefix.endswith('.games'):
                games = value
            elif prefix.endswith('.colorID'):
                colorID = value
            elif prefix.endswith('.commander'):
                commander = value
            elif prefix.endswith('.date'):
                date = value
            elif prefix.endswith('.decklist.item'):
                if value in presence:
                    presence.update({value: True})
    
    #   Зная количество побед и игр, подсчитываем винрейт и погрешность и записываем их в результат
    for i in range(len(listOfCardlists)):
        if res[i]["games"] != 0:
            res[i].update({"winrate": res[i]["wins"]/res[i]["games"]})
            res[i].update({"inaccuracy": res[i]["games"]**(-0.61)})

    return res

def newCalculateImpact(filters: classes.Filters, listOfSets: list, dataFile: str):
    listOfCardlists = []
    for i in range(len(listOfSets)):
        listOfCardlists.append(classes.cardlist(listOfSets[i], set()))
        listOfCardlists.append(classes.cardlist(set(), listOfSets[i]))
    parseRes = parse(filters, listOfCardlists, dataFile)
    res = []

    for i in range(len(listOfSets)):
        res.append({})
        res[i].update({"set": listOfSets[i]})
        res[i].update({"impact": parseRes[2*i]["winrate"]-parseRes[2*i+1]["winrate"]})
        res[i].update({"inaccuracy": (parseRes[2*i]["inaccuracy"]**2 + parseRes[2*i+1]["inaccuracy"]**2)**0.5})
    return res

# Функция, которая считает погрешность измерения винрейта на основе количества игр в выборке
def calculateInaccuracy(games):
    return games**(-0.61)

# Функция, которая подсчитывает средний винрейт всех колод в data, удовлетворяющих всем выставленным фильтрам
def calculateWinrate(filters: classes.Filters, data):
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
def calculateImpact(filters: classes.Filters, cardList: set, data):
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
def calculateIncludeRecomendations(filters: classes.Filters, stapleList, data):
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
def calculateExcludeRecomendations(filters: classes.Filters, data):
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
def calculatePopularity(filters: classes.Filters, data):
    return 0

# Функция, обновляющая базу данных
def updateDatabase():
    #   Берем из файла время последнего обновления, добавляем к нему секунду
    #   во избежание повторов. Если даты последнего обновления нет, берем 0.
    try:
        with open('sources/data/lastUpdateTime.txt', 'r') as file:
            lastUpdateTime = int(file.read()) + 1
    except:
        lastUpdateTime = 0

    #   Выставляем новое время последнего обновления базы данных
    newUpdateTime = round(time.time())
    with open('sources/data/lastUpdateTime.txt', 'w') as file:
        file.write(str(newUpdateTime))

    #   Загружаем базу данных турниров, проведенных после времени
    #   последнего обновления базы с сайта edhtop16.com
    base_url = "https://edhtop16.com/api/"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    filters = {
        'tourney_filter': {
            'dateCreated': {'$gte': lastUpdateTime}
        }
    }
    updateData = json.loads(requests.post(base_url + 'req', json=filters, headers=headers).text)

    with open('sources/data/data.json', 'r') as f:
        data = json.load(f)
        for entry in updateData:
            #   Отсеиваем все записи, в которых игрок не сыграл
            #   ни одной игры либо не указал ссылку на деклист,
            #   либо сыграл все игры вничью
            sum = entry['wins'] + entry['losses']
            if ((sum == 0)
                or ('decklist' not in entry)
                or (entry['decklist'] == "")
                or (entry['decklist'] == None)):
                    continue
            
            #   Блок try/except нужен для того, чтобы в случае
            #   неудачной попытки прочтения деклиста с сайта
            #   пропускать эту запись
            try:
                decklist = []
                url = entry['decklist']
                cards = mtg_parser.parse_deck(url)

                #   Разные сайты содержат деклисты в разных форматах,
                #   читаем название карты с первой буквы до первой
                #   скобки ( или до конца строки
                for card0 in cards:
                    card = str(card0)
                    j = 0
                    while j < len(card):
                        if card[j].isalpha():
                            break
                        j += 1
                    left = j

                    while j < len(card):
                        if card[j] == '(':
                            break
                        j += 1
                    right = j-1
                    if j == len(card):
                        right += 1
                    decklist.append(card[left:right])
            except Exception:
                continue
            
            #   Добавляем новую запись в базу данных
            if entry['decklist'] not in data:
                data.update({entry['decklist']: {
                    "wins": 0,
                    "games": 0,
                    "colorID": entry["colorID"],
                    "commander": entry["commander"],
                    "date": entry["dateCreated"],
                    "decklist": decklist          
                }})
            data[entry['decklist']].update({
                "wins": data[entry['decklist']]["wins"]+entry["wins"],
                "games": data[entry['decklist']]["games"]+sum,
                "date": entry["dateCreated"]
            })
    
    with open('sources/data/data.json', 'w') as f:
        json.dump(data, f, indent= '')