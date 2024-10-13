
class MapLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_map(self):
        """
        Lee el archivo de texto y genera una matriz que representa el mapa.
        Luego invierte el orden de las filas.
        """
        with open(self.file_path, 'r') as f:
            map_data = []
            for line in f:
                row = [cell.strip() for cell in line.strip().split(',') if cell.strip()]
                if row:
                    map_data.append(row)
        # Invertir las filas de la matriz
        map_data.reverse()
        return map_data

