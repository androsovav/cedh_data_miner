from classes import *
from functions import *
import json
import ijson

updateDatabase()

# Открываем файл и загружаем фильтры поиска
with open("sources/criteria/filters.json", 'r') as file:
    filtersJson = json.load(file)

filters = Filters(filtersJson)

# Открываем файл и читаем его содержимое
with open('sources/data/data.json', 'r') as file:
    parser = ijson.parse(file)
    i = 0
    wins = 0
    games = 0
    for prefix, event, value in parser:
        if prefix.endswith('games'):
            games += value
print(games)