import pandas as pd
import re

# Función para limpiar los nombres de las competencias
def clean_competence_name(name):
    return re.sub(r'^\d+\.\s*', '', name)

# Leer el archivo CSV principal
data = pd.read_csv("3W-DICIEMBRE-MEX-jobposts_competences_llm.csv")

# Limpiar los nombres de las competencias en la columna competences_llm
data["competences_llm"] = data["competences_llm"].apply(lambda x: [clean_competence_name(comp.strip()) for comp in str(x).split("\n") if comp.strip()])

# Leer el archivo CSV de clasificación
classification_data = pd.read_csv("tax-infocomm-3w-diciembre-MEX-2024.csv")

# Filtrar competencias que aparecen al menos 50 veces
competence_counts = {}
for competences in data["competences_llm"]:
    for comp in competences:
        competence_counts[comp] = competence_counts.get(comp, 0) + 1

filtered_competences = {comp for comp, count in competence_counts.items() if count >= 50}
data["competences_llm"] = data["competences_llm"].apply(lambda x: [comp for comp in x if comp in filtered_competences])

# Filtrar y guardar competencias por categoría
categories = ["Knowledge", "Skill", "Ability", "Other"]
for category in categories:
    category_competences = classification_data[classification_data["Label"] == category]["Competence"]
    category_data = data.copy()
    category_data["competences_llm"] = category_data["competences_llm"].apply(lambda x: [comp for comp in x if comp in category_competences.values])
    category_data.to_csv(f"{category.lower()}_competences.csv", index=False)
    print(f"Guardado archivo para la categoría: {category}")