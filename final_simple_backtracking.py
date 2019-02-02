import re
import sys
from operator import attrgetter  # для сортировки объектов по атрибутам
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont


horizontalCount = 20
verticalCount = 10
matrix = [[0] * horizontalCount for _ in range(verticalCount)]
buttons = [[0] * horizontalCount for _ in range(verticalCount)]
lastFirstWords = []


class Draw(QWidget):

    def __init__(self):
        super().__init__()

        self.indent = 20
        self.buttonSize = 50
        self.width = self.indent * 2 + horizontalCount * self.buttonSize + 5 * horizontalCount
        self.height = self.indent * 2 + verticalCount * self.buttonSize + 5 * verticalCount + 100

        self.start = 0
        self.end = 0

        self.white = 0

        self.initUI()

    def initUI(self):

        self.resize(self.width, self.height)
        self.center()
        self.setWindowTitle('Crossword')

        self.createGridLayout()

        btn = QPushButton('create crossword', self)
        btn.resize(150, 50)
        btn.clicked.connect(self.createCrossword)
        btn.move(self.indent, self.height - 90)

        self.show()


    def clearMatrix(self):
        # очистка матрицы для дальнейшей работы
        for i in range(verticalCount):
            for j in range(horizontalCount):
                if matrix[i][j] != 0:
                    matrix[i][j] = 1
        for row in range(verticalCount):
            for col in range(horizontalCount):
                if matrix[row][col] != 0:
                    btn = buttons[row][col]
                    btn.setText('')
                    btn.setStyleSheet('background-color: white')

    def createCrossword(self):
        self.clearMatrix()
        Crossword(matrix)
        # заполнение ячеек кроссворда
        for row in range(verticalCount):
            for col in range(horizontalCount):
                if matrix[row][col] != 0:
                    btn = buttons[row][col]
                    btn.setText(str(matrix[row][col]))
                    btn.setStyleSheet('color: black; background-color: white')

    # создание кнопок на поле
    def createGridLayout(self):
        for row in range(verticalCount):
            for col in range(horizontalCount):
                btn = QPushButton('', self)
                btn.setStyleSheet("background-color: black")
                btn.clicked.connect(self.onButtonClicked)
                btn.resize(self.buttonSize, self.buttonSize)
                btn.setFont(QFont('SansSerif', 18))
                btn.move(col * (self.buttonSize + 5) + self.indent, row * (self.buttonSize + 5) + self.indent)

                buttons[row][col] = btn  # массив кнопок


    def onButtonClicked(self):
        self.clearMatrix()
        if self.start == 0:
            self.start = self.sender()
        else:  # если нажаты обе кнопки
            self.end = self.sender()
            # поиск координат кнопок начала и конца слова
            for row in range(verticalCount):
                for col in range(horizontalCount):
                    if self.start == buttons[row][col]:
                        sRow = row
                        sCol = col
                        self.white = True if matrix[sRow][sCol] == 1 else False if matrix[sRow][sCol] == 0 else 0

                    if self.end == buttons[row][col]:
                        eRow = row
                        eCol = col

            self.start = 0
            self.end = 0

            if sCol > eCol or sRow > eRow:
                sCol, eCol = eCol, sCol
                sRow, eRow = eRow, sRow
            if sCol == eCol and sRow == eRow:
                print("Ошибка задания слова - количество букв должно быть больше 1")
                return -1

            # если слово расположено по горизонтали
            if sRow == eRow:
                if matrix[sRow][sCol] == 0:  # если начало не задано, то задаются все кнопки
                    for col in range(sCol, eCol + 1):
                        button = buttons[sRow][col]
                        if not self.white:  # matrix[sRow][col] == 0:
                            button.setStyleSheet("background-color: white")
                            matrix[eRow][col] = 1
                else:  # если начало задано, то стираем слово
                    for col in range(sCol, eCol + 1):
                        button = buttons[sRow][col]
                        if self.white:  # matrix[sRow][col] == 1:
                            button.setStyleSheet("background-color: black")
                            matrix[eRow][col] = 0

            elif sCol == eCol:  # если по вертикали
                if matrix[sRow][sCol] == 0:  # если начало не задано, то задаются все кнопки
                    for row in range(sRow, eRow + 1):
                        button = buttons[row][sCol]
                        if not self.white:  # matrix[row][sCol] == 0:
                            button.setStyleSheet("background-color: white")
                            matrix[row][sCol] = 1
                else:  # если начало задано, то стираем слово
                    for row in range(sRow, eRow + 1):
                        button = buttons[row][sCol]
                        if self.white:  # matrix[row][sCol] == 1:
                            button.setStyleSheet("background-color: black")
                            matrix[row][sCol] = 0
            else:
                print("Неверный способ задания слова - задайте по горизонтали или вертикали")
                return -1

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Word(object):

    def __init__(self, length, x, y, rotation, intersection):
        self.length = length  # длина слова
        self.x = x  # координаты начала
        self.y = y
        self.rotation = rotation  # ориентация
        self.intersection = intersection  # количество пересечений
        self.wordAlphas = list()  # буквы выбранного слова
        self.description = ''


