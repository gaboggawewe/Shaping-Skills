import pandas as pd

csv_path = "3W-DICIEMBRE-MEX-jobposts_competences_llm.csv"

try:
    df = pd.read_csv(csv_path, delimiter='\t', on_bad_lines='warn', encoding='utf-8')
    df.columns = df.columns.str.strip()  # Elimina espacios en los nombres de las columnas
    print("Columnas encontradas:", df.columns.tolist())  # Verifica los nombres de las columnas
except pd.errors.ParserError as e:
    print(f"Error al leer el CSV: {e}")
