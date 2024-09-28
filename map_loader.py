class MapLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_map(self):
        """
        Lee el archivo de texto y genera una matriz que representa el mapa.
        Carga los diferentes elementos: caminos (C), rocas (R), metales (M), bomberman (C_b), globos (C_g), roca con salida (R_s).
        """
        with open(self.file_path, 'r') as f:
            map_data = []
            for line in f:
                # Limpiar la línea, remover celdas vacías y espacios
                row = [cell.strip() for cell in line.strip().split(',') if cell.strip()]
                if row:  # Solo añadir filas no vacías
                    map_data.append(row)
        return map_data
