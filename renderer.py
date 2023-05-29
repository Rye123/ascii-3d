import numpy as np
from typing import List
from math import floor, ceil
from geometry import Vertex, Geometry

class Camera:
    DOF = 20 # Depth of Field (i.e. viewer's distance from the screen)
    WIDTH = 20
    HEIGHT = 10
    MAX_DEPTH = 100
    OUT_OF_SCREEN_VTX = Vertex(0, 0, MAX_DEPTH+1)

    # Determines how 'bright' a point is -- taken from https://www.a1k0n.net/2011/07/20/donut-math.html
    ILLUM_CHAR = " .,-~:;=!*#$@"

    def __init__(self, pos: Vertex):
        self.pos = pos
    
    def getIllum(self, depth: float) -> str:
        """
        Based on the depth of a coordinate, get the corresponding
        'illumination' of it.
        """
        idx = ceil((depth / self.MAX_DEPTH) * len(self.ILLUM_CHAR))
        return self.ILLUM_CHAR[-idx]
        # return str(f" {(depth / self.MAX_DEPTH) * len(ILLUM_CHAR)})
    
    def project(self, vtx: Vertex) -> Vertex:
        """
        Returns a Vertex representing the projected `vtx` on a screen.
        - This screen is `DOF` units away from the camera.
        """
        depth = vtx.v[2] - self.pos.v[2]
        if depth <= 0:
            return self.OUT_OF_SCREEN_VTX
        
        ratio = self.DOF / (depth + self.DOF)
        return Vertex(
            ratio * vtx.v[0],
            ratio * vtx.v[1],
            depth
        )
    
class Scene:
    def __init__(self):
        self.geometry:List[Geometry] = []
    
    def add(self, geom:Geometry):
        self.geometry.append(geom)
    
    def render(self, camera: Camera):
        W = camera.WIDTH
        H = camera.HEIGHT
        depth_buffer = [[camera.MAX_DEPTH for x in range(W)] for y in range(H)]
        for geom in self.geometry:
            coords = geom.lerp()
            for coord in coords:
                coord = camera.project(coord)
                x = floor(coord.v[0] + (W // 2))
                y = floor(coord.v[1] + (H // 2))
                depth = coord.v[2]
                # print(f"({coord.v[0]}, {coord.v[1]}, {coord.v[2]}) --> ({x}, {y}, {depth})")
                if x < 0 or y < 0 or x >= W or y >= H:
                    continue

                # occlude objects if they are closer
                if depth < depth_buffer[y][x]:
                    depth_buffer[y][x] = depth
        
        # render, based on the depth buffer
        screen = ""
        for y in range(H):
            line = ""
            for x in range(W):
                line += camera.getIllum(depth_buffer[y][x])
            screen += line + "\n"
        print(screen)

if __name__ == "__main__":
    cam = Camera(Vertex(0, 0, 0))
    scene = Scene()

    tri = Geometry(
        [
            Vertex(-10,   0,   3),
            Vertex( 10, -10,  20),
            Vertex( 10,  10,  20)
        ]
    )
    scene.add(tri)
    scene.render(cam)