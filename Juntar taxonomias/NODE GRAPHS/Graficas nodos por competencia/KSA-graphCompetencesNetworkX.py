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

# Función para limpiar los nombres de las competencias
def clean_competence_name(name):
    return re.sub(r'^\d+\.\s*', '', name)

# Leer el archivo CSV principal
start_time = time.time()
data = pd.read_csv("3W-DICIEMBRE-MEX-jobposts_competences_llm.csv")
print(f"Tiempo de lectura del CSV: {time.time() - start_time:.2f} segundos")

# Limpiar los nombres de las competencias en la columna competences_llm
start_time = time.time()
data["competences_llm"] = data["competences_llm"].apply(lambda x: [clean_competence_name(comp.strip()) for comp in str(x).split("\n") if comp.strip()])
print(f"Tiempo de limpieza de nombres de competencias: {time.time() - start_time:.2f} segundos")

# Leer el archivo CSV de clasificación
classification_data = pd.read_csv("tax-infocomm-3w-diciembre-MEX-2024.csv")

# Filtrar competencias que aparecen al menos 100 veces
start_time = time.time()
competence_counts = {}
for competences in data["competences_llm"]:
    for comp in competences:
        competence_counts[comp] = competence_counts.get(comp, 0) + 1

filtered_competences = {comp for comp, count in competence_counts.items() if count >= 50}
data["competences_llm"] = data["competences_llm"].apply(lambda x: [comp for comp in x if comp in filtered_competences])
print(f"Tiempo de filtrado de competencias: {time.time() - start_time:.2f} segundos")

# Filtrar competencias por categoría y crear gráficos
categories = ["Knowledge", "Skill", "Ability", "Other"]
for category in categories:
    print(f"Procesando categoría: {category}")
    start_time = time.time()
    
    # Filtrar competencias por categoría
    category_competences = classification_data[classification_data["Label"] == category]["Competence"]
    category_data = data.copy()
    category_data["competences_llm"] = category_data["competences_llm"].apply(lambda x: [comp for comp in x if comp in category_competences.values])
    
    # Crear el grafo
    G = nx.Graph()
    edge_weights = {}

    # Procesar cada fila del DataFrame
    for competences in category_data["competences_llm"]:
        for comp1, comp2 in combinations(competences, 2):
            if (comp1, comp2) in edge_weights:
                edge_weights[(comp1, comp2)] += 1
            elif (comp2, comp1) in edge_weights:
                edge_weights[(comp2, comp1)] += 1
            else:
                edge_weights[(comp1, comp2)] = 1
    print(f"Tiempo de construcción de aristas: {time.time() - start_time:.2f} segundos")

    # Agregar nodos y aristas al grafo con el criterio de mínimo 5 matches
    start_time = time.time()
    for (comp1, comp2), weight in edge_weights.items():
        if weight >= 5:
            G.add_edge(comp1, comp2, weight=weight)
    print(f"Tiempo de agregar nodos y aristas: {time.time() - start_time:.2f} segundos")

    # Asegurar que todas las competencias seleccionadas están como nodos
    start_time = time.time()
    for comp in filtered_competences:
        if comp not in G:
            G.add_node(comp)
    print(f"Tiempo de agregar nodos aislados: {time.time() - start_time:.2f} segundos")

    # Filtrar nodos con menos de 10 conexiones
    nodes_to_remove = [node for node, degree in dict(G.degree()).items() if degree < 10]
    G.remove_nodes_from(nodes_to_remove)

    # Asignar colores a los nodos
    start_time = time.time()
    colors = list(mcolors.TABLEAU_COLORS.values())
    random.shuffle(colors)
    node_colors = {node: colors[i % len(colors)] for i, node in enumerate(G.nodes())}
    print(f"Tiempo de asignación de colores: {time.time() - start_time:.2f} segundos")

    # Tamaño de nodos basado en su grado (cantidad de conexiones)
    start_time = time.time()
    node_sizes = [((G.degree(node) // 10 + 1) ** 2) * 1 for node in G.nodes()]
    print(f"Tiempo de cálculo de tamaños de nodos: {time.time() - start_time:.2f} segundos")

    # Posiciones de nodos
    start_time = time.time()
    pos = nx.spring_layout(G, seed=42, k=2)
    print(f"Tiempo de cálculo de posiciones de nodos: {time.time() - start_time:.2f} segundos")

    # Obtener pesos de conexiones
    start_time = time.time()
    edges = nx.get_edge_attributes(G, 'weight')
    print(f"Tiempo de obtención de pesos de conexiones: {time.time() - start_time:.2f} segundos")

    # Crear segmentos de líneas para las aristas
    start_time = time.time()
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
    print(f"Tiempo de procesamiento de aristas: {time.time() - start_time:.2f} segundos")

    # Crear colección de líneas
    start_time = time.time()
    lc = LineCollection(edge_segments, linewidths=[max(weight, 0.5) for weight in edges.values()], colors=edge_colors, alpha=0.6)
    print(f"Tiempo de creación de la colección de líneas: {time.time() - start_time:.2f} segundos")

    # Dibujar el grafo
    start_time = time.time()
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=[node_colors[node] for node in G.nodes()], alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=9, font_family="Arial")
    ax = plt.gca()
    ax.add_collection(lc)
    plt.title(f"Red de Competencias - {category}", fontsize=14)
    plt.axis("off")
    plt.show()
    print(f"Tiempo total de dibujo del grafo: {time.time() - start_time:.2f} segundos")