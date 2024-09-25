from classes import Filters
import json
import time

# Основная функция парсинга базы данных. Принимает на вход фильтры и список из деклистов,
# возвращает количество побед, игр, винрейт и погрешность вычисления винрейта для
# каждого деклиста в списке.
def parse(filters: Filters, listOfCardlists: list, dataFile: str):

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