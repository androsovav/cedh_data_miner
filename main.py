from classes import *
from functions import *
import json

# updateDatabase()

# Открываем файл и загружаем фильтры поиска
with open("sources/criteria/filters.json", 'r') as file:
    filtersJson = json.load(file)

filters = Filters(filtersJson)

dataFile = 'sources/data/data.json'

cardList = [set()]

res = parse(filters, cardList, dataFile)
print('winrate: ', round(res[0]['wins']/res[0]['games']*100, 2))
print('inaccuracy: ', round(res[0]['inaccuracy']*100, 2))