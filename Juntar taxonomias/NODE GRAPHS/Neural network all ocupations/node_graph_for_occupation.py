# Neural Network
# Los nodos son las ocupaciones
# Se crea una arista cuando una ocupacion comparte un K,S o A con otra
# Si la arista ya existe, se le suma 1 de peso a la arista.

import pandas as pd
from pyvis.network import Network
from itertools import combinations

# Crear la red
tax_net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

# Leer el archivo
tax_data = pd.read_csv("tax-infocomm-junio-diciembre-MEX-2024.csv")

# Crear un diccionario para almacenar las ocupaciones y sus competencias
occupation_competences = {}

for index, row in tax_data.iterrows():
    occupation = row["Occupation"]
    competence = row["Competence"]

    if occupation not in occupation_competences:
        occupation_competences[occupation] = set()
    
    occupation_competences[occupation].add(competence)
    
    if index % 100000 == 0:
        print(f"Procesadas {index} filas de {len(tax_data)}")

# Crear diccionario de conexiones con pesos
edges = {}

# Comparar cada par de ocupaciones
occupations = list(occupation_competences.keys())

for idx, (src, dst) in enumerate(combinations(occupations, 2)):
    shared_competences = occupation_competences[src] & occupation_competences[dst]  # Intersección de competencias
    if shared_competences:  # Si comparten al menos una competencia
        if (src, dst) in edges:
            edges[(src, dst)] += len(shared_competences)
        elif (dst, src) in edges:
            edges[(dst, src)] += len(shared_competences)
        else:
            edges[(src, dst)] = len(shared_competences)  # Se inicializa con el número de competencias compartidas
    
    if idx % 100000 == 0:
        print(f"Procesadas {idx} comparaciones de {len(occupations) * (len(occupations) - 1) // 2}")

# Agregar nodos y conexiones al grafo
for (src, dst), weight in edges.items():
    tax_net.add_node(src, src, title=src)
    tax_net.add_node(dst, dst, title=dst)
    tax_net.add_edge(src, dst, value=weight, title=f"Weight: {weight}", width = weight)

tax_net.barnes_hut() #Se utiliza para darle estabilidad a los notos, para que queden fijos y se visualicen de mejor manera
# Guardar visualización
tax_net.show("tax_infocomm_network.html", notebook=False)

