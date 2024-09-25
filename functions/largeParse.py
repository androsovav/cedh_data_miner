from classes import Filters
import ijson

# Копия функции parse, оптимизированная для работы с большими базами данных, не вмещающимися в память.
def largeParse(filters: Filters, listOfCardlists: list, dataFile: str):

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