from graphviz import Digraph
from PIL import Image

dot = Digraph('Forrester_CrowdStrike_Incident_July2024', format='png')
dot.attr(rankdir='LR', size='12,6')
dot.attr('node', shape='rectangle', style='filled', fillcolor='#a8d0e6', fontname='Helvetica', fontsize='10')

# Stocks (niveles)
dot.node('SOF', 'Sistemas Operativos Funcionales')
dot.node('SA', 'Sistemas Afectados')

# Flujos (usaremos óvalos)
dot.attr('node', shape='oval', fillcolor='#f76c6c')
dot.node('DU', 'Despliegue de Actualización')
dot.node('DE', 'Detección de Errores')

# Variables auxiliares (elipses)
dot.attr('node', shape='ellipse', fillcolor='#ffd166')
dot.node('TR', 'Tiempo de Respuesta')
dot.node('NT', 'Número de Técnicos Disponibles')

# Relaciones con flechas y signos (+ / -)

# Despliegue de actualización
dot.edge('SOF', 'DU', label='Fuente', color='black')
dot.edge('DU', 'SOF', label='-', color='red')  # disminuye funcionales
dot.edge('DU', 'SA', label='+', color='green')  # aumenta afectados

# Detección de errores
dot.edge('SA', 'DE', label='Fuente', color='black')
dot.edge('DE', 'SA', label='-', color='red')  # reduce afectados

# Influencias en detección de errores
dot.edge('TR', 'DE', label='-', color='red')  # Menor TR aumenta DE (signo negativo)
dot.edge('NT', 'DE', label='+', color='green')  # Más técnicos aumentan DE

# Agregar leyenda para colores y signos
with dot.subgraph(name='cluster_legend') as c:
    c.attr(label='Leyenda')
    c.node('L1', 'Stock (Nivel)', shape='rectangle', style='filled', fillcolor='#a8d0e6')
    c.node('L2', 'Flujo', shape='oval', style='filled', fillcolor='#f76c6c')
    c.node('L3', 'Variable Auxiliar', shape='ellipse', style='filled', fillcolor='#ffd166')
    c.node('L4', '+: Influencia Positiva', shape='plaintext')
    c.node('L5', '-: Influencia Negativa', shape='plaintext')
    c.edges([('L1', 'L2'), ('L2', 'L3')])  # dummy edges for layout

# Guardar PNG
png_path = dot.render('forrester_crowdstrike_diagram', view=False)
print(f"Archivo PNG generado en: {png_path}")

# Convertir PNG a JPG
img = Image.open(png_path)
jpg_path = 'forrester_crowdstrike_diagram.jpg'
img.convert('RGB').save(jpg_path, 'JPEG')
print(f"Archivo JPG generado en: {jpg_path}")
