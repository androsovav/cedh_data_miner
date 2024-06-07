from collections import defaultdict
import json
import time
import itertools

# Функция, которая проверяет, удовлетворяет ли вход на турнир entry всем выставленным фильтрам
def myFilter(filters, entry):
    try:
            # Условие выполняется только если в колоде найдется каждая карта из списка cardlist
            return ((entry['colorID'] == filters[0] or filters[0] == '')
                    and ((entry['dateCreated'] >= filters[1]) or (filters[1] == 0))
                    and ((entry['dateCreated'] <= filters[2]) or (filters[2] == 0))
                    and (any((commander == entry['commander']) for commander in filters[3]) or filters[3] == set())
                    and (any((commander != entry['commander']) for commander in filters[4]) or filters[4] == set())
                    and all((card in set(entry['truedecklist']) for card in filters[5]))
                    and not any((card in set(entry['truedecklist']) for card in filters[6])))
    except Exception:
        return False

# Функция, которая подсчитывает средний винрейт всех колод в data, удовлетворяющих всем выставленным фильтрам
def calculateWinrate(filters, data):
    wins = 0
    games = 0

    for entry in data:
        if myFilter(filters, entry):
            wins += entry['wins']
            games += entry['wins'] + entry['losses']

    if games >= 25:
        winrate = round((wins / games) * 100, 2)
    else:
        winrate = 0

    return winrate

# Функция, которая оценивает вклад карт из includeCardList на основе разницы винрейта с ними и без них для колод, удовлетворяющих выставленным фильтрам
def calculateImpact(filters: list, cardList: set, data: list):
    winrateWith = calculateWinrate([filters[0], filters[1], filters[2], filters[3], filters[4], cardList.union(filters[5]), filters[6]], data)
    winrateWithout = calculateWinrate([filters[0], filters[1], filters[2], filters[3], filters[4], filters[5], cardList.union(filters[6])], data)
    if winrateWith != 0 and winrateWithout != 0:
        return round(winrateWith - winrateWithout, 2)
    else:
        return 0

# Функция, которая составляет список рекомендаций среди карт из списка stapleList для колоды includeCardList на основе колод из data, удовлетворяющих выставленным фильтрам
def calculateIncludeRecomendations(filters, data, stapleList):
    combinations = [(card, staple) for card in filters[5] for staple in stapleList if not staple in filters[5]]

    winsWith = defaultdict(int)
    winsWithout = defaultdict(int)
    gamesWith = defaultdict(int)
    gamesWithout = defaultdict(int)
    synergies = defaultdict(int)

    for entry in data:
        try:
            if myFilter([filters[0], filters[1], filters[2], filters[3], filters[4], [], filters[6]], entry):
                decklist = set(entry['truedecklist'])
                for combination in combinations:
                    if combination[0] in decklist:
                        if combination[1] in decklist:
                            winsWith[combination] += entry['wins']
                            gamesWith[combination] += entry['wins'] + entry['losses']
                        else:
                            winsWithout[combination] += entry['wins']
                            gamesWithout[combination] += entry['wins'] + entry['losses']
        except Exception:
            continue

    for combination in combinations:
        if gamesWith[combination] >= 20 and gamesWithout[combination] >= 20:
            synergies[combination[1]] = round(((winsWith[combination]/gamesWith[combination]) - (winsWithout[combination]/gamesWithout[combination]))*100, 2)

    sorted_synergies = {k: v for k, v in sorted(synergies.items(), key=lambda item: item[1], reverse=True)[:10]}
    return sorted_synergies

