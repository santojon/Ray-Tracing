import sys

from src.Ponto import Ponto
from src.Vetor import Vetor
from src.Raio import Raio
from src.Esfera import Esfera
from src.Plano import Plano
from src.Malha import Malha
from utils.Scene.sceneParser import SceneJsonLoader


def base_camera(data):
    """Constrói a base ortonormal da câmera: três eixos perpendiculares entre si.

    w  aponta para TRÁS (de M em direção a C) — eixo de profundidade.
    u  aponta para a DIREITA — calculado como w × up.
    v  aponta para CIMA     — calculado como u × w.

    A ordem w × up (e não up × w) é necessária porque a cena usa a convenção
    de que +X no mundo equivale à direita da imagem. Com up × w o eixo u ficaria
    apontando para -X e a imagem sairia espelhada horizontalmente.

    Os vetores são normalizados para formar uma base ortonormal: comprimento 1
    garante que o parâmetro t das interseções corresponda à distância real."""
    C    = data.camera.lookfrom       # posição da câmera no mundo
    M    = data.camera.lookat         # ponto para onde a câmera aponta
    v_up = data.camera.up_vector      # vetor "para cima" do mundo (geralmente Y)

    w = (C - M).normalizar()                  # eixo de profundidade (aponta para trás)
    u = w.prodVetorial(v_up).normalizar()     # eixo horizontal (aponta para a direita)
    v = u.prodVetorial(w)                     # eixo vertical (aponta para cima)

    return C, u, v, w


def gerar_raio(i, j, C, u, v, w, largura, altura, d):
    """Gera o raio que passa pelo centro do pixel (i, j).

    Usa o modelo de câmera pinhole: a tela fica a d unidades à frente
    da câmera (C - w*d) e cada pixel é mapeado para coordenadas NDC.

    NDC (Normalized Device Coordinates): índices de pixel são convertidos
    para o intervalo [-aspect, +aspect] no eixo horizontal e [-1, +1] no
    vertical, com (0, 0) no centro exato da imagem.

    O +0.5 nos índices faz o raio passar pelo centro do pixel, não pelo canto.
    Multiplicar px pela razão de aspecto evita que objetos circulares apareçam
    como elipses em imagens não quadradas."""
    aspect = largura / altura

    px = (2 * (i + 0.5) / largura  - 1) * aspect   # coordenada horizontal NDC
    py =  1 - 2 * (j + 0.5) / altura               # coordenada vertical NDC (j=0 é o topo)

    # O ponto na tela é C - w*d + u*px + v*py. O vetor direção é esse ponto menos C,
    # o que cancela C e deixa só -w*d + u*px + v*py.
    direcao = ((-w) * d + u * px + v * py).normalizar()

    return Raio(C, direcao)


def criar_objetos(scene):
    """Converte os dados carregados do JSON em objetos de cena concretos.
    Itera sobre scene.objects e instancia Esfera ou Plano conforme o tipo,
    passando centro/ponto, dimensões e material de cada um."""
    objetos = []
    for obj in scene.objects:
        if obj.obj_type == "sphere":
            centro = obj.get_ponto("center")
            raio   = obj.get_num("radius")
            objetos.append(Esfera(centro, raio, obj.material))

        elif obj.obj_type == "plane":
            ponto  = obj.get_ponto("point_on_plane")
            normal = obj.get_vetor("normal")
            objetos.append(Plano(ponto, normal, obj.material))

        elif obj.obj_type == "mesh":
            path = obj.get_property("path")
            objetos.append(Malha(path, obj.material, obj.transforms))

    return objetos


def renderizar(scene_path="utils/input/sampleScene.json"):
    """Renderiza a cena e imprime o resultado no stdout no formato PPM.

    Para cada pixel (i, j) lança um raio e testa contra todos os objetos.
    O objeto com menor t (mais próximo da câmera) determina a cor do pixel.
    Se nenhum objeto for atingido, o pixel fica preto (fundo).

    A cor usada é a componente difusa bruta do material (kd), sem iluminação.
    O PPM é impresso no stdout — redirecionar para arquivo gera o arquivo de imagem."""
    scene   = SceneJsonLoader.load_file(scene_path)
    largura = scene.camera.image_width
    altura  = scene.camera.image_height
    d       = scene.camera.screen_distance

    C, u, v, w = base_camera(scene)
    objetos     = criar_objetos(scene)

    # Cabeçalho PPM: tipo P3 (texto RGB), dimensões e valor máximo por canal
    linhas = [f"P3\n{largura} {altura}\n255"]

    for j in range(altura):
        for i in range(largura):
            raio = gerar_raio(i, j, C, u, v, w, largura, altura, d)

            # Busca o objeto mais próximo: menor t positivo entre todas as interseções
            t_min    = float("inf")
            material = None

            for obj in objetos:
                t = obj.intersectar(raio)
                if t is not None and t < t_min:
                    t_min    = t
                    material = obj.material

            # Converte a cor difusa de [0.0, 1.0] para [0, 255] ou usa preto no fundo
            if material is not None:
                r = int(material.color.r * 255)
                g = int(material.color.g * 255)
                b = int(material.color.b * 255)
            else:
                r = g = b = 0

            linhas.append(f"{r} {g} {b}")

    sys.stdout.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    scene_file = sys.argv[1] if len(sys.argv) > 1 else "utils/input/sampleScene.json"
    renderizar(scene_file)
