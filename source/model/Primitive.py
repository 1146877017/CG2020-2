from typing import List
from abc import ABC, abstractmethod
from .Utils import *
from math import atan2, cos, sin, degrees, radians, sqrt


class Primitive(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def render(self) -> List[Point]:
        pass

    @abstractmethod
    def translate(self, dx: int, dy: int) -> None:
        pass

    @abstractmethod
    def rotate(self, x: int, y: int, r: int) -> None:
        pass

    @abstractmethod
    def scale(self, x: int, y: int, s: float) -> None:
        pass

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
