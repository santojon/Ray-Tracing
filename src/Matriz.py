import math
from src.Ponto import Ponto
from src.Vetor import Vetor


class Matriz:
    """Matriz 4×4 em coordenadas homogêneas para transformações afins (TRS).

    Coordenadas homogêneas adicionam uma quarta componente 'w' a pontos e
    vetores, o que permite representar translação como multiplicação de matriz
    — algo impossível com matrizes 3×3 comuns.

    Ponto  → w = 1: a translação AFETA o ponto  (queremos mover o ponto)
    Vetor  → w = 0: a translação NÃO afeta o vetor (apenas direção importa)
    """

    def __init__(self, dados=None):
        """Cria a matriz a partir de uma lista 4×4. Se omitida, começa como zeros."""
        if dados is None:
            self.m = [[0.0] * 4 for _ in range(4)]
        else:
            self.m = [row[:] for row in dados]

    @staticmethod
    def identidade():
        """Matriz identidade: não altera nenhum ponto ou vetor.
        Ponto de partida para compor uma sequência de transformações."""
        M = Matriz()
        for i in range(4):
            M.m[i][i] = 1.0
        return M

    @staticmethod
    def translacao(tx, ty, tz):
        """Desloca um ponto por (tx, ty, tz).
        A translação vai na 4ª coluna — por isso w=1 em pontos é essencial."""
        M = Matriz.identidade()
        M.m[0][3] = tx
        M.m[1][3] = ty
        M.m[2][3] = tz
        return M

    @staticmethod
    def escala(sx, sy, sz):
        """Escala cada eixo independentemente.
        Valores > 1 ampliam; valores < 1 contraem; valor negativo espelha."""
        M = Matriz.identidade()
        M.m[0][0] = sx
        M.m[1][1] = sy
        M.m[2][2] = sz
        return M

    @staticmethod
    def rotacao_x(angulo):
        """Rotação em torno do eixo X por 'angulo' radianos (regra da mão direita).
        Mantém X fixo; rotaciona Y e Z."""
        M = Matriz.identidade()
        c, s = math.cos(angulo), math.sin(angulo)
        M.m[1][1] =  c;  M.m[1][2] = -s
        M.m[2][1] =  s;  M.m[2][2] =  c
        return M

    @staticmethod
    def rotacao_y(angulo):
        """Rotação em torno do eixo Y por 'angulo' radianos.
        Mantém Y fixo; rotaciona X e Z."""
        M = Matriz.identidade()
        c, s = math.cos(angulo), math.sin(angulo)
        M.m[0][0] =  c;  M.m[0][2] =  s
        M.m[2][0] = -s;  M.m[2][2] =  c
        return M

    @staticmethod
    def rotacao_z(angulo):
        """Rotação em torno do eixo Z por 'angulo' radianos.
        Mantém Z fixo; rotaciona X e Y."""
        M = Matriz.identidade()
        c, s = math.cos(angulo), math.sin(angulo)
        M.m[0][0] =  c;  M.m[0][1] = -s
        M.m[1][0] =  s;  M.m[1][1] =  c
        return M

    def __mul__(self, other):
        """Composição de duas matrizes: (A*B)*v = A*(B*v).
        Ou seja, B é aplicada ao vértice primeiro, depois A."""
        if isinstance(other, Matriz):
            R = Matriz()
            for i in range(4):
                for j in range(4):
                    R.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
            return R
        raise TypeError(f"Não posso multiplicar Matriz por {type(other)}")

    def aplicar_ponto(self, p: Ponto) -> Ponto:
        """Transforma um Ponto usando w=1, incluindo a translação.
        Usado para mover vértices da malha para o espaço do mundo."""
        x = self.m[0][0]*p.x + self.m[0][1]*p.y + self.m[0][2]*p.z + self.m[0][3]
        y = self.m[1][0]*p.x + self.m[1][1]*p.y + self.m[1][2]*p.z + self.m[1][3]
        z = self.m[2][0]*p.x + self.m[2][1]*p.y + self.m[2][2]*p.z + self.m[2][3]
        return Ponto(x, y, z)

    def aplicar_vetor(self, v: Vetor) -> Vetor:
        """Transforma um Vetor usando w=0, ignorando a translação.
        Usado para transformar normais (sem deslocamento, só orientação)."""
        x = self.m[0][0]*v.x + self.m[0][1]*v.y + self.m[0][2]*v.z
        y = self.m[1][0]*v.x + self.m[1][1]*v.y + self.m[1][2]*v.z
        z = self.m[2][0]*v.x + self.m[2][1]*v.y + self.m[2][2]*v.z
        return Vetor(x, y, z)

    def __str__(self):
        """Representação em texto para debug."""
        return "\n".join(
            "[ " + "  ".join(f"{self.m[i][j]:8.4f}" for j in range(4)) + " ]"
            for i in range(4)
        )
