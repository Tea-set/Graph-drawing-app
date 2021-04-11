from dataclasses import dataclass
from datetime import time
from math import cos, sin, atan2, sqrt
import random
from time import sleep
from typing import Optional, Any, List

from Lab_1 import Form

from PyQt5 import QtWidgets
import sys

from PyQt5.QtWidgets import QWidget, QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsEllipseItem, QGraphicsSceneMouseEvent, QGraphicsLineItem, QGraphicsSceneEvent, QGraphicsTextItem, \
    QTextEdit, QTableWidgetItem, QLineEdit
from PyQt5.QtGui import QPainter, QColor, QFont, QMouseEvent, QCursor, QPen
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF, QLineF
from PyQt5.uic.properties import QtCore


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = f"{ex_cls.__name__}: {ex}:\n"
    import traceback
    text += ''.join(traceback.format_tb(tb))
    print(f"\n{text}\n")


sys.excepthook = log_uncaught_exceptions  # noqa


@dataclass
class Point:
    point: QGraphicsEllipseItem
    label: QGraphicsTextItem


@dataclass
class Arrow:
    line: QGraphicsLineItem
    first_leaf: QGraphicsLineItem
    second_leaf: QGraphicsLineItem
    weight: QGraphicsTextItem


@dataclass
class Graph:
    start_point: Point
    finish_point: Point
    arrow: Arrow


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
        self.ellipse_diameter = 30
        self.ellipse_radius = self.ellipse_diameter / 2

        self.start_line_item: QGraphicsLineItem = None
        self.current_text = None
        self.start_line_pos_x, self.start_line_pos_y = None, None
        self.current_weight = None

        # ----------------------<Переопределенеия ивентов>----------------------
        self.draw_scene.mouseMoveEvent = lambda x: None
        self.draw_scene.mouseReleaseEvent = lambda x: None

        self.draw_scene.mousePressEvent = self.myMousePressCreateEvent

        self.pushButton.clicked.connect(self.change_mod)
        self.pushButton_2.clicked.connect(self.create_points_by_edit)
        self.pushButton_3.clicked.connect(self.refresh_table)

        # ----------------------<Переменные для хранения данных графов>----------------------
        self.point_items: List[Point] = []
        self.graph_items: List[Graph] = []
        self.graph_names = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9', 'X10']
        self.hard_points_positions: List[QPointF] = [QPointF(135.0, 100.0), QPointF(725.0, 100.0), QPointF(135.0, 175.0), QPointF(725.0, 175.0),
                                                     QPointF(275.0, 60.0), QPointF(425.0, 60.0), QPointF(575.0, 60.0),
                                                     QPointF(275.0, 200.0), QPointF(425.0, 200.0), QPointF(575.0, 200.0)]

        self.current_graph: Graph
        self.current_start_point: Point
        self.current_finish_point: Point
        self.item = None
        # graph = namedtuple()

    def myMousePressCreateEvent(self, event):
        if event.button() == Qt.LeftButton:  # noqa
            item: QGraphicsItem = self.get_item_under_mouse(QGraphicsEllipseItem)
            if not item:
                self.draw_circle(event.scenePos().x(), event.scenePos().y())
            else:
                self.current_point: Point = self.find_point_in_list(item)
                # print(self.current_point.point.pos())
                self.current_point.point.setBrush(Qt.yellow)
                self.draw_scene.mouseMoveEvent = self.myMouseMoveEvent
                self.draw_scene.mouseReleaseEvent = self.scene_move_mouse_release_event  # print(item.pos())

        elif event.button() == Qt.RightButton:
            item = self.get_item_under_mouse(QGraphicsEllipseItem)
            if item:
                self.draw_arrow(item)
            else:
                if self.start_line_pos_x:
                    self.start_line_item.setBrush(Qt.red)
                    self.start_line_item = None
                self.start_line_pos_x, self.start_line_pos_y = None, None

    def myMouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # self.current_item.setBrush(Qt.yellow)
        item: QGraphicsEllipseItem = self.current_point.point
        lable: QGraphicsTextItem = self.current_point.label

        item_x = item.rect().x()
        item_y = item.rect().y()

        # здесь мы отнимаем ещё и радиус точки, чтобы создавалось ощущение, что курсор тянет точку за центр
        item.setPos(
            event.scenePos().x() - self.ellipse_radius,
            event.scenePos().y() - self.ellipse_radius
        )

        lable.setPos(
            event.scenePos().x() - self.ellipse_radius + self.ellipse_radius,
            event.scenePos().y() - self.ellipse_radius - self.ellipse_radius - 5
        )

    def scene_move_mouse_release_event(self, _: QGraphicsSceneMouseEvent) -> None:
        """Просто отключаем движение после отпускания кнопки мыши"""
        self.draw_scene.mouseMoveEvent = lambda x: None
        self.draw_scene.mouseReleaseEvent = lambda x: None

        self.redraw_items()
        self.current_point.point.setBrush(Qt.red)

    def remove_items(self, item):
        """Удаление элементов"""

        # флаг для проверки удаления вершины из графа
        remove_flag = False

        # листы на удалене итемов
        list_to_remove_points: List[Point] = []
        list_to_remove_arrows: List[Arrow] = []
        list_to_remove_graphs: List[Graph] = []

        # пробегаем списко графоф
        for graph in self.graph_items:
            # TODO : надоб засплитить на разыне методы удаления
            if item == graph.start_point.point or item == graph.finish_point.point or item == graph.arrow.line:
                remove_flag = True

                list_to_remove_graphs.append(graph)

                # если удаляем по начальной вершине
                if item == graph.start_point.point:
                    # remove all except finish
                    list_to_remove_arrows.append(graph.arrow)
                    list_to_remove_points.append(graph.start_point)

                # если удаляем по конечной вершине
                elif item == graph.finish_point.point:
                    list_to_remove_arrows.append(graph.arrow)
                    list_to_remove_points.append(graph.finish_point)

                # удаляем стрелку
                else:
                    list_to_remove_arrows.append(graph.arrow)
                    break

        # удаляем граф
        if remove_flag:
            # проврка для случая удаления не только стрелки
            if list_to_remove_points:
                self.point_items.remove(list_to_remove_points[0])

            for arrow in list_to_remove_arrows:
                self.remove_arrow(arrow)
            for point in list_to_remove_points:
                self.remove_point(point)
            for graph in list_to_remove_graphs:
                self.graph_items.remove(graph)
            # print('graph deleted')

        # удаляем вершину
        else:
            for point in self.point_items:
                if item == point.point:  # за названия стыдно, но править лень
                    self.remove_point(point)
                    self.point_items.remove(point)
                    # print('point deleted')
                    break

    def remove_point(self, point: Point):
        """Удаление вершины"""
        self.draw_scene.removeItem(point.point)
        self.draw_scene.removeItem(point.label)

    def remove_arrow(self, arrow: Arrow):
        """Удаление стрелки"""
        self.draw_scene.removeItem(arrow.line)
        self.draw_scene.removeItem(arrow.first_leaf)
        self.draw_scene.removeItem(arrow.second_leaf)
        self.draw_scene.removeItem(arrow.weight)

    def draw_circle(self, x_pos, y_pos):
        """Рисовние кргуа"""
        if not len(self.point_items) >= 10:
            ellipse_item = QGraphicsEllipseItem(QRectF(0, 0, self.ellipse_diameter, self.ellipse_diameter))
            ellipse_item.setBrush(Qt.red)
            x_pos -= self.ellipse_radius
            y_pos -=  self.ellipse_radius
            # print(x_pos, y_pos)
            # print('-' * 11)
            ellipse_item.setPos(x_pos, y_pos)
            ellipse_item.setFlag(QGraphicsItem.ItemIsMovable)
            self.draw_scene.addItem(ellipse_item)
            text = self.get_graph_name(x_pos, y_pos)
            self.draw_scene.addItem(text)
            self.point_items.append(Point(ellipse_item, text))

    def draw_arrow(self, item: QGraphicsItem):
        """Рисовние стрелок"""
        if self.start_line_pos_x:

            self.start_line_item.setBrush(Qt.red)

            if self.would_be_bidirectionality(item):
                self.start_line_item = None
                self.start_line_pos_x, self.start_line_pos_y = None, None
                return

            sharp = 0.25  # острота стрелки

            weight: int = random.randint(1, 30)

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

            arrow_weight = self.get_arrow_weight(weight, line)
            self.draw_scene.addItem(arrow_weight)

            x = x2 - x1
            y = y2 - y1

            # lons = sqrt(x * x + y * y) / 7  # длина лепестков % от длины стрелки
            angle = atan2(y, x)  # угол наклона линии

            lons = 20  # noqa

            f1x2 = x2 - lons * cos(angle - sharp)
            f1y2 = y2 - lons * sin(angle - sharp)
            firs_leaf = QGraphicsLineItem(x2, y2, f1x2, f1y2)
            firs_leaf.setFlag(QGraphicsItem.ItemClipsChildrenToShape)
            firs_leaf.setPen(pen)
            self.draw_scene.addItem(firs_leaf)

            f1x2 = x2 - lons * cos(angle + sharp)
            f1y2 = y2 - lons * sin(angle + sharp)

            second_leaf = QGraphicsLineItem(x2, y2, f1x2, f1y2)
            second_leaf.setFlag(QGraphicsItem.ItemClipsChildrenToShape)
            second_leaf.setPen(pen)
            self.draw_scene.addItem(second_leaf)

            # создаём переменные для занесения их в граф
            current_arrow = Arrow(line, firs_leaf, second_leaf, arrow_weight)
            start_point = self.find_point_in_list(self.start_line_item)
            finish_point = self.find_point_in_list(item)

            # создаём граф и заносим его в лист графоф
            self.current_graph = Graph(start_point, finish_point, current_arrow)  # noqa
            self.graph_items.append(self.current_graph)

            # зануливаем позиции, для возможности отрисовки стрелки снова
            self.start_line_item = None
            self.start_line_pos_x, self.start_line_pos_y = None, None
        else:
            # перекрашиваем текущую вершину и устанваливаем начальные позиции для стрелки
            item.setBrush(Qt.green)
            self.start_line_item = item
            self.start_line_pos_x, self.start_line_pos_y = self.get_circle_center(item)

    def get_graph_name(self, x, y):
        """Получение подписи к вершине"""
        text = QGraphicsTextItem(self.graph_names[len(self.point_items)])
        x_pos = x + self.ellipse_radius
        y_pos = y - self.ellipse_radius - 5
        text.setPos(x_pos, y_pos)
        self.current_text = text
        return text

    def get_arrow_weight(self, weight: int, line: QGraphicsLineItem) -> QGraphicsTextItem:  # noqa
        arrow_weight = QGraphicsTextItem(str(weight))
        arrow_weight.setPos(line.line().center().x(),
                            line.line().center().y() - 30)
        return arrow_weight

    def get_item_under_mouse(self, t: Optional[Any] = None) -> Optional[Any]:
        """Получение итема под графом"""
        for item in self.draw_scene.items():
            if item.isUnderMouse() and (isinstance(item, t) if t is not None else True):
                # print(f'Item under mouse: {item}')
                return item

    def find_point_in_list(self, item) -> Point:
        for i in self.point_items:
            if i.point == item:
                return i

    def get_circle_center(self, item: QGraphicsItem):
        """Поулчение координат центра круга"""
        center_x = item.pos().x() + self.ellipse_radius
        center_y = item.pos().y() + self.ellipse_radius
        return center_x, center_y

    def chek_for_collisions(self, event):
        pass

    def update_table(self):
        pass

    def change_mod(self):
        """Переключение в режим удаления"""
        if self.draw_scene.mousePressEvent == self.myMousePressCreateEvent:
            self.draw_scene.mousePressEvent = self.mouseRemoveItemEvent
        else:
            self.draw_scene.mousePressEvent = self.myMousePressCreateEvent

    def mouseRemoveItemEvent(self, event):
        if event.button() == Qt.RightButton:
            item = self.get_item_under_mouse()
            self.remove_items(item)
        elif event.button() == Qt.LeftButton:
            print(self.get_item_under_mouse().type())

    # TODO : тут такой бред в плане логики функций, надоб исправить
    def redraw_items(self):
        """Удаление элементов"""

        # флаг для проверки удаления вершины из графа
        item = self.current_point.point

        # пробегаем списко графоф
        for graph in self.graph_items:
            if item == graph.start_point.point or item == graph.finish_point.point:

                # если удаляем по начальной вершине
                if item == graph.start_point.point:
                    # remove all except finish
                    self.redraw_arrow(graph.arrow, True)

                # если удаляем по конечной вершине
                else:
                    self.redraw_arrow(graph.arrow, False)

    def redraw_arrow(self, arrow: Arrow, from_start: bool):
        sharp = 0.25  # острота стрелки
        if not from_start:
            x2, y2 = self.get_circle_center(self.current_point.point)

            lineCoords: QLineF = arrow.line.line()
            lineCoords.setP2(QPointF(x2, y2))
            arrow.line.setLine(lineCoords)

            x1, y1 = lineCoords.p1().x(), lineCoords.p1().y()

            x = x2 - x1
            y = y2 - y1

            # lons = sqrt(x * x + y * y) / 7  # длина лепестков % от длины стрелки
            angle = atan2(y, x)  # угол наклона линии

            lons = 20

            f1x2 = x2 - lons * cos(angle - sharp)
            f1y2 = y2 - lons * sin(angle - sharp)
            lineCoords.setP1(QPointF(x2, y2))
            lineCoords.setP2(QPointF(f1x2, f1y2))
            arrow.first_leaf.setLine(lineCoords)

            f1x2 = x2 - lons * cos(angle + sharp)
            f1y2 = y2 - lons * sin(angle + sharp)

            lineCoords.setP1(QPointF(x2, y2))
            lineCoords.setP2(QPointF(f1x2, f1y2))
            arrow.second_leaf.setLine(lineCoords)

        else:
            x1, y1 = self.get_circle_center(self.current_point.point)

            lineCoords: QLineF = arrow.line.line()
            lineCoords.setP1(QPointF(x1, y1))
            arrow.line.setLine(lineCoords)

            # костыли это наше всё
            for graph in self.graph_items:
                if graph.arrow == arrow:
                    x2, y2 = self.get_circle_center(graph.finish_point.point)
                    break
                else:
                    x2, y2 = self.get_circle_center(self.current_point.point)

            x = x2 - x1
            y = y2 - y1

            # lons = sqrt(x * x + y * y) / 7  # длина лепестков % от длины стрелки
            angle = atan2(y, x)  # угол наклона линии

            lons = 20

            f1x2 = x2 - lons * cos(angle - sharp)
            f1y2 = y2 - lons * sin(angle - sharp)
            lineCoords.setP1(QPointF(x2, y2))
            lineCoords.setP2(QPointF(f1x2, f1y2))
            arrow.first_leaf.setLine(lineCoords)

            f1x2 = x2 - lons * cos(angle + sharp)
            f1y2 = y2 - lons * sin(angle + sharp)

            lineCoords.setP1(QPointF(x2, y2))
            lineCoords.setP2(QPointF(f1x2, f1y2))
            arrow.second_leaf.setLine(lineCoords)

        arrow.weight.setPos(
            arrow.line.line().center().x(),
            arrow.line.line().center().y() - 30
        )

    def would_be_bidirectionality(self, item: QGraphicsItem) -> bool:  # noqa
        for graph in self.graph_items:
            if item == graph.start_point.point or item == graph.finish_point.point:
                if self.start_line_item == graph.start_point.point or self.start_line_item == graph.finish_point.point:
                    return True
            return False

    def create_points_by_edit(self):
        for item in self.draw_scene.items():
            self.draw_scene.removeItem(item)
        self.point_items = []
        self.graph_items = []
        for i in range(int(self.spinBox.text())):
            self.draw_circle(self.hard_points_positions[i].x(), self.hard_points_positions[i].y())

    def change_weight(self, weight: QGraphicsTextItem):
        for graph in self.graph_items:
            if weight == graph.arrow.weight:
                edit = QTextEdit(weight.toPlainText())
        pass

    def refresh_table(self):
        for i in range(0, self.tableWidget.columnCount()):
            for j in range(0, self.tableWidget.rowCount()):
                cell_item = QTableWidgetItem()
                cell_item.setText('')
                self.tableWidget.setItem(i,j,cell_item)

        for i in range(0, len(self.point_items)):
            for j in range(0, len(self.point_items)):
                cell_item = QTableWidgetItem()
                cell_item.setText('0')
                self.tableWidget.setItem(i, j, cell_item)

        for graph in self.graph_items:
            col = self.label_to_int(graph.start_point.label) - 1
            row = self.label_to_int(graph.finish_point.label) - 1
            cell_item = QTableWidgetItem()
            cell_item.setText(graph.arrow.weight.toPlainText())
            self.tableWidget.setItem(col, row, cell_item)

    def label_to_int(self, lavel: QGraphicsTextItem) -> int:
        label_text = lavel.toPlainText()
        label_text = label_text.replace('X', '')
        label_int = int(label_text)
        return label_int

    # def create_label_on_line(self, weight: QGraphicsTextItem):
    #     for graph in self.graph_items:
    #         if weight == graph.arrow.weight:
    #             edit = QLineEdit()
    #             edit.setText(weight.toPlainText())
    #             edit.setParent(self)
    #             edit.setGeometry(int(weight.pos().x()), int(weight.pos().y()), 20, 30)
    #             edit.setMaxLength(2)
    #             edit.show()
    #
    #             self.current_weight = weight.toPlainText()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = GUI()  # создаём объект класса приложения
    window.show()  # показываем окно
    app.exec_()  # запускаем приложение


if __name__ == '__main__':
    main()

# TODO : изменение веса у стрелки
# TODO : импорт/экспорт
# TODO : методы из задания
# TODO : проверка на коллизии
# TODO : раскидать функцию обновления таблицы
# TODO : сделать изменение веса на зименение в таблице
