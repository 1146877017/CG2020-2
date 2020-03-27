from model import *
import numpy as np
from PIL import Image

if __name__ == "__main__":
    board: Board = Board(400, 400)

    # board.addPrimitive(
    #     1,
    #     Polygon([(40, 20), (50, 50), (30, 100),
    #              (10, 30), (20, 10)], Line.Algorithm.DDA)
    # )

    board.addPrimitive(
        1,
        Ellipse(150, 20, 20, 300)
    )

    board.setColor(ColorTable.RED)

    board.addPrimitive(
        2,
        Ellipse(150, 20, 20, 300)
    )

    # board.translate(2, 100, 100)
    # board.scale(2, 0, 0, 0.5)
    # board.rotate(2, 100, 200, 180)

    board.show()
    # board.save("test.bmp")