# Функция, которая составляет список рекомендаций среди карт из списка stapleList для колоды includeCardList на основе колод из data, удовлетворяющих выставленным фильтрам
def calculateExcludeRecomendations(filters, data):
    combinations = set(itertools.combinations(filters[5], 2))

    # TODO: УДАЛИТБ
    # winsWith = defaultdict(int)
    # winsWithout = defaultdict(int)
    # gamesWith = defaultdict(int)
    # gamesWithout = defaultdict(int)

    # В этих словарях ключом является комбинация карт, значением является список из побед/игр/винрейтов первой карты из комбинации без второй,
    # второй карты из комбинации без первой, и самой комбинации
    combinationWins = {}
    combinationGames = {}
    combinationWinrates = {}
    combinationSynergies = {}
    synergies = {}
    for card in filters[5]:
        synergies[card] = 0

    for combination in combinations:
        combinationWins[combination] = [0, 0, 0]
        combinationGames[combination] = [0, 0, 0]
        combinationWinrates[combination] = 0
        combinationSynergies[combination] = 0


    for entry in data:
        try:
            if myFilter([filters[0], filters[1], filters[2], filters[3], filters[4], [], filters[6]], entry):
                decklist = set(entry['truedecklist'])
                for combination in combinations:
                    if combination[0] in decklist and combination[1] in decklist:
                        combinationWins[combination][2] += entry['wins']
                        combinationGames[combination][2] += entry['wins'] + entry['losses']
                    elif combination[0] in decklist:
                        combinationWins[combination][0] += entry['wins']
                        combinationGames[combination][0] += entry['wins'] + entry['losses']
                    elif combination[1] in decklist:
                        combinationWins[combination][1] += entry['wins']
                        combinationGames[combination][1] += entry['wins'] + entry['losses']
        except Exception:
            continue

    for combination in combinations:
        if all(games > 0 for games in combinationGames[combination]):
            combinationSynergies[combination] = round(((combinationWins[combination][0]/combinationGames[combination][0]) - (combinationWins[combination][1]/combinationGames[combination][1]))*100,2)
    
    for card in filters[5]:
        for combination in combinations:
            if(combinationGames[combination][2] <= 20):
                continue
            if combination[0] == card and (combinationGames[combination][1] >= 20):
                synergies[card] += (combinationWins[combination][2]/combinationGames[combination][2]) - (combinationWins[combination][1]/combinationGames[combination][1])
            elif combination[1] == card and (combinationGames[combination][0] >= 20):
                synergies[card] += (combinationWins[combination][2]/combinationGames[combination][2]) - (combinationWins[combination][0]/combinationGames[combination][0])

    sorted_synergies = {k: v for k, v in sorted(synergies.items(), key=lambda item: item[1], reverse=False)[:10]}
    return sorted_synergies

def calculatePopularity(filters, data):
    return 0

# Функция, читающая деклист с сайта mtggoldfish в формате для MTGA
def mtgaReader(file_name):
    commander_cards = []
    deck_cards = []
    in_deck_section = False
    in_commander_section = False
    
    with open(file_name, 'r') as file:
        for line in file:
            line = line.strip()
            
            if line == 'Commander':
                in_commander_section = True
                in_deck_section = False
                continue
            elif line == 'Deck':
                in_commander_section = False
                in_deck_section = True
                continue
            
            if in_commander_section and line:
                cmdr_card = line.split(' ', 1)[-1]
                commander_cards.append(cmdr_card)
                deck_cards.append(cmdr_card)  # Добавляем командира в список карт
            elif in_deck_section and line:
                card = line.split(' ', 1)[-1]
                deck_cards.append(card)
    
    return [' / '.join(commander_cards), deck_cards]

# Функция, читающая деклист с сайта moxfield в формате для moxfield
def moxfieldReader(file_name):
    card_names = set()  # Инициализация пустого набора set()
    
    with open(file_name, 'r') as file:
        for line in file:
            card_info = line.split('(')[0].split(' ', 2)
            if len(card_info) > 1:
                card_name = ' '.join(card_info[1:]).strip()  # Объединяем слова, начиная с второго и удаляем лишние пробелы
                card_names.add(card_name)
    
    return card_names

# Открываем файл и загружаем данные
# with open('top16_players_with_cleaned_decklists.json', 'r') as file:
#     data = json.load(file)

# # Задаем начальные условия
# colors = 'WUR'
# initialTime = '01.01.2024'
# finalTime = ''
# epochInitialTime = 0
# epochFinalTime = 0
# includeCommanders = set()
# excludeCommanders = set()
# includeCardList = set()
# excludeCardList = set()

