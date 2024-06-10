from classes import *
from functions import *
import json

# Открываем файл и загружаем данные
with open('sources/data/database.json', 'r') as file:
    data = json.load(file)

# Открываем файл и загружаем фильтры поиска
with open("sources/criteria/filters.json", 'r') as file:
    filtersJson = json.load(file)

filters = Filters(filtersJson)