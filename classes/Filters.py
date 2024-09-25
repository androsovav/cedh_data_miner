from itertools import combinations
import time
from functions.readers import *


class Filters:
    def __init__(self, filtersJson):
        filterObj = filtersJson[0]
        epochInitialTime = 0
        epochFinalTime = 0
        # Преобразовываем время из формата дд.мм.гггг во время с начала эпохи и проверяем граничные условия
        if filterObj['initialTime'] != '':
            epochInitialTime = round(time.mktime(time.strptime(filterObj['initialTime'], "%d.%m.%Y")))
        if filterObj['finalTime'] != '':
            epochFinalTime = round(time.mktime(time.strptime(filterObj['finalTime'], "%d.%m.%Y")))
        if ((filterObj['initialTime'] != '' and filterObj['finalTime'] != '' and epochFinalTime < epochInitialTime) or (epochInitialTime > time.time())):
                print('Wrong time filter')
                exit()
        # Фильтр колод по цветам. Составляются комбинации из всех возможных цветов WUBRG,
        # подходящих под выбранный режим. Все комбинации цветов принято записывать в 
        # порядке WUBRG.
        if filterObj['colors'] != "":       
            if filterObj['colorsMode'] == '=':
                self.colors = {filterObj['colors']}
            else:
                colors = filterObj['colors']
                combos = []
                if filterObj['colorsMode'] == '>=':
                    s = "WUBRG"
                    for r in range(1, len(s)+1):
                        for comb in combinations(s, r):
                            if all(letter in "".join(comb) for letter in colors):
                                combos.append("".join(comb))
                elif filterObj['colorsMode'] == '<=':
                    for r in range(1, len(colors)+1):
                        for comb in combinations(colors, r):
                            combos.append("".join(comb))
                self.colors = set(combos)
        else:
            self.colors = {}
        # Фильтр колод по дате проведения турнира
        self.initialTime = epochInitialTime
        self.finalTime = epochFinalTime
        # Фильтр колод по командиру
        self.includeCommanders = set(filterObj['includeCommanders'])
        self.excludeCommanders = set(filterObj['excludeCommanders'])
        # Фильтр колод по деклисту
        with open('sources/criteria/includeCardList.txt', 'r') as file:
            if file.readline() == 'Commander':
                self.includeCardList = mtgaReader('sources/criteria/includeCardList.txt')[1]
            else:
                self.includeCardList = moxfieldReader('sources/criteria/includeCardList.txt')
        with open('sources/criteria/includeCardList.txt', 'r') as file:
            if file.readline() == 'Commander':
                self.excludeCardList = mtgaReader('sources/criteria/excludeCardList.txt')[1]
            else:
                self.excludeCardList = moxfieldReader('sources/criteria/excludeCardList.txt')