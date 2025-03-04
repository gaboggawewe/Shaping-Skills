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
tax_data = pd.read_csv("tax-infocomm-junio-diciembre-SF-2024.csv")

# Diccionario de subsectores y sus ocupaciones
subsectors = {
    "Business intelligence and IT systems design": [
        "ICT sales professional",
        "Marketing manager",
        "Product analyst",
        "Product manager",
        "Product designer",
        "Business Intelligence professional"
    ],
    "Software engineering": [
        "Infraestructure engineer",
        "Computer Systems Analyst",
        "Software infrastructure architect",
        "Web developer",
        "Software developer",
        "App developer",
        "User interface designer",
        "Software engineer",
        "Software architect",
        "Software Quality Assurance Analysts and Testers",
        "Embedded systems engineer",
        "Web and Digital Interface Designers"
    ],
    "Database and network management and design": [
        "Database infrastructure engineer",
        "Network architect",
        "Database Administrators",
        "Database Architects",
        "Network and Computer Systems Administrator"
    ],
    "Data science and AI": [
        "Artificial intelligence engineer",
        "Machine Learning engineer",
        "Data science engineer",
        "Data analyst",
        "Data scientist",
        "Artificial Intelligence scientist",
        "Data architect"
    ],
    "Cyber security": [
        "ICT security specialist",
        "IT security operations",
        "Information Security Analysts",
        "Product Security and IT Security Integration Specialist",
        "Product risk specialist",
        "Security architect"
    ],
    "Operations and Support": [
        "Database support engineer",
        "Data center operations engineer",
        "Support systems engineer",
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
    tax_net.add_edge(src, dst, value=weight, title=f"Weight: {weight}", width=weight * 2)

tax_net.barnes_hut() #Se utiliza para darle estabilidad a los notos, para que queden fijos y se visualicen de mejor manera
# Guardar visualización
# Guardar visualización
tax_net.show(f"{selected_subsector}.html", notebook=False)