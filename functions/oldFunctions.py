from collections import defaultdict
import classes.classes as classes
import itertools
import json
import requests
import time
import mtg_parser
import os
import ijson

# Основная функция парсинга базы данных. Принимает на вход фильтры и список из деклистов,
# возвращает количество побед, игр, винрейт и погрешность вычисления винрейта для
# каждого деклиста в списке.
def parse(filters: classes.Filters, listOfCardlists: list, dataFile: str):

    #   Инициализируем словарь-результат и словарь presence, запоминающий присутствие
    #   интересующих карт в деклисте
    res = dict()
    for i in range(len(listOfCardlists)):
        res.update({i: {"wins": 0, "games": 0, "winrate": 0, "inaccuracy": 0}})
    
    #   Загружаем базу данных в переменную
    with open(dataFile, 'r') as file:
        data = json.load(file)
    
    timer = []
    t = 0

    #   Парсим базу данных
    for entry in data:
        timer.append({})
        timer[t].update({"start": time.time()})
        decklist = set(data[entry]["decklist"])
        timer[t].update({"loading decklist": time.time()})
        #   В этом блоке if отсеиваются все колоды, не удовлетворяющие выставленным фильтрам
        if (any(color == data[entry]["colorID"] for color in filters.colors) or (filters.colors == {})
                and ((data[entry]["date"] >= filters.initialTime) or (filters.initialTime == 0))
                and ((data[entry]["date"] <= filters.finalTime) or (filters.finalTime == 0))
                and (any((card == data[entry]["commander"]) for card in filters.includeCommanders) or filters.includeCommanders == set())
                and (any((card != data[entry]["commander"]) for card in filters.excludeCommanders) or filters.excludeCommanders == set())
                and all(card in decklist for card in filters.includeCardList)
                and not any((card in decklist for card in filters.excludeCardList))):
                    timer[t].update({"checking all ifs": time.time()})

                    #   В этом цикле проверяем наличие каждой карты из тех, что должны присутствовать 
                    #   либо отсутствовать в деклисте (список таких карт хранится в полях .including 
                    #   и .excluding класса cardlist). Если условия выполнены, победы и игры учитываются
                    #   при подсчете статистики
                    for i in range(len(listOfCardlists)):
                        if (listOfCardlists[i].including.issubset(decklist)
                        and not listOfCardlists[i].excluding.intersection(decklist)):
                            res[i].update({"wins": res[i]["wins"]+data[entry]["wins"]})
                            res[i].update({"games": res[i]["games"]+data[entry]["games"]})
                    timer[t].update({"checking decklist for including/excluding": time.time()})
        else:
            timer[t].update({"checking all ifs": time.time()})
        t += 1
    
    #  Зная количество побед и игр, подсчитываем винрейт и погрешность и записываем их в результат
    for i in range(len(listOfCardlists)):
        if res[i]["games"] != 0:
            res[i].update({"winrate": res[i]["wins"]/res[i]["games"]})
            res[i].update({"inaccuracy": res[i]["games"]**(-0.61)})
        else:
            res[i].update({"winrate": 0, "inaccuracy": 0})
    
    #   Сортируем полученный результат
    sorted_res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1]["winrate"]-item[1]["inaccuracy"], reverse=True)}
    final_res = []
    
    res_timer = {"loading decklist": 0, "checking all ifs": 0, "checking decklist for including/excluding": 0}
    helper = 0
    for t in range(len(timer)):
        res_timer["loading decklist"] = res_timer["loading decklist"] + (timer[t]["loading decklist"]-timer[t]["start"])
        res_timer["checking all ifs"] = res_timer["checking all ifs"] + (timer[t]["checking all ifs"]-timer[t]["loading decklist"])
        if "checking decklist for including/excluding" in timer[t]:
            res_timer["checking decklist for including/excluding"] = res_timer["checking decklist for including/excluding"] + (timer[t]["checking decklist for including/excluding"]-timer[t]["checking all ifs"])
            helper += 1
    print("loading decklist" + " " + str(res_timer["loading decklist"]/len(timer)))
    print("checking all ifs" + " " + str(res_timer["checking all ifs"]/len(timer)))
    print("checking decklist for including/excluding" + " " + str(res_timer["checking decklist for including/excluding"]/helper))

    #   Возвращаем результат в формате [[список карт, его показатели], ...]
    for item in sorted_res:
        final_res.append([listOfCardlists[item], sorted_res[item]])
    return final_res

