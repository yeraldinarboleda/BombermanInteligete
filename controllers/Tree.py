class TreeNode:
    def __init__(self, position, parent=None):
        self.position = position  
        self.parent = parent      
        self.children = []        

    def add_child(self, child_node):
        self.children.append(child_node)

    def get_path(self):
        """Reconstruir el camino desde el nodo actual hasta la raíz (nodo inicial)."""
        path = []
        current_node = self
        while current_node is not None:
            path.append(current_node.position)
            current_node = current_node.parent
        camino = path[::-1]  # Invertir el camino para que comience desde el inicio
        print(camino)
        return camino

class TreeG:
    def __init__(self, start_position):
        self.root = TreeNode(start_position)  
        self.nodes = {start_position: self.root}  # Diccionario de nodos por su posición

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
    
    """ def print_tree(self, node=None, level=0):
            """"Imprimir el árbol completo en forma jerárquica.""""
            if node is None:
                node = self.root  # Comienza desde el nodo raíz si no se proporciona otro nodo
            print("  " * level + f"- {node.position}")  # Imprime el nodo actual con indentación
            for child in node.children:
                self.print_tree(child, level + 1) """
                
    def to_dict(self):
        """Convertir el árbol en un diccionario donde cada padre tiene una lista de hijos."""
        tree_dict = {}
        for position, node in self.nodes.items():
            # Extraer las posiciones de los hijos de cada nodo
            tree_dict[position] = [child.position for child in node.children]
        return tree_dict

