from src.Ponto import Ponto
from src.Vetor import Vetor


class Raio:
    """
    Raio = Origem + t * Direção
    t > 0  →  ponto à frente da câmera
    """

    def __init__(self, origem: Ponto, direcao: Vetor):
        self.origem = origem
        self.direcao = direcao  # deve estar normalizado

    def ponto_em(self, t: float) -> Ponto:
        """Retorna o ponto ao longo do raio no parâmetro t."""
        return self.origem + self.direcao * t
