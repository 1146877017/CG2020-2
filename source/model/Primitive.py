from typing import List
from abc import ABC, abstractmethod
from .Utils import *
from math import atan2, cos, sin, degrees, radians, sqrt


class Primitive(ABC):
    def __init__(self):
        self.saved = None

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
        radian = radians(degree - r)
        return (round(x+l*cos(radian)), round(y+l*sin(radian)))

    def scalePoint(self, x0: int, y0: int, x: int, y: int, s: float) -> Point:
        return (round(x0*s+(1-s)*x), round(y0*s+(1-s)*y))

    @abstractmethod
    def __str__(self):
        pass
