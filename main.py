import json
from functions import updateDatabase, calculateImpact
from functions.readers import *
from classes import *

updateDatabase()

with open("sources/data/data.json", "r") as file:
    data = json.load(file)

with open("sources/criteria/filters.json", "r") as file:
    filters = Filters(json.load(file))
stapleListRaw = mtgtop8Reader("sources\decklists\stapleList.txt")
setList = []
for item in stapleListRaw:
    setList.append(set([item]))

res = calculateImpact(filters, setList, "sources/data/data.json")

for item in res:
    print(item)