# Копия функции parse, оптимизированная для работы с большими базами данных, не вмещающимися в память.
def largeParse(filters: classes.Filters, listOfCardlists: list, dataFile: str):

    #   Инициализируем словарь-результат и словарь presence, запоминающий присутствие
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
    
    #  Зная количество побед и игр, подсчитываем винрейт и погрешность и записываем их в результат
    for i in range(len(listOfCardlists)):
        if res[i]["games"] != 0:
            res[i].update({"winrate": res[i]["wins"]/res[i]["games"]})
            res[i].update({"inaccuracy": res[i]["games"]**(-0.61)})
    
    #   Сортируем полученный результат
    sorted_res = {k: v for k, v in sorted(res.items(), key=lambda item: item[1]["winrate"]-item[1]["inaccuracy"], reverse=True)}
    final_res = []
    
    #   Возвращаем результат в формате [[список карт, его показатели], ...]
    for item in sorted_res:
        final_res.append([listOfCardlists[item], sorted_res[item]])
    return final_res

# Функция, которая оценивает вклад в победу каждого из наборов карт в listOfSets
# на основе разницы винрейта колод с этим набором карт и без него с учетом выставленных фильтров
def CalculateImpact(filters: classes.Filters, listOfSets: list, dataFile: str):
    listOfCardlists = []
    #   Формируем список из наборов карт для функции parse. Для каждого набора из listOfSets
    #   будет учтена статистика колод, включающих каждую карту этого набора, и колод,
    #   исключающих каждую карту этого набора
    for i in range(len(listOfSets)):
        listOfCardlists.append(classes.cardlist(listOfSets[i], set()))
        listOfCardlists.append(classes.cardlist(set(), listOfSets[i]))
    
    parseRes = parse(filters, listOfCardlists, dataFile)

    res = []

    #   Теперь из данных, возвращенных функцией parse, нужно извлечь все необходимое. В список res
    #   для каждого набора попадет информация о винрейте с ним и без него, количестве игр
    #   с ним и без него, а так же погрешности для рассчета конечной погрешности
    for i in range(len(listOfSets)):
        gamesWith = 0
        gamesWithout = 0
        winrateWith = 0
        winrateWithout = 0
        impact = 0
        inaccuracyWith = 0
        inaccuracyWithout = 0
        inaccuracy = 0
        for j in range(len(parseRes)):
            if parseRes[j][0].including == listOfSets[i]:
                winrateWith = parseRes[j][1]["winrate"]
                inaccuracyWith = parseRes[j][1]["inaccuracy"]
                gamesWith = parseRes[j][1]["games"]
            if parseRes[j][0].excluding == listOfSets[i]:
                winrateWithout = parseRes[j][1]["winrate"]
                inaccuracyWithout = parseRes[j][1]["inaccuracy"]
                gamesWithout = parseRes[j][1]["games"]
                
        #   Импакт, он же вклад, рассчитывается как разница винрейтов колод с этим набором карт и без него
        impact = winrateWith - winrateWithout

        #   Погрешность импакта рассчитывается из погрешностей винрейтов с набором карт и без него
        inaccuracy = (inaccuracyWith**2 + inaccuracyWithout**2)**0.5
        res.append([listOfSets[i], {"impact": impact, "inaccuracy": inaccuracy, "winrateWith": winrateWith, "gamesWith": gamesWith, "winrateWithout": winrateWithout, "gamesWithout": gamesWithout}])
    
    #   Полученный список сортируется по разнице импакта и погрешности. Сортирую именно так, чтобы
    #   в верху полученного списка не оказались карты с сильно завышенным импактом в силу
    #   недостоверности собранной статистики
    res.sort(key=lambda item: item[1]["impact"]-item[1]["inaccuracy"], reverse= True)
    
    #   Винрейты, импакты и погрешности умножаю на 100 и округляю до 2 знака после запятой для улучшения читаемости
    for i in range(len(res)):
        for item in res[i][1]:
            if (item != "gamesWith"
                and item != "gamesWithout"):
                res[i][1][item] = round(res[i][1][item]*100, 2)
    return res

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