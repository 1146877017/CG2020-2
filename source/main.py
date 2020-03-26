from model.Utils import *
from model.Line import Line
from model.Board import Board
import numpy as np
from PIL import Image

if __name__ == "__main__":
    board = Board(100, 200)

    board.addPrimitive(
        1,
        Line(3, 2, 90, 170, Line.Algorithm.Bresenham)
    )

    board.setColor(ColorTable.RED)

    board.addPrimitive(
        2,
        Line(50, 2, 20, 130, Line.Algorithm.Bresenham)
    )

    board.translate(2, 50, 0)

    board.show()
    # board.save("test.bmp")
