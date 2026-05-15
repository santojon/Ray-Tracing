from src.Ponto import Ponto
from src.Raio import Raio
from src.HitInfo import HitInfo


class Triangulo:
    """Triângulo definido por três vértices e um material.
    Sabe testar se um raio o acerta usando o algoritmo de Möller-Trumbore."""

    def __init__(self, p0: Ponto, p1: Ponto, p2: Ponto, material):
        """Cria o triângulo com os três vértices já no espaço do mundo
        (após aplicar as transformações da malha) e o material associado.
        Pré-computa edge1, edge2 e a normal (constante por triângulo)."""
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.material = material

        self.edge1 = p1 - p0
        self.edge2 = p2 - p0
        self.normal = self.edge1.prodVetorial(self.edge2).normalizar()

    def intersectar(self, raio: Raio):
        """Algoritmo de Möller-Trumbore: interseção raio-triângulo em O(1).

        A ideia é expressar o ponto de interseção P em coordenadas
        baricêntricas do triângulo: P = P0 + u*(P1-P0) + v*(P2-P0)
        e ao mesmo tempo P = O + t*D (ponto no raio).
        Isso forma um sistema linear 3×3 resolvido por regra de Cramer.

        Variáveis:
            edge1, edge2  — arestas do triângulo a partir de P0
            h = D × edge2 — vetor auxiliar (produto vetorial)
            a = edge1 · h — determinante principal; ≈ 0 se raio paralelo
            f = 1/a       — fator de escala
            s = O - P0    — vetor da origem do raio ao vértice P0
            u = f*(s·h)   — coordenada baricêntrica U; deve estar em [0,1]
            q = s × edge1 — segundo vetor auxiliar
            v = f*(D·q)   — coordenada baricêntrica V; u+v deve ser ≤ 1
            t = f*(edge2·q) — distância ao longo do raio

        Rejeita: raio paralelo, u<0, u>1, v<0, u+v>1, t≤0 (atrás da câmera).
        """
        edge1 = self.edge1
        edge2 = self.edge2

        h = raio.direcao.prodVetorial(edge2)
        a = edge1.prodEscalar(h)

        EPS = 1e-6
        if abs(a) < EPS:
            return None   # raio paralelo ao plano do triângulo

        f = 1.0 / a
        s = raio.origem - self.p0   # Ponto - Ponto = Vetor
        u = f * s.prodEscalar(h)

        if u < 0.0 or u > 1.0:
            return None   # fora do triângulo (coordenada U inválida)

        q = s.prodVetorial(edge1)
        v = f * raio.direcao.prodEscalar(q)

        if v < 0.0 or u + v > 1.0:
            return None   # fora do triângulo (coordenada V inválida)

        t = f * edge2.prodEscalar(q)
        if t <= EPS:
            return None   # interseção atrás da câmera

        ponto  = raio.ponto_em(t)
        # Normal sempre voltada para o lado do raio (double-sided shading)
        normal = self.normal if raio.direcao.prodEscalar(self.normal) < 0 else -self.normal
        return HitInfo(t, ponto, normal, self.material)
