from enum import Enum
from typing import Tuple, List
from abc import ABC, abstractmethod
from math import atan2, cos, sin, degrees, radians, sqrt


Point = Tuple[int, int]
Color = Tuple[int, int, int]


class ColorTable():
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)


class Primitive(ABC):
    class PType(Enum):
        line = 0
        polygon = 1
        ellipse = 2
        curve = 3

    def __init__(self, t: PType):
        self.saved = None
        self.type = t

    @abstractmethod
    def boundingRect(self):
        pass

    @abstractmethod
    def _render(self) -> List[Point]:
        pass

    def render(self) -> List[Point]:
        if not self.saved:
            self.saved = self._render()
        return self.saved

    @abstractmethod
    def _translate(self, dx: int, dy: int) -> None:
        pass

    @abstractmethod
    def _rotate(self, x: int, y: int, r: int) -> None:
        pass

    @abstractmethod
    def _scale(self, x: int, y: int, s: float) -> None:
        pass

    def translate(self, dx: int, dy: int) -> None:
        self.saved = None
        self._translate(dx, dy)

    def rotate(self, x: int, y: int, r: int) -> None:
        self.saved = None
        self._rotate(x, y, r)

    def scale(self, x: int, y: int, s: float) -> None:
        self.saved = None
        self._scale(x, y, s)

    def translatePoint(self, x0: int, y0: int, dx: int, dy: int) -> Point:
        return (round(x0+dx), round(y0+dy))

    def rotatePoint(self, x0: int, y0: int, x: int, y: int, r: int) -> Point:
        dx = x0 - x
        dy = y0 - y
        l = sqrt(dx**2+dy**2)
        degree = degrees(atan2(float(dy), float(dx)))
        radian = radians(degree + r)
        return (round(x+l*cos(radian)), round(y+l*sin(radian)))

    def scalePoint(self, x0: int, y0: int, x: int, y: int, s: float) -> Point:
        return (round(x0*s+(1-s)*x), round(y0*s+(1-s)*y))

    @abstractmethod
    def __str__(self):
        pass


class Line(Primitive):
    class Algorithm(Enum):
        DDA = 1
        Bresenham = 2

    class ClipAlgorithm(Enum):
        Cohen_Sutherland = 1
        Liang_Barsky = 2

    def __init__(self, x0: int, y0: int, x1: int, y1: int, algorithm: Algorithm):
        super().__init__(Primitive.PType.line)
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.algorithm = algorithm

    def boundingRect(self):
        x = (self.x0, self.x1)
        y = (self.y0, self.y1)
        return min(x)-1, min(y)-1, max(x)-min(x)+2, max(y)-min(y)+2

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
            self.x0 = int(x0)
            self.y0 = int(y0)
            self.x1 = int(x1)
            self.y1 = int(y1)
        return accept

    def clip_Liang_Barsky(self, cx0: int, cy0: int, cx1: int, cy1: int) -> bool:
        x1 = self.x0
        y1 = self.y0
        x2 = self.x1
        y2 = self.y1
        xmin = cx0
        xmax = cx1
        ymin = cy0
        ymax = cy1

        p1 = -(x2 - x1)
        p2 = -p1
        p3 = -(y2 - y1)
        p4 = -p3

        q1 = x1 - xmin
        q2 = xmax - x1
        q3 = y1 - ymin
        q4 = ymax - y1

        pos = [0.0] * 5
        pos[0] = 1.0
        neg = [0.0] * 5
        posind = 1
        negind = 1

        if (p1 == 0 and q1 < 0) or (p2 == 0 and q2 < 0) or (p3 == 0 and q3 < 0) or (p4 == 0 and q4 < 0):
            return False

        if p1 != 0:
            r1 = q1 / p1
            r2 = q2 / p2
            if p1 < 0:
                neg[negind] = r1
                pos[posind] = r2
            else:
                neg[negind] = r2
                pos[posind] = r1
            negind += 1
            posind += 1

        if p3 != 0:
            r3 = q3 / p3
            r4 = q4 / p4
            if p3 < 0:
                neg[negind] = r3
                pos[posind] = r4
            else:
                neg[negind] = r4
                pos[posind] = r3
            negind += 1
            posind += 1

        rn1 = max(neg[:negind])
        rn2 = min(pos[:posind])

        if rn1 > rn2:
            return False

        self.x0 = round(x1 + p2 * rn1)
        self.y0 = round(y1 + p4 * rn1)
        self.x1 = round(x1 + p2 * rn2)
        self.y1 = round(y1 + p4 * rn2)

        return True

    def clip(self, x0: int, y0: int, x1: int, y1: int, algorithm: ClipAlgorithm) -> bool:
        self.saved = None
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        if algorithm == self.ClipAlgorithm.Cohen_Sutherland:
            return self.clip_Cohen_Sutherland(x0, y0, x1, y1)
        elif algorithm == self.ClipAlgorithm.Liang_Barsky:
            return self.clip_Liang_Barsky(x0, y0, x1, y1)
        else:
            raise TypeError("Invalid clip algorithm")

    def __str__(self):
        return f"Line ({self.x0}, {self.y0})\u2192({self.x1}, {self.y1})"


