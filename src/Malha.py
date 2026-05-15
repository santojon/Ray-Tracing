from src.Matriz import Matriz
from src.Triangulo import Triangulo
from src.Raio import Raio
from utils.MeshReader.ObjReader import ObjReader
from utils.MeshReader.Colormap import MaterialProperties
from utils.Scene.sceneSchema import MaterialData, ColorData


class Malha:
    """Malha de triângulos carregada de um arquivo .obj com transformações afins.

    O pipeline é:
        1. Ler vértices, faces e MATERIAIS do .obj+.mtl via ObjReader
        2. Construir a matriz de transformação M combinando scaling, rotation e translation
        3. Aplicar M a cada vértice (espaço do objeto → espaço do mundo)
        4. Para cada face, criar um Triangulo com os vértices transformados e o
           material da própria face (vindo do arquivo .mtl referenciado pelo .obj)
        5. Ao testar interseção, testar o raio contra todos os triângulos
           e retornar o menor t positivo (o triângulo mais próximo)

    IMPORTANTE: para malhas, o material vem do arquivo .mtl, não do JSON da cena.
    O parâmetro 'material' do construtor é usado apenas como fallback para
    triângulos cujo .obj não declarou material via 'usemtl'.
    """

    def __init__(self, path: str, material, transforms: list):
        """Carrega a malha do arquivo 'path' e aplica as transformações.

        As transformações em 'transforms' são aplicadas na ordem da lista:
        a primeira transforma os vértices primeiro (TRS → escala, depois rotação,
        depois translação). A composição é M = T * R * S, aplicada como M * vértice."""
        M = self._construir_matriz(transforms)

        reader     = ObjReader(path)
        vertices   = reader.get_vertices()
        faces      = reader.get_faces()

        # Aplica a transformação a todos os vértices de uma vez
        vertices_mundo = [M.aplicar_ponto(v) for v in vertices]

        # Cache de conversões MaterialProperties → MaterialData para evitar trabalho
        # redundante quando várias faces compartilham o mesmo material
        material_cache: dict[int, MaterialData] = {}
        fallback_material = material  # usado se a face não tem material no .mtl

        self.triangulos = []
        first_material = None
        for face in faces:
            tri_material = self._material_da_face(face.material, material_cache, fallback_material)
            if first_material is None:
                first_material = tri_material

            i0, i1, i2 = face.vertice_indice
            self.triangulos.append(Triangulo(
                vertices_mundo[i0],
                vertices_mundo[i1],
                vertices_mundo[i2],
                tri_material,
            ))

        # self.material guarda o material "principal" da malha (primeira face).
        # Não é mais usado diretamente na renderização — o material vem do
        # HitInfo de cada triângulo. Mantemos por compatibilidade.
        self.material = first_material if first_material is not None else fallback_material

        # AABB (axis-aligned bounding box) da malha no espaço do mundo.
        # Usada como teste rápido em intersectar(): se o raio não atravessa a caixa,
        # pula os N testes triângulo-a-triângulo.
        if vertices_mundo:
            xs = [p.x for p in vertices_mundo]
            ys = [p.y for p in vertices_mundo]
            zs = [p.z for p in vertices_mundo]
            self.bbox_min = (min(xs), min(ys), min(zs))
            self.bbox_max = (max(xs), max(ys), max(zs))
        else:
            self.bbox_min = self.bbox_max = (0.0, 0.0, 0.0)

    @staticmethod
    def _material_da_face(props: MaterialProperties,
                          cache: dict,
                          fallback: MaterialData) -> MaterialData:
        """Converte MaterialProperties (do .mtl) em MaterialData usado pelo renderer.

        Se a face não tem material declarado (kd, ka e ks todos zero), usa o material
        de fallback (vindo do JSON da cena).
        """
        # Sem .mtl ativo: usa fallback
        if (props.kd.x == 0 and props.kd.y == 0 and props.kd.z == 0
                and props.ka.x == 0 and props.ka.y == 0 and props.ka.z == 0
                and props.ks.x == 0 and props.ks.y == 0 and props.ks.z == 0):
            return fallback

        key = id(props)
        cached = cache.get(key)
        if cached is not None:
            return cached

        mat = MaterialData(
            name="",
            color=ColorData(props.kd.x, props.kd.y, props.kd.z),
            ks=ColorData(props.ks.x, props.ks.y, props.ks.z),
            ka=ColorData(props.ka.x, props.ka.y, props.ka.z),
            kr=ColorData(props.kr.x, props.kr.y, props.kr.z),
            kt=ColorData(props.kt.x, props.kt.y, props.kt.z),
            ns=props.ns,
            ni=props.ni if props.ni > 0 else 1.0,
            d=props.d  if props.d  > 0 else 1.0,
        )
        cache[key] = mat
        return mat

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
        Antes do teste por triângulo, descarta o raio se ele nem atravessa a AABB
        da malha — isso evita N testes Möller-Trumbore para a maioria dos pixels,
        que são fundo. Retorna o HitInfo mais próximo, ou None se não houver colisão."""
        if not self._intersecta_bbox(raio):
            return None

        best = None
        for tri in self.triangulos:
            hit = tri.intersectar(raio)
            if hit is not None and (best is None or hit.t < best.t):
                best = hit
        return best

    def _intersecta_bbox(self, raio: Raio) -> bool:
        """Slab test: para cada eixo, calcula o intervalo [t1, t2] em que o raio
        está dentro do par de planos da AABB. A interseção dos três intervalos
        (eixos X, Y, Z) só é não-vazia se o raio realmente atravessa a caixa."""
        EPS = 1e-12
        origem_xyz  = (raio.origem.x,  raio.origem.y,  raio.origem.z)
        direcao_xyz = (raio.direcao.x, raio.direcao.y, raio.direcao.z)

        tmin = float("-inf")
        tmax = float("inf")

        for axis in range(3):
            o = origem_xyz[axis]
            d = direcao_xyz[axis]
            bmin = self.bbox_min[axis]
            bmax = self.bbox_max[axis]

            if abs(d) < EPS:
                # Raio paralelo a esse par de planos: só passa se a origem já está dentro
                if o < bmin or o > bmax:
                    return False
                continue

            t1 = (bmin - o) / d
            t2 = (bmax - o) / d
            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > tmin:
                tmin = t1
            if t2 < tmax:
                tmax = t2
            if tmin > tmax:
                return False

        # tmax >= 0 garante que a caixa não está inteiramente atrás do raio
        return tmax >= 0