# stapleList = set(['Sol Ring', 'Mana Crypt', 'Chrome Mox', 'Lotus Petal', 'Arcane Signet', 'Mox Diamond', 'Mana Vault', 'Mystic Remora', 'Rhystic Study', 'Force of Will', 'Jeweled Lotus', 'Mental Misstep', 'Flusterstorm', 'Swan Song', 'Vampiric Tutor', 'Fierce Guardianship', 'The One Ring', 'Demonic Tutor', 'Mox Opal', 'Pact of Negation', 'Dockside Extortionist', 'Cyclonic Rift', 'Mindbreak Trap', 'Fellwar Stone', 'Force of Negation', 'Deflecting Swat', 'Mystical Tutor', 'Orcish Bowmasters', 'Dark Ritual', "An Offer You Can't Refuse", 'Esper Sentinel', 'Silence', 'Tainted Pact', 'Ragavan, Nimble Pilferer', 'Imperial Seal', 'Enlightened Tutor', 'Wishclaw Talisman', 'Chain of Vapor', "Thassa's Oracle", 'Opposition Agent', 'Swords to Plowshares', 'Gamble', 'Ranger-Captain of Eos', "Lion's Eye Diamond", 'Simian Spirit Guide', 'Demonic Consultation', 'Underworld Breach', 'Grand Abolisher', 'Birds of Paradise', 'Red Elemental Blast', 'Drannith Magistrate', 'Mox Amber', 'Phyrexian Metamorph', 'Worldly Tutor', 'Brain Freeze', 'Grim Monolith', 'Diabolic Intent', 'Ad Nauseam', 'Rite of Flame', 'Phantasmal Image', "Sevinne's Reclamation", 'Final Fortune', 'Wheel of Fortune', 'Pyroblast', 'Lotho, Corrupt Shirriff', 'Cabal Ritual', 'Finale of Devastation', 'Mnemonic Betrayal', 'Talisman of Dominance', 'Mana Drain', 'Intuition', 'Snap', 'Dispel', 'Smothering Tithe', 'Culling the Weak', 'Eldritch Evolution', 'Toxic Deluge', 'Elvish Spirit Guide', 'Delighted Halfling', 'Chord of Calling', 'Borne Upon a Wind', 'Veil of Summer', "Jeska's Will", 'Dauthi Voidwalker', 'Gilded Drake', 'Displacer Kitten', 'Teferi, Time Raveler', 'Windfall', 'Archivist of Oghma', 'March of Swirling Mist', 'Bloom Tender', 'Invasion of Ikoria', 'Imperial Recruiter', 'Path to Exile', 'Talisman of Progress', 'Touch the Spirit Realm', 'Deadly Rollick', 'Llanowar Elves', 'Deathrite Shaman', 'Muddle the Mixture', 'Crop Rotation', 'Lightning Bolt', 'Necropotence', 'Reanimate', 'Noble Hierarch', 'Elvish Mystic', "Praetor's Grasp", "Eladamri's Call", 'Hullbreaker Horror', 'Springleaf Drum', 'Abrupt Decay', 'Eternal Witness', 'Fyndhorn Elves', 'Endurance', 'Dress Down', 'Faerie Mastermind', 'Sylvan Library', 'Gitaxian Probe', 'Noxious Revival', 'Flesh Duplicate', 'Blind Obedience', 'Talion, the Kindly Lord', 'Beseech the Mirror', 'Carpet of Flowers', 'Defense Grid', 'Spellseeker', 'Neoform', 'Basalt Monolith', 'Kinnan, Bonder Prodigy', 'Ignoble Hierarch', 'Transmute Artifact', 'Delay', 'Talisman of Creativity', 'Birgi, God of Storytelling', 'Seedborn Muse', "Grafdigger's Cage", 'Culling Ritual', 'Talisman of Indulgence', 'Emiel the Blessed', 'Timetwister', 'Tinder Wall', "Agatha's Soul Cauldron", 'Imposter Mech', 'Entomb', 'Derevi, Empyrial Tactician', "Sensei's Divining Top", 'Wild Growth', 'Talisman of Curiosity', 'Spellskite', 'Manglehorn', "Green Sun's Zenith", 'Abrade', 'Brainstorm', 'Fire Covenant', 'Cursed Totem', 'Resculpt', 'Tezzeret the Seeker', 'Professional Face-Breaker', 'Dauntless Dismantler', 'Kutzil, Malamet Exemplar', 'Dualcaster Mage', 'Force of Vigor', "Yawgmoth's Will", "Avacyn's Pilgrim", 'Sea Gate Restoration', 'Consecrated Sphinx', 'Aven Mindcensor', 'Deafening Silence', 'Spell Pierce', 'Walking Ballista', 'Relic of Legends', 'Dismember', 'Lavinia, Azorius Renegade', 'Miscast', 'Grinding Station', 'Twinflame', 'Faeburrow Elder', 'Wandering Archaic', 'Shatterskull Smashing', 'Animate Dead', 'Birthing Pod', 'Whir of Invention', 'Boromir, Warden of the Tower', 'Survival of the Fittest', "Lim-Dûl's Vault", 'Grim Tutor', 'Mayhem Devil', 'Tidespout Tyrant', 'Moonsilver Key', 'Cursed Mirror', "Assassin's Trophy", 'Temur Sabertooth', 'Elves of Deep Shadow', 'Serra Ascendant', 'Fabricate', 'Necromancy', 'Pongify', 'Tyvar, Jubilant Brawler', 'Karn, the Great Creator', 'Misdirection'])

