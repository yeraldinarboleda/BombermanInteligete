class TreeNode:
    def __init__(self, position, parent=None):
        self.position = position  # (x, y) posición en la matriz
        self.parent = parent      # Nodo padre
        self.children = []        # Lista de nodos hijos

    def add_child(self, child_node):
        self.children.append(child_node)

    def get_path(self):
        """Reconstruir el camino desde el nodo actual hasta la raíz (nodo inicial)."""
        path = []
        current_node = self
        while current_node is not None:
            path.append(current_node.position)
            current_node = current_node.parent
        return path[::-1]  # Devolver el camino en orden correcto


class TreeG:
    def __init__(self, start_position):
        self.root = TreeNode(start_position)  # El nodo raíz representa la posición inicial de Bomberman
        self.nodes = {start_position: self.root}  # Diccionario para acceder a los nodos por posición

    def add_node(self, position, parent_position):
        """Agregar un nuevo nodo al árbol."""
        parent_node = self.nodes.get(parent_position)
        if parent_node:
            new_node = TreeNode(position, parent_node)
            parent_node.add_child(new_node)
            self.nodes[position] = new_node
            return new_node
        return None

    def find_node(self, position):
        """Buscar un nodo por su posición."""
        return self.nodes.get(position)
