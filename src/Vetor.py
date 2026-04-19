import math


class Vetor:
    """Vetor tridimensional com todas as operações necessárias para ray tracing."""

    def __init__(self, x=0, y=0, z=0):
        """Cria um vetor com as componentes x, y, z."""
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        """Soma componente a componente: (ax+bx, ay+by, az+bz)."""
        return Vetor(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """Subtração componente a componente: (ax-bx, ay-by, az-bz)."""
        return Vetor(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        """Inverte o sentido do vetor: (-x, -y, -z)."""
        return Vetor(-self.x, -self.y, -self.z)

    def __mul__(self, t):
        """Multiplica o vetor por um escalar t: (x*t, y*t, z*t)."""
        return Vetor(self.x * t, self.y * t, self.z * t)

    def __rmul__(self, t):
        """Permite escrever t * vetor além de vetor * t."""
        return self.__mul__(t)

    def __truediv__(self, t):
        """Divide o vetor por um escalar t: (x/t, y/t, z/t)."""
        return Vetor(self.x / t, self.y / t, self.z / t)

    def modulo(self):
        """Retorna o comprimento (norma) do vetor: √(x²+y²+z²)."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalizar(self):
        """Retorna um vetor unitário (comprimento 1) na mesma direção.
        Essencial para direções de raio e eixos da câmera — sem isso
        as distâncias t das interseções não seriam comparáveis entre si."""
        m = self.modulo()
        return Vetor(self.x / m, self.y / m, self.z / m)

    def prodEscalar(self, other):
        """Produto escalar (dot product): a·b = ax*bx + ay*by + az*bz.
        Resulta em um número. Usado para projetar um vetor sobre outro
        e para verificar o ângulo entre dois vetores."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def prodVetorial(self, other):
        """Produto vetorial (cross product): a×b.
        Resulta em um vetor perpendicular aos dois operandos.
        Usado para construir a base ortonormal da câmera (eixos u e v)."""
        return Vetor(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def __str__(self):
        """Representação em texto para debug."""
        return f"({self.x}, {self.y}, {self.z})T"
