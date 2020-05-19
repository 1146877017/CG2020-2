from cg_algorithms import *
import sys
import os
from typing import Dict
import numpy as np
from PIL import Image


class Board():
    def __init__(self, width: int, height: int, output_dir: str = ""):
        if height <= 0 or width <= 0:
            raise ValueError("Board size should be greater to 0")
        self.height = height
        self.width = width
        self.color = ColorTable.BLACK
        self.primitives: Dict[str, (Primitive, Color)] = {}
        self.output_dir = output_dir

    def setColor(self, color: Color):
        self.color = color

    def getColor(self) -> Color:
        return self.color

    def reset(self, width: int, height: int):
        self.__init__(width, height, self.output_dir)

    def render(self):
        canvas = np.zeros([self.height, self.width, 3], np.uint8)
        canvas.fill(255)
        for primitive, color in self.primitives.values():
            for p in primitive.render():
                if p[0] >= 0 and p[0] < self.width and p[1] >= 0 and p[1] < self.height:
                    canvas[self.height-p[1]-1][p[0]] = color
        return canvas

    def addPrimitive(self, id: str, p: Primitive):
        self.primitives[id] = (p, self.color)

    def removePrimitive(self, id: str):
        try:
            del self.primitives[id]
        except KeyError:
            pass

    def translate(self, id: str, dx: int, dy: int):
        prim = self.primitives.get(id)
        if prim:
            prim[0].translate(dx, dy)

    def rotate(self, id: str, x: int, y: int, r: int) -> None:
        prim = self.primitives.get(id)
        if prim:
            prim[0].rotate(x, y, -r)

    def scale(self, id: str, x: int, y: int, s: float) -> None:
        prim = self.primitives.get(id)
        if prim:
            prim[0].scale(x, y, s)

    def clip(self, id: str, x0: int, y0: int, x1: int, y1: int, algorithm) -> None:
        prim = self.primitives.get(id)
        if prim:
            op = getattr(prim[0], "clip", None)
            if op:
                accept = prim[0].clip(x0, y0, x1, y1, algorithm)
                if not accept:
                    del self.primitives[id]

    def setPrimColor(self, id: str, color: Color):
        prim = self.primitives.get(id)
        if prim:
            self.primitives[id] = (prim[0], color)

    def getPrimColor(self, id: str) -> Color:
        prim = self.primitives.get(id)
        if prim:
            return prim[1]
        return (0, 0, 0)

    def show(self):
        Image.fromarray(self.render()).show()

    def save(self, path: str):
        Image.fromarray(self.render()).save(path)

    def exec(self, cmd: str):
        argv = cmd.split()
        argc = len(argv)
        if argc <= 0:
            return
        if argv[0] == "resetCanvas":
            self.reset(int(argv[1]), int(argv[2]))
        elif argv[0] == "saveCanvas":
            if self.output_dir:
                self.save(os.path.join(self.output_dir, argv[1] + ".bmp"))
        elif argv[0] == "setColor":
            self.setColor((
                int(argv[1]),
                int(argv[2]),
                int(argv[3]),
            ))
        elif argv[0] == "drawLine":
            self.addPrimitive(
                argv[1], Line(
                    int(argv[2]), int(argv[3]),
                    int(argv[4]), int(argv[5]),
                    Line.Algorithm.DDA if argv[6] == "DDA" else Line.Algorithm.Bresenham
                )
            )
        elif argv[0] == "drawPolygon":
            pn = (argc - 3) // 2
            ps = []
            for i in range(pn):
                ps.append(
                    (int(argv[i*2+2]), int(argv[i*2+3]))
                )
            self.addPrimitive(
                argv[1], Polygon(
                    ps,
                    Line.Algorithm.DDA if argv[-1] == "DDA" else Line.Algorithm.Bresenham
                )
            )
        elif argv[0] == "drawEllipse":
            self.addPrimitive(
                argv[1], Ellipse(
                    int(argv[2]), int(argv[3]),
                    int(argv[4]), int(argv[5]),
                )
            )
        elif argv[0] == "drawCurve":
            pn = (argc - 3) // 2
            ps = []
            for i in range(pn):
                ps.append(
                    (int(argv[i*2+2]), int(argv[i*2+3]))
                )
            self.addPrimitive(
                argv[1], Curve(
                    ps,
                    Curve.Algorithm.B_spline if argv[-1] == "B-spline" else Curve.Algorithm.Bezier
                )
            )
        elif argv[0] == "translate":
            self.translate(
                argv[1], int(argv[2]), int(argv[3])
            )
        elif argv[0] == "rotate":
            self.rotate(
                argv[1], int(argv[2]), int(argv[3]), int(argv[4])
            )
        elif argv[0] == "scale":
            self.scale(
                argv[1], int(argv[2]), int(argv[3]), float(argv[4])
            )
        elif argv[0] == "clip":
            self.clip(
                argv[1],
                int(argv[2]), int(argv[3]),
                int(argv[4]), int(argv[5]),
                Line.ClipAlgorithm.Cohen_Sutherland if argv[-1] == "Cohen-Sutherland" else Line.ClipAlgorithm.Liang_Barsky
            )
        else:
            # invalid
            pass


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    # default
    board = Board(1000, 1000, output_dir)

    with open(input_file, "r") as File:
        for line in File.readlines():
            try:
                board.exec(line)
            except Exception as e:
                print(e)
