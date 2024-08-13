import json

with open('databaseProcessing/database/database.json') as database:
    data = json.load(database)

entryStatsToClear = set(['name', 'profile', 'standing', 'tournamentName', 'winsSwiss', 'winsBracket',
                        'winRate', 'winRateSwiss', 'winRateBracket', 'draws', 'losses', 'lossesSwiss', 'lossesBracket'])

i = 0
while i < len(data):
    if ('decklist' not in data[i]) or (data[i]['decklist'] == "") or (data[i]['decklist'] == None):
        data.remove(data[i])
        continue
    data[i]['games'] = data[i]['wins'] + data[i]['draws'] + data[i]['losses']
    if data[i]['games'] == 0:
        data.remove(data[i])
        continue
    for stat in entryStatsToClear:
        if stat in data[i]:
            del data[i][stat]
    data[i]['url'] = data[i]['decklist']
    del data[i]['decklist']
    i += 1

with open('databaseProcessing/database/databaseCleaned.json', 'w') as cleanedDatabase:
    json.dump(data, cleanedDatabase, indent= "")