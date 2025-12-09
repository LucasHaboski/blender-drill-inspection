# Blender Drill Inspection

## Objetivo
Este projeto visa automatizar a geração de datasets de imagens sintéticas para o Controle de Qualidade (QC) de brocas odontológicas. Utilizando Python e a API do Blender (`bpy`), o sistema simula um ambiente de estúdio industrial para criar imagens de referência ("Golden Master") baseadas em desenhos técnicos rigorosos.

O objetivo final é utilizar essas imagens para treinar algoritmos de Visão Computacional capazes de detectar defeitos ou desvios geométricos em brocas reais na linha de produção.

## Funcionalidades
- **Geração Automatizada:** Captura 60 imagens cobrindo 360° do objeto (passo de 6°).
- **Fidelidade Geométrica:** Baseado nas especificações técnicas da broca (ISO 2768-1).
- **Renderização Realista (Cycles):** Simulação de materiais metálicos (High Contrast AgX) e iluminação de estúdio para facilitar a detecção de bordas.
- **Denoising:** Uso de IA (OpenImageDenoise) para limpeza de ruído no render.

## Tecnologias
- Python 3.13.7
- **Blender 4.0+ / 5.0 (Alpha)**: Motor de renderização e modelagem.

### Pré-requisitos
1. Ter o Blender instalado.
2. Possuir o arquivo `.blend` com o modelo 3D da broca (corrigido conforme desenho técnico).

### Passo a Passo
1. Abra o arquivo do modelo no Blender.
2. Navegue até a aba **Scripting**.
3. Abra o arquivo `src/generate_dataset.py`.
4. Edite a variável `OUTPUT_DIR` no início do script para a pasta desejada.
5. Selecione o objeto da broca na viewport 3D.
6. Clique no botão **Play** (Run Script).

## 👤 Autor
Desenvolvido por Lucas Haboski.
