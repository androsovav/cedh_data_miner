import json
import requests

base_url = "https://edhtop16.com/api/"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

data = {
    'tourney_filter': {
        'dateCreated': {'$gte': 1673715600}
    }
}
entries = json.loads(requests.post(base_url + 'req', json=data, headers=headers).text)
with open('decklistParser/database/database.json', 'w') as file:
    json.dump(entries, file, indent = "")

file.close()