import numpy as np
import logging
from typing import List
from math import floor, ceil
from geometry import Vertex, Geometry
from time import sleep
from os import system
from shutil import get_terminal_size
from traceback import format_exc
from threading import Event
from curses import wrapper
import curses

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

defHandler = logging.FileHandler(__file__ + ".log")
defHandler.setLevel(logging.DEBUG)

logger.addHandler(defHandler)

class Camera:
    DOF = 25 # Depth of Field (i.e. viewer's distance from the screen)
    MAX_DEPTH = 1000
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
        color = vtx.color
        if depth <= 0:
            return self.OUT_OF_SCREEN_VTX
        
        ratio = self.DOF / (depth + self.DOF)
        return Vertex(
            ratio * vtx.v[0],
            ratio * vtx.v[1],
            depth,
            color
        )
    
class Scene:
    def __init__(self, window):
        self.geometry:List[Geometry] = []
        self.depth_buffer:List[List[float]] = []
        self.screen_buffer:List[List[str]] = []
        self.screen_ready = Event()
        self.window = window

        # Color Settings
        default_bg = curses.COLOR_BLACK
        curses.init_pair(1, default_bg, default_bg)
        curses.init_pair(2, curses.COLOR_RED, default_bg)
        curses.init_pair(3, curses.COLOR_GREEN, default_bg)
        curses.init_pair(4, curses.COLOR_YELLOW, default_bg)
        curses.init_pair(5, curses.COLOR_BLUE, default_bg)
        curses.init_pair(6, curses.COLOR_MAGENTA, default_bg)
        curses.init_pair(7, curses.COLOR_CYAN, default_bg)

        # Initialise window size and buffers
        H, W = window.getmaxyx()
        self.window_width = W
        self.window_height = H
        self.depth_buffer = [[-1 for x in range(W)] for y in range(H)]
        self.color_buffer = [[1 for x in range(W)] for y in range(H)] 
    
    def add(self, geom:Geometry):
        self.geometry.append(geom)

    def render(self, camera: Camera):
        self.depth_buffer = [[-1 for x in range(self.window_width)] for y in range(self.window_height)]
        for geom in self.geometry:
            coords = geom.generate_surfaces()
            for coord in coords:
                coord = camera.project(coord)
                x = floor(coord.v[0] + (self.window_width // 2))
                y = floor(coord.v[1] + (self.window_height // 2))
                depth = coord.v[2]
                # print(f"({coord.v[0]}, {coord.v[1]}, {coord.v[2]}) --> ({x}, {y}, {depth})")
                if x < 0 or y < 0 or x >= self.window_width or y >= self.window_height:
                    continue

                # occlude objects if they are closer
                if depth < self.depth_buffer[y][x] or self.depth_buffer[y][x] == -1:
                    self.depth_buffer[y][x] = depth
                    self.color_buffer[y][x] = coord.color
        
        # render, based on the depth buffer
        for y in range(self.window_height):
            for x in range(self.window_width):
                try:
                    self.window.addstr(y, x, camera.getIllum(self.depth_buffer[y][x]), curses.color_pair(self.color_buffer[y][x]))
                except curses.error:
                    pass
                
        #self.window.clear()
        self.window.refresh()

def main(window):
    curses.curs_set(0)
    cam = Camera(Vertex(0, 0, -5))
    scene = Scene(window)

    tri = Geometry(
        [
            Vertex(-20,   0,  70),
            Vertex( 20, -20,  100),
            Vertex( 20,  20,  100)
        ],
        color=2
    )
    quad = Geometry(
        [
            Vertex(-20, -20,  50),
            Vertex(-20,  20,  50),
            Vertex( 20, -20,  50),
            Vertex( 20,  20,  50)
        ],
        color=3
    )
    scene.add(tri)
    scene.add(quad)

    # Render Loop
    try:
        while True:
            scene.render(cam)
            quad.rotate(0, 0.25, 0)
            sleep(0.05)
    except KeyboardInterrupt:
        logger.info("Exiting due to interrupt.")
    except Exception as e:
        logger.info("Exiting due to exception.")
        logger.critical(format_exc())

if __name__ == "__main__":
    wrapper(main)

    
