from .Utils import *
from .Primitive import Primitive
from typing import List
from .Line import Line


class Curve(Primitive):
    class Algorithm(Enum):
        Bezier = 1
        B_spline = 2

    def __init__(self, points: List[Point], algorithm: Algorithm):
        super().__init__()
        if len(points) <= 1:
            raise ValueError("Points number should be greater than 1")
        self.points = points
        self.algorithm = algorithm

    def render_Bezier(self, points) -> List[Point]:
        npoints = len(points)
        xs = [0] * npoints
        ys = [0] * npoints
        facts = [1] * (npoints)
        for i in range(1, npoints):
            facts[i] = facts[i-1] * i

        for i in range(npoints):
            base = facts[npoints-1] / (facts[i] * facts[npoints-1-i])
            xs[i] = base * points[i][0]
            ys[i] = base * points[i][1]

        ret = []
        steps = 10000
        for s in range(steps+1):
            u = s / steps
            x = 0
            y = 0
            for i in range(npoints):
                x += xs[i] * (u ** i) * ((1-u) ** (npoints-1-i))
                y += ys[i] * (u ** i) * ((1-u) ** (npoints-1-i))
            ret.append((round(x), round(y)))

        return ret

    def render_B_spline(self) -> List[Point]:
        ret = []
        return ret

    def _render(self) -> List[Point]:
        if self.algorithm == self.Algorithm.Bezier:
            return self.render_Bezier(self.points)
        elif self.algorithm == self.Algorithm.B_spline:
            return self.render_B_spline()
        else:
            raise TypeError("Invalid curve algorithm")

    def _translate(self, dx: int, dy: int) -> None:
        for i in range(len(self.points)):
            self.points[i] = self.translatePoint(
                self.points[i][0], self.points[i][1], dx, dy)

    def _rotate(self, x: int, y: int, r: int) -> None:
        for i in range(len(self.points)):
            self.points[i] = self.rotatePoint(
                self.points[i][0], self.points[i][1], x, y, r)

    def _scale(self, x: int, y: int, s: float) -> None:
        for i in range(len(self.points)):
            self.points[i] = self.scalePoint(
                self.points[i][0], self.points[i][1], x, y, s)

    def __str__(self):
        return f"Curve"
