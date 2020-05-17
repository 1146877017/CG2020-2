from cg_algorithms import *

import sys
from enum import Enum
import math

from PyQt5.QtCore import (
    Qt,
    QRectF
)

from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    qApp,
    QApplication,
    QMenu,
    QLabel,
    QColorDialog,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsView,
    QGraphicsItem,
    QGraphicsScene,
    QPushButton,
    QGridLayout,
    QSpacerItem,
    QSizePolicy,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QLayout
)


from PyQt5.QtGui import (
    QIcon,
    QColor,
    QPainter,
    QPalette,
    QImage,
    QPixmap,
    QMouseEvent
)


class Acting(Enum):
    Free = 0

    Translate = 1
    Rotate = 2
    Scale = 3
    Clip = 4

    Line = 5
    Polygon = 6
    Ellipse = 7
    Curve = 8


class Element(QGraphicsItem):
    class ListItem(QListWidgetItem):
        def __init__(self, element, *args):
            super().__init__(*args)
            self.element = element

    def __init__(self, id: str, primitive: Primitive, color: Color, parent=None):
        super().__init__(parent=parent)
        self.id = id
        self.primitive: Primitive = primitive
        self.color: Color = color
        self.listItem: self.ListItem = self.ListItem(self, self.__str__())
        self.canvas: MainCanvas = None

    def __str__(self):
        return self.id + " " + self.primitive.__str__()

    def paint(self, painter: QPainter, option, widget=None):
        c = QColor()
        c.setRgb(*self.color)
        painter.setPen(c)
        for p in self.primitive.render():
            painter.drawPoint(*p)
        if self.listItem.isSelected():
            pen = painter.pen()
            c.setAlpha(96)
            painter.setPen(c)
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        return QRectF(*self.primitive.boundingRect())

    # def mousePressEvent(self, event: QMouseEvent):
    #     self.canvas.selectElementFromCanvas(self)


