import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from itertools import combinations
from matplotlib.colors import to_rgb
from matplotlib.collections import LineCollection
import ast
import re
from matplotlib import font_manager
import community as community_louvain

# Configuración
competences_folder = "jobposts_competences_llm/"
taxonomy_folder = "tax-infocomm/"
synonym_map_path = "k_tax.csv"

# Parámetros
minimum_repetitions = 350
minimum_weight = 105
grosor_conexiones = 150 #entre mayor, menor grosor de conexiones
minimum_connections = 50
node_size = 5
node_separation = 10
community_resolution = 3
label_alpha = 0.6

# Fuente Lato
font_manager.fontManager.addfont('fonts/Lato-Regular.ttf')
plt.rcParams['font.family'] = 'Lato'

# Función para limpiar nombre de competencias
def clean_competence_name(name):
    return re.sub(r'^\d+\.\s*', '', name)

# Función para construir mapa de sinónimos
def build_merge_map(csv_path: str) -> dict:
    df_map = pd.read_csv(csv_path, header=None)
    synonym_map = {}
    for _, row in df_map.iterrows():
        parent = row[0]
        synonyms_list = ast.literal_eval(row[1])
        for syn in synonyms_list:
            synonym_map[syn] = parent
    def_map = {
        "Problem-solving": "Problem-solving",
        "Problem-solving skills": "Problem-solving",
        "Software development": "Software engineering",
        "Software engineering": "Software engineering",
        "Communication": "Communication",
        "Communication skills": "Communication",
        "Collaboration": "Collaboration",
        "Collaboration skills": "Collaboration",
    }
    synonym_map.update(def_map)
    return synonym_map

# Cargar mapa de sinónimos
synonym_map = build_merge_map(synonym_map_path)

# Unir múltiples archivos
all_data = []
all_classifications = []

for file in os.listdir(competences_folder):
    if file.endswith(".csv"):
        name = file.replace("-jobposts_competences_llm.csv", "").lower()
        comp_path = os.path.join(competences_folder, file)
        tax_file = f"tax-infocomm-{name}-2024.csv"
        tax_path = os.path.join(taxonomy_folder, tax_file)

        data = pd.read_csv(comp_path)
        data["competences_llm"] = data["competences_llm"].apply(
            lambda x: [clean_competence_name(synonym_map.get(comp.strip(), comp.strip())) for comp in str(x).split("\n") if comp.strip()]
        )
        all_data.append(data)

        if os.path.exists(tax_path):
            classification = pd.read_csv(tax_path)
            all_classifications.append(classification)
        else:
            print(f"⚠️ Archivo de taxonomía no encontrado: {tax_file}")

# DataFrame unificado
if not all_data:
    raise ValueError("❌ No se encontraron archivos de competencias.")

if not all_classifications:
    raise ValueError("❌ No se encontraron archivos de taxonomía correspondientes.")

full_data = pd.concat(all_data, ignore_index=True)
full_classification = pd.concat(all_classifications, ignore_index=True)
full_classification = full_classification[['Competence', 'Label']]

# Recontar competencias y filtrar
competence_counts = {}
for competences in full_data["competences_llm"]:
    for comp in competences:
        competence_counts[comp] = competence_counts.get(comp, 0) + 1

filtered_competences = {comp for comp, count in competence_counts.items() if count >= minimum_repetitions}
full_data["competences_llm"] = full_data["competences_llm"].apply(lambda x: [comp for comp in x if comp in filtered_competences])
full_classification = full_classification[full_classification['Competence'].isin(filtered_competences)]

# --- GRAFICADOR ---
def process_category(label):
    print(f"Procesando categoría: {label}")
    category_competences = set(full_classification[full_classification['Label'] == label]['Competence'])

    category_data = full_data.copy()
    category_data["competences_llm"] = category_data["competences_llm"].apply(lambda x: [comp for comp in x if comp in category_competences])
    category_data = category_data[category_data["competences_llm"].str.len() > 1]

    G = nx.Graph()
    edge_weights = {}
    for competences in category_data["competences_llm"]:
        for comp1, comp2 in combinations(competences, 2):
            key = tuple(sorted((comp1, comp2)))
            edge_weights[key] = edge_weights.get(key, 0) + 1

    for (comp1, comp2), weight in edge_weights.items():
        if weight >= minimum_weight:
            G.add_edge(comp1, comp2, weight=weight)

    for comp in category_competences:
        if comp not in G:
            G.add_node(comp)

    nodes_to_remove = [node for node, degree in dict(G.degree()).items() if degree < minimum_connections]
    G.remove_nodes_from(nodes_to_remove)

    partition = community_louvain.best_partition(G, resolution=community_resolution)
    unique_clusters = list(set(partition.values()))
    colors = ['#386191', '#77ABD2', '#5CC09B', '#F8D660', '#EAE9E6']
    cluster_colors = {cluster: colors[i % len(colors)] for i, cluster in enumerate(unique_clusters)}
    node_colors = {node: cluster_colors[partition[node]] for node in G.nodes()}
    node_sizes = [((G.degree(node) + 1) ** 2) * node_size for node in G.nodes()]
    pos = nx.spring_layout(G, seed=42, k=node_separation)

    edges = nx.get_edge_attributes(G, 'weight')
    edge_segments, edge_colors = [], []
    for (node1, node2), weight in edges.items():
        x1, y1 = pos[node1]
        x2, y2 = pos[node2]
        edge_segments.append([(x1, y1), (x2, y2)])
        blended_color = (np.array(to_rgb(node_colors[node1])) + np.array(to_rgb(node_colors[node2]))) / 2
        edge_colors.append(blended_color)

    lc = LineCollection(edge_segments, linewidths=[max(weight/grosor_conexiones, 0.5) for weight in edges.values()], colors=edge_colors, alpha=0.6)

    plt.figure(figsize=(12, 8))
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), alpha=0.6)
    ax = plt.gca()
    ax.add_collection(lc)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=[node_colors[node] for node in G.nodes()], alpha=0.95)
    nx.draw_networkx_labels(
        G, pos, font_size=11, font_family="Lato", font_color='black',
        bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2', alpha=label_alpha)
    )
    plt.title(f"Competence Network - {label}", fontsize=18, fontfamily="Lato", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.5'))
    plt.axis("off")
    plt.show()

    category_data.to_csv(f"competences_{label.lower()}.csv", index=False)

# Ejecutar categoría
process_category("Knowledge")
