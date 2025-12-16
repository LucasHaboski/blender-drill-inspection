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


# CONFIGURAÇÕES DO USUÁRIO (troque a pasta)
OUTPUT_DIR = r"C:\Users\Lucas Haboski\Desktop\dataset_final_v25"
FILE_PREFIX = "Ref_Drill_103-418_" # Nome de cada foto

# CONFIGURAÇÕES DE CAPTURA
TOTAL_PHOTOS = 60           # 1 foto cada 6 graus
ROTATION_STEP = 360 / TOTAL_PHOTOS

# CONFIGURAÇÂO CÂMERA
RESOLUTION_X = 2224
RESOLUTION_Y = 2224
FOCAL_LENGTH = 100.0
SENSOR_WIDTH = 36.0
CAM_DISTANCE = 0.24
CAM_HEIGHT = -0.0175 

def setup_scene_final():
    print("Configurando Motor Cycles (Qualidade Final)...")
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    
    scene.cycles.samples = 512 
    scene.cycles.use_adaptive_sampling = True
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    
    try:
        
        scene.view_settings.view_transform = 'AgX'
        scene.view_settings.look = 'AgX - High Contrast' 
        
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        scene.cycles.device = 'GPU'
        
        
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get('Background')
        if bg: bg.inputs[0].default_value = (0, 0, 0, 1) 
    except: pass

def setup_material_v25_steel(obj):
    """ 
    Material V25: Aço Escuro (0.02) com Roughness 0.30.
    Equilíbrio ideal entre corpo escuro e bordas brilhantes.
    """
    mat_name = "Steel_Final_Master_V25"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.30 
        # Cor Base: Quase preto (0.02)
        bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
    
    if obj.data.materials: obj.data.materials[0] = mat
    else: obj.data.materials.append(mat)

def create_blister_final():
    """ 
    Fundo: Plástico Cinza Claro com Textura.
    TRUQUE: Invisível para reflexo da broca.
    """
    if "Blister_Plane" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Blister_Plane"], do_unlink=True)

    bpy.ops.mesh.primitive_plane_add(size=0.5, enter_editmode=False, align='WORLD')
    plane = bpy.context.active_object
    plane.name = "Blister_Plane"
    plane.location = (0, 0.02, 0) 
    plane.rotation_euler = (math.radians(90), 0, 0)

    plane.visible_glossy = False 

    mat = bpy.data.materials.new(name="Plastic_Blister_Final")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    if bsdf:
        # Cor Base: 0.6 (Cinza claro)
        bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1.0) 
        bsdf.inputs["Roughness"].default_value = 0.5
        bsdf.inputs["Metallic"].default_value = 0.0
        
        # Textura Procedural
        noise = nodes.new(type="ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 150.0 
        noise.inputs["Detail"].default_value = 2.0
        bump = nodes.new(type="ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.05 
        
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    
    plane.data.materials.append(mat)

def setup_lighting_final_v25():
    """ 
    Iluminação V25: Spread 160 para as bordas.
    Energia: 15 Watts.
    """
    for obj in bpy.data.objects:
        if "Luz_" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)

    light_y_pos = -CAM_DISTANCE + 0.02 
    energy_per_bar = 15.0 
    
    bar_len = 0.12; bar_wid = 0.04; offset = 0.07   
    lights_config = [
        ("Luz_Top", 0, CAM_HEIGHT + offset, 0, bar_len, bar_wid),
        ("Luz_Bottom", 0, CAM_HEIGHT - offset, 0, bar_len, bar_wid),
        ("Luz_Left", -offset, CAM_HEIGHT, 0, bar_wid, bar_len),
        ("Luz_Right", offset, CAM_HEIGHT, 0, bar_wid, bar_len)
    ]
    for name, pos_x, pos_z, rot_z, size_x, size_y in lights_config:
        light_data = bpy.data.lights.new(name=f"{name}_Data", type='AREA')
        light_data.energy = energy_per_bar
        light_data.shape = 'RECTANGLE'
        light_data.size = size_x; light_data.size_y = size_y
        
        # SPREAD 160: O segredo para os reflexos nas bordas
        light_data.spread = 160 
        
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (pos_x, light_y_pos, pos_z)
        light_obj.rotation_euler = (math.radians(90), 0, rot_z)

def setup_camera_final():
    scene = bpy.context.scene
    if "Camera_QC" in bpy.data.objects: cam_obj = bpy.data.objects["Camera_QC"]
    else:
        cam_data = bpy.data.cameras.new(name='Camera_QC')
        cam_obj = bpy.data.objects.new(name='Camera_QC', object_data=cam_data)
        bpy.context.collection.objects.link(cam_obj)
    cam_obj.data.lens = FOCAL_LENGTH
    cam_obj.data.sensor_width = SENSOR_WIDTH
    cam_obj.location = (0, -CAM_DISTANCE, CAM_HEIGHT)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cam_obj

def run_full_batch(target_obj):
    # Cria a pasta se não existir
    if not os.path.exists(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR)
            print(f"Pasta criada: {OUTPUT_DIR}")
        except OSError:
            print(f"ERRO CRÍTICO: Não foi possível criar a pasta {OUTPUT_DIR}")
            return

    print(f"--- INICIANDO GERAÇÃO FINAL ({TOTAL_PHOTOS} FOTOS) ---")
    print(f"Setup: V25 Gold Master | Samples: 512")
    
    original_rot_z = target_obj.rotation_euler[2]
    target_obj.rotation_euler[2] = 0 

    for i in range(TOTAL_PHOTOS):
        filename = f"{FILE_PREFIX}{i:02d}.png"
        bpy.context.scene.render.filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Renderiza a foto
        bpy.ops.render.render(write_still=True)
        print(f"-> Salvo: {filename} ({i+1}/{TOTAL_PHOTOS})")
        
        # Rotaciona para a próxima
        target_obj.rotation_euler[2] += math.radians(ROTATION_STEP)
    
    target_obj.rotation_euler[2] = original_rot_z
    print("--- PROCESSO CONCLUÍDO! Verifique a pasta. ---")

if __name__ == "__main__":
    obj_selecionado = bpy.context.active_object
    if obj_selecionado and obj_selecionado.type == 'MESH':
        setup_scene_final()
        setup_material_v25_steel(obj_selecionado)
        create_blister_final()
        setup_lighting_final_v25()
        setup_camera_final()
        
        # DISPARAR O LOTE FINAL
        run_full_batch(obj_selecionado)
    else:
        print("ERRO: Selecione a broca na tela antes de rodar.")