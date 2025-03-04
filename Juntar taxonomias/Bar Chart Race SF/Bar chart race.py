import pandas as pd
import bar_chart_race as bcr
import os
import glob

# Define the folder containing the CSV files
folder_path = "ARCHIVOS_CSV"

# Get a list of all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# Check if any CSV files were found
if not csv_files:
    print("No CSV files found in the specified folder.")
    exit()
else:
    print(f"Found {len(csv_files)} CSV files.")

# Read the grouped CSV file to determine the top 10 competences
grouped_file_path = "ARCHIVO_GLOBAL/tax-infocomm-junio-diciembre-SF-2024.csv"
try:
    grouped_data = pd.read_csv(grouped_file_path)
    print(f"Successfully read the grouped file: {grouped_file_path}")
except Exception as e:
    print(f"An error occurred while reading the grouped file: {e}")
    exit()

# Determine the top 10 competences for each category
top10_knowledge = (
    grouped_data[grouped_data['Label'] == 'Knowledge']
    .groupby('Competence', as_index=False)['Count']
    .sum()
    .sort_values('Count', ascending=False)
    .head(10)
)

top10_skill = (
    grouped_data[grouped_data['Label'] == 'Skill']
    .groupby('Competence', as_index=False)['Count']
    .sum()
    .sort_values('Count', ascending=False)
    .head(10)
)

top10_ability = (
    grouped_data[grouped_data['Label'] == 'Ability']
    .groupby('Competence', as_index=False)['Count']
    .sum()
    .sort_values('Count', ascending=False)
    .head(10)
)

# Create a mapping of file names to the desired labels
file_label_mapping = {
    "tax-infocomm-1w-junio-SF-2024.csv": "1W JUNIO",
    "tax-infocomm-3w-junio-SF-2024.csv": "3W JUNIO",
    "tax-infocomm-1w-julio-SF-2024.csv": "1W JULIO",
    "tax-infocomm-3w-julio-SF-2024.csv": "3W JULIO",
    "tax-infocomm-1w-agosto-SF-2024.csv": "1W AGOSTO",
    "tax-infocomm-3w-agosto-SF-2024.csv": "3W AGOSTO",
    "tax-infocomm-1w-septiembre-SF-2024.csv": "1W SEPTIEMBRE",
    "tax-infocomm-3w-septiembre-SF-2024.csv": "3W SEPTIEMBRE",
    "tax-infocomm-1w-octubre-SF-2024.csv": "1W OCTUBRE",
    "tax-infocomm-3w-octubre-SF-2024.csv": "3W OCTUBRE",
    "tax-infocomm-1w-noviembre-SF-2024.csv": "1W NOVIEMBRE",
    "tax-infocomm-3w-noviembre-SF-2024.csv": "3W NOVIEMBRE",
    "tax-infocomm-1w-diciembre-SF-2024.csv": "1W DICIEMBRE",
    "tax-infocomm-3w-diciembre-SF-2024.csv": "3W DICIEMBRE"
}


# Sort the csv_files list based on the order in file_label_mapping
csv_files.sort(key=lambda x: list(file_label_mapping.keys()).index(os.path.basename(x)))

# Concatenate data from all CSV files
all_data = pd.DataFrame()
for file in csv_files:
    try:
        print(f"Processing file: {file}")
        df = pd.read_csv(file)
        file_name = os.path.basename(file)
        df['File'] = file_label_mapping.get(file_name, file_name.split('.')[0])  # Use the mapping to set the label
        all_data = pd.concat([all_data, df], ignore_index=True)
    except Exception as e:
        print(f"An error occurred while processing file {file}: {e}")

# Filter the original data to include only the top 10 competences
filtered_knowledge = all_data[all_data['Competence'].isin(top10_knowledge['Competence'])]
filtered_skill = all_data[all_data['Competence'].isin(top10_skill['Competence'])]
filtered_ability = all_data[all_data['Competence'].isin(top10_ability['Competence'])]

# Aggregate the data to remove duplicates
aggregated_knowledge = filtered_knowledge.groupby(['File', 'Competence'], as_index=False)['Count'].sum()
aggregated_skill = filtered_skill.groupby(['File', 'Competence'], as_index=False)['Count'].sum()
aggregated_ability = filtered_ability.groupby(['File', 'Competence'], as_index=False)['Count'].sum()

# Define the correct order of files
file_order = list(file_label_mapping.values())

# Ensure the correct order before accumulation
aggregated_knowledge['File'] = pd.Categorical(aggregated_knowledge['File'], categories=file_order, ordered=True)
aggregated_skill['File'] = pd.Categorical(aggregated_skill['File'], categories=file_order, ordered=True)
aggregated_ability['File'] = pd.Categorical(aggregated_ability['File'], categories=file_order, ordered=True)

# Ensure sorting is applied before accumulation
aggregated_knowledge = aggregated_knowledge.sort_values(by=['Competence', 'File'])
aggregated_skill = aggregated_skill.sort_values(by=['Competence', 'File'])
aggregated_ability = aggregated_ability.sort_values(by=['Competence', 'File'])

# Accumulate the counts over time
aggregated_knowledge['Cumulative_Count'] = aggregated_knowledge.groupby('Competence')['Count'].cumsum()
aggregated_skill['Cumulative_Count'] = aggregated_skill.groupby('Competence')['Count'].cumsum()
aggregated_ability['Cumulative_Count'] = aggregated_ability.groupby('Competence')['Count'].cumsum()

# Ensure sorting is applied after accumulation
aggregated_knowledge = aggregated_knowledge.sort_values(by='File')
aggregated_skill = aggregated_skill.sort_values(by='File')
aggregated_ability = aggregated_ability.sort_values(by='File')

# Create bar chart races for each category
output_dir = "output_videos"  # Change the output directory
os.makedirs(output_dir, exist_ok=True)

bcr.bar_chart_race(
    df=aggregated_knowledge.pivot(index='File', columns='Competence', values='Cumulative_Count').fillna(0),
    filename=os.path.join(output_dir, 'knowledge_race.mp4'),
    title='Top 10 Knowledge Competences',
    steps_per_period=40, #Con esto modificamos la fluidez de la animación, son el número de frames para cada periodo.
    period_length=1200 #Con esto modificamos la duración de cada periodo, está en milisegundos.
)

bcr.bar_chart_race(
    df=aggregated_skill.pivot(index='File', columns='Competence', values='Cumulative_Count').fillna(0),
    filename=os.path.join(output_dir, 'skill_race.mp4'),
    title='Top 10 Skill Competences',
    steps_per_period=40, #Con esto modificamos la fluidez de la animación, son el número de frames para cada periodo.
    period_length=1200 #Con esto modificamos la duración de cada periodo, está en milisegundos.
)

bcr.bar_chart_race(
    df=aggregated_ability.pivot(index='File', columns='Competence', values='Cumulative_Count').fillna(0),
    filename=os.path.join(output_dir, 'ability_race.mp4'),
    title='Top 10 Ability Competences',
    steps_per_period=40, #Con esto modificamos la fluidez de la animación, son el número de frames para cada periodo.
    period_length=1200 #Con esto modificamos la duración de cada periodo, está en milisegundos.
)

print("Finished processing all files.")