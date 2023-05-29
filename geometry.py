import numpy as np
from typing import List

class Vertex:
    """
    A single vertex in 3D space. 
    
    The vector can be accessed with `Vertex.v`.
    """
    def __init__(self, x: float, y: float, z: float):
        self.v = np.array([x, y, z])
    
    @staticmethod
    def lerp(v0: 'Vertex', v1: 'Vertex', t: float) -> 'Vertex':
        """
        Linearly interpolate between `v0` and `v1`.
    Code from https://gamedev.stackexchange.com/a/49185.
        """
        return Vertex.from_ndarray((v0.v * t) + (v1.v * (1 - t)))
    
    @staticmethod
    def from_ndarray(v: np.ndarray) -> 'Vertex':
        if len(v) != 3:
            raise ValueError("Expected a 3D numpy array")
        return Vertex(v[0], v[1], v[2])

class Geometry:
    """
    An enclosed set of two or more vertices in 3D space.
    """
    def __init__(self, vertices: List[Vertex]):
        if len(vertices) < 2:
            raise ValueError("Expected 2 or more vertices")
        self.vertices = vertices

    def lerp(self, interval: float=0.01) -> List[Vertex]:
        """
        Returns the geometry, interpolated by `interval`.

        This generates an edge between every two vertices in the geometry.
        """
        if interval < 0 or interval > 1:
            raise ValueError("Invalid interval (Expected 0 <= interval <= 1).")
        lerp_geom = []
        pairs = []
        for i in range(len(self.vertices)):
            for j in range(len(self.vertices)):
                if i == j or (i, j) in pairs or (j, i) in pairs:
                    continue
                pairs.append((i, j)) # Ensure we don't repeat an edge
                v0 = self.vertices[i]
                v1 = self.vertices[j]
                t = 0
                while t <= 1:
                    lerp_geom.append(Vertex.lerp(v0, v1, t))
                    t += interval
        return lerp_geom

        