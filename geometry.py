import numpy as np
from typing import List, Union

class Vertex:
    """
    A single vertex in 3D space. 
    
    The vector can be accessed with `Vertex.v`.
    """
    def __init__(self, x: float, y: float, z: float):
        self.v = np.array([x, y, z])
    
    @staticmethod
    def rotate(vtx: 'Vertex', alpha: float=0, beta: float=0, gamma: float=0) -> 'Vertex':
        """
        Returns the given coordinate, rotated by:
        - `alpha`: Rotation about the x-axis
        - `beta`: Rotation about the y-axis
        - `gamma`: Rotation about the z-axis
        """
        R = np.array([
            [np.cos(beta)*np.cos(gamma), (np.sin(alpha)*np.sin(beta)*np.cos(gamma)) - (np.cos(alpha)*np.sin(gamma)), (np.cos(alpha)*np.sin(beta)*np.cos(gamma)) + (np.sin(alpha)*np.sin(gamma))],
            [np.cos(beta)*np.sin(gamma), (np.sin(alpha)*np.sin(beta)*np.sin(gamma)) + (np.cos(alpha)*np.cos(gamma)), (np.cos(alpha)*np.sin(beta)*np.sin(gamma)) - (np.sin(alpha)*np.cos(gamma))],
            [-np.sin(beta), np.sin(alpha)*np.cos(beta), np.cos(alpha)*np.cos(beta)]
        ])
        return Vertex.from_ndarray(np.matmul(R, vtx.v))
    
    @staticmethod
    def rotate_about_origin(vtx: 'Vertex', origin: 'Vertex', alpha: float=0, beta: float=0, gamma: float=0) -> 'Vertex':
        """
        Returns the given coordinate, rotated by:
        - `alpha`: Rotation about the x-axis
        - `beta`: Rotation about the y-axis
        - `gamma`: Rotation about the z-axis
        """
        R = np.array([
            [np.cos(beta)*np.cos(gamma), (np.sin(alpha)*np.sin(beta)*np.cos(gamma)) - (np.cos(alpha)*np.sin(gamma)), (np.cos(alpha)*np.sin(beta)*np.cos(gamma)) + (np.sin(alpha)*np.sin(gamma))],
            [np.cos(beta)*np.sin(gamma), (np.sin(alpha)*np.sin(beta)*np.sin(gamma)) + (np.cos(alpha)*np.cos(gamma)), (np.cos(alpha)*np.sin(beta)*np.sin(gamma)) - (np.sin(alpha)*np.cos(gamma))],
            [-np.sin(beta), np.sin(alpha)*np.cos(beta), np.cos(alpha)*np.cos(beta)]
        ])
        return Vertex.from_ndarray(np.matmul(R, vtx.v - origin.v) + origin.v)
    
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
    def __init__(self, vertices: List[Vertex], origin: Union[Vertex, None]=None):
        if len(vertices) < 2:
            raise ValueError("Expected 2 or more vertices")
        self.vertices = vertices
        if origin == None:
            origin = self.vertices[0]
        self.origin = origin

    def generate_edges(self, interval: float=0.01) -> List[Vertex]:
        """
        Returns the geometry as an edge between every two vertices in the geometry, interpolated by `interval`.
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
    
    def generate_surfaces(self, interval: float=0.1) -> List[Vertex]:
        """
        Returns the geometry as a surface between every three vertices in the geometry, interpolated by `interval`.
        TODO: VERY INEFFICIENT
        """
        if interval < 0 or interval > 1:
            raise ValueError("Invalid interval (Expected 0 <= interval <= 1).")
        lerp_geom = []
        
        for i in range(len(self.vertices)):
            vs = self.vertices[i] # the static point

            edge = []  # edge from j to k
            pairs = [] # pairs processed in j-k
            for j in range(len(self.vertices)):
                for k in range(len(self.vertices)):
                    if j == k or (j, k) in pairs or (k, j) in pairs:
                        continue
                    pairs.append((j, k))
                    v0 = self.vertices[j]
                    v1 = self.vertices[k]
                    t = 0
                    while t <= 1:
                        edge.append(Vertex.lerp(v0, v1, t))
                        t += interval
            
            # Generate edge from vs to every point in edge
            for vtx in edge:
                t = 0
                while t <= 1:
                    lerp_geom.append(Vertex.lerp(vs, vtx, t))
                    t += interval
                
        return lerp_geom


    def rotate(self, alpha: float, beta: float, gamma: float):
        """
        Rotates the geometry about its origin.
        """
        for i in range(len(self.vertices)):
            self.vertices[i] = Vertex.rotate_about_origin(self.vertices[i], self.origin, alpha, beta, gamma)

        