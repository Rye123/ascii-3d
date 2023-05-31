import numpy as np
from typing import List, Union

class Vertex:
    """
    A single vertex in 3D space. 
    
    The vector can be accessed with `Vertex.v`.
    """
    def __init__(self, x: float, y: float, z: float, color: int = 0):
        self.v = np.array([x, y, z])
        self.color = color
    
    @staticmethod
    def rotate(vtx: 'Vertex', alpha: float=0, beta: float=0, gamma: float=0) -> 'Vertex':
        """
        Returns the given coordinate, rotated by:
        - `alpha`: Rotation about the x-axis
        - `beta`: Rotation about the y-axis
        - `gamma`: Rotation about the z-axis
        """
        # cached variables
        cA = np.cos(alpha)
        sA = np.sin(alpha)
        cB = np.cos(beta)
        sB = np.sin(beta)
        cG = np.cos(gamma)
        sG = np.sin(gamma)
        R = np.array([
            [cB*cG, (sA*sB*cG) - (cA*sG), (cA*sB*cG) + (sA*sG)],
            [cB*sG, (sA*sB*sG) + (cA*cG), (cA*sB*sG) - (sA*cG)],
            [-sB, sA*cB, cA*cB]
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
        cA = np.cos(alpha)
        sA = np.sin(alpha)
        cB = np.cos(beta)
        sB = np.sin(beta)
        cG = np.cos(gamma)
        sG = np.sin(gamma)
        R = np.array([
            [cB*cG, (sA*sB*cG) - (cA*sG), (cA*sB*cG) + (sA*sG)],
            [cB*sG, (sA*sB*sG) + (cA*cG), (cA*sB*sG) - (sA*cG)],
            [-sB, sA*cB, cA*cB]
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
    def lerp_gen(vertices: List['Vertex'], coeffs: List[float]) -> 'Vertex':
        """
        
        """
        if not np.isclose(sum(coeffs), 1):
            print(coeffs)
            raise ValueError("Cannot lerp_gen when sum of coefficients is not 1.")
        if len(coeffs) != len(vertices):
            raise ValueError("Coeff length does not match vertices length.")
        new_v = np.array([0.0, 0.0, 0.0])
        for vtx, coeff in zip(vertices, coeffs):
            new_v += vtx.v * coeff
        return Vertex.from_ndarray(new_v)
    
    @staticmethod
    def from_ndarray(v: np.ndarray) -> 'Vertex':
        if len(v) != 3:
            raise ValueError("Expected a 3D numpy array")
        return Vertex(v[0], v[1], v[2])

class Geometry:
    """
    An enclosed set of two or more vertices in 3D space.
    """
    def __init__(self, vertices: List[Vertex], origin: Union[Vertex, None]=None, color: int=0):
        if len(vertices) < 2:
            raise ValueError("Expected 2 or more vertices")
        self.vertices = vertices
        if origin == None:
            origin = self.vertices[0]
        self.origin = origin
        self.color = color

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
                    v = Vertex.lerp(v0, v1, t)
                    v.color = self.color
                    lerp_geom.append(v)
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
        triples = []
        for i in range(len(self.vertices)):
            for j in range(len(self.vertices)):
                for k in range(len(self.vertices)):
                    if (i, j, k) in triples or (i, k, j) in triples or (j, i, k) in triples or (j, k, i) in triples or (k, i, j) in triples or (k, j, i) in triples:
                        continue
                    triples.append((i, j, k))

                    vertices = [self.vertices[i], self.vertices[j], self.vertices[k]]
                    
                    coeff0 = 0.0
                    while coeff0 <= 1.0:
                        coeff1 = 0.0
                        while coeff1 <= (1.0 - coeff0):
                            coeff2 = 1.0 - coeff0 - coeff1
                            coeffs = [coeff0, coeff1, coeff2]
                            v = Vertex.lerp_gen(vertices, coeffs)
                            v.color = self.color
                            lerp_geom.append(v)
                            coeff1 += interval
                        coeff0 += interval
                
        return lerp_geom


    def rotate(self, alpha: float, beta: float, gamma: float):
        """
        Rotates the geometry about its origin.
        """
        for i in range(len(self.vertices)):
            self.vertices[i] = Vertex.rotate_about_origin(self.vertices[i], self.origin, alpha, beta, gamma)

        
