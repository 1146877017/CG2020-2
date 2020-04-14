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
        prim = self.primitives.get(id)
        if prim:
            prim[0].translate(dx, dy)

    def rotate(self, id: str, x: int, y: int, r: int) -> None:
        prim = self.primitives.get(id)
        if prim:
            prim[0].rotate(x, y, r)

    def scale(self, id: str, x: int, y: int, s: float) -> None:
        prim = self.primitives.get(id)
        if prim:
            prim[0].scale(x, y, s)

    def clip(self, id: str, x0: int, y0: int, x1: int, y1: int, algorithm) -> None:
        prim = self.primitives.get(id)
        if prim:
            op = getattr(prim[0], "clip", None)
            if op:
                accept = prim[0].clip(x0, y0, x1, y1, algorithm)
                if not accept:
                    del self.primitives[id]

    def show(self):
        Image.fromarray(self.render()).show()

    def save(self, path: str):
        Image.fromarray(self.render()).save(path)
