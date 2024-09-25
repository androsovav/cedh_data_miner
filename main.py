from classes import *
from functions import *
from readers import *

with open("sources/data/data.json", "r") as file:
    data = json.load(file)

with open("sources/criteria/filters.json", "r") as file:
    filters = Filters(json.load(file))
stapleListRaw = readers.mtgtop8Reader("sources\decklists\stapleList.txt")
setList = []
for item in stapleListRaw:
    setList.append(set([item]))

res = newCalculateImpact(filters, setList, "sources/data/data.json")

for item in res:
    print(item)

# for item in res:
#     print("Including:")
#     for card in item[0].including:
#         print(card)
#     print("Excluding:")
#     for card in item[0].excluding:
#         print(card)
#     print(item[1])