# # Преобразовываем время из формата дд.мм.гггг во время с начала эпохи и проверяем граничные условия
# if initialTime != '':
#     epochInitialTime = round(time.mktime(time.strptime(initialTime, "%d.%m.%Y")))
# if finalTime != '':
#     epochFinalTime = round(time.mktime(time.strptime(finalTime, "%d.%m.%Y")))
# if ((initialTime != '' and finalTime != '' and epochFinalTime < epochInitialTime) or (epochInitialTime > time.time())):
#         print('Wrong time filter')
#         exit()

# includeCardList = moxfieldReader('Hinata.txt')

# print(includeCardList)

# filters = [colors, epochInitialTime, epochFinalTime, includeCommanders, excludeCommanders, includeCardList, excludeCardList]

# print('Include recomendations:')

# for card, synergy in calculateIncludeRecomendations(filters, data, stapleList).items():
#     print(round(synergy, 2), card)

# print('\nExclude recomendations:')

# for card, synergy in calculateExcludeRecomendations(filters, data).items():
#     print(round(synergy, 2), card)

# cardList = set(['Hullbreaker Horror'])
# filters[5] = set()
# print(calculateImpact(filters, data))
# oswaldCardsWins = defaultdict(int)
# oswaldCardsGames = defaultdict(int)
# games = 0
# wins = 0

# for item in data:
#     if myFilter(includeCardList, excludeCardList, epochInitialTime, epochFinalTime, colors, includeCommanders, excludeCommanders, item):
#         try:
#             for card in set(item['truedecklist']):
#                 oswaldCardsWins[card] += item['wins']
#                 oswaldCardsGames[card] += item['wins'] + item['losses']
#             wins += item['wins']
#             games += item['wins'] + item['losses']
#         except Exception:
#             continue
        

# oswaldCardWinrates = {}
# for card in oswaldCardsGames:
#     if oswaldCardsGames[card] >= games/2:
#         oswaldCardWinrates[card] = round((oswaldCardsWins[card] / oswaldCardsGames[card])*100, 2)

# sortedOswaldCardWinrates = {k: v for k, v in sorted(oswaldCardWinrates.items(), key=lambda item: item[1], reverse=True)}
# for card, synergy in sortedOswaldCardWinrates.items():
#     print(str(synergy)+'%', card)
# print('Games:', games)
# print('Average winrate:', round((wins/games)*100, 2))

# synergiesList = {}
# for staple in stapleList:
#     if not(staple in includeCardList):
#         for card in includeCardList:
#             synergy = calculateImpact(set([staple, card]), excludeCardList, epochInitialTime, epochFinalTime, colors, includeCommanders, excludeCommanders, data)
#             if synergy != 0:
#                 synergiesList[staple] = synergy

# sorted_synergies = {k: v for k, v in sorted(synergiesList.items(), key=lambda item: item[1], reverse=True)}
# for card, synergy in sorted_synergies.items():
#     print(synergy, card)