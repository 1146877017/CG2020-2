from .Primitive import Primitive
from .Utils import *
from enum import Enum


class Line(Primitive):
    class Algorithm(Enum):
        DDA = 1
        Bresenham = 2

    class ClipAlgorithm(Enum):
        Cohen_Sutherland = 1
        Liang_Barsky = 2

    def __init__(self, x0: int, y0: int, x1: int, y1: int, algorithm: Algorithm):
        super().__init__()
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

    def _render(self) -> List[Point]:
        if self.algorithm == self.Algorithm.DDA:
            return self.render_DDA()
        elif self.algorithm == self.Algorithm.Bresenham:
            return self.render_Bresenham()
        else:
            raise TypeError("Invalid line algorithm")

    def _translate(self, dx: int, dy: int) -> None:
        self.x0, self.y0 = self.translatePoint(self.x0, self.y0, dx, dy)
        self.x1, self.y1 = self.translatePoint(self.x1, self.y1, dx, dy)

    def _rotate(self, x: int, y: int, r: int) -> None:
        self.x0, self.y0 = self.rotatePoint(self.x0, self.y0, x, y, r)
        self.x1, self.y1 = self.rotatePoint(self.x1, self.y1, x, y, r)

    def _scale(self, x: int, y: int, s: float) -> None:
        self.x0, self.y0 = self.scalePoint(self.x0, self.y0, x, y, s)
        self.x1, self.y1 = self.scalePoint(self.x1, self.y1, x, y, s)

    def clip_Cohen_Sutherland(self, cx0: int, cy0: int, cx1: int, cy1: int) -> bool:
        INSIDE = 0
        LEFT = 1
        RIGHT = 2
        BOTTOM = 4
        TOP = 8

        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        xmin = cx0
        xmax = cx1
        ymin = cy0
        ymax = cy1

        def encode(x: int, y: int) -> int:
            c = INSIDE
            if x < xmin:
                c |= LEFT
            elif x > xmax:
                c |= RIGHT
            if y < ymin:
                c |= BOTTOM
            elif y > ymax:
                c |= TOP

            return c

        code0 = encode(x0, y0)
        code1 = encode(x1, y1)

        accept = False
        while True:
            if not(code0 | code1):
                accept = True
                break
            elif code0 & code1:
                break
            else:
                x = 0.0
                y = 0.0
                codet = max(code1, code0)
                if codet & TOP:
                    x = x0 + (x1-x0)*(ymax-y0)/(y1-y0)
                    y = ymax
                elif codet & BOTTOM:
                    x = x0 + (x1-x0)*(ymin-y0)/(y1-y0)
                    y = ymin
                elif codet & RIGHT:
                    y = y0 + (y1-y0)*(xmax-x0)/(x1-x0)
                    x = xmax
                elif codet & LEFT:
                    y = y0 + (y1-y0)*(xmin-x0)/(x1-x0)
                    x = xmin

                if codet == code0:
                    x0 = x
                    y0 = y
                    code0 = encode(x0, y0)
                else:
                    x1 = x
                    y1 = y
                    code1 = encode(x1, y1)
        if accept:
            self.x0 = x0
            self.y0 = y0
            self.x1 = x1
            self.y1 = y1
        return accept

    def clip(self, x0: int, y0: int, x1: int, y1: int, algorithm: ClipAlgorithm) -> bool:
        if algorithm == self.ClipAlgorithm.Cohen_Sutherland:
            return self.clip_Cohen_Sutherland(x0, y0, x1, y1)

    def __str__(self):
        return f"Line from ({self.x0}, {self.y0}), to ({self.x1}, {self.y1}), using {self.algorithm}"
