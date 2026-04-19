import sys

from src.Ponto import Ponto
from src.Vetor import Vetor
from src.Raio import Raio
from src.Esfera import Esfera
from src.Plano import Plano
from utils.Scene.sceneParser import SceneJsonLoader


# ---------------------------------------------------------------------------
# Base ortonormal da câmera
# ---------------------------------------------------------------------------

def base_camera(data):
    """
    Constrói os três eixos do sistema de coordenadas da câmera.

    w  aponta para TRÁS (de M em direção a C) — eixo de profundidade
    u  aponta para a DIREITA — produto vetorial de up com w
    v  aponta para CIMA     — produto vetorial de w com u

    Por que normalizar? Precisamos de uma base ortonormal: vetores com
    comprimento 1 para que o mapeamento de pixel → ponto na tela seja
    uniforme, sem distorção de escala.
    """
    C    = data.camera.lookfrom       # posição da câmera
    M    = data.camera.lookat         # alvo (centro da tela)
    v_up = data.camera.up_vector      # direção "para cima" do mundo

    w = (C - M).normalizar()                  # eixo Z da câmera (para trás)
    u = w.prodVetorial(v_up).normalizar()     # eixo X (direita)  —  w × up garante que +X do mundo caia à direita da imagem nesta convenção de cena
    v = u.prodVetorial(w)                     # eixo Y (cima) — já ortogonal, não precisa normalizar de novo

    return C, u, v, w


# ---------------------------------------------------------------------------
# Geração do raio para o pixel (i, j)
# ---------------------------------------------------------------------------

def gerar_raio(i, j, C, u, v, w, largura, altura, d):
    """
    Modelo de câmera pinhole:

      - O centro da tela está a 'd' unidades à frente da câmera: C - w*d
      - Cada pixel é mapeado para coordenadas NDC em [-1, 1] (height) e
        [-aspect, +aspect] (width), para preservar proporções.
      - O raio parte de C e aponta para o ponto correspondente na tela.

    NDC (Normalized Device Coordinates):
        px ∈ [-aspect, +aspect]   →  esquerda/direita
        py ∈ [-1, +1]             →  baixo/cima

    Por que subtrair 0.5 de (i+0.5)?
        Queremos o centro do pixel, não a borda.
    """
    aspect = largura / altura

    px = (2 * (i + 0.5) / largura  - 1) * aspect   # coordenada horizontal
    py =  1 - 2 * (j + 0.5) / altura               # coordenada vertical (j=0 → topo)

    # Direção = ponto na tela  -  câmera
    # Ponto na tela = C  -  w*d  +  u*px  +  v*py
    # Portanto: direção = -w*d + u*px + v*py  (sem C, pois se cancela)
    direcao = ((-w) * d + u * px + v * py).normalizar()

    return Raio(C, direcao)


# ---------------------------------------------------------------------------
# Cria os objetos da cena a partir dos dados carregados do JSON
# ---------------------------------------------------------------------------

def criar_objetos(scene):
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

    return objetos


# ---------------------------------------------------------------------------
# Renderizador principal
# ---------------------------------------------------------------------------

def renderizar(scene_path="utils/input/sampleScene.json"):
    scene   = SceneJsonLoader.load_file(scene_path)
    largura = scene.camera.image_width
    altura  = scene.camera.image_height
    d       = scene.camera.screen_distance

    C, u, v, w = base_camera(scene)
    objetos     = criar_objetos(scene)

    # Cabeçalho PPM (formato P3 = texto, RGB, valores 0-255)
    linhas = [f"P3\n{largura} {altura}\n255"]

    for j in range(altura):
        for i in range(largura):
            raio = gerar_raio(i, j, C, u, v, w, largura, altura, d)

            # Encontrar a intersecção mais próxima (menor t positivo)
            t_min    = float("inf")
            material = None

            for obj in objetos:
                t = obj.intersectar(raio)
                if t is not None and t < t_min:
                    t_min    = t
                    material = obj.material

            # Cor final: cor difusa (kd) do material atingido, ou preto
            if material is not None:
                r = int(material.color.r * 255)
                g = int(material.color.g * 255)
                b = int(material.color.b * 255)
            else:
                r = g = b = 0   # fundo preto

            linhas.append(f"{r} {g} {b}")

    sys.stdout.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    scene_file = sys.argv[1] if len(sys.argv) > 1 else "utils/input/sampleScene.json"
    renderizar(scene_file)
