from PyQt5 import QtWidgets
import sys

import simple

class SearchGUI(QtWidgets.QMainWindow, simple.Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # инициализация дизайна
        self.circle()


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = SearchGUI()  # создаём объект класса приложения
    window.show()  # показываем окно
    app.exec_()  # запускаем приложение
    print('Команда Лучших Общий сбор')


if __name__ == '__main__':
    main()

