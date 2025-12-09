import bpy
import math
import os

"""
GERADOR DE DATASET SINTÉTICO - BROCAS ODONTOLÓGICAS
---------------------------------------------------
Autor: Lucas Haboski
Projeto: Controle de Qualidade via Visão Computacional
Data: Dezembro/2025

Este script automatiza o Blender para gerar um dataset de 60 imagens (rotação 360°)
de uma broca odontológica, simulando um ambiente de estúdio controlado.
O objetivo é criar um modelo para treinamento de algoritmos
de detecção de defeitos.

COMO USAR:
1. Abra o arquivo .blend contendo o modelo 3D da broca.
2. Certifique-se de que a broca é o objeto ativo na Viewport.
3. Vá na aba 'Scripting' (A direita na barra superior), cole este código e clique em 'Run Script' (Play).
4. As imagens serão salvas na pasta configurada em OUTPUT_DIR.
"""

# Altere o caminho para a pasta onde deseja salvar as fotos.
OUTPUT_DIR = r"C:\Users\Lucas Haboski\Desktop\fotos_teste"

# Prefixo dos arquivos
FILE_PREFIX = "broca_padrao"

# --- CONFIGURAÇÕES DE CAPTURA ---
TOTAL_PHOTOS = 60          
ROTATION_STEP = 360 / TOTAL_PHOTOS

# --- PARÂMETROS DA CÂMERA (Sensor Full Frame 36mm) ---
RESOLUTION_X = 2224
RESOLUTION_Y = 2224
FOCAL_LENGTH = 100.0        # Lente Macro 100mm
SENSOR_WIDTH = 36.0
CAM_DISTANCE = 0.24        
CAM_HEIGHT = -0.0175        

def setup_scene_defaults():
    """Configura o motor Cycles, Samples e Perfil de Cor AgX."""
    print("Configurando Motor de Renderização...")
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    
    # Qualidade Industrial
    scene.cycles.samples = 256
    scene.cycles.use_adaptive_sampling = True
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    
    # Denoising + Contraste
    try:
        scene.view_settings.view_transform = 'AgX'
        scene.view_settings.look = 'AgX - High Contrast'
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        scene.cycles.device = 'GPU'
    except Exception as e:
        print(f"Aviso de Configuração: {e}")

def setup_lighting_ring_square():
    """
    Simula um Ring Light Quadrado acoplado à lente da câmera.
    Cria 4 Area Lights (Retangulares) ao redor do eixo de visão.
    """
    # Remove luzes antigas
    for obj in bpy.data.objects:
        if "Luz_" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Configuração do Ring Light
    light_y_pos = -CAM_DISTANCE + 0.01 
    
    energy_per_bar = 150.0  # Total 600W de luz distribuída
    
    # Dimensões das barras de luz
    bar_len = 0.10
    bar_wid = 0.02
    offset = 0.06   # Distância do centro da lente

    # Definição das 4 luzes: (Nome, Posição X, Posição Z, Rotação Z, Tamanho X, Tamanho Y)
    # Nota: CAM_HEIGHT é o centro Z da câmera.
    lights_config = [
        ("Luz_Ring_Top", 0, CAM_HEIGHT + offset, 0, bar_len, bar_wid),
        ("Luz_Ring_Bottom", 0, CAM_HEIGHT - offset, 0, bar_len, bar_wid),
        ("Luz_Ring_Left", -offset, CAM_HEIGHT, 0, bar_wid, bar_len),
        ("Luz_Ring_Right", offset, CAM_HEIGHT, 0, bar_wid, bar_len)
    ]

    for name, pos_x, pos_z, rot_z, size_x, size_y in lights_config:
        light_data = bpy.data.lights.new(name=f"{name}_Data", type='AREA')
        light_data.energy = energy_per_bar
        light_data.shape = 'RECTANGLE'
        light_data.size = size_x
        light_data.size_y = size_y
        
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        
        # Posiciona
        light_obj.location = (pos_x, light_y_pos, pos_z)
        
        # Aponta para frente (Y+)
        # Area lights apontam para -Z nativamente. Rotação X 90 as faz apontar para +Y.
        light_obj.rotation_euler = (math.radians(90), 0, rot_z)

def setup_camera_final():
    """Posiciona a câmera ortogonalmente para a captura."""
    scene = bpy.context.scene
    if "Camera_QC" in bpy.data.objects:
        cam_obj = bpy.data.objects["Camera_QC"]
    else:
        cam_data = bpy.data.cameras.new(name='Camera_QC')
        cam_obj = bpy.data.objects.new(name='Camera_QC', object_data=cam_data)
        bpy.context.collection.objects.link(cam_obj)

    cam_obj.data.lens = FOCAL_LENGTH
    cam_obj.data.sensor_width = SENSOR_WIDTH
    cam_obj.location = (0, -CAM_DISTANCE, CAM_HEIGHT)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cam_obj

def rotate_and_render_batch(target_obj):
    """Executa o loop de renderização e rotação."""

    if not os.path.exists(OUTPUT_DIR):
        print(f"ERRO CRÍTICO: A pasta '{OUTPUT_DIR}' não existe.")
        print("Crie a pasta ou ajuste a variável OUTPUT_DIR no script.")
        return 

    print(f"--- INICIANDO CAPTURA DE {TOTAL_PHOTOS} IMAGENS ---")
    print("O Blender pode congelar durante o processo. Isso é normal.")
    
    # Salva rotação original
    original_rot_z = target_obj.rotation_euler[2]
    target_obj.rotation_euler[2] = 0

    for i in range(TOTAL_PHOTOS):
        filename = f"{FILE_PREFIX}{i:02d}.png"
        bpy.context.scene.render.filepath = os.path.join(OUTPUT_DIR, filename)

        bpy.ops.render.render(write_still=True)
        print(f"Salvo: {filename} ({i+1}/{TOTAL_PHOTOS})")

        target_obj.rotation_euler[2] += math.radians(ROTATION_STEP)
    
    # Restaura o ponto inciial
    target_obj.rotation_euler[2] = original_rot_z
    print("--- CONCLUÍDO COM SUCESSO ---")


if __name__ == "__main__":
    obj_selecionado = bpy.context.active_object
    
    if obj_selecionado and obj_selecionado.type == 'MESH':
        print(f"Objeto selecionado: {obj_selecionado.name}")
        setup_scene_defaults()
        setup_lighting_ring_square() # Nova iluminação Ring Light
        setup_camera_final()
        
        # Inicia a geração
        rotate_and_render_batch(obj_selecionado)
    else:
        print("ERRO: Selecione o objeto 3D da broca na tela antes de rodar o script.")