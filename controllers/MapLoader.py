
class MapLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_map(self):
        """
        Lee el archivo de texto y genera una matriz que representa el mapa.
        """
        with open(self.file_path, 'r') as f:
            map_data = []
            for line in f:
                row = [cell.strip() for cell in line.strip().split(',') if cell.strip()]
                if row:
                    map_data.append(row)
        return map_data
