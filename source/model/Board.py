from typing import Dict
from .Utils import *
from .Primitive import Primitive
import numpy as np
from PIL import Image


class Board():
    def __init__(self, height: int, width: int):
        if height <= 0 or width <= 0:
            raise ValueError("Board size should be greater to 0")
        self.height = height
        self.width = width
        self.color = ColorTable.BLACK
        self.primitives: Dict[int, (Primitive, Color)] = {}

    def setColor(self, color: Color):
        self.color = color

    def reset(self, height: int, width: int):
        self.__init__(height, width)

    def render(self):
        canvas = np.zeros([self.height, self.width, 3], np.uint8)
        canvas.fill(255)
        for primitive, color in self.primitives.values():
            for p in primitive.render():
                if p[0] >= 0 and p[0] < self.height and p[1] >= 0 and p[1] < self.width:
                    canvas[p[0]][p[1]] = color
        return canvas

    def addPrimitive(self, id: int, p: Primitive):
        self.primitives[id] = (p, self.color)

    def removePrimitive(self, id: int):
        try:
            del self.primitives[id]
        except KeyError:
            pass

    def translate(self, id: int, dx: int, dy: int):
        if self.primitives.get(id):
            self.primitives[id][0].translate(dx, dy)

    def rotate(self, id: int, x: int, y: int, r: int) -> None:
        if self.primitives.get(id):
            self.primitives[id][0].rotate(x, y, r)

    def scale(self, id: int, x: int, y: int, s: float) -> None:
        if self.primitives.get(id):
            self.primitives[id][0].scale(x, y, s)

    def show(self):
        Image.fromarray(self.render()).show()

    def save(self, path: str):
        Image.fromarray(self.render()).save(path)
