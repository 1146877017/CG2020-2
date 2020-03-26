from typing import List
from abc import ABC, abstractmethod
from .Utils import *


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
        return x0+dx, y0+dy

    def rotatePoint(self, x0: int, y0: int, x: int, y: int, r: int) -> Point:
        pass

    def scalePoint(self, x0: int, y0: int, x: int, y: int, s: float) -> Point:
        pass

    @abstractmethod
    def __str__(self):
        pass
