import json

with open('databaseProcessing/database/databaseCleaned.json') as databaseCleaned:
    data = json.load(databaseCleaned)

result = dict()

i = 0
while i < len(data):
    if 'moxfield' in data[i]['url']:
        result.update({i: data[i]})
    i += 1

with open('databaseProcessing/database/moxfieldDatabase.json', 'w') as moxfieldDatabase:
    json.dump(result, moxfieldDatabase, indent= "")