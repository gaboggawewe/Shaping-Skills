import pandas as pd
import bar_chart_race as bcr
import os

# Ruta del archivo único con los datos
file_path = "ARCHIVO_GLOBAL/tax-infocomm-junio-diciembre-SF-2024-ratio-cured.csv"

# Directorio de salida para los videos
output_dir = "output_videos"
os.makedirs(output_dir, exist_ok=True)

# Leer archivo
try:
    data = pd.read_csv(file_path)
    print(f"Archivo leído exitosamente: {file_path}")
except Exception as e:
    print(f"Ocurrió un error al leer el archivo: {e}")
    exit()

# Multiplicar las columnas de ratio por 10,000
ratio_cols = [col for col in data.columns if col.startswith("ratio_")]
data[ratio_cols] = data[ratio_cols] * 10000

# Meses válidos (ignoramos junio)
valid_months = ['julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

# Ordenar las columnas sin errores y sin junio
ordered_columns = []
for col in ratio_cols:
    try:
        week_part, month_part = col.replace("ratio_", "").split('-')
        month = month_part.lower()
        if month in valid_months:
            week_number = int(''.join(filter(str.isdigit, week_part)))  # Extrae 1 o 3 de 1w/3w
            ordered_columns.append((col, valid_months.index(month), week_number))
    except Exception as e:
        print(f"Error ordenando columna {col}: {e}")

# Ordenar correctamente
ordered_columns.sort(key=lambda x: (x[1], x[2]))  # Primero mes, luego semana
ordered_columns = [col[0] for col in ordered_columns]

# Función para procesar por Label
def process_category(label):
    filtered = data[data['Label'] == label]

    # Agrupar por Competence y sumar los ratios
    summed = filtered[["Competence"] + ordered_columns].groupby("Competence").sum()

    # Calcular suma total por competencia para filtrar top 10
    summed['total'] = summed.sum(axis=1)
    top10_competences = summed.nlargest(10, 'total').index

    # Filtrar solo top 10
    top10_df = summed.loc[top10_competences].drop(columns='total').reset_index()

    # Transformar a formato largo
    long_df = pd.melt(top10_df, id_vars='Competence', var_name='File', value_name='Count')

    # Ajustar nombre de las "fechas" (sin "ratio_")
    long_df['File'] = long_df['File'].str.replace("ratio_", "").str.upper()

    # Ordenar por fechas
    file_order = [col.replace("ratio_", "").upper() for col in ordered_columns]
    long_df['File'] = pd.Categorical(long_df['File'], categories=file_order, ordered=True)
    long_df = long_df.sort_values(by=['Competence', 'File'])

    # Acumulado
    long_df['Cumulative_Count'] = long_df.groupby('Competence')['Count'].cumsum()

    return long_df

# Función para crear el bar chart race
def create_bcr(df, filename, title):
    grouped = df.groupby(['File', 'Competence'], as_index=False)['Cumulative_Count'].sum()

    pivot_df = grouped.pivot(index='File', columns='Competence', values='Cumulative_Count').fillna(0)

    bcr.bar_chart_race(
        df=pivot_df,
        filename=os.path.join(output_dir, filename),
        title=title,
        steps_per_period=40,
        period_length=1200,
        dpi = 800
    )

# Generar datos por categoría
knowledge_data = process_category('Knowledge')
skill_data = process_category('Skill')
ability_data = process_category('Ability')

# Crear los videos
create_bcr(knowledge_data, "knowledge_race.mp4", "Top 10 Knowledge Competences")
create_bcr(skill_data, "skill_race.mp4", "Top 10 Skill Competences")
create_bcr(ability_data, "ability_race.mp4", "Top 10 Ability Competences")

print("¡Barchart races generados exitosamente!")
