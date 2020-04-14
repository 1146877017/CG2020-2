from model import *
import sys
import os

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    # default
    board = Board(1000, 1000)

    with open(input_file, "r") as File:
        for line in File.readlines():
            argv = line.split()
            argc = len(argv)

            if argv[0] == "resetCanvas":
                board.reset(int(argv[1]), int(argv[2]))
            elif argv[0] == "saveCanvas":
                board.save(os.path.join(output_dir, argv[1] + ".bmp"))
            elif argv[0] == "setColor":
                board.setColor((
                    int(argv[1]),
                    int(argv[2]),
                    int(argv[3]),
                ))
            elif argv[0] == "drawLine":
                board.addPrimitive(
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
                board.addPrimitive(
                    argv[1], Polygon(
                        ps,
                        Line.Algorithm.DDA if argv[-1] == "DDA" else Line.Algorithm.Bresenham
                    )
                )
            elif argv[0] == "drawEllipse":
                board.addPrimitive(
                    argv[1], Ellipse(
                        int(argv[2]), int(argv[3]),
                        int(argv[4]), int(argv[5]),
                        Line.Algorithm.DDA if argv[-1] == "DDA" else Line.Algorithm.Bresenham
                    )
                )
            elif argv[0] == "drawCurve":
                pn = (argc - 3) // 2
                ps = []
                for i in range(pn):
                    ps.append(
                        (int(argv[i*2+2]), int(argv[i*2+3]))
                    )
                board.addPrimitive(
                    argv[1], Curve(
                        ps,
                        Curve.Algorithm.B_spline if argv[-1] == "B-spline" else Curve.Algorithm.Bezier
                    )
                )
            elif argv[0] == "translate":
                board.translate(
                    argv[1], int(argv[2]), int(argv[3])
                )
            elif argv[0] == "rotate":
                board.rotate(
                    argv[1], int(argv[2]), int(argv[3]), int(argv[4])
                )
            elif argv[0] == "scale":
                board.scale(
                    argv[1], int(argv[2]), int(argv[3]), float(argv[4])
                )
            elif argv[0] == "clip":
                board.clip(
                    argv[1],
                    int(argv[2]), int(argv[3]),
                    int(argv[4]), int(argv[5]),
                    Line.ClipAlgorithm.Cohen_Sutherland if argv[-1] == "Cohen-Sutherland" else Line.ClipAlgorithm.Liang_Barsky
                )
            else:
                # invalid
                pass
