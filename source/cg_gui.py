from cg_algorithms import *

import sys

from PyQt5.QtCore import Qt, QRectF

from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    qApp,
    QApplication,
    QMenu,
    QLabel,
    QColorDialog,
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
    QLayout)


from PyQt5.QtGui import QIcon, QColor, QPainter, QPalette


class Element(QGraphicsItem):
    def __init__(self, id: str, primitive: Primitive, color: Color, parent=None):
        super().__init__(parent=parent)
        self.id = id
        self.primitive = primitive
        self.color = color
        self.listItem = QListWidgetItem(id + " " + self.__str__())

    def __str__(self):
        return self.primitive.__str__()

    def paint(self, painter: QPainter, option, widget=None):
        c = QColor()
        c.setRgb(*self.color)
        painter.setPen(c)
        for p in self.primitive.render():
            painter.drawPoint(*p)

    def boundingRect(self) -> QRectF:
        return QRectF(*self.primitive.boundingRect())


class MainCanvas(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent=parent)
        self.listWidget = QListWidget(parent)
        self.scene = scene
        self.elements = {}

    def addElement(self, e: Element):
        self.elements[e.id] = e
        self.scene.addItem(e)
        self.listWidget.addItem(e.listItem)

    def delElement(self, id: str):
        try:
            e = self.elements[id]
            self.scene.removeItem(e)
            self.listWidget.takeItem(
                self.listWidget.indexFromItem(e.listItem).row())
            del self.elements[id]

        except KeyError:
            pass

    def clearElement(self):
        for key in self.elements:
            self.delElement(key)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.color = (0, 0, 0)
        self.size = (0, 0)
        self.scene = QGraphicsScene(self)
        self.canvas = MainCanvas(self.scene, self)

        self.initUI()

        self.id = 0
        self.setColor(0, 0, 0)
        self.setSize(500, 500)

        self.addElement(Line(100, 400, 300, 200, Line.Algorithm.DDA))
        self.addElement(Line(200, 200, 400, 400, Line.Algorithm.DDA))
        self.setColor(96, 211, 148)
        self.addElement(Ellipse(200, 100, 350, 460))

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
        self.sizeStatusLabel = QLabel("", self)
        self.statusBar().insertPermanentWidget(0, self.sizeStatusLabel)
        self.infoStatusLabel = QLabel("", self)
        self.statusBar().insertPermanentWidget(1, self.infoStatusLabel)
        self.colorStatusLabel = QLabel("", self)
        self.statusBar().insertPermanentWidget(2, self.colorStatusLabel)

    def initMenu(self):
        self.initFileMenu()
        self.initCanvasMenu()
        self.initPrimitiveMenu()
        self.initTransformMenu()

    def initFileMenu(self):
        fileMenu = self.menuBar().addMenu('&File')

        # Load action
        loadAction = QAction('&Load', self)
        loadAction.setStatusTip('Load from script')
        loadAction.setShortcut('Ctrl+L')
        fileMenu.addAction(loadAction)

        # Save action
        saveAction = QAction('&Save', self)
        saveAction.setStatusTip('Save the canvas')
        saveAction.setShortcut('Ctrl+S')
        fileMenu.addAction(saveAction)

        # Exit action
        exitAction = QAction('&Exit', self)
        exitAction.setStatusTip('Exit application')
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

    def initCanvasMenu(self):
        canvasMenu = self.menuBar().addMenu('&Canvas')

        # Reset action
        resetAction = QAction('&Reset', self)
        resetAction.setStatusTip('Reset the canvas')
        resetAction.setShortcut('Ctrl+R')
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
        canvasMenu.addAction(deleteAction)

    def initPrimitiveMenu(self):
        primitiveMenu = self.menuBar().addMenu('&Primitive')

        # Line
        lineMenu = QMenu('&Line', self)
        # DDA
        lineActionDDA = QAction('&DDA', self)
        lineActionDDA.setStatusTip('Draw line with DDA algorithm')
        lineMenu.addAction(lineActionDDA)
        # Bresenham
        lineActionBresenham = QAction('&Bresenham', self)
        lineActionBresenham.setStatusTip('Draw line with Bresenham algorithm')
        lineMenu.addAction(lineActionBresenham)
        primitiveMenu.addMenu(lineMenu)

        # Polygon
        polygonMenu = QMenu('&Polygon', self)
        # DDA
        polygonActionDDA = QAction('&DDA', self)
        polygonActionDDA.setStatusTip('Draw polygon with DDA algorithm')
        polygonMenu.addAction(polygonActionDDA)
        # Bresenham
        polygonActionBresenham = QAction('&Bresenham', self)
        polygonActionBresenham.setStatusTip(
            'Draw polygon with Bresenham algorithm')
        polygonMenu.addAction(polygonActionBresenham)
        primitiveMenu.addMenu(polygonMenu)

        # Ellipse
        ellipseAction = QAction('&Ellipse', self)
        ellipseAction.setStatusTip('Draw ellipse')
        primitiveMenu.addAction(ellipseAction)

        # Curve
        curveAction = QAction('&Curve', self)
        curveAction.setStatusTip('Draw curve')
        primitiveMenu.addAction(curveAction)

    def initTransformMenu(self):
        transformMenu = self.menuBar().addMenu('&Transform')

        # Translate
        translateAction = QAction('&Translate', self)
        translateAction.setStatusTip('Translate primitive')
        transformMenu.addAction(translateAction)

        # Rotate
        rotateAction = QAction('&Rotate', self)
        rotateAction.setStatusTip('Rotate any primitive')
        transformMenu.addAction(rotateAction)

        # Scale
        scaleAction = QAction('&Scale', self)
        scaleAction.setStatusTip('Scale any primitive')
        transformMenu.addAction(scaleAction)

        # Clip
        clipMenu = QMenu('&Clip', self)
        # Cohen-Sutherland
        clipActionCohen = QAction('&Cohen-Sutherland', self)
        clipActionCohen.setStatusTip(
            'Clip line with Cohen-Sutherland algorithm')
        clipMenu.addAction(clipActionCohen)
        # Liang-Barsky
        clipActionLiang = QAction('&Liang-Barsky', self)
        clipActionLiang.setStatusTip('Clip line with Liang-Barsky algorithm')
        clipMenu.addAction(clipActionLiang)
        transformMenu.addMenu(clipMenu)

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
        horizonLayout.addSpacerItem(QSpacerItem(
            0, 0, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Expanding))

        # List
        self.canvas.listWidget.setFixedWidth(200)
        horizonLayout.addWidget(self.canvas.listWidget)

    def initToolBar(self):
        self.toolBar = QGridLayout()
        self.toolBar.setVerticalSpacing(5)
        self.toolBar.setHorizontalSpacing(5)
        col = 0
        widthFull = 3

        # Primitives
        self.toolBar.addWidget(QLabel("Primitive"), col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(QPushButton("Line"), col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(QPushButton("Polygon"), col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(QPushButton("Ellipse"), col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(QPushButton("Curve"), col, 0, 1, widthFull)
        col += 1

        # Transform
        self.toolBar.addWidget(QLabel("Transform"), col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(QPushButton("Translate"), col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(QPushButton("Rotate"), col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(QPushButton("Scale"), col, 0, 1, widthFull)
        col += 1
        self.toolBar.addWidget(QPushButton("Clip"), col, 0, 1, widthFull)
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
                b1.setStyleSheet(
                    f"QPushButton {{color:rgb({cs[i][0]},{cs[i][1]},{cs[i][2]});}}")
                b1.clicked.connect(getSetColor(self, *cs[i]))
                self.toolBar.addWidget(b1, col, i, 1, 1)

            col += 1

        # Spacer
        self.toolBar.addItem(QSpacerItem(
            0, 0, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Expanding), col, 0, 1, widthFull)

    def setColor(self, r: int, g: int, b: int):
        self.color = (r, g, b)
        self.colorStatusLabel.setText(f"Color: ({r},{g},{b})")

    def pickColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            c = color.getRgb()
            self.setColor(c[0], c[1], c[2])

    def setSize(self, width: int, height: int):
        if width < 100 or width > 1000 or height < 100 or height > 1000:
            return
        self.size = (width, height)
        self.scene.setSceneRect(0, 0, width, height)
        self.scene.addRect(-1, -1, width+2, height+2)
        self.canvas.setFixedSize(width*1.05, height*1.05)
        self.adjustSize()
        self.sizeStatusLabel.setText(f"Size: ({width},{height})")

    def getNewID(self) -> str:
        self.id += 1
        return str(self.id)

    def addElement(self, primitive: Primitive):
        self.canvas.addElement(Element(self.getNewID(), primitive, self.color))

    def delElement(self, id: str):
        self.canvas.delElement(id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
