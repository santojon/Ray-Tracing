from dataclasses import dataclass
from src.Ponto import Ponto
from src.Vetor import Vetor


@dataclass
class HitInfo:
    """Resultado de uma interseção raio-objeto.

    t          — distância ao longo do raio (P = O + t*D)
    point      — coordenadas do ponto de interseção no mundo
    normal     — normal da superfície em 'point', já orientada para o lado do raio
    material   — material do objeto (ou face) atingido
    front_face — True se o raio atingiu a superfície "por fora" (vindo do ar),
                 False se atingiu "por dentro" (raio saindo do material). Usado
                 na entrega 4 para escolher a razão de índices de refração
                 (ar→material vs. material→ar) na lei de Snell.
    """
    t: float
    point: Ponto
    normal: Vetor
    material: object
    front_face: bool = True
