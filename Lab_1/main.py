from dataclasses import dataclass
from math import cos, sin, atan2, sqrt
from typing import Optional, Any, List

from Lab_1 import Form

from PyQt5 import QtWidgets
import sys

from PyQt5.QtWidgets import QWidget, QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsEllipseItem, QGraphicsSceneMouseEvent, QGraphicsLineItem, QGraphicsSceneEvent, QGraphicsTextItem
from PyQt5.QtGui import QPainter, QColor, QFont, QMouseEvent, QCursor, QPen
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF
from PyQt5.uic.properties import QtCore


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = f"{ex_cls.__name__}: {ex}:\n"
    import traceback
    text += ''.join(traceback.format_tb(tb))
    print(f"\n{text}\n")


sys.excepthook = log_uncaught_exceptions  # noqa


@dataclass
class Graph:
    start_point: QGraphicsEllipseItem
    finish_point: QGraphicsEllipseItem
    line: QGraphicsLineItem
    first_leaf: QGraphicsItem
    second_leaf: QGraphicsItem



class GUI(QtWidgets.QMainWindow, Form.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # инициализация дизайна
        self.setWindowTitle('Lab_1')

        # ----------------------<Настройка сцены для рисования>----------------------
        self.draw_scene = QGraphicsScene(self.frame)
        self.view = QGraphicsView(self.draw_scene, self)
        self.view.setGeometry(self.frame.pos().x(), self.frame.pos().y(), 840, 250)
        self.view.setSceneRect(self.frame.pos().x(), self.frame.pos().y(), 840, 250)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ----------------------<Переменные для рисования фигур>----------------------
        self.ellipse_total = 0
        self.ellipse_diameter = 30

        self.start_line_item = None

        self.start_line_pos_x, self.start_line_pos_y = None, None

        # ----------------------<Переопределенеия ивентов>----------------------
        self.draw_scene.mousePressEvent = self.myMousePressCreateEvent

        self.pushButton.clicked.connect(self.some_event)

        # ----------------------<Переменные для хранения данных графов>----------------------
        self.graph_items: List[Graph] = []
        self.graph_names = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9', 'X10']

        self.current_graph = Graph
        # graph = namedtuple()

    def myMousePressCreateEvent(self, event):
        if event.button() == Qt.LeftButton:
            item: QGraphicsItem = self.get_item_under_mouse(QGraphicsEllipseItem)
            if not item:
                self.draw_circle(event)
            else:
                print(item.pos())
                self.draw_scene.mousePressEvent = self.myMousePressCreateEvent
        elif event.button() == Qt.RightButton:
            item = self.get_item_under_mouse(QGraphicsEllipseItem)
            if item:
                self.draw_arrow(item)
            else:
                if self.start_line_pos_x:
                    self.start_line_item.setBrush(Qt.red)
                    self.start_line_item = None
                self.start_line_pos_x, self.start_line_pos_y = None, None

    def myMousePressDeleteEvent(self, event):
        """Обработка клика на удаление"""
        if event.button() == Qt.LeftButton:
            item: QGraphicsItem = self.get_item_under_mouse()
            self.delete_graph(item)

    def myMouseMoveEvent(self, event):
        pass

    def delete_graph(self, item):
        """Удаление вершины графа её путей"""
        for graph in self.graph_items:
            if item in graph:
                for graph_item in graph:
                    self.draw_scene.removeItem(graph_item)
                break

    # def draw_line(self, event):
    #
    #     if self.start_line_pos_x and self.start_line_pos_y:
    #         line = QGraphicsLineItem(self.start_line_pos_x, self.start_line_pos_y, event.scenePos().x(),
    #                                  event.scenePos().y())
    #         pen = QPen(Qt.black, 2)
    #         line.setPen(pen)
    #         line.setFlag(QGraphicsItem.ItemIsMovable)
    #         print(self.start_line_pos_x, self.start_line_pos_y)
    #         print(event.scenePos().x(), event.scenePos().y())
    #         self.start_line_pos_x = None
    #         self.start_line_pos_y = None
    #         self.draw_scene.addItem(line)
    #
    #         # ------------------------------------------------------
    #     else:
    #         self.start_line_pos_x = event.scenePos().x()
    #         self.start_line_pos_y = event.scenePos().y()
    #     # обращаться к итему через

    def draw_arrow(self, item: QGraphicsItem):
        """Рисовние стрелок"""
        if self.start_line_pos_x and self.start_line_pos_y:
            shape = 0.25  # острота стрелки

            self.start_line_item.setBrush(Qt.red)
            self.start_line_item = None

            x1 = self.start_line_pos_x
            y1 = self.start_line_pos_y
            x2, y2 = self.get_circle_center(item)

            if x1 == x2 and y1 == y2:
                return

            pen = QPen(Qt.black, 2)
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(pen)
            line.setFlag(QGraphicsItem.ItemClipsChildrenToShape)
            self.draw_scene.addItem(line)

            x = x2 - x1
            y = y2 - y1

            # lons = sqrt(x * x + y * y) / 7  # длина лепестков % от длины стрелки
            angle = atan2(y, x)  # угол наклона линии

            lons = 20

            f1x2 = x2 - lons * cos(angle - shape)
            f1y2 = y2 - lons * sin(angle - shape)
            firs_leaf = QGraphicsLineItem(x2, y2, f1x2, f1y2)
            firs_leaf.setFlag(QGraphicsItem.ItemClipsChildrenToShape)
            firs_leaf.setPen(pen)
            self.draw_scene.addItem(firs_leaf)

            f1x2 = x2 - lons * cos(angle + shape)
            f1y2 = y2 - lons * sin(angle + shape)

            second_leaf = QGraphicsLineItem(x2, y2, f1x2, f1y2)
            second_leaf.setFlag(QGraphicsItem.ItemClipsChildrenToShape)
            second_leaf.setPen(pen)
            self.draw_scene.addItem(second_leaf)



            # graph.line = line
            # graph.first_leaf = firs_leaf
            # graph.second_leaf = second_leaf
            # graph.finish_point = item


            self.start_line_pos_x, self.start_line_pos_y = None, None
        else:
            item.setBrush(Qt.green)
            # graph = Graph
            # graph.first_leaf = item
            # self.start_line_item = item
            self.start_line_pos_x, self.start_line_pos_y = self.get_circle_center(item)

    def draw_circle(self, event):
        """Рисовние кргуа"""
        if not self.ellipse_total >= 10:
            ellipse_item = QGraphicsEllipseItem(QRectF(0, 0, self.ellipse_diameter, self.ellipse_diameter))
            ellipse_item.setBrush(Qt.red)
            x_pos = event.scenePos().x() - self.ellipse_diameter / 2
            y_pos = event.scenePos().y() - self.ellipse_diameter / 2
            print(x_pos, y_pos)
            print('-' * 11)
            ellipse_item.setPos(x_pos, y_pos)
            ellipse_item.setFlag(QGraphicsItem.ItemIsMovable)
            self.draw_scene.addItem(ellipse_item)
            self.add_graph_name(x_pos, y_pos)
            self.ellipse_total += 1

    def add_graph_name(self, x, y):
        """Рисование поидписи к графу"""
        text = QGraphicsTextItem(self.graph_names[self.ellipse_total])
        x_pos = x + self.ellipse_diameter / 2
        y_pos = y - self.ellipse_diameter / 2 - 5
        text.setPos(x_pos, y_pos)
        self.draw_scene.addItem(text)

    def get_item_under_mouse(self, t: Optional[Any] = None) -> Optional[Any]:
        """Получение итема под графом"""
        item: QGraphicsItem
        for item in self.draw_scene.items():
            if item.isUnderMouse() and (isinstance(item, t) if t is not None else True):
                print(f'Item under mouse: {item}')
                return item

    def get_circle_center(self, item: QGraphicsItem):
        """Поулчение координат центра круга"""
        center_x = item.pos().x() + self.ellipse_diameter / 2
        center_y = item.pos().y() + self.ellipse_diameter / 2
        return center_x, center_y

    def chek_for_collisions(self, event):
        pass

    def some_event(self):
        """Переключение в режим удаления"""
        if self.draw_scene.mousePressEvent == self.myMousePressCreateEvent:
            self.draw_scene.mousePressEvent = self.mouseRemoveItemEvent
        else:
            self.draw_scene.mousePressEvent = self.myMousePressCreateEvent

    def mouseRemoveItemEvent(self, event):
        if event.button() == Qt.RightButton:
            item = self.get_item_under_mouse()
            self.draw_scene.removeItem(item)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = GUI()  # создаём объект класса приложения
    window.show()  # показываем окно
    app.exec_()  # запускаем приложение


if __name__ == '__main__':
    main()

# TODO : фигура не двигается
# TODO : сделать удаление
# TODO : продумать хранение графов
# TODO : прописать ивент на движение
# TODO : подпись веса к стрелке
# TODO : импорт/экспорт
# TODO : динамическая перерисовка таблицы
