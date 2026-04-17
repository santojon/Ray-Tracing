from src.Ponto import Ponto
from src.Vetor import Vetor
from src.Raio import Raio


class Plano:
    def __init__(self, ponto: Ponto, normal: Vetor, material):
        self.ponto = ponto
        self.normal = normal.normalizar()
        self.material = material

    def intersectar(self, raio: Raio):
        """
        Plano definido por um ponto P0 e normal N: (P - P0) · N = 0
        Substituindo P = O + t*D:

            t = ((P0 - O) · N) / (D · N)

        D · N ≈ 0  → raio paralelo ao plano (sem intersecção)
        t ≤ 0      → intersecção atrás da câmera (descartado)
        """
        denom = raio.direcao.prodEscalar(self.normal)
        if abs(denom) < 1e-6:
            return None   # raio paralelo ao plano

        # (P0 - O) como Vetor
        p0_menos_o = self.ponto - raio.origem   # Ponto - Ponto = Vetor
        t = p0_menos_o.prodEscalar(self.normal) / denom

        if t > 1e-6:
            return t
        return None
