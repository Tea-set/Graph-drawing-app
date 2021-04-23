from dataclasses import dataclass
import csv
from pandas._libs.internals import defaultdict
from datetime import time
from math import cos, sin, atan2, sqrt
import random
from time import sleep
from typing import Optional, Any, List
from Lab_1.Dijkstra import Node
from Lab_1.Dijkstra import Graph as Graph_d

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
        self.view.setGeometry(self.frame.pos().x(), self.frame.pos().y(), 890, 290)
        self.view.setSceneRect(self.frame.pos().x(), self.frame.pos().y(), 890, 290)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ----------------------<Переменные для рисования фигур>----------------------
        self.ellipse_diameter = 30
        self.ellipse_radius = self.ellipse_diameter / 2

        self.start_line_item: QGraphicsLineItem = None
        self.current_text = None
        self.start_line_pos_x, self.start_line_pos_y = None, None
        self.current_weight = None
        self.min_way = None

        # ----------------------<Переопределенеия ивентов>----------------------
        self.draw_scene.mouseMoveEvent = lambda x: None
        self.draw_scene.mouseReleaseEvent = lambda x: None

        self.draw_scene.mousePressEvent = self.myMousePressCreateEvent

        self.pushButton.clicked.connect(self.change_mod)
        self.pushButton_2.clicked.connect(self.create_points_by_edit)
        self.pushButton_3.clicked.connect(self.dijkstra_method)

        self.actionexport_to_csv.triggered.connect(self.export_form_csv)
        self.actionimport_form_csv.triggered.connect(self.import_form_csv)

        self.tableWidget.cellChanged.connect(self.change_table)

        # ----------------------<Переменные для хранения данных графов>----------------------
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

        self.point_items: List[Point] = []
        self.graph_items: List[Graph] = []
        self.graph_names = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9', 'X10']
        self.hard_points_positions: List[QPointF] = [QPointF(135.0, 100.0), QPointF(725.0, 100.0),
                                                     QPointF(135.0, 175.0), QPointF(725.0, 175.0),
                                                     QPointF(275.0, 60.0), QPointF(425.0, 60.0), QPointF(575.0, 60.0),
                                                     QPointF(275.0, 200.0), QPointF(425.0, 200.0),
                                                     QPointF(575.0, 200.0)]

        self.refresh_mode = True
        self.current_graph: Graph
        self.last_drawn_point: Point
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

        elif event.button() == Qt.MiddleButton:
            item = self.get_item_under_mouse()
            self.remove_items(item)

    def myMouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # self.current_item.setBrush(Qt.yellow)
        item: QGraphicsEllipseItem = self.current_point.point
        lable: QGraphicsTextItem = self.current_point.label

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

        self.refresh_table()

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

    def draw_circle(self, x_pos, y_pos, name: str = None):
        """Рисовние кргуа"""
        if not len(self.point_items) >= 10:
            ellipse_item = QGraphicsEllipseItem(QRectF(0, 0, self.ellipse_diameter, self.ellipse_diameter))
            ellipse_item.setBrush(Qt.red)
            x_pos -= self.ellipse_radius
            y_pos -= self.ellipse_radius
            # print(x_pos, y_pos)
            # print('-' * 11)
            ellipse_item.setPos(x_pos, y_pos)
            ellipse_item.setFlag(QGraphicsItem.ItemIsMovable)
            self.draw_scene.addItem(ellipse_item)
            text = self.get_graph_name(x_pos, y_pos, name)
            self.draw_scene.addItem(text)
            point = Point(ellipse_item, text)
            self.point_items.append(point)
            self.last_drawn_point = point
            if self.refresh_mode:
                self.refresh_table()

    def draw_arrow(self, item: QGraphicsItem, weight: int = None):
        """Рисовние стрелок"""
        if self.start_line_pos_x:

            self.start_line_item.setBrush(Qt.red)

            if self.would_be_bidirectionality(item):
                self.start_line_item = None
                self.start_line_pos_x, self.start_line_pos_y = None, None
                return

            sharp = 0.25  # острота стрелки

            if not weight:
                weight: int = random.randint(1, 10)

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

            if self.refresh_mode:
                self.refresh_table()

            # зануливаем позиции, для возможности отрисовки стрелки снова
            self.start_line_item = None
            self.start_line_pos_x, self.start_line_pos_y = None, None
        else:
            # перекрашиваем текущую вершину и устанваливаем начальные позиции для стрелки
            item.setBrush(Qt.green)
            self.start_line_item = item
            self.start_line_pos_x, self.start_line_pos_y = self.get_circle_center(item)

    def get_graph_name(self, x, y, name: str = None):
        """Получение подписи к вершине"""
        if name:
            text = QGraphicsTextItem(name)
        else:
            # TODO : метод подбора имени точки
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
        # TODO : доделать
        pass

    def change_table(self, row_pos: int, col_pos: int):

        if self.refresh_mode:
            for graph in self.graph_items:
                if self.label_to_int(graph.start_point.label) == row_pos + 1 and \
                        self.label_to_int(graph.finish_point.label) == col_pos + 1:
                    weight_int = self.tableWidget.item(row_pos, col_pos).text()
                    if weight_int == '':
                        weight_int = 0
                    else:
                        weight_int = int(weight_int)
                    self.draw_scene.removeItem(graph.arrow.weight)
                    weight = self.get_arrow_weight(weight_int, graph.arrow.line)
                    graph.arrow.weight = weight
                    self.draw_scene.addItem(weight)

                    return

    def change_mod(self):
        """Переключение в режим удаления"""
        if self.draw_scene.mousePressEvent == self.myMousePressCreateEvent:
            self.pushButton.setStyleSheet("color:green")
            self.draw_scene.mousePressEvent = self.mouseRemoveItemEvent
        else:
            self.draw_scene.mousePressEvent = self.myMousePressCreateEvent
            self.pushButton.setStyleSheet("color:black")

    def mouseRemoveItemEvent(self, event):
        if event.button() == Qt.RightButton:
            item = self.get_item_under_mouse()
            self.remove_items(item)
        elif event.button() == Qt.LeftButton:
            item = self.get_item_under_mouse()
            if item.type() == 8:
                self.create_label_on_line(item)
            print(self.get_item_under_mouse().type())

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

            graph.start_point.point.setBrush(Qt.red)
            pen = QPen(Qt.black, 2)
            graph.arrow.line.setPen(pen)
            graph.arrow.first_leaf.setPen(pen)
            graph.arrow.second_leaf.setPen(pen)

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

    def clear_scene(self):
        for item in self.draw_scene.items():
            self.draw_scene.removeItem(item)
        self.point_items = []
        self.graph_items = []

    def create_points_by_edit(self):
        self.clear_scene()
        for i in range(int(self.spinBox.text())):
            self.draw_circle(self.hard_points_positions[i].x(), self.hard_points_positions[i].y())
        self.refresh_table()

    def refresh_table(self):
        self.refresh_mode = False
        for i in range(0, self.tableWidget.columnCount()):
            for j in range(0, self.tableWidget.rowCount()):
                cell_item = QTableWidgetItem()
                cell_item.setText('')
                self.tableWidget.setItem(i, j, cell_item)

        max_label_index = 0
        for point in self.point_items:
            if self.label_to_int(point.label) > max_label_index:
                max_label_index = self.label_to_int(point.label)

        for i in range(0, max_label_index):
            for j in range(0, max_label_index):
                cell_item = QTableWidgetItem()
                cell_item.setText('0')
                self.tableWidget.setItem(i, j, cell_item)

        for graph in self.graph_items:
            col = self.label_to_int(graph.start_point.label) - 1
            row = self.label_to_int(graph.finish_point.label) - 1
            cell_item = QTableWidgetItem()
            cell_item.setText(graph.arrow.weight.toPlainText())
            self.tableWidget.setItem(col, row, cell_item)

        self.refresh_mode = True

    def label_to_int(self, label: QGraphicsTextItem) -> int:  # noqa
        label_text = label.toPlainText()
        label_text = label_text.replace('X', '')
        label_int = int(label_text)
        return label_int

    def create_label_on_line(self, weight: QGraphicsTextItem):
        # TODO : доделать
        for graph in self.graph_items:
            if weight == graph.arrow.weight:
                edit = QLineEdit()
                edit.setText(weight.toPlainText())
                edit.setParent(self)
                edit.setGeometry(int(weight.pos().x()), int(weight.pos().y()), 20, 30)
                edit.setMaxLength(2)

                self.current_weight = weight.toPlainText()
                self.default_key_press_event = edit.keyPressEvent
                edit.keyPressEvent == self.line_edit_release_key_event

                edit.show()

    def line_edit_release_key_event(self, event):
        # TODO : доделать
        if event.key == Qt.key_enter:
            print('some ')

    def import_form_csv(self, path="graph.csv"):
        j = 0
        with open('graph.csv', encoding="utf-8") as class_file:
            file_reader = csv.reader(class_file, delimiter=",")
            for row in file_reader:
                for i in range(0, len(row)):
                    cell_item = QTableWidgetItem()
                    cell_item.setText(row[i])
                    self.tableWidget.setItem(j, i, cell_item)
                j += 1
        self.create_graph_by_table()

    def export_form_csv(self, path='graph.csv'):
        names = self.graph_names
        if len(self.point_items) == 0:
            return
        with open(path, mode="w", encoding="utf-8") as graph_file:
            file_writer = csv.DictWriter(graph_file, delimiter=",", lineterminator="\r", fieldnames=names)

            rows = self.tableWidget.rowCount()
            cols = self.tableWidget.columnCount()
            for row in range(rows):
                data = []
                for col in range(cols):
                    text = self.tableWidget.item(row, col).text()
                    if text != '':
                        data.append(self.tableWidget.item(row, col).text())
                    else:
                        data.append('')
                while len(data) != 10:
                    data.append('')
                dictionary = dict(zip(self.graph_names, data))
                file_writer.writerow(dictionary)

    def create_graph_by_table(self):
        self.clear_scene()

        self.refresh_mode = False

        for i in range(0, 10):
            for j in range(0, 10):
                if self.tableWidget.item(i, j).text() != '' and self.tableWidget.item(i, j).text() != '0':

                    # print(' ', self.tableWidget.item(i, j).text(), end = ' ')
                    name = "X" + str(i + 1)
                    # print(name)
                    crate_name_key = True
                    for point in self.point_items:
                        if name == point.label.toPlainText():
                            crate_name_key = False
                    if crate_name_key:
                        self.draw_circle(self.hard_points_positions[i].x(), self.hard_points_positions[i].y(), name)

                    for point in self.point_items:
                        if name == point.label.toPlainText():
                            start_point = point
                            break

                    name = "X" + str(j + 1)
                    crate_name_key = True
                    for point in self.point_items:
                        if name == point.label.toPlainText():
                            crate_name_key = False
                    if crate_name_key:
                        self.draw_circle(self.hard_points_positions[j].x(), self.hard_points_positions[j].y(), name)

                    for point in self.point_items:
                        if name == point.label.toPlainText():
                            finish_point = point
                            break

                    self.start_line_item = start_point.point
                    self.start_line_pos_x, self.start_line_pos_y = self.get_circle_center(self.start_line_item)
                    self.draw_arrow(finish_point.point, int(self.tableWidget.item(i, j).text()))

        self.refresh_mode = True

    def dijkstra_method(self):
        if self.spinBox_2.text() == self.spinBox_3.text():
            text = "Начальная и конечная вершины соввпадают"
            self.textBrowser.setText(text)
            return

        key_in_start = False
        key_in_fining = False
        for graph in self.graph_items:
            if self.label_to_int(graph.start_point.label) == int(self.spinBox_2.text()):
                key_in_start = True
            if self.label_to_int(graph.finish_point.label) == int(self.spinBox_3.text()):
                key_in_fining = True

        if not key_in_start or not key_in_fining:
            text = "Выбраны неверные вершины"
            self.textBrowser.setText(text)
            return

        node_list = []
        for name in self.graph_names:
            for point in self.point_items:
                if name == point.label.toPlainText():
                    node_list.append(Node(point.label.toPlainText()))
        # TODO : обработать начальную вершину
        # TODO : вспомнить о чём тудуха выше
        w_graph = Graph_d.create_from_nodes(node_list)

        for i in range(0, 10):
            for j in range(0, 10):
                if self.tableWidget.item(i, j).text() != '' and self.tableWidget.item(i, j).text() != '0':
                    # print(' ', self.tableWidget.item(i, j).text(), end = ' ')
                    start_point = node_list[i]
                    finish_point = node_list[j]
                    weight = int(self.tableWidget.item(i, j).text())

                    w_graph.connect(start_point, finish_point, weight)

        min_ways = w_graph.dijkstra(node_list[int(self.spinBox_2.text()) - 1])
        # str = ([(weight, [n.data for n in node]) for (weight, node) in min_ways])
        # print(str)

        nodes = []
        weights = []
        for (weight, node) in min_ways:
            temp = []
            for n in node:
                temp.append(n.data)
            weights.append(weight)
            nodes.append(temp)
        self.textBrowser.setText('')

        min_way = nodes[int(self.spinBox_3.text()) - 1]
        min_wei = weights[int(self.spinBox_3.text()) - 1]

        str_l = []

        for el in min_way:
            str_l.append(el)
            str_l.append('->')
        str_l.pop()

        str_out = str(min_wei) + ' : '
        for s in str_l:
            str_out += s

        self.textBrowser.setText(str_out)
        self.paint_graph_by_min_way(min_way)

    def paint_graph_by_min_way(self, min_way):
        """Выделяет минимальный путь"""
        self.draw_default()

        for i in range(0, len(min_way) - 1):
            for graph in self.graph_items:
                if min_way[i] == graph.start_point.label.toPlainText() and \
                        min_way[i + 1] == graph.finish_point.label.toPlainText():
                    graph.start_point.point.setBrush(Qt.blue)
                    graph.finish_point.point.setBrush(Qt.blue)
                    pen = QPen(Qt.red, 4)
                    graph.arrow.line.setPen(pen)
                    graph.arrow.first_leaf.setPen(pen)
                    graph.arrow.second_leaf.setPen(pen)

    def draw_default(self):
        """Красит граф в нормальные цывета"""
        for graph in self.graph_items:
            graph.start_point.point.setBrush(Qt.red)
            graph.finish_point.point.setBrush(Qt.red)
            pen = QPen(Qt.black, 2)
            graph.arrow.line.setPen(pen)
            graph.arrow.first_leaf.setPen(pen)
            graph.arrow.second_leaf.setPen(pen)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = GUI()  # создаём объект класса приложения
    window.show()  # показываем окно
    app.exec_()  # запускаем приложение


if __name__ == '__main__':
    main()

# TODO : изменение веса у стрелки

# TODO : сделать метод на выбор имён для вершин
# TODO : проверка на коллизии
