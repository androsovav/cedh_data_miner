import classes
import ijson
import json

def newparse(filters: classes.Filters, listOfCardlists: list, data: dict):
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
    return res

def oldparse(filters: classes.Filters, listOfCardlists: list, dataFile: str):

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


code = """
print('wow')
"""
exec(code)