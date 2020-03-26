from .Primitive import Primitive
from .Utils import *
from enum import Enum


class Ellipse(Primitive):

    def __init__(self, x0: int, y0: int, x1: int, y1: int):
        self.cx = round((x0 + x1) / 2)
        self.cy = round((y0 + y1) / 2)
        self.rx = round(abs(x1 - x0) / 2)
        self.ry = round(abs(y1 - y0) / 2)

    def render(self) -> List[Point]:
        def draw4(l: List[Point], cx, cy, x, y):
            l.append((round(cx + x), round(cy + y)))
            l.append((round(cx + x), round(cy - y)))
            l.append((round(cx - x), round(cy + y)))
            l.append((round(cx - x), round(cy - y)))

        ret = []

        x = self.rx
        y = 0

        taa = self.rx ** 2
        t2aa = 2 * taa
        t4aa = 2 * t2aa

        tbb = self.ry ** 2
        t2bb = 2 * tbb
        t4bb = 2 * t2bb

        t2abb = self.rx * t2bb
        t2bbx = t2bb * x
        tx = x

        d1 = round(t2bbx * (x - 1) + tbb / 2 + t2aa * (1 - tbb))

        while t2bb * tx > t2aa * y:
            draw4(ret, self.cx, self.cy, x, y)
            if d1 < 0:
                y += 1
                d1 += (t4aa * y + t2aa)
                tx = x - 1
            else:
                x -= 1
                y += 1
                d1 = d1 - t4bb * x + t4aa * y + t2aa
                tx = x

        d2 = round(t2bb * (x ** 2 + 1) - t4bb * x +
                   t2aa * (y ** 2 + y - tbb) + taa / 2)

        while x >= 0:
            draw4(ret, self.cx, self.cy, x, y)
            if d2 < 0:
                x -= 1
                y += 1
                d2 += (t4aa * y - t4bb * x + t2bb)
            else:
                x -= 1
                d2 = d2 - t4bb * x + t2bb

        return ret

    def translate(self, dx: int, dy: int) -> None:
        self.cx, self.cy = self.translatePoint(self.cx, self.cy, dx, dy)

    def rotate(self, x: int, y: int, r: int) -> None:
        self.cx, self.cy = self.rotatePoint(self.cx, self.cy, x, y, r)

    def scale(self, x: int, y: int, s: float) -> None:
        self.cx, self.cy = self.scalePoint(self.cx, self.cy, x, y, s)
        self.rx = round(self.rx * s)
        self.ry = round(self.ry * s)

    def __str__(self):
        return f"Ellipse at ({self.cx}, {self.cy}), {self.rx}, {self.ry}"
