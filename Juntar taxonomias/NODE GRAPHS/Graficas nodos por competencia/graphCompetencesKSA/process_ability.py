import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from itertools import combinations
from matplotlib.colors import to_rgb
from matplotlib.collections import LineCollection
import random
import time
import re

#Variables
minimum_repetitions = 20  #para filtrarlas, entre más alto, menos competencias
minimum_weight = 5  #para filtrar las conexiones, entre más alto, menos conexiones
minimum_connections = 4    #para filtrar los nodos, entre más alto, menos nodos
node_size = 6   #tamaño de los nodos
node_separation = 2   #separación entre nodos

# Función para limpiar los nombres de las competencias
def clean_competence_name(name):
    return re.sub(r'^\d+\.\s*', '', name)

# Leer archivos CSV
data = pd.read_csv("3W-DICIEMBRE-MEX-jobposts_competences_llm.csv")
classification = pd.read_csv("tax-infocomm-3w-diciembre-MEX-2024.csv")

# Limpiar los nombres de las competencias en la columna competences_llm
data["competences_llm"] = data["competences_llm"].apply(lambda x: [clean_competence_name(comp.strip()) for comp in str(x).split("\n") if comp.strip()])

# Filtrar competencias que aparecen al menos n veces

competence_counts = {}
for competences in data["competences_llm"]:
    for comp in competences:
        competence_counts[comp] = competence_counts.get(comp, 0) + 1
filtered_competences = {comp for comp, count in competence_counts.items() if count >= minimum_repetitions}
data["competences_llm"] = data["competences_llm"].apply(lambda x: [comp for comp in x if comp in filtered_competences])

# Unir con la clasificación de competencias
classification = classification[['Competence', 'Label']]
classification = classification[classification['Competence'].isin(filtered_competences)]

# Filtrar por categorías
def process_category(label):
    print(f"Procesando categoría: {label}")
    category_competences = set(classification[classification['Label'] == label]['Competence'])
    
    category_data = data.copy()
    category_data["competences_llm"] = category_data["competences_llm"].apply(lambda x: [comp for comp in x if comp in category_competences])
    category_data = category_data[category_data["competences_llm"].str.len() > 1]
    
    # Construir el grafo, con peso minimo N para hacer una conexión
    G = nx.Graph()
    edge_weights = {}
    for competences in category_data["competences_llm"]:
        for comp1, comp2 in combinations(competences, 2):
            if (comp1, comp2) in edge_weights:
                edge_weights[(comp1, comp2)] += 1
            elif (comp2, comp1) in edge_weights:
                edge_weights[(comp2, comp1)] += 1
            else:
                edge_weights[(comp1, comp2)] = 1
    
    for (comp1, comp2), weight in edge_weights.items():
        if weight >= minimum_weight:
            G.add_edge(comp1, comp2, weight=weight)
    
    for comp in category_competences:
        if comp not in G:
            G.add_node(comp)
    
    # Filtrar nodos con menos de n conexiones
    nodes_to_remove = [node for node, degree in dict(G.degree()).items() if degree < minimum_connections]
    G.remove_nodes_from(nodes_to_remove)
    
    # Asignar colores a los nodos
    colors = list(mcolors.TABLEAU_COLORS.values())
    random.shuffle(colors)
    node_colors = {node: colors[i % len(colors)] for i, node in enumerate(G.nodes())}
    
    # Tamaño de nodos basado en su grado
    node_sizes = [((G.degree(node) + 1) ** 2) * node_size for node in G.nodes()]
    
    # Posiciones de nodos
    pos = nx.spring_layout(G, seed=42, k=node_separation)
    
    # Obtener pesos de conexiones
    edges = nx.get_edge_attributes(G, 'weight')
    
    # Crear segmentos de líneas para las aristas
    edge_segments = []
    edge_colors = []
    for (node1, node2), weight in edges.items():
        x1, y1 = pos[node1]
        x2, y2 = pos[node2]
        edge_segments.append([(x1, y1), (x2, y2)])
        color1 = np.array(to_rgb(node_colors[node1]))
        color2 = np.array(to_rgb(node_colors[node2]))
        blended_color = (color1 + color2) / 2
        edge_colors.append(blended_color)
    
    lc = LineCollection(edge_segments, linewidths=[max(weight/30, 0.5) for weight in edges.values()], colors=edge_colors, alpha=0.6)
    
    # Dibujar el grafo
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=[node_colors[node] for node in G.nodes()], alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=9, font_family="Arial")
    ax = plt.gca()
    ax.add_collection(lc)
    plt.title(f"Red de Competencias - {label}", fontsize=14)
    plt.axis("off")
    plt.show()
    
    # Guardar el subconjunto en un archivo CSV
    category_data.to_csv(f"competences_{label.lower()}.csv", index=False)

# Procesar cada categoría
process_category("Ability")
