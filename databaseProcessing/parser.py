import mtg_parser
import json

with open('databaseProcessing/database/moxfieldDatabase.json', 'r') as database:
    data = json.load(database)

# data['0'].update({'decklist': mtg_parser.parse_deck(data['0']['url'])})
i = 0
while i < len(data):
    decklist = []
    cards = mtg_parser.parse_deck(data[str(i)]['url'])
    for card in cards:
        decklist.append(str(card))
    data[str(i)].update({'decklist': decklist})
    i += 1

with open('databaseProcessing/database/moxfieldDatabaseDecklists.json', 'w') as newdatabase:
    json.dump(data, newdatabase, indent= "")