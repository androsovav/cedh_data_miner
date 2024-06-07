from classes import *
from functions import *
import random

# Открываем файл и загружаем данные
with open('sources\data\database.json', 'r') as file:
    data = json.load(file)

# Задаем начальные условия
colors = 'WUR'
initialTime = ''
finalTime = ''
epochInitialTime = 0
epochFinalTime = 0
includeCommanders = set()
excludeCommanders = set()
includeCardList = set()
excludeCardList = set()

stapleList = set(['Sol Ring', 'Mana Crypt', 'Chrome Mox', 'Lotus Petal', 'Arcane Signet', 'Mox Diamond', 'Mana Vault', 'Mystic Remora', 'Rhystic Study', 'Force of Will', 'Jeweled Lotus', 'Mental Misstep', 'Flusterstorm', 'Swan Song', 'Vampiric Tutor', 'Fierce Guardianship', 'The One Ring', 'Demonic Tutor', 'Mox Opal', 'Pact of Negation', 'Dockside Extortionist', 'Cyclonic Rift', 'Mindbreak Trap', 'Fellwar Stone', 'Force of Negation', 'Deflecting Swat', 'Mystical Tutor', 'Orcish Bowmasters', 'Dark Ritual', "An Offer You Can't Refuse", 'Esper Sentinel', 'Silence', 'Tainted Pact', 'Ragavan, Nimble Pilferer', 'Imperial Seal', 'Enlightened Tutor', 'Wishclaw Talisman', 'Chain of Vapor', "Thassa's Oracle", 'Opposition Agent', 'Swords to Plowshares', 'Gamble', 'Ranger-Captain of Eos', "Lion's Eye Diamond", 'Simian Spirit Guide', 'Demonic Consultation', 'Underworld Breach', 'Grand Abolisher', 'Birds of Paradise', 'Red Elemental Blast', 'Drannith Magistrate', 'Mox Amber', 'Phyrexian Metamorph', 'Worldly Tutor', 'Brain Freeze', 'Grim Monolith', 'Diabolic Intent', 'Ad Nauseam', 'Rite of Flame', 'Phantasmal Image', "Sevinne's Reclamation", 'Final Fortune', 'Wheel of Fortune', 'Pyroblast', 'Lotho, Corrupt Shirriff', 'Cabal Ritual', 'Finale of Devastation', 'Mnemonic Betrayal', 'Talisman of Dominance', 'Mana Drain', 'Intuition', 'Snap', 'Dispel', 'Smothering Tithe', 'Culling the Weak', 'Eldritch Evolution', 'Toxic Deluge', 'Elvish Spirit Guide', 'Delighted Halfling', 'Chord of Calling', 'Borne Upon a Wind', 'Veil of Summer', "Jeska's Will", 'Dauthi Voidwalker', 'Gilded Drake', 'Displacer Kitten', 'Teferi, Time Raveler', 'Windfall', 'Archivist of Oghma', 'March of Swirling Mist', 'Bloom Tender', 'Invasion of Ikoria', 'Imperial Recruiter', 'Path to Exile', 'Talisman of Progress', 'Touch the Spirit Realm', 'Deadly Rollick', 'Llanowar Elves', 'Deathrite Shaman', 'Muddle the Mixture', 'Crop Rotation', 'Lightning Bolt', 'Necropotence', 'Reanimate', 'Noble Hierarch', 'Elvish Mystic', "Praetor's Grasp", "Eladamri's Call", 'Hullbreaker Horror', 'Springleaf Drum', 'Abrupt Decay', 'Eternal Witness', 'Fyndhorn Elves', 'Endurance', 'Dress Down', 'Faerie Mastermind', 'Sylvan Library', 'Gitaxian Probe', 'Noxious Revival', 'Flesh Duplicate', 'Blind Obedience', 'Talion, the Kindly Lord', 'Beseech the Mirror', 'Carpet of Flowers', 'Defense Grid', 'Spellseeker', 'Neoform', 'Basalt Monolith', 'Kinnan, Bonder Prodigy', 'Ignoble Hierarch', 'Transmute Artifact', 'Delay', 'Talisman of Creativity', 'Birgi, God of Storytelling', 'Seedborn Muse', "Grafdigger's Cage", 'Culling Ritual', 'Talisman of Indulgence', 'Emiel the Blessed', 'Timetwister', 'Tinder Wall', "Agatha's Soul Cauldron", 'Imposter Mech', 'Entomb', 'Derevi, Empyrial Tactician', "Sensei's Divining Top", 'Wild Growth', 'Talisman of Curiosity', 'Spellskite', 'Manglehorn', "Green Sun's Zenith", 'Abrade', 'Brainstorm', 'Fire Covenant', 'Cursed Totem', 'Resculpt', 'Tezzeret the Seeker', 'Professional Face-Breaker', 'Dauntless Dismantler', 'Kutzil, Malamet Exemplar', 'Dualcaster Mage', 'Force of Vigor', "Yawgmoth's Will", "Avacyn's Pilgrim", 'Sea Gate Restoration', 'Consecrated Sphinx', 'Aven Mindcensor', 'Deafening Silence', 'Spell Pierce', 'Walking Ballista', 'Relic of Legends', 'Dismember', 'Lavinia, Azorius Renegade', 'Miscast', 'Grinding Station', 'Twinflame', 'Faeburrow Elder', 'Wandering Archaic', 'Shatterskull Smashing', 'Animate Dead', 'Birthing Pod', 'Whir of Invention', 'Boromir, Warden of the Tower', 'Survival of the Fittest', "Lim-Dûl's Vault", 'Grim Tutor', 'Mayhem Devil', 'Tidespout Tyrant', 'Moonsilver Key', 'Cursed Mirror', "Assassin's Trophy", 'Temur Sabertooth', 'Elves of Deep Shadow', 'Serra Ascendant', 'Fabricate', 'Necromancy', 'Pongify', 'Tyvar, Jubilant Brawler', 'Karn, the Great Creator', 'Misdirection'])

