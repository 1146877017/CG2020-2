from .Utils import *
from .Primitive import Primitive
from typing import List
from .Line import Line


class Polygon(Primitive):

    def __init__(self, points: List[Point], algorithm: Line.Algorithm):
        if not points:
            raise ValueError("Points number should be greater than 0")
        self.lines: List[Line] = []
        for i in range(len(points)):
            self.lines.append(
                Line(points[i-1][0], points[i-1][1], points[i][0], points[i][1], algorithm))

    def render(self) -> List[Point]:
        ret = []
        for line in self.lines:
            ret += line.render()
        return ret

    def translate(self, dx: int, dy: int) -> None:
        for line in self.lines:
            line.translate(dx, dy)

    def rotate(self, x: int, y: int, r: int) -> None:
        for line in self.lines:
            line.rotate(x, y, r)

    def scale(self, x: int, y: int, s: float) -> None:
        for line in self.lines:
            line.scale(x, y, s)

    def __str__(self):
        return f"Polygon"
