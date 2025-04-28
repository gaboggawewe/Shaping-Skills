import pandas as pd

# Ruta al archivo CSV
excel_file_path = "tax-infocomm-junio-diciembre-MEX-2024-ratio-cured.csv"
month_keywords=["julio","agosto","septiembre","octubre","noviembre","diciembre"]

# Leer el archivo CSV
df_local = pd.read_csv(excel_file_path)

# Crear columnas combinadas por mes
for m in month_keywords:
        cols_for_month = [col for col in df_local.columns if col.endswith(m) and col.startswith("ratio_")]
        if not cols_for_month:
            print(f"No columns found for month: {m}")
            continue

        print(f"Columns for month {m}: {cols_for_month}")
        df_local[f"month_{m}"] = df_local[cols_for_month].mean(axis=1)

# NUEVO CÓDIGO: Sumar las columnas de los 6 meses generados
month_columns = [f"month_{m}" for m in month_keywords]
print("\nSuma de cada mes combinado (excluyendo la primera fila):")
for mes_columna in month_columns:
    if mes_columna in df_local.columns:  # Verificar que la columna existe
        suma_mes = df_local[mes_columna][1:].sum()
        print(f"La suma de '{mes_columna}' es: {suma_mes}")

# Si también quieres la suma total de todos los meses combinados
total_todos_meses = df_local[month_columns][1:].sum().sum()
print(f"\nLa suma TOTAL de todos los meses combinados es: {total_todos_meses}")