import re
from operator import attrgetter                 #для сортировки объектов по атрибутам


class Word(object):
    def __init__(self, length, x, y, rotation, intersection):
        self.length = length                    #длина слова
        self.x = x                              #координаты начала
        self.y = y
        self.rotation = rotation                #ориентация
        self.intersection = intersection        #количество пересечений
        self.wordAlphas = list()                #буквы выбранного слова
        self.description = ''


class Crossword(object):
    wordList = []
    def __init__(self, matrix):
        self.matrix = matrix
        self.width = len(matrix[0])
        self.height = len(matrix)

        self.horizontalSearch()
        self.verticalSearch()

        self.wordList = sorted(self.wordList, key=attrgetter('intersection'), reverse=True)     # сортировка по пересечениям
        self.wordList = sorted(self.wordList, key=attrgetter('length'), reverse=True)           # сортировка по длине слова)


    # поиск пересечений
    def intersectionSearch(self,sx,sy,len,rotation):
        num = 0
        if rotation == 0:
            if sx > 0 and sx < self.height - 1:
                for i in range(len):
                    if self.matrix[sx - 1][sy + i] == 1 or self.matrix[sx + 1][sy + i] == 1:
                        num += 1
            elif sx == 0:
                for i in range(len):
                    if self.matrix[sx + 1][sy + i] == 1:
                        num += 1
            elif sx == self.height - 1:
                for i in range(len):
                    if self.matrix[sx - 1][sy + i] == 1:
                        num += 1
        if rotation == 1:
            if sy > 0 and sy < self.width - 1:
                for j in range(len):
                    if self.matrix[sx + j][sy - 1] == 1 or self.matrix[sx + j][sy + 1] == 1:
                        num += 1
            if sy == 0:
                for j in range(len):
                    if self.matrix[sx + j][sy + 1] == 1:
                        num += 1
            if sy == self.width - 1:
                for j in range(len):
                    if self.matrix[sx + j][sy - 1] == 1:
                        num += 1
        return num


    def horizontalSearch(self):
        fx = fy = 0
        isWord = False
        lenOfWord = 0
        for row in range(self.height):
            for col in range(self.width):

                # конец слова или строки
                if (col + 1 == self.width) or (
                        self.matrix[row][col] > 0 and self.matrix[row][col + 1] == 0 and isWord):
                    if isWord:
                        lenOfWord += 1

                        intersection = self.intersectionSearch(fx,fy,lenOfWord,0)   #поиск пересечений
                        w = Word(lenOfWord, fx, fy, 0, intersection)
                        self.wordList.append(w)                                     #добавление слова в список

                        isWord = False
                        lenOfWord = 0
                        continue
                    else:
                        break

                # начало слова
                elif self.matrix[row][col] > 0 and self.matrix[row][col + 1] > 0 and not isWord:
                    isWord = True
                    lenOfWord += 1
                    fx = row
                    fy = col

                # середина слова
                elif self.matrix[row][col] > 0 and self.matrix[row][col + 1] > 0 and isWord:
                    lenOfWord += 1


    def verticalSearch(self):
        fx = fy = 0
        isWord = False
        lenOfWord = 0
        for col in range(self.width):
            for row in range(self.height):

                # конец слова или строки
                if (row + 1 == self.height) or (
                        self.matrix[row][col] > 0 and self.matrix[row + 1][col] == 0 and isWord):
                    if isWord:
                        lenOfWord += 1

                        intersection = self.intersectionSearch(fx,fy,lenOfWord,1)   #поиск пересечений
                        w = Word(lenOfWord, fx, fy, 1, intersection)
                        self.wordList.append(w)                                     #добавление слова в список

                        isWord = False
                        lenOfWord = 0
                        continue
                    else:
                        break

                # начало слова
                elif self.matrix[row][col] > 0 and self.matrix[row + 1][col] > 0 and not isWord:
                    isWord = True
                    lenOfWord += 1
                    fx = row
                    fy = col

                # середина слова
                elif self.matrix[row][col] > 0 and self.matrix[row + 1][col] > 0 and isWord:
                    lenOfWord += 1


    # обновление матрицы
    def refresh(self):
        for w in self.wordList:
            if len(w.wordAlphas) != 0:
                if w.rotation == 0:
                    for i in range(w.length):
                        self.matrix[w.x][w.y + i] = w.wordAlphas[i]
                else:
                    for i in range(w.length):
                        self.matrix[w.x + i][w.y] = w.wordAlphas[i]


    # поиск входящих букв в слово
    def checkWord(self,w):
        x = w.x
        y = w.y
        # создание списка с входящими буквами
        check = [0] * w.length
        if w.rotation == 0:
            for n in range(w.length):
                if self.matrix[x][y + n] != 1:
                    check[n] = self.matrix[x][y + n]
        else:
            for n in range(w.length):
                if self.matrix[x + n][y] != 1:
                    check[n] = self.matrix[x + n][y]
        return check


    # удаление неподошедшего слова
    def deleteWord(self, w):
        # удаление из списка слов
        w.wordAlphas = []
        w.description = ''
        # удаление из матрицы
        for i in range(w.length):
            if w.rotation == 0:
                self.matrix[w.x][w.y + i] = 1
            else:
                self.matrix[w.x + i][w.y] = 1
        # обновление матрицы
        self.refresh()


    # алгоритм с возвратом
    def backTracking(self, id):
        # если конец списка
        if(id == len(self.wordList)):
            return True
        else:
            w = self.wordList[id]

            with open('test.txt', 'r', encoding='utf-8-sig') as file:  # автомотическое закрытие файла после окончания блока
                for row in file:
                    check = self.checkWord(w)
                    case = re.split(' - ', row)
                    alphas = list(case[0])  # буквы слова
                    # сравнение check и слова из файла
                    if(w.length == len(alphas)):
                        flag = True
                        for i in range(w.length):
                            if(check[i] != 0 and check[i] != alphas[i]):
                                flag = False
                                break
                        if flag == False:
                            continue
                        w.wordAlphas = alphas.copy()
                        w.description = case[1]
                        self.refresh()
                        if self.backTracking(id + 1) == True:
                            return True
                        else:
                            self.deleteWord(w)
                            continue
        return False


    def printResult(self):
        searched = self.wordList = sorted(self.wordList, key=attrgetter('rotation'))
        for n in self.matrix:
            for a in n:
                if a == 0:
                    print('-', end='\t')
                else:
                    print(a, end='\t')
            print('\n')
        print("По горизонтали:")
        for d in self.wordList:
            if d.rotation == 0:
                print("x:", end='')
                print(d.x, end=', ')
                print("y:",end='')
                print(d.y, end=' - ')
                print(d.description)
        print("По вертикали:")
        for d in self.wordList:
            if d.rotation == 1:
                print("x:", end='')
                print(d.x, end=', ')
                print("y:",end='')
                print(d.y, end=' - ')
                print(d.description)
        # self.drawResult()

matrix= [[1,1,1,1,1,1,1],
         [0,0,1,0,1,0,1],
         [0,1,1,1,1,0,1],
         [0,0,1,0,1,0,0]]

field = Crossword(matrix)
if field.backTracking(0) == False:
    print("Невозможн составить кроссворд")

else:
    field.printResult()