class MainCanvas(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent=parent)
        self.main: MainWindow = parent
        self.listWidget: QListWidget = QListWidget(parent)
        self.listWidget.itemSelectionChanged.connect(self.onSelectChanged)

        self.scene: QGraphicsScene = scene
        self.scene.setBackgroundBrush(Qt.white)

        self.elements = {}
        self.selecting: Element = None

        self.pointList = []
        # self.helperCanvasItems = []
        self.drawingElement: Element = None

    def clearSelection(self):
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item.setSelected(False)
        self.scene.update()

    def selectElementFromCanvas(self, e: Element):
        self.clearSelection()
        e.listItem.setSelected(True)

    def onSelectChanged(self):
        items = self.listWidget.selectedItems()
        if not items:
            self.selecting = None
            self.main.infoStatusLabel.setText("")
            return
        self.selecting = items[0]
        self.main.infoStatusLabel.setText("Selecting: " + items[0].element.__str__())
        self.scene.update(self.scene.sceneRect())

    def addElement(self, e: Element):
        e.canvas = self
        self.elements[e.id] = e
        self.scene.addItem(e)
        self.listWidget.addItem(e.listItem)

    def delElement(self, id: str):
        try:
            e = self.elements[id]
            self.translateElement(id, self.main.size[0]*2, self.main.size[1]*2)
            self.scene.update()
            self.scene.removeItem(e)
            self.listWidget.takeItem(self.listWidget.indexFromItem(e.listItem).row())
            del self.elements[id]

        except Exception as e:
            print(e)

        self.clearSelection()

    def getElement(self, id: str) -> Element:
        try:
            return self.elements[id]
        except Exception as e:
            print(e)

    def clearElement(self):
        keys = [_ for _ in self.elements]
        for key in keys:
            self.delElement(key)

    def updateElement(self, id: str):
        e = self.getElement(id)
        if e:
            self.scene.update()
            e.listItem.setText(e.__str__())

    def translateElement(self, id: str, dx: int, dy: int):
        e = self.getElement(id)
        if not e:
            return
        e.primitive.translate(dx, dy)
        self.updateElement(id)

    def rotateElement(self, id: str, x0: int, y0: int, deg: int):
        e = self.getElement(id)
        if not e:
            return
        e.primitive.rotate(x0, y0, deg)
        self.updateElement(id)

    def scaleElement(self, id: str, x0: int, y0: int, rate: float):
        e = self.getElement(id)
        if not e:
            return
        e.primitive.scale(x0, y0, rate)
        self.updateElement(id)

    def clipElement(self, id: str, x0: int, y0: int, x1: int, y1: int, algorithm: Line.ClipAlgorithm):
        e = self.getElement(id)
        if not e or e.primitive.type != Primitive.PType.line:
            return
        if e.primitive.clip(x0, y0, x1, y1, algorithm):
            self.updateElement(id)
        else:
            print("delete")
            self.delElement(id)

    # def clearHelperCanvasItems(self):
    #     for i in self.helperCanvasItems:
    #         self.scene.removeItem(i)
    #     self.helperCanvasItems = []

    def clearDrawingElement(self):
        if self.drawingElement:
            self.scene.removeItem(self.drawingElement)
            self.drawingElement = None

    def updateDrawingElement(self):
        if self.drawingElement:
            self.scene.addItem(self.drawingElement)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.main.acting == Acting.Free:
            self.clearSelection()
        elif self.main.acting == Acting.Polygon:
            self.clearDrawingElement()
            if len(self.pointList) >= 3:
                self.main.addElement(Polygon(self.pointList[:-1], Line.Algorithm.DDA))
            self.main.bPolygon.toggle()
        elif self.main.acting == Acting.Curve:
            self.clearDrawingElement()
            if len(self.pointList) >= 3:
                self.main.addElement(Curve(self.pointList[:-1], self.main.curveAlgorithm))
            if self.main.curveAlgorithm == Curve.Algorithm.Bezier:
                self.main.bCurveBezier.toggle()
            else:
                self.main.bCurveBSpline.toggle()

    def mousePressEvent(self, event: QMouseEvent):
        self.clearDrawingElement()
        pos = self.mapToScene(event.localPos().toPoint())
        x, y = int(pos.x()), int(pos.y())
        if self.main.acting == Acting.Free or (self.main.acting in [Acting.Translate, Acting.Rotate, Acting.Scale, Acting.Clip] and not self.selecting):
            minSquare = 10000 ** 2
            targetE: Element = None
            for id in self.elements:
                e = self.elements[id]
                rect = e.boundingRect()
                if e.boundingRect().contains(x, y) and rect.width()*rect.height() < minSquare:
                    targetE = e
                    minSquare = rect.width()*rect.height()
            if targetE:
                self.selectElementFromCanvas(targetE)
            else:
                self.clearSelection()
        else:
            self.pointList.append((x, y))
            if self.main.acting == Acting.Line:
                if len(self.pointList) >= 2:
                    self.main.addElement(Line(*self.pointList[0], *self.pointList[1], Line.Algorithm.DDA))
                    self.main.bLine.toggle()
            elif self.main.acting == Acting.Polygon:
                if len(self.pointList) >= 2:
                    self.drawingElement = Element("", Polygon(self.pointList, Line.Algorithm.DDA), self.main.color)
            elif self.main.acting == Acting.Ellipse:
                if len(self.pointList) >= 2:
                    self.main.addElement(Ellipse(*self.pointList[0], *self.pointList[1]))
                    self.main.bEllipse.toggle()
            elif self.main.acting == Acting.Curve:
                if len(self.pointList) >= 2:
                    self.drawingElement = Element("", Curve(self.pointList, self.main.curveAlgorithm), self.main.color)
            elif self.main.acting == Acting.Translate:
                rect = self.selecting.element.boundingRect()
                x0 = rect.x() + rect.width() / 2
                y0 = rect.y() + rect.height() / 2
                self.translateElement(self.selecting.element.id, int(x - x0), int(y - y0))
                self.main.bTranslate.toggle()
            elif self.main.acting == Acting.Rotate:
                if len(self.pointList) >= 2:
                    rect = self.selecting.element.boundingRect()
                    x0 = rect.x() + rect.width() / 2
                    y0 = rect.y() + rect.height() / 2
                    x1, y1 = self.pointList[0][0], self.pointList[0][1]
                    x2, y2 = self.pointList[1][0], self.pointList[1][1]
                    if x1 == x0 and y1 == y0:
                        x1 += 1
                    if x2 == x0 and y2 == y0:
                        x2 += 1
                    dx1, dy1 = x1 - x0, y1 - y0
                    dx2, dy2 = x2 - x0, y2 - y0
                    d1 = math.acos(dx1 / math.sqrt(dx1**2 + dy1**2)) * 180 / math.pi
                    d2 = math.acos(dx2 / math.sqrt(dx2**2 + dy2**2)) * 180 / math.pi
                    # cos1 = (dx1*dx2 + dy1*dy2) / (math.sqrt((dx1**2 + dy1**2) * (dx2**2 + dy2**2)))
                    deg = 0
                    if dy1 >= 0 and dy2 >= 0:
                        deg = d1 - d2
                    elif dy1 >= 0 and dy2 < 0:
                        deg = d1 + d2
                    elif dy1 < 0 and dy2 >= 0:
                        deg = -d1 - d2
                    else:
                        # dy1, dy2 < 0
                        deg = d2 - d1
                    self.rotateElement(self.selecting.element.id, x0, y0, -int(deg))
                    self.main.bRotate.toggle()

            elif self.main.acting == Acting.Scale:
                if len(self.pointList) >= 2:
                    rect = self.selecting.element.boundingRect()
                    x0 = rect.x() + rect.width() / 2
                    y0 = rect.y() + rect.height() / 2
                    d1 = math.sqrt((self.pointList[0][0] - x0)**2 + (self.pointList[0][1] - y0)**2)
                    d2 = math.sqrt((self.pointList[1][0] - x0)**2 + (self.pointList[1][1] - y0)**2)
                    if d1 == 0:
                        d1 = 1
                    self.scaleElement(self.selecting.element.id, x0, y0, d2/d1)
                    self.main.bScale.toggle()
            elif self.main.acting == Acting.Clip:
                if self.selecting.element.primitive.type != Primitive.PType.line:
                    self.main.bClip.toggle()
                if len(self.pointList) >= 2:
                    self.clipElement(
                        self.selecting.element.id, *self.pointList[0], *self.pointList[1], Line.ClipAlgorithm.Cohen_Sutherland)
                    self.main.bClip.toggle()

        self.updateDrawingElement()
        self.scene.update()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.acting: Acting = Acting.Free
        self.color = (0, 0, 0)
        self.size = (0, 0)
        self.scene = QGraphicsScene(self)
        self.canvas = MainCanvas(self.scene, self)
        self.curveAlgorithm = Curve.Algorithm.Bezier

        self.initUI()

        self.id = 0
        self.setColor(0, 0, 0)
        self.resetSize(500, 500)
        self.updateActingStatus(Acting.Free)

        self.addElement(Line(100, 400, 300, 200, Line.Algorithm.DDA))
        self.addElement(Line(200, 200, 400, 400, Line.Algorithm.Bresenham))
        self.setColor(96, 211, 148)
        self.addElement(Ellipse(200, 100, 350, 460))
        self.setColor(255, 0, 0)
        self.addElement(Polygon([(0, 0), (100, 200), (300, 100)], Line.Algorithm.Bresenham))
        self.setColor(0, 255, 0)
        self.addElement(Curve([(0, 0), (100, 200), (300, 100)], Curve.Algorithm.B_spline))

    def initUI(self):

        self.setWindowTitle("CG2020 Drawing Board")
        self.statusBar()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        self.setGeometry(300, 300, 1200, 800)

        self.initStatusBar()
        self.initMenu()
        self.initMain()

        self.show()

    def initStatusBar(self):
        self.infoStatusLabel = QLabel("", self)
        self.statusBar().insertPermanentWidget(0, self.infoStatusLabel)
        self.sizeStatusLabel = QLabel("", self)
        self.statusBar().insertPermanentWidget(1, self.sizeStatusLabel)
        self.colorStatusLabel = QLabel("", self)
        self.statusBar().insertPermanentWidget(2, self.colorStatusLabel)

    def updateActingStatus(self, acting: Acting):
        self.acting = acting

    def initMenu(self):
        self.initFileMenu()
        self.initCanvasMenu()
        self.initPrimitiveMenu()
        self.initTransformMenu()

    def initFileMenu(self):
        fileMenu = self.menuBar().addMenu('&File')

        # Load action
        # loadAction = QAction('&Load', self)
        # loadAction.setStatusTip('Load from script')
        # loadAction.setShortcut('Ctrl+L')
        # fileMenu.addAction(loadAction)

        # Save BMP action
        saveBMPAction = QAction('&Save BMP', self)
        saveBMPAction.setStatusTip('Save the canvas as BMP')
        saveBMPAction.setShortcut('Ctrl+E')
        saveBMPAction.triggered.connect(self.getSaveBMPDialog)
        fileMenu.addAction(saveBMPAction)

        # Save TXT action
        saveTXTAction = QAction('&Save TXT', self)
        saveTXTAction.setStatusTip('Save the canvas as TXT')
        saveTXTAction.setShortcut('Ctrl+S')
        saveTXTAction.triggered.connect(self.getSaveTXTDialog)
        fileMenu.addAction(saveTXTAction)

        # Exit action
        exitAction = QAction('&Exit', self)
        exitAction.setStatusTip('Exit application')
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

    def saveFileBMP(self, name: str):
        self.canvas.clearSelection()
        img = QImage(self.size[0], self.size[1], QImage.Format_ARGB32)
        painter = QPainter(img)
        self.scene.render(painter)
        img.save(name)
        painter.end()

    def getSaveBMPDialog(self):
        fileName = QFileDialog.getSaveFileName(self, "Save Canvas as BMP", "output.bmp", "Images (*.bmp)")[0]
        if not fileName:
            return
        try:
            self.saveFileBMP(fileName)
        except Exception as e:
            print(e)

    def saveFileTXT(self, name: str):
        with open(name, "w") as File:
            File.write(f"resetCanvas {self.size[0]} {self.size[1]}\n")
            for k in self.canvas.elements:
                e: Element = self.canvas.elements[k]
                File.write(f"setColor {e.color[0]} {e.color[1]} {e.color[2]}\n")
                p: Primitive = e.primitive
                text = ""
                if p.type == Primitive.PType.line:
                    text = f"drawLine {e.id} {p.x0} {p.y0} {p.x1} {p.y1} {p.algorithm.name}"
                elif p.type == Primitive.PType.polygon:
                    text = f"drawPolygon {e.id} "
                    for l in p.lines:
                        text += f"{l.x1} {l.y1} "
                    text += f"{p.algorithm.name}"
                elif p.type == Primitive.PType.ellipse:
                    text = f"drawEllipse {e.id} {p.cx - p.rx} {p.cy - p.ry} {p.cx + p.rx} {p.cy + p.ry}"
                elif p.type == Primitive.PType.curve:
                    text = f"drawCurve {e.id} "
                    for point in p.points:
                        text += f"{point[0]} {point[1]} "
                    if p.algorithm == Curve.Algorithm.Bezier:
                        text += "Bezier"
                    else:
                        text += "B-spline"
                File.write(text + "\n")

    def getSaveTXTDialog(self):
        fileName = QFileDialog.getSaveFileName(self, "Save Canvas as TXT", "output.txt")[0]
        if not fileName:
            return
        try:
            self.saveFileTXT(fileName)
        except Exception as e:
            print(e)

    def initCanvasMenu(self):
        canvasMenu = self.menuBar().addMenu('&Canvas')

        # Reset action
        resetAction = QAction('&Reset', self)
        resetAction.setStatusTip('Reset the canvas')
        resetAction.setShortcut('Ctrl+R')
        resetAction.triggered.connect(self.getResetDialog)
        canvasMenu.addAction(resetAction)

        # Set color
        colorAction = QAction('&Color', self)
        colorAction.setStatusTip('Set pen color')
        colorAction.setShortcut('Ctrl+P')
        colorAction.triggered.connect(self.pickColor)
        canvasMenu.addAction(colorAction)

        # Delete
        deleteAction = QAction('&Delete', self)
        deleteAction.setStatusTip('Delete primitive')
        deleteAction.setShortcut('Ctrl+D')
        deleteAction.triggered.connect(self.getDeleteDialog)
        canvasMenu.addAction(deleteAction)

    def getResetDialog(self):
        text, ok = QInputDialog().getText(self, f"Reset Canvas", "width height(empty for keep current size)", echo=QLineEdit.Normal)
        if not ok:
            return
        args = []
        try:
            args = list(map(lambda s: int(s), text.split()))
        except Exception as e:
            print(e)
        if len(args) == 0:
            self.resetSize(*self.size)
        elif len(args) == 2:
            self.resetSize(*args)

    def resetSize(self, width: int, height: int):
        if width < 100 or width > 1000 or height < 100 or height > 1000:
            return
        self.id = 0
        self.canvas.clearElement()
        self.size = (width, height)
        self.scene.clear()
        self.scene.setSceneRect(0, 0, width, height)
        self.scene.addRect(-1, -1, width+2, height+2)
        self.canvas.setFixedSize(width*1.05, height*1.05)
        self.adjustSize()
        self.sizeStatusLabel.setText(f"Size: ({width},{height})")

    def getNewID(self) -> str:
        self.id += 1
        return str(self.id)

    def getDeleteDialog(self):
        text, ok = QInputDialog().getText(self, f"Reset Canvas", "width height(empty for keep current size)", echo=QLineEdit.Normal)
        if not ok or not text:
            return
        self.canvas.delElement(text)

    def initPrimitiveMenu(self):
        primitiveMenu = self.menuBar().addMenu('&Primitive')

        # Line
        lineMenu = QMenu('&Line', self)
        # DDA
        lineActionDDA = QAction('&DDA', self)
        lineActionDDA.setStatusTip('Draw line with DDA algorithm')
        lineActionDDA.triggered.connect(self.getLineDialog(Line.Algorithm.DDA))
        lineMenu.addAction(lineActionDDA)
        # Bresenham
        lineActionBresenham = QAction('&Bresenham', self)
        lineActionBresenham.setStatusTip('Draw line with Bresenham algorithm')
        lineMenu.addAction(lineActionBresenham)
        lineActionBresenham.triggered.connect(self.getLineDialog(Line.Algorithm.Bresenham))
        primitiveMenu.addMenu(lineMenu)

        # Polygon
        polygonMenu = QMenu('&Polygon', self)
        # DDA
        polygonActionDDA = QAction('&DDA', self)
        polygonActionDDA.setStatusTip('Draw polygon with DDA algorithm')
        polygonActionDDA.triggered.connect(self.getPolygonDialog(Line.Algorithm.DDA))
        polygonMenu.addAction(polygonActionDDA)
        # Bresenham
        polygonActionBresenham = QAction('&Bresenham', self)
        polygonActionBresenham.setStatusTip('Draw polygon with Bresenham algorithm')
        polygonMenu.addAction(polygonActionBresenham)
        polygonActionBresenham.triggered.connect(self.getPolygonDialog(Line.Algorithm.Bresenham))
        primitiveMenu.addMenu(polygonMenu)

        # Ellipse
        ellipseAction = QAction('&Ellipse', self)
        ellipseAction.setStatusTip('Draw ellipse')
        ellipseAction.triggered.connect(self.getEllipseDialog())
        primitiveMenu.addAction(ellipseAction)

        # Curve
        # Bezier
        curveMenu = QMenu('&Curve', self)
        curveActionBezier = QAction('&Bezier', self)
        curveActionBezier.setStatusTip('Draw curve with Bezier algorithm')
        curveActionBezier.triggered.connect(self.getCurveDialog(Curve.Algorithm.Bezier))
        curveMenu.addAction(curveActionBezier)
        # B Spline
        curveActionB_spline = QAction('&B-spline', self)
        curveActionB_spline.setStatusTip('Draw curve with B-spline algorithm')
        curveActionB_spline.triggered.connect(self.getCurveDialog(Curve.Algorithm.B_spline))
        curveMenu.addAction(curveActionB_spline)

        primitiveMenu.addMenu(curveMenu)

    def getLineDialog(self, algorithm: Line.Algorithm):
        def f():
            text, ok = QInputDialog().getText(
                self, f"Draw Line({algorithm.name})", "x0 y0 x1 y1", echo=QLineEdit.Normal)
            if not ok:
                return
            args = []
            try:
                args = list(map(lambda s: int(s), text.split()))
            except Exception as e:
                print(e)
            if len(args) == 4:
                self.addElement(Line(*args, algorithm))
        return f

    def getPolygonDialog(self, algorithm: Line.Algorithm):
        def f():
            text, ok = QInputDialog().getText(
                self, f"Draw Polygon({algorithm.name})", "x0 y0 x1 y1 x2 y2 ...", echo=QLineEdit.Normal)
            if not ok:
                return
            args = []
            try:
                args = list(map(lambda s: int(s), text.split()))
            except Exception as e:
                print(e)
            points = []
            for i in range(len(args) // 2):
                points.append((args[i*2], args[i*2+1]))
            if points:
                self.addElement(Polygon(points, algorithm))
        return f

    def getEllipseDialog(self):
        def f():
            text, ok = QInputDialog().getText(self, "Draw Ellipse", "x0 y0 x1 y1 ...", echo=QLineEdit.Normal)
            if not ok:
                return
            args = []
            try:
                args = list(map(lambda s: int(s), text.split()))
            except Exception as e:
                print(e)
            if len(args) == 4:
                self.addElement(Ellipse(*args))
        return f

    def getCurveDialog(self, algorithm: Curve.Algorithm):
        def f():
            text, ok = QInputDialog().getText(
                self, f"Draw Curve({algorithm.name})", "x0 y0 x1 y1 x2 y2 ...", echo=QLineEdit.Normal)
            if not ok:
                return
            args = []
            try:
                args = list(map(lambda s: int(s), text.split()))
            except Exception as e:
                print(e)
            points = []
            for i in range(len(args) // 2):
                points.append((args[i*2], args[i*2+1]))
            if points:
                self.addElement(Curve(points, algorithm))
        return f

    def initTransformMenu(self):
        transformMenu = self.menuBar().addMenu('&Transform')

        # Translate
        translateAction = QAction('&Translate', self)
        translateAction.setStatusTip('Translate primitive')
        translateAction.triggered.connect(self.getTranslateDialog)
        transformMenu.addAction(translateAction)

        # Rotate
        rotateAction = QAction('&Rotate', self)
        rotateAction.setStatusTip('Rotate any primitive')
        rotateAction.triggered.connect(self.getRotateDialog)
        transformMenu.addAction(rotateAction)

        # Scale
        scaleAction = QAction('&Scale', self)
        scaleAction.setStatusTip('Scale any primitive')
        scaleAction.triggered.connect(self.getScaleDialog)
        transformMenu.addAction(scaleAction)

        # Clip
        clipMenu = QMenu('&Clip', self)
        # Cohen-Sutherland
        clipActionCohen = QAction('&Cohen-Sutherland', self)
        clipActionCohen.setStatusTip('Clip line with Cohen-Sutherland algorithm')
        clipActionCohen.triggered.connect(self.getClipDialog(Line.ClipAlgorithm.Cohen_Sutherland))
        clipMenu.addAction(clipActionCohen)
        # Liang-Barsky
        clipActionLiang = QAction('&Liang-Barsky', self)
        clipActionLiang.setStatusTip('Clip line with Liang-Barsky algorithm')
        clipActionLiang.triggered.connect(self.getClipDialog(Line.ClipAlgorithm.Liang_Barsky))
        clipMenu.addAction(clipActionLiang)
        transformMenu.addMenu(clipMenu)

    def getTranslateDialog(self):
        text, ok = QInputDialog().getText(self, f"Translate", "id dx dy", echo=QLineEdit.Normal)
        if not ok or not text:
            return
        try:
            args = text.split()
            self.canvas.translateElement(args[0], int(args[1]), int(args[2]))
        except Exception as e:
            print(e)

    def getRotateDialog(self):
        text, ok = QInputDialog().getText(self, f"Rotate", "id x0 y0 degree", echo=QLineEdit.Normal)
        if not ok or not text:
            return
        try:
            args = text.split()
            self.canvas.rotateElement(args[0], int(args[1]), int(args[2]), int(args[3]))
        except Exception as e:
            print(e)

    def getScaleDialog(self):
        text, ok = QInputDialog().getText(self, f"Scale", "id x0 y0 rate", echo=QLineEdit.Normal)
        if not ok or not text:
            return
        try:
            args = text.split()
            self.canvas.scaleElement(args[0], int(args[1]), int(args[2]), float(args[3]))
        except Exception as e:
            print(e)

    def getClipDialog(self, algorithm: Line.ClipAlgorithm):
        def f():
            text, ok = QInputDialog().getText(self, f"Clip", "id x0 y0 x1 x2", echo=QLineEdit.Normal)
            if not ok or not text:
                return
            try:
                args = text.split()
                self.canvas.clipElement(
                    args[0], int(args[1]), int(args[2]), int(args[3]), int(args[4]), algorithm)
            except Exception as e:
                print(e)
        return f

    def initMain(self):
        mainWidget = QWidget(self)
        self.setCentralWidget(mainWidget)
        horizonLayout = QHBoxLayout(mainWidget)

        # Toolbar
        self.initToolBar()
        horizonLayout.addLayout(self.toolBar)

        # Canvas
        horizonLayout.addWidget(self.canvas, alignment=Qt.AlignTop)

        # Spacing
        horizonLayout.addSpacerItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Expanding))

        # List
        self.canvas.listWidget.setFixedWidth(200)
        horizonLayout.addWidget(self.canvas.listWidget)

    def initToolBar(self):
        self.toolBar = QGridLayout()
        self.toolBar.setVerticalSpacing(5)
        self.toolBar.setHorizontalSpacing(5)
        col = 0
        widthFull = 3

        # Canvas
        self.toolBar.addWidget(QLabel("Canvas"), col, 0, 1, widthFull)
        col += 1

        # Clear
        def bClearFunc():
            mBox = QMessageBox()
            mBox.setText("The canvas will be cleared.")
            mBox.setInformativeText("Are you sure?")
            mBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            mBox.setDefaultButton(QMessageBox.No)
            if mBox.exec_() == QMessageBox.Yes:
                self.resetSize(*self.size)
        bClear = QPushButton("Clear")
        bClear.clicked.connect(bClearFunc)
        self.toolBar.addWidget(bClear, col, 0, 1, widthFull)
        col += 1

        # Delete
        def bDeleteFunc():
            if self.canvas.selecting:
                self.canvas.delElement(self.canvas.selecting.element.id)
        bDelete = QPushButton("Delete")
        bDelete.clicked.connect(bDeleteFunc)
        self.toolBar.addWidget(bDelete, col, 0, 1, widthFull)
        col += 1

        # Primitives
        self.toolBar.addWidget(QLabel("Primitive"), col, 0, 1, widthFull)
        col += 1

        def getPrimitiveButton(a: Acting, algo: Curve.Algorithm = None):
            text = ""
            if algo:
                text = f"{algo.name} {a.name}"
            else:
                text = f"{a.name}"
            ret = QPushButton(text)
            ret.setCheckable(True)
            return ret

        self.bLine = getPrimitiveButton(Acting.Line)
        self.bPolygon = getPrimitiveButton(Acting.Polygon)
        self.bEllipse = getPrimitiveButton(Acting.Ellipse)
        self.bCurveBezier = getPrimitiveButton(Acting.Curve, Curve.Algorithm.Bezier)
        self.bCurveBSpline = getPrimitiveButton(Acting.Curve, Curve.Algorithm.B_spline)

        def getTransformButton(a: Acting):
            ret = QPushButton(a.name)
            ret.setCheckable(True)
            return ret

        self.bTranslate = getTransformButton(Acting.Translate)
        self.bRotate = getTransformButton(Acting.Rotate)
        self.bScale = getTransformButton(Acting.Scale)
        self.bClip = getTransformButton(Acting.Clip)

        buttonList = [
            self.bLine, self.bPolygon, self.bEllipse, self.bCurveBezier, self.bCurveBSpline,
            self.bTranslate, self.bRotate, self.bScale, self.bClip
        ]

        self.toolBar.addWidget(self.bLine, col, 0, 1, widthFull)
        col += 1

        self.toolBar.addWidget(self.bPolygon, col, 0, 1, widthFull)
        col += 1

        self.toolBar.addWidget(self.bEllipse, col, 0, 1, widthFull)
        col += 1

        self.toolBar.addWidget(self.bCurveBezier, col, 0, 1, widthFull)
        col += 1

        self.toolBar.addWidget(self.bCurveBSpline, col, 0, 1, widthFull)
        col += 1

        def getPrimitiveButtonFunc(s, a: Acting, algo: Curve.Algorithm = None):
            def f(b: bool):
                if not b:
                    self.canvas.pointList = []
                    self.updateActingStatus(Acting.Free)
                    return
                if algo:
                    self.curveAlgorithm = algo
                for button in buttonList:
                    if button != s and button.isChecked():
                        button.toggle()
                self.canvas.clearSelection()
                self.updateActingStatus(a)
                self.canvas.pointList = []
            return f
        self.bLine.toggled.connect(getPrimitiveButtonFunc(self.bLine, Acting.Line))
        self.bPolygon.toggled.connect(getPrimitiveButtonFunc(self.bPolygon, Acting.Polygon))
        self.bEllipse.toggled.connect(getPrimitiveButtonFunc(self.bEllipse, Acting.Ellipse))
        self.bCurveBezier.toggled.connect(getPrimitiveButtonFunc(
            self.bCurveBezier, Acting.Curve, Curve.Algorithm.Bezier))
        self.bCurveBSpline.toggled.connect(getPrimitiveButtonFunc(
            self.bCurveBSpline, Acting.Curve, Curve.Algorithm.B_spline))

        # Transform
        self.toolBar.addWidget(QLabel("Transform"), col, 0, 1, widthFull)
        col += 1

        def getTransformButtonFunc(s, a: Acting):
            def f(b: bool):
                if not b:
                    self.canvas.pointList = []
                    self.updateActingStatus(Acting.Free)
                    return
                for button in buttonList:
                    if button != s and button.isChecked():
                        button.toggle()
                self.updateActingStatus(a)
                self.canvas.pointList = []
            return f

        self.bTranslate.toggled.connect(getTransformButtonFunc(self.bTranslate, Acting.Translate))
        self.bRotate.toggled.connect(getTransformButtonFunc(self.bRotate, Acting.Rotate))
        self.bScale.toggled.connect(getTransformButtonFunc(self.bScale, Acting.Scale))
        self.bClip.toggled.connect(getTransformButtonFunc(self.bClip, Acting.Clip))

        self.toolBar.addWidget(self.bTranslate, col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(self.bRotate, col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(self.bScale, col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(self.bClip, col, 0, 1, widthFull)
        col += 1

        # Color
        self.toolBar.addWidget(QLabel("Color"), col, 0, 1, widthFull)
        col += 1
        colors = [
            [(0, 0, 0), (85, 85, 85), (170, 170, 170)],
            [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
            [(0, 255, 255), (255, 0, 255), (255, 255, 0)],
            [(223, 96, 85), (96, 211, 148), (170, 246, 231)],
            [(203, 144, 77), (223, 203, 116), (195, 233, 145)],
            [(180, 206, 179), (219, 211, 201), (250, 212, 216)],
        ]

        def getSetColor(main, r: int, g: int, b: int):
            def f():
                return main.setColor(r, g, b)
            return f

        for cs in colors:
            for i in range(len(cs)):

                b1 = QPushButton(u"\u25A0")
                b1.setStyleSheet(f"QPushButton {{color:rgb({cs[i][0]},{cs[i][1]},{cs[i][2]});}}")
                b1.clicked.connect(getSetColor(self, *cs[i]))
                self.toolBar.addWidget(b1, col, i, 1, 1)

            col += 1

        # Spacer
        self.toolBar.addItem(
            QSpacerItem(0, 0, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Expanding),
            col, 0, 1, widthFull)

    def setColor(self, r: int, g: int, b: int):
        self.color = (r, g, b)
        self.colorStatusLabel.setText(f"Color: ({r},{g},{b})")

    def pickColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            c = color.getRgb()
            self.setColor(c[0], c[1], c[2])

    def addElement(self, primitive: Primitive):
        self.canvas.addElement(Element(self.getNewID(), primitive, self.color))

    def delElement(self, id: str):
        self.canvas.delElement(id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
