from .parse import parse
from classes import cardlist, Filters

# Функция, которая оценивает вклад в победу каждого из наборов карт в listOfSets
# на основе разницы винрейта колод с этим набором карт и без него с учетом выставленных фильтров
def calculateImpact(filters: Filters, listOfSets: list, dataFile: str):
    listOfCardlists = []
    #   Формируем список из наборов карт для функции parse. Для каждого набора из listOfSets
    #   будет учтена статистика колод, включающих каждую карту этого набора, и колод,
    #   исключающих каждую карту этого набора
    for i in range(len(listOfSets)):
        listOfCardlists.append(cardlist(listOfSets[i], set()))
        listOfCardlists.append(cardlist(set(), listOfSets[i]))
    
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