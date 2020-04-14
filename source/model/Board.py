from typing import Dict
from .Utils import *
from .Primitive import Primitive
import numpy as np
from PIL import Image


class Board():
    def __init__(self, width: int, height: int):
        if height <= 0 or width <= 0:
            raise ValueError("Board size should be greater to 0")
        self.height = height
        self.width = width
        self.color = ColorTable.BLACK
        self.primitives: Dict[str, (Primitive, Color)] = {}

    def setColor(self, color: Color):
        self.color = color

    def reset(self, width: int, height: int):
        self.__init__(width, height)

    def render(self):
        canvas = np.zeros([self.height, self.width, 3], np.uint8)
        canvas.fill(255)
        for primitive, color in self.primitives.values():
            for p in primitive.render():
                if p[0] >= 0 and p[0] < self.width and p[1] >= 0 and p[1] < self.height:
                    canvas[p[1]][p[0]] = color
        return canvas

    def addPrimitive(self, id: str, p: Primitive):
        self.primitives[id] = (p, self.color)

    def removePrimitive(self, id: str):
        try:
            del self.primitives[id]
        except KeyError:
            pass

    def translate(self, id: str, dx: int, dy: int):
        if self.primitives.get(id):
            self.primitives[id][0].translate(dx, dy)

    def rotate(self, id: str, x: int, y: int, r: int) -> None:
        if self.primitives.get(id):
            self.primitives[id][0].rotate(x, y, r)

    def scale(self, id: str, x: int, y: int, s: float) -> None:
        if self.primitives.get(id):
            self.primitives[id][0].scale(x, y, s)

    def show(self):
        Image.fromarray(self.render()).show()

    def save(self, path: str):
        Image.fromarray(self.render()).save(path)
