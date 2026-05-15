from dataclasses import dataclass
from src.Ponto import Ponto
from src.Vetor import Vetor


@dataclass
class HitInfo:
    """Resultado de uma interseção raio-objeto.

    t        — distância ao longo do raio (P = O + t*D)
    point    — coordenadas do ponto de interseção no mundo
    normal   — normal da superfície em 'point', já orientada para o lado do raio
    material — material do objeto (ou face) atingido
    """
    t: float
    point: Ponto
    normal: Vetor
    material: object
