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

        steps = 1

        for i in range(npoints-1):
            dx = abs(points[i+1][0]-points[i][0])
            dy = abs(points[i+1][1]-points[i][1])
            steps += round((dx + dy) * 3)

        ret = []
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
        points = self.points
        ret = []

        npoints = len(points)
        if npoints < 4:
            return self.render_Bezier(points)

        p0 = points[0]
        p1 = points[1]
        p2 = points[2]
        p3 = points[3]

        x1 = p1[0]
        y1 = p1[1]
        x2 = (p1[0] + p2[0]) / 2
        y2 = (p1[1] + p2[1]) / 2
        x4 = (2 * p2[0] + p3[0]) / 3
        y4 = (2 * p2[1] + p3[1]) / 3
        x3 = (x2 + x4) / 2
        y3 = (y2 + y4) / 2

        ret += self.render_Bezier([
            (points[0][0], points[0][1]),
            (x1, y1),
            (x2, y2),
            (x3, y3)
        ])

        for i in range(2, npoints - 4):
            p1 = p2
            p2 = p3
            p3 = points[i + 2]
            x1 = x4
            y1 = y4
            x2 = (p1[0] + 2 * p2[0]) / 3
            y2 = (p1[1] + 2 * p2[1]) / 3
            x4 = (2 * p2[0] + p3[0]) / 3
            y4 = (2 * p2[1] + p3[1]) / 3

            x3_s = x3
            y3_s = y3

            x3 = (x2 + x4) / 2
            y3 = (y2 + y4) / 2

            ret += self.render_Bezier([
                (x3_s, y3_s),
                (x1, y1),
                (x2, y2),
                (x3, y3)
            ])

        p1 = p2
        p2 = p3
        p3 = points[npoints-2]
        x1 = x4
        y1 = y4
        x2 = (p1[0] + 2 * p2[0]) / 3
        y2 = (p1[1] + 2 * p2[1]) / 3
        x4 = (p2[0] + p3[0]) / 2
        y4 = (p2[1] + p3[1]) / 2
        x3_s = x3
        y3_s = y3
        x3 = (x2 + x4) / 2
        y3 = (y2 + y4) / 2

        ret += self.render_Bezier([
            (x3_s, y3_s),
            (x1, y1),
            (x2, y2),
            (x3, y3)
        ])

        p2 = p3
        p3 = points[npoints-1]
        x1 = x4
        y1 = y4
        x2 = p2[0]
        y2 = p2[1]
        x3_s = x3
        y3_s = y3
        x3 = p3[0]
        y3 = p3[1]

        ret += self.render_Bezier([
            (x3_s, y3_s),
            (x1, y1),
            (x2, y2),
            (x3, y3)
        ])

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
