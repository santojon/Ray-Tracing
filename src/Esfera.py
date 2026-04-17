import math
from src.Ponto import Ponto
from src.Raio import Raio


class Esfera:
    def __init__(self, centro: Ponto, raio: float, material):
        self.centro = centro
        self.raio = raio
        self.material = material

    def intersectar(self, raio: Raio):
        """
        Resolve |O + t*D - C|² = r²  →  equação quadrática em t.

        oc = O - C  (vetor da origem do raio ao centro da esfera)
        a  = D · D
        b  = 2 * (oc · D)
        c  = (oc · oc) - r²
        Δ  = b² - 4ac

        Δ < 0  → raio não intersecta a esfera (passa fora)
        Δ = 0  → tangente (1 ponto)
        Δ > 0  → 2 intersecções; pegamos o t mínimo positivo (mais próximo)
        """
        oc = raio.origem - self.centro   # Ponto - Ponto = Vetor
        a = raio.direcao.prodEscalar(raio.direcao)
        b = 2.0 * oc.prodEscalar(raio.direcao)
        c = oc.prodEscalar(oc) - self.raio ** 2

        discriminante = b * b - 4 * a * c
        if discriminante < 0:
            return None

        raiz = math.sqrt(discriminante)
        t1 = (-b - raiz) / (2 * a)   # intersecção mais próxima
        t2 = (-b + raiz) / (2 * a)   # intersecção mais distante

        EPS = 1e-6
        if t1 > EPS:
            return t1
        if t2 > EPS:
            return t2
        return None
