import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations
from matplotlib.colors import to_rgb
from matplotlib.collections import LineCollection
import community as community_louvain
import re

# Variables
minimum_weight = 1  # Queremos incluir todas las conexiones posibles
node_size = 1400
node_separation = 1
community_resolution = 2.5

print("Cargando archivos CSV...")
# Leer archivos CSV
data = pd.read_csv("3W-JULIO-MEX-jobposts_competences_llm.csv")
classification = pd.read_csv("tax-infocomm-3w-julio-MEX-2024.csv")

# Limpiar los nombres de las competencias
def clean_competence_name(name):
    return re.sub(r'^\d+\.\s*', '', name)

print("Limpiando nombres de competencias...")
data["competences_llm"] = data["competences_llm"].fillna("").apply(lambda x: [clean_competence_name(comp.strip()) for comp in x.split("\n") if comp.strip()])

# Filtrar competencias de la categoría Knowledge
print("Filtrando competencias de la categoría Knowledge...")
classification = classification[['Competence', 'Label']]
knowledge_competences = set(classification[classification['Label'] == "Knowledge"]['Competence'])

# Filtrar las competencias en el dataset que están en la lista de "Knowledge"
data["competences_llm"] = data["competences_llm"].apply(lambda x: [comp for comp in x if comp in knowledge_competences])

data = data[data["competences_llm"].str.len() > 0]

# Contar frecuencia de competencias
print("Contando frecuencia de competencias...")
competence_counts = {}
for competences in data["competences_llm"]:
    for comp in competences:
        competence_counts[comp] = competence_counts.get(comp, 0) + 1

# Seleccionar las 10 competencias más comunes
print("Seleccionando top 10 competencias...")
top10_competences = sorted(competence_counts, key=competence_counts.get, reverse=True)[:10]
print("Top 10 competencias:", top10_competences)

# Filtrar los datos para que solo contengan esas 10 competencias
data["competences_llm"] = data["competences_llm"].apply(lambda x: [comp for comp in x if comp in top10_competences])
data = data[data["competences_llm"].str.len() > 1]

print("Construyendo grafo...")
# Construir el grafo solo con las 10 competencias
G = nx.Graph()
edge_weights = {}
for competences in data["competences_llm"]:
    for comp1, comp2 in combinations(competences, 2):
        if comp1 != comp2:  # Excluir autoconexiones
            edge_weights[(comp1, comp2)] = edge_weights.get((comp1, comp2), 0) + 1

for (comp1, comp2), weight in edge_weights.items():
    if weight >= minimum_weight:
        G.add_edge(comp1, comp2, weight=weight)

# Asegurar que los 10 nodos estén en el grafo
for comp in top10_competences:
    if comp not in G:
        G.add_node(comp)

print("Detectando comunidades...")
# Detectar comunidades
partition = community_louvain.best_partition(G, resolution=community_resolution)
unique_clusters = list(set(partition.values()))
colors = ['#386191', '#77ABD2', '#5CC09B', '#F8D660', '#EAE9E6']
cluster_colors = {cluster: colors[i % len(colors)] for i, cluster in enumerate(unique_clusters)}
node_colors = {node: cluster_colors[partition[node]] for node in G.nodes()}

# Tamaño de nodos basado en su grado
node_sizes = [node_size for _ in G.nodes()]

# Posiciones de nodos
print("Calculando posiciones de nodos...")
pos = nx.spring_layout(G, seed=42, k=node_separation)

# Obtener pesos de conexiones
edges = nx.get_edge_attributes(G, 'weight')

# Crear segmentos de líneas para las aristas
print("Preparando aristas para visualización...")
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

lc = LineCollection(edge_segments, linewidths=[max(weight/10, 1) for weight in edges.values()], colors=edge_colors, alpha=0.6)

print("Dibujando el grafo...")
# Dibujar el grafo
plt.figure(figsize=(8, 6))
nx.draw_networkx_edges(G, pos, alpha=0.6)
ax = plt.gca()
ax.add_collection(lc)
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=[node_colors[node] for node in G.nodes()], alpha=0.9)
nx.draw_networkx_labels(G, pos, font_size=11, font_family="Lato", font_color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
plt.title("Top 10 Knowledge Competences Network", fontsize=14, fontfamily="Lato", color='black')
plt.axis("off")
plt.show()

print("Guardando el CSV con los datos filtrados...")
# Guardar el subconjunto en un archivo CSV
data.to_csv("top10_knowledge_competences.csv", index=False)

print("Proceso completado.")