# Преобразовываем время из формата дд.мм.гггг во время с начала эпохи и проверяем граничные условия
if initialTime != '':
    epochInitialTime = round(time.mktime(time.strptime(initialTime, "%d.%m.%Y")))
if finalTime != '':
    epochFinalTime = round(time.mktime(time.strptime(finalTime, "%d.%m.%Y")))
if ((initialTime != '' and finalTime != '' and epochFinalTime < epochInitialTime) or (epochInitialTime > time.time())):
        print('Wrong time filter')
        exit()

filters = [colors, epochInitialTime, epochFinalTime, includeCommanders, excludeCommanders, includeCardList, excludeCardList]

print(calculateImpact(filters, {'Island'}, data))

# for card, synergy in calculateExcludeRecomendations(filters, data).items():
#     print(round(synergy, 2), card)


# games = 0
# wins = 0
# decks = 0
# winrate = 0
# sigma = 0
# sum = 0
# sigmasum = 0
# winrates = [0, 0, 0, 0]

# random.shuffle(data)
# with open('numbers.csv', 'w') as file:
#         for entry in data:
#             try:
#                 if (entry['wins'] + entry['losses']):
#                     wins += entry['wins']
#                     games += entry['wins'] + entry['losses']
#                 if entry['wins']/(entry['wins'] + entry['losses']) == 0:
#                     winrates[0] += 1
#                 elif entry['wins']/(entry['wins'] + entry['losses']) == 0.25:
#                     winrates[1] += 1
#                 elif entry['wins']/(entry['wins'] + entry['losses']) == 0.5:
#                     winrates[2] += 1
#                 elif entry['wins']/(entry['wins'] + entry['losses']) == 1:
#                     winrates[3] += 1
#                 decks += 1
#                 sum += ((entry['wins']/(entry['wins'] + entry['losses'])) - wins/games)**2
#                 sigma = (sum/decks)**0.5
#                 sigmasum +=sigma
#                 file.write(f"{games}, {sigma}\n")
#             except Exception:
#                 continue

# print(sigmasum/decks)
# print(wins/games)
# print(games/decks)
# print(winrates[0]/games, winrates[1]/games, winrates[2]/games, winrates[3]/games,)
        
         

# filters = [colors, epochInitialTime, epochFinalTime, includeCommanders, excludeCommanders, [], excludeCardList.union({'Yawgmoth\'s Will'})]
# print(calculateWinrate(filters, data))


# wincons = [{'Underworld Breach', 'Brain Freeze', 'Lion\'s Eye Diamond'}, {'Dualcaster Mage', 'Twinflame'}, {'Walking Ballista'}]
# winrates = []
# for wincon1 in wincons:
#     for wincon2 in wincons:
#         for wincon3 in wincons:
#             filters = [colors, epochInitialTime, epochFinalTime, includeCommanders, excludeCommanders, wincon3.union(wincon1.union(wincon2)), excludeCardList]
#             winrates.append([wincon3.union(wincon1.union(wincon2)), calculateWinrate(filters, data)])        
    

# winrates.sort(key=lambda x: int(x[1]), reverse=True)
# for winrate in winrates:
#      print(str(winrate[1])+'%', winrate[0])



# includeCardList = moxfieldReader('Hinata.txt')


# filters = [colors, epochInitialTime, epochFinalTime, includeCommanders, excludeCommanders, includeCardList, excludeCardList]

# print('Include recomendations:')

# for card, synergy in calculateIncludeRecomendations(filters, data, stapleList).items():
#     print(round(synergy, 2), card)

# print('\nExclude recomendations:')

# for card, synergy in calculateExcludeRecomendations(filters, data).items():
#     print(round(synergy, 2), card)