class Crossword(object):

    def __init__(self, matrix):
        self.wordList = []
        self.matrix = matrix
        self.width = len(matrix[0])
        self.height = len(matrix)
        self.compute()

    def compute(self):

        self.horizontalSearch()
        self.verticalSearch()

        self.wordList = sorted(self.wordList, key=attrgetter('intersection'),
                               reverse=True)  # сортировка по пересечениям
        self.wordList = sorted(self.wordList, key=attrgetter('length'), reverse=True)  # сортировка по длине слова)

        if not self.backTracking(0):
            print("Невозможно составить кроссворд")
        else:
            lastFirstWords.append(
                self.wordList[0].wordAlphas)  # запомнить первое слово для дальнейшего поиска без повторений
            self.printResult()

    # поиск пересечений
    def intersectionSearch(self, sx, sy, len, rotation):
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

                        intersection = self.intersectionSearch(fx, fy, lenOfWord, 0)  # поиск пересечений
                        w = Word(lenOfWord, fx, fy, 0, intersection)
                        self.wordList.append(w)  # добавление слова в список

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

                        intersection = self.intersectionSearch(fx, fy, lenOfWord, 1)  # поиск пересечений
                        w = Word(lenOfWord, fx, fy, 1, intersection)
                        self.wordList.append(w)  # добавление слова в список

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
    def checkWord(self, w):
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
        if id == len(self.wordList):
            return True
        else:
            w = self.wordList[id]

            with open('cross.txt', 'r',
                      encoding='utf-8-sig') as file:  # автомотическое закрытие файла после окончания блока
                for row in file:
                    check = self.checkWord(w)
                    case = re.split(' - ', row)
                    alphas = list(case[0])  # буквы слова
                    # сравнение check и слова из файла
                    if w.length == len(alphas):
                        flag = True
                        for i in range(w.length):
                            if check[i] != 0 and check[i] != alphas[i]:  # проверка пересечений
                                flag = False
                                break
                        if not flag:
                            continue
                        w.wordAlphas = alphas.copy()
                        w.description = case[1]

                        # проверка для нового кроссворда
                        if id == 0:
                            isRepeat = False
                            for last in lastFirstWords:
                                if last == alphas:
                                    isRepeat = True
                                    break
                            if isRepeat == True:
                                continue

                        self.refresh()
                        if self.backTracking(id + 1):
                            return True
                        else:
                            self.deleteWord(w)
                            continue
        return False

    def printResult(self):
        self.wordList = sorted(self.wordList, key=attrgetter('rotation'))
        for n in self.matrix:
            for a in n:
                if a == 0:
                    print('-', end=' ')
                else:
                    print(a, end=' ')
            print('\n')
        print("По горизонтали:")
        for d in self.wordList:
            if d.rotation == 0:
                print("x:", end='')
                print(d.x, end=', ')
                print("y:", end='')
                print(d.y, end=' - ')
                print(d.description)
        print("По вертикали:")
        for d in self.wordList:
            if d.rotation == 1:
                print("x:", end='')
                print(d.x, end=', ')
                print("y:", end='')
                print(d.y, end=' - ')
                print(d.description)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Draw()
    sys.exit(app.exec_())
