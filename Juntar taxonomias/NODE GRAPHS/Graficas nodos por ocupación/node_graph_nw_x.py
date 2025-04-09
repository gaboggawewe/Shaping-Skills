import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from itertools import combinations
from matplotlib.colors import to_rgb
from matplotlib.collections import LineCollection
import random

# Leer el archivo CSV
tax_data = pd.read_csv("tax-infocomm-junio-diciembre-MEX-2024.csv")

# Diccionario de subsectores y sus ocupaciones
subsectors = {
    "Business intelligence and IT systems design": [
        "ICT sales professional", "Marketing manager", "Product analyst",
        "Product manager", "Product designer", "Business Intelligence professional"
    ],
    "Software engineering": [
        "Infraestructure engineer", "Computer Systems Analyst", "Software infrastructure architect",
        "Web developer", "Software developer", "App developer", "User interface designer",
        "Software engineer", "Software architect", "Software Quality Assurance Analysts and Testers",
        "Embedded systems engineer", "Web and Digital Interface Designers"
    ],
    "Database and network management and design": [
        "Database infrastructure engineer", "Network architect", "Database Administrators",
        "Database Architects", "Network and Computer Systems Administrator"
    ],
    "Data science and AI": [
        "Artificial intelligence engineer", "Machine Learning engineer", "Data science engineer",
        "Data analyst", "Data scientist", "Artificial Intelligence scientist", "Data architect"
    ],
    "Cyber security": [
        "ICT security specialist", "IT security operations", "Information Security Analysts",
        "Product Security and IT Security Integration Specialist", "Product risk specialist",
        "Security architect"
    ],
    "Operations and Support": [
        "Database support engineer", "Data center operations engineer", "Support systems engineer",
        "Computer Network Support Specialists"
    ]
}

# Solicitar al usuario que elija un subsector
print("Seleccione un subsector:")
for i, subsector in enumerate(subsectors.keys(), 1):
    print(f"{i}. {subsector}")

choice = int(input("Ingrese el número del subsector: ")) - 1
selected_subsector = list(subsectors.keys())[choice]
selected_occupations = subsectors[selected_subsector]

# Filtrar el DataFrame para incluir solo las ocupaciones seleccionadas
tax_data = tax_data[tax_data["Occupation"].isin(selected_occupations)]

# Crear un diccionario para almacenar las ocupaciones y sus competencias
occupation_competences = {}

for _, row in tax_data.iterrows():
    occupation = row["Occupation"]
    competence = row["Competence"]

    if occupation not in occupation_competences:
        occupation_competences[occupation] = set()
    
    occupation_competences[occupation].add(competence)

# Crear el grafo utilizando NetworkX
G = nx.Graph()

# Agregar nodos y conexiones con pesos
for occupation1, occupation2 in combinations(selected_occupations, 2):
    if occupation1 in occupation_competences and occupation2 in occupation_competences:
        shared_competences = occupation_competences[occupation1] & occupation_competences[occupation2]
        if shared_competences:
            weight = len(shared_competences)
            G.add_edge(occupation1, occupation2, weight=weight)

# Agregar nodos aislados (sin conexiones)
for occupation in selected_occupations:
    if occupation not in G:
        G.add_node(occupation)

# Generar colores distintos para cada ocupación
colors = list(mcolors.TABLEAU_COLORS.values())  # Usamos una paleta de colores predefinida
random.shuffle(colors)  # Mezclamos los colores para asignarlos aleatoriamente
occupation_colors = {occupation: colors[i % len(colors)] for i, occupation in enumerate(selected_occupations)}

node_sizes = [((G.degree(node) + 1) ** 2) * 100 for node in G.nodes()]


# Calcular posiciones de los nodos
pos = nx.spring_layout(G, seed=42)

# Obtener los pesos de las conexiones
edges = nx.get_edge_attributes(G, 'weight')

# Crear una lista de segmentos de líneas para los edges
edge_segments = []
edge_colors = []

for (node1, node2), weight in edges.items():
    # Obtener posiciones de los nodos
    x1, y1 = pos[node1]
    x2, y2 = pos[node2]
    
    # Agregar segmento de línea
    edge_segments.append([(x1, y1), (x2, y2)])
    
    # Obtener colores de los nodos
    color1 = np.array(to_rgb(occupation_colors[node1]))  # Convertir a RGB
    color2 = np.array(to_rgb(occupation_colors[node2]))
    
    # Generar color intermedio basado en un peso (50/50)
    blended_color = (color1 + color2) / 2  # Promedio de colores
    
    edge_colors.append(blended_color)

# Crear la colección de líneas con los colores gradientes
lc = LineCollection(edge_segments, linewidths=[max(weight / 45, 0.5) for weight in edges.values()], colors=edge_colors, alpha=0.6)

# Dibujar el grafo
plt.figure(figsize=(12, 8))

# Dibujar nodos
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=[occupation_colors[node] for node in G.nodes()], alpha=0.8)

# Dibujar etiquetas
nx.draw_networkx_labels(G, pos, font_size=9, font_family="Arial")

# Agregar las líneas con gradiente al plot
ax = plt.gca()
ax.add_collection(lc)

# Ajustar y mostrar el grafo
plt.title(f"Red de Ocupaciones en {selected_subsector}", fontsize=14)
plt.axis("off")
plt.show()
