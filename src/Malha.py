from src.Matriz import Matriz
from src.Triangulo import Triangulo
from src.Raio import Raio
from utils.MeshReader.ObjReader import ObjReader


class Malha:
    """Malha de triângulos carregada de um arquivo .obj com transformações afins.

    O pipeline é:
        1. Ler vértices e faces do .obj via ObjReader
        2. Construir a matriz de transformação M combinando scaling, rotation e translation
        3. Aplicar M a cada vértice (espaço do objeto → espaço do mundo)
        4. Para cada face, criar um Triangulo com os vértices transformados
        5. Ao testar interseção, testar o raio contra todos os triângulos
           e retornar o menor t positivo (o triângulo mais próximo)
    """

    def __init__(self, path: str, material, transforms: list):
        """Carrega a malha do arquivo 'path' e aplica as transformações.

        As transformações em 'transforms' são aplicadas na ordem da lista:
        a primeira transforma os vértices primeiro (TRS → escala, depois rotação,
        depois translação). A composição é M = T * R * S, aplicada como M * vértice."""
        self.material = material
        M = self._construir_matriz(transforms)

        reader     = ObjReader(path)
        vertices   = reader.get_vertices()
        faces      = reader.get_faces()

        # Aplica a transformação a todos os vértices de uma vez
        vertices_mundo = [M.aplicar_ponto(v) for v in vertices]

        self.triangulos = []
        for face in faces:
            i0, i1, i2 = face.vertice_indice
            self.triangulos.append(Triangulo(
                vertices_mundo[i0],
                vertices_mundo[i1],
                vertices_mundo[i2],
                material,
            ))

    @staticmethod
    def _construir_matriz(transforms: list) -> Matriz:
        """Compõe a sequência de transformações em uma única matriz 4×4.

        Para cada transform na lista, calcula sua matriz e faz:
            M = T_nova * M_acumulada
        Isso faz com que a primeira transformação da lista seja aplicada
        primeiro ao vértice (fica mais à direita na multiplicação final).

        Ordem padrão nos JSONs de cena: scaling → rotation → translation,
        resultando em M = T * R * S (o que é o padrão TRS em 3D).
        """
        M = Matriz.identidade()
        for t in transforms:
            if t.t_type == "scaling":
                M = Matriz.escala(t.data.x, t.data.y, t.data.z) * M

            elif t.t_type == "rotation":
                # Euler XYZ: aplica X primeiro, depois Y, depois Z ao vértice
                # Portanto a matriz combinada é Rz * Ry * Rx
                Rx = Matriz.rotacao_x(t.data.x)
                Ry = Matriz.rotacao_y(t.data.y)
                Rz = Matriz.rotacao_z(t.data.z)
                M = Rz * Ry * Rx * M

            elif t.t_type == "translation":
                M = Matriz.translacao(t.data.x, t.data.y, t.data.z) * M
        return M

    def intersectar(self, raio: Raio):
        """Testa o raio contra todos os triângulos da malha.
        Retorna o menor t positivo encontrado, ou None se não houver colisão.
        Complexidade O(n_triangulos) — sem aceleração espacial nesta entrega."""
        t_min = None
        for tri in self.triangulos:
            t = tri.intersectar(raio)
            if t is not None and (t_min is None or t < t_min):
                t_min = t
        return t_min
