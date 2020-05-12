from cg_algorithms import *

import sys

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
    QGraphicsView,
    QGraphicsItem,
    QGridLayout)

from PyQt5.QtGui import QIcon, QColor


class Element(QGraphicsItem):
    def __init__(self, id: str, primitive: Primitive, color: Color, parent=None):
        super().__init__(parent=parent)
        self.id = id
        self.primitive = primitive
        self.color = color

    def __str__(self):
        return f"{self.id} {self.primitive.type.name} ({self.color[0]},{self.color[1]},{self.color[2]})"


class MainCanvas(QGraphicsView):
    def __init__(self,  parent=None):
        super().__init__(parent=parent)
        self.listWidget = QListWidget(parent)
        self.elements = {}

    def addElement(self, e: Element):
        self.elements[e.id] = e
        self.listWidget.addItem(e.__str__())

    def delElement(self, id: str):
        try:
            del self.elements[id]
        except KeyError:
            pass


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.color = (0, 0, 0)
        self.size = (0, 0)
        self.canvas = MainCanvas(self)

        self.initUI()

        self.setColor(0, 0, 0)
        self.setSize(500, 500)

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

        self.canvas.addElement(Element("fuck", Line(
            1, 1, 100, 100, Line.Algorithm.DDA), self.color))

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
        horizonLayout.addWidget(self.canvas)

        # List
        self.canvas.listWidget.setFixedWidth(150)
        horizonLayout.addWidget(self.canvas.listWidget)

    def initToolBar(self):
        self.toolBar = QGridLayout()
        self.toolBar.addWidget(QLabel("Tools"))

    def setColor(self, r: int, g: int, b: int):
        self.color = (r, g, b)
        self.colorStatusLabel.setText(f"Color: ({r}, {g}, {b})")

    def pickColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            c = color.getRgb()
            self.setColor(c[0], c[1], c[2])

    def setSize(self, width: int, height: int):
        if width < 100 or width > 1000 or height < 100 or height > 1000:
            return
        self.size = (width, height)
        self.sizeStatusLabel.setText(f"Size: ({width}, {height})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
