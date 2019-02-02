import sys
from PyQt5.QtWidgets import *
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import pyqtSlot
 
horizontalCount = 7
verticalCount = 4
matrix = [[0] * horizontalCount for _ in range(verticalCount)]
buttons = [[0] * horizontalCount for _ in range(verticalCount)]
 
class Draw(QWidget):
 
    def __init__(self):
        super().__init__()
 
        self.indent = 20
        self.buttonSize = 100
        self.width = self.indent * 2 + horizontalCount * self.buttonSize + 5 * horizontalCount
        self.height = self.indent * 2  + verticalCount * self.buttonSize + 5 * verticalCount + 100
 
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
 
    def createCrossword(self):
        but = buttons[0][0]
        but.setText('HH')
 
    def createGridLayout(self):
        for row in range(verticalCount):
            for col in range(horizontalCount):
                btn = QPushButton('', self)
                btn.setStyleSheet("background-color: black")
                btn.clicked.connect(self.onButtonClicked)
                btn.resize(self.buttonSize, self.buttonSize)
                btn.move(col * (self.buttonSize + 5) + self.indent, row * (self.buttonSize + 5) + self.indent)
 
                buttons[row][col] = btn
 
    def onButtonClicked(self):
        button = self.sender()
        for row in range(verticalCount):
            for col in range(horizontalCount):
                if button == buttons[row][col]:
                    if matrix[row][col] == 0:
                        button.setStyleSheet("background-color: white")
                        matrix[row][col] = 1
                    else:
                        button.setStyleSheet("background-color: black")
                        matrix[row][col] = 0
                    print(matrix)
                    break
 
 
    def center(self):
 
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
 
 
if __name__ == '__main__':
 
    app = QApplication(sys.argv)
    ex = Draw()
    sys.exit(app.exec_())
    
