import numpy as np
from typing import List
from copy import copy
from math import floor, ceil

# Determines how 'bright' a point is -- taken from https://www.a1k0n.net/2011/07/20/donut-math.html
ILLUM_CHAR = " .,-~:;=!*#$@"

# Screen Settings
DOF = 20 # Depth of Field (i.e. viewer's distance from the screen)
WIDTH = 20
HEIGHT = 10
MAX_DEPTH = 100

Vector3 = np.ndarray
InvalidVector3 = np.array([WIDTH+1, HEIGHT + 1, DOF])

# Camera Position
Camera = np.array([0, 0, 0])


def lerp(v0: Vector3, v1: Vector3, t: float) -> Vector3:
    """
    Linearly interpolate between `v0` and `v1`.
    Code from https://gamedev.stackexchange.com/a/49185.
    """
    return (v0 * t) + (v1 * (1 - t))

class Geometry:
    def __init__(self, vertices: List[Vector3]):
        self.v = vertices
    
    def generate(self) -> List[Vector3]:
        ret = []
        pairs = []
        interval = 0.01
        for i in range(len(self.v)):
            v0 = self.v[i]
            for j in range(len(self.v)):
                if i == j:
                    continue
                v1 = self.v[j]
                if (i, j) in pairs or (j, i) in pairs:
                    continue
                pairs.append((i, j))
                t = 0
                while t <= 1:
                    ret.append(lerp(v0, v1, t))
                    t += interval
        return ret
    
class Line(Geometry):
    def __init__(self, start: Vector3, end: Vector3):
        vertices = [start, end]
        super().__init__(vertices)

def project(v: Vector3) -> Vector3:
    depth = v[2] - Camera[2] # distance of screen from v
    if depth <= 0:
        return InvalidVector3
    ratio = DOF / (depth + DOF)
    return np.array([
        ratio * v[0],
        ratio * v[1],
        depth
    ])

def getIllum(depth: float) -> str:
    index = ceil((depth/MAX_DEPTH) * len(ILLUM_CHAR))
    return ILLUM_CHAR[-index]
    # return str(f" {(depth / MAX_DEPTH) * len(ILLUM_CHAR)} ")

def render(scene: List[Geometry]):
    depth_buffer = [[MAX_DEPTH for x in range(WIDTH)] for y in range(HEIGHT)]
    for geom in scene:
        coords = geom.generate()
        for coord in coords:
            coord = project(coord)
            x = floor(coord[0] + (WIDTH//2))
            y = floor(-coord[1] + (HEIGHT//2))
            depth = coord[2]
            # print(f"({coord[0]}, {coord[1]}, {coord[2]}) --> ({x}, {y}, {depth})")
            if x < 0 or y < 0 or x >= WIDTH or y >= HEIGHT:
                continue

            if depth < depth_buffer[y][x]:
                depth_buffer[y][x] = depth
    
    screen = ''
    for y in range(HEIGHT):
        line = ""
        for x in range(WIDTH):
            line += getIllum(depth_buffer[y][x])
        line += "\n"
        screen += line
    print(screen)


if __name__ == "__main__":
    scene = []
    # scene.append(Line(np.array([0,0,5]), np.array([200, 0, 100])))
    Plane = Geometry(
        [
            np.array([-10, 0, 3]), np.array([10, -10, 20]),
            np.array([10, 10, 20])
        ]
    )
    scene.append(Plane)
    
    render(scene)