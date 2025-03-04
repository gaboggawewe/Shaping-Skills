import os

def count_lines_in_folder(folder_path):
    total_lines = 0
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines += sum(1 for _ in f)
            except Exception as e:
                print(f"No se pudo leer {file_path}: {e}")
    
    return total_lines

if __name__ == "__main__":
    folder_path = "sf ratio"
    total = count_lines_in_folder(folder_path)
    print(f"El número total de líneas en '{folder_path}' es: {total}")