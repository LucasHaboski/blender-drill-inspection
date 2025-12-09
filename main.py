import bpy
import math
import os

# --- CONFIGURAÇÕES GERAIS ---
# Pasta onde as fotos serão salvas (USE BARRAS DUPLAS OU INVERTIDAS NO WINDOWS)
OUTPUT_DIR = "C:\Users\Lucas Haboski\Desktop\fotos_teste" 
# Nome base do arquivo
FILE_PREFIX = "camera"

# --- CONFIGURAÇÕES DA CÂMERA ---
RESOLUTION_X = 2224
RESOLUTION_Y = 2224
FOCAL_LENGTH = 50.0  # Em mm (Ajuste este valor se o zoom estiver errado)
SENSOR_WIDTH = 36.0  # Padrão Full Frame (pode variar em câmeras industriais)
CAM_DISTANCE = 0.2   # 200mm convertidos para metros (Blender usa metros)

# --- CONFIGURAÇÕES DO LOOP ---
TOTAL_PHOTOS = 60
ROTATION_STEP = 360 / TOTAL_PHOTOS # 6 graus

def setup_scene():
    # 1. Configurar Resolução
    scene = bpy.context.scene
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    scene.render.resolution_percentage = 100
    
    # 2. Criar ou Buscar Câmera
    if "Camera_QC" in bpy.data.objects:
        cam_obj = bpy.data.objects["Camera_QC"]
    else:
        cam_data = bpy.data.cameras.new(name='Camera_QC')
        cam_obj = bpy.data.objects.new(name='Camera_QC', object_data=cam_data)
        bpy.context.collection.objects.link(cam_obj)
    
    # 3. Configurar Lente e Sensor
    cam_obj.data.lens = FOCAL_LENGTH
    cam_obj.data.sensor_width = SENSOR_WIDTH
    
    # 4. Posicionar Câmera
    # Posiciona a câmera em Y negativo (frente) na altura 0
    cam_obj.location = (0, -CAM_DISTANCE, 0)
    # Rotaciona para apontar para a origem (rotação em X de 90 graus)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    
    # Define essa câmera como a ativa
    scene.camera = cam_obj
    
    print(f"Câmera configurada a {CAM_DISTANCE}m com lente {FOCAL_LENGTH}mm")
    return cam_obj

def rotate_and_render(target_obj):
    # Cria diretório se não existir
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    original_rotation = target_obj.rotation_euler[2] # Salva rotação original Z
    
    print("Iniciando captura...")
    
    for i in range(TOTAL_PHOTOS):
        # 1. Define o nome do arquivo
        filename = f"{FILE_PREFIX}{i:02d}.png" # Ex: broca_ideal_00.png, broca_ideal_01.png
        bpy.context.scene.render.filepath = os.path.join(OUTPUT_DIR, filename)
        
        # 2. Renderiza
        bpy.ops.render.render(write_still=True)
        print(f"Renderizado: {filename} (Ângulo: {i * 6}°)")
        
        # 3. Rotaciona o objeto (Eixo Z)
        target_obj.rotation_euler[2] += math.radians(6)
        
    # Restaura rotação original (opcional)
    # target_obj.rotation_euler[2] = original_rotation
    print("Processo finalizado!")

# --- EXECUÇÃO ---
# Para usar: Selecione a BROCA na viewport 3D antes de rodar o script
obj_selecionado = bpy.context.active_object

if obj_selecionado:
    setup_scene()
    # Descomente a linha abaixo quando estiver pronto para gerar as 60 fotos:
    # rotate_and_render(obj_selecionado)
    print("Setup concluído. Verifique a câmera e descomente 'rotate_and_render' para rodar.")
else:
    print("ERRO: Por favor, selecione o objeto da broca antes de rodar o script.")