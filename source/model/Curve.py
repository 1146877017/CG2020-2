from .Utils import *
from .Primitive import Primitive
from typing import List
from .Line import Line


class Curve(Primitive):
    class Algorithm(Enum):
        Bezier = 1
        B_spline = 2

    def __init__(self, points: List[Point], algorithm: Algorithm):
        if not points:
            raise ValueError("Points number should be greater than 0")
        self.points = points
        self.algorithm = algorithm

    def render_Bezier(self) -> List[Point]:
        ret = []
        return ret

    def render_B_spline(self) -> List[Point]:
        ret = []
        return ret

    def render(self) -> List[Point]:
        if self.algorithm == self.Algorithm.Bezier:
            return self.render_Bezier()
        elif self.algorithm == self.Algorithm.B_spline:
            return self.render_B_spline()
        else:
            raise TypeError("Invalid curve algorithm")

    def translate(self, dx: int, dy: int) -> None:
        for i in range(len(self.points)):
            self.points[i] = self.translatePoint(
                self.points[i][0], self.points[i][1], dx, dy)

    def rotate(self, x: int, y: int, r: int) -> None:
        for i in range(len(self.points)):
            self.points[i] = self.rotatePoint(
                self.points[i][0], self.points[i][1], x, y, r)

    def scale(self, x: int, y: int, s: float) -> None:
        for i in range(len(self.points)):
            self.points[i] = self.scalePoint(
                self.points[i][0], self.points[i][1], x, y, s)

    def __str__(self):
        return f"Curve"
