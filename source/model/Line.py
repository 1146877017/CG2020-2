from .Primitive import Primitive
from .Utils import *
from enum import Enum



class Line(Primitive):
    class Algorithm(Enum):
        DDA = 1
        Bresenham = 2

    def __init__(self, x0: int, y0: int, x1: int, y1: int, algorithm: Algorithm):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.algorithm = algorithm

    def render_DDA(self) -> List[Point]:
        ret = []
        dx0 = self.x1 - self.x0
        dy0 = self.y1 - self.y0
        length = abs(dx0) if abs(dx0) > abs(dy0) else abs(dy0)
        dx = dx0 / length
        dy = dy0 / length
        x = self.x0
        y = self.y0
        for i in range(length + 1):
            ret.append((round(x), round(y)))
            x += dx
            y += dy
        return ret

    def render_Bresenham(self) -> List[Point]:
        ret = []
        dx0 = abs(self.x1 - self.x0)
        dy0 = abs(self.y1 - self.y0)
        sx = -1 if self.x0 > self.x1 else 1
        sy = -1 if self.y0 > self.y1 else 1
        x, y = self.x0, self.y0
        if dx0 > dy0:
            err = dx0 / 2.0
            while x != self.x1:
                ret.append((x, y))
                err -= dy0
                if err < 0:
                    y += sy
                    err += dx0
                x += sx
        else:
            err = dy0 / 2.0
            while y != self.y1:
                ret.append((x, y))
                err -= dx0
                if err < 0:
                    x += sx
                    err += dy0
                y += sy
        ret.append((x, y))
        return ret

    def render(self) -> List[Point]:
        if self.algorithm == self.Algorithm.DDA:
            return self.render_DDA()
        elif self.algorithm == self.Algorithm.Bresenham:
            return self.render_Bresenham()
        else:
            raise TypeError("Invalid line algorithm")

    def translate(self, dx: int, dy: int) -> None:
        self.x0, self.y0 = self.translatePoint(self.x0, self.y0, dx, dy)
        self.x1, self.y1 = self.translatePoint(self.x1, self.y1, dx, dy)

    def rotate(self, x: int, y: int, r: int) -> None:
        self.x0, self.y0 = self.rotatePoint(self.x0, self.y0, x, y, r)
        self.x1, self.y1 = self.rotatePoint(self.x1, self.y1, x, y, r)

    def scale(self, x: int, y: int, s: float) -> None:
        self.x0, self.y0 = self.scalePoint(self.x0, self.y0, x, y, s)
        self.x1, self.y1 = self.scalePoint(self.x1, self.y1, x, y, s)

    def __str__(self):
        return f"Line from ({self.x0}, {self.y0}), to ({self.x1}, {self.y1}), using {self.algorithm}"
