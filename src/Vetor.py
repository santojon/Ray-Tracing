import math


class Vetor:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vetor(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vetor(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Vetor(-self.x, -self.y, -self.z)

    # escalar * vetor  e  vetor * escalar
    def __mul__(self, t):
        return Vetor(self.x * t, self.y * t, self.z * t)

    def __rmul__(self, t):
        return self.__mul__(t)

    def __truediv__(self, t):
        return Vetor(self.x / t, self.y / t, self.z / t)

    def modulo(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalizar(self):
        m = self.modulo()
        return Vetor(self.x / m, self.y / m, self.z / m)

    # Produto escalar (dot product): a · b = ax*bx + ay*by + az*bz
    def prodEscalar(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    # Produto vetorial (cross product): a × b
    # Resulta em vetor perpendicular ao plano formado por a e b
    def prodVetorial(self, other):
        return Vetor(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})T"
