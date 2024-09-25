import time
import json
import mtg_parser
import requests

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