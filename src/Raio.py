from src.Ponto import Ponto
from src.Vetor import Vetor


class Raio:
    """Representa um raio no espaço 3D: O + t*D.
    O é a origem (onde o raio começa) e D é a direção (normalizada).
    O parâmetro t indica a distância ao longo do raio — só valores t > 0
    representam pontos à frente da câmera."""

    def __init__(self, origem: Ponto, direcao: Vetor):
        """Cria o raio com origem e direção. A direção deve estar normalizada
        para que o valor de t corresponda à distância real no espaço."""
        self.origem = origem
        self.direcao = direcao

    def ponto_em(self, t: float) -> Ponto:
        """Calcula o ponto P = O + t*D ao longo do raio.
        Usado para encontrar as coordenadas exatas de um ponto de interseção."""
        return self.origem + self.direcao * t