class Polygon(Primitive):

    def __init__(self, points: List[Point], algorithm: Line.Algorithm):
        super().__init__(Primitive.PType.polygon)
        if not points:
            raise ValueError("Points number should be greater than 0")
        self.lines: List[Line] = []
        for i in range(len(points)):
            self.lines.append(
                Line(points[i-1][0], points[i-1][1], points[i][0], points[i][1], algorithm))

    def boundingRect(self):
        x = []
        y = []
        for l in self.lines:
            x0, y0, xl, yl = l.boundingRect()
            x.append(x0+1)
            x.append(x0+xl-1)
            y.append(y0+1)
            y.append(y0+yl-1)
        return min(x)-1, min(y)-1, max(x)-min(x)+2, max(y)-min(y)+2

    def _render(self) -> List[Point]:
        ret = []
        for line in self.lines:
            ret += line.render()
        return ret

    def _translate(self, dx: int, dy: int) -> None:
        for line in self.lines:
            line.translate(dx, dy)

    def _rotate(self, x: int, y: int, r: int) -> None:
        for line in self.lines:
            line.rotate(x, y, r)

    def _scale(self, x: int, y: int, s: float) -> None:
        for line in self.lines:
            line.scale(x, y, s)

    def __str__(self):
        return f"Polygon ({self.lines[0].x0}, {self.lines[0].y0})..."


class Ellipse(Primitive):

    def __init__(self, x0: int, y0: int, x1: int, y1: int):
        super().__init__(Primitive.PType.ellipse)
        self.cx = round((x0 + x1) / 2)
        self.cy = round((y0 + y1) / 2)
        self.rx = round(abs(x1 - x0) / 2)
        self.ry = round(abs(y1 - y0) / 2)

    def boundingRect(self):
        x = [self.cx - self.rx, self.cx + self.rx]
        y = [self.cy - self.ry, self.cy + self.ry]
        return min(x)-1, min(y)-1, max(x)-min(x)+2, max(y)-min(y)+2

    def _render(self) -> List[Point]:
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

    def _translate(self, dx: int, dy: int) -> None:
        self.cx, self.cy = self.translatePoint(self.cx, self.cy, dx, dy)

    def _rotate(self, x: int, y: int, r: int) -> None:
        self.cx, self.cy = self.rotatePoint(self.cx, self.cy, x, y, r)

    def _scale(self, x: int, y: int, s: float) -> None:
        self.cx, self.cy = self.scalePoint(self.cx, self.cy, x, y, s)
        self.rx = round(self.rx * s)
        self.ry = round(self.ry * s)

    def __str__(self):
        return f"Ellipse ({self.cx}\u00B1{self.rx}, {self.cy}\u00B1{self.ry})"


class Curve(Primitive):
    class Algorithm(Enum):
        Bezier = 1
        B_spline = 2

    def __init__(self, points: List[Point], algorithm: Algorithm):
        super().__init__(Primitive.PType.curve)
        if len(points) <= 1:
            raise ValueError("Points number should be greater than 1")
        self.points = points
        self.algorithm = algorithm

    def boundingRect(self):
        x = []
        y = []
        for p in self.render():
            x.append(p[0])
            y.append(p[1])
        return min(x)-1, min(y)-1, max(x)-min(x)+2, max(y)-min(y)+2

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
        def b(i: int, t: float):
            if i == -2:
                return (((-t + 3) * t - 3) * t + 1) / 6
            elif i == -1:
                return (((3 * t - 6) * t) * t + 4) / 6
            elif i == 0:
                return (((-3 * t + 3) * t + 3) * t + 1) / 6
            elif i == 1:
                return (t * t * t) / 6
            return 0

        def point(i: int, t: float, xps, yps):
            px = 0
            py = 0
            for j in range(-2, 2):
                px += b(j, t)*xps[i+j]
                py += b(j, t)*yps[i+j]
            return (round(px), round(py))

        if len(self.points) < 4:
            return self.render_Bezier(self.points)

        points = self.points
        npoints = len(points) - 1
        steps = 1
        for i in range(npoints):
            dx = abs(points[i+1][0]-points[i][0])
            dy = abs(points[i+1][1]-points[i][1])
            steps = max(round(dx + dy) * 3, steps)
        pts = npoints * steps + 1
        ret = []

        xs = [_[0] for _ in points]
        ys = [_[1] for _ in points]

        ret.append(point(2, 0, xs, ys))
        for i in range(2, npoints):
            for j in range(1, steps+1):
                ret.append(
                    point(i, j/steps, xs, ys)
                )

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
        return f"Curve ({self.points[0][0]}, {self.points[0][1]})\u2192({self.points[-1][0]}, {self.points[-1][1]})"
