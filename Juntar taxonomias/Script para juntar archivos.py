import pandas as pd
import glob

def merge_csv_files(input_folder, output_file):
    all_files = glob.glob(f"{input_folder}/*.csv")
    combined_data = {}
    
    for file in all_files:
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except Exception as e:
            print(f"Error reading file {file}: {e}")
            continue
        
        # Limpiar los nombres de las columnas
        df.columns = [col.strip() for col in df.columns]
        
        # Revisar si las columnas están en todos los archivos de la carpeta.
        required_columns = ['Occupation', 'Competence', 'Label', 'Count']
        if not all(col in df.columns for col in required_columns):
            print(f"Error: Missing required columns in {file}")
            print(f"Columns found: {df.columns}")  # Print the actual columns found
            continue
        # Se hace la suma de los counts de cada match en Occupation,Competence y Label, tienen que coincidir los 3.
        for _, row in df.iterrows():
            try:
                key = (row['Occupation'], row['Competence'], row['Label'])
                count = int(row['Count'])
                
                if key in combined_data:
                    combined_data[key] += count
                else:
                    combined_data[key] = count
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
    
    # Convertir el diccionario en DataFrame
    final_df = pd.DataFrame([(k[0], k[1], k[2], v) for k, v in combined_data.items()], 
                             columns=['Occupation', 'Competence', 'Label', 'Count'])
    
    # Mantenemos header solo una vez
    if not final_df.empty:
        final_df.to_csv(output_file, index=False, header=True)
        print(f"Archivo final guardado en: {output_file}")
    else:
        print("No data to write to CSV.")

merge_csv_files("JUN-DIC MEX", "JUN-DIC MEX/tax-infocomm-junio-diciembre-MEX-2024.csv")