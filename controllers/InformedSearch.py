from collections import deque
import math
import heapq
from controllers.Tree import TreeG 
from controllers.Node import Node

class InformedSearch:
    def __init__(self, nodos, matriz, beam_width=4, heuristic_type="manhattan"):
        self.nodos = nodos
        self.matriz = matriz
        self.beam_width = beam_width
        self.heuristic_type = heuristic_type

    def beam_search(self, inicio, objetivo):
        print("Beam Search")
        tree = TreeG(inicio.get_position())
        queue = deque([inicio])  # Cola inicial con el nodo de inicio
        visited_nodes = set()
        visited_nodes.add(inicio.get_position())
        visit_order = {}
        visit_counter = 1

        while queue:
            next_level = []  # Para almacenar los nodos del siguiente nivel
            
            # Procesar todos los nodos en la cola actual
            while queue:
                current_node = queue.popleft()
                visit_order[current_node.get_position()] = visit_counter
                visit_counter += 1

                # Si encontramos el objetivo, devolvemos el camino
                if current_node.get_position() == objetivo.get_position():
                    final_node = tree.find_node(current_node.get_position())
                    tree_dict = tree.to_dict()
                    print(tree_dict)
                    #tree.print_tree()
                    return final_node.get_path(), visit_order

                # Obtener nodos adyacentes
                children = self.obtener_nodos_adyacentes(current_node)
                for child in children:
                    if child.get_position() not in visited_nodes:
                        next_level.append(child)  # Añadir a la lista de nodos del siguiente nivel
                        visited_nodes.add(child.get_position())
                        tree.add_node(child.get_position(), current_node.get_position())

            # Ordenar los nodos del siguiente nivel según la heurística
            next_level.sort(key=lambda node: self.heuristic(node, objetivo))
            
            # Aquí limitamos el número de nodos a expandir en el siguiente nivel
            queue = deque(next_level[:self.beam_width])  # Sólo tomamos los mejores según beam_width
            
        #tree.print_tree()
        tree_dict = tree.to_dict()
        print(tree_dict)
        return None, visit_order  # Si no se encuentra un camino

    def a_star(self, inicio, objetivo):
        print("A* Search")
        tree = TreeG(inicio.get_position())
        open_list = []
        heapq.heappush(open_list, (0, inicio))
        g_costs = {inicio.get_position(): 0}
        visited_nodes = set()
        visit_order = {}
        visit_counter = 1

        while open_list:
            current_cost, current_node = heapq.heappop(open_list)
            visit_order[current_node.get_position()] = visit_counter
            visit_counter += 1

            if current_node.get_position() == objetivo.get_position():
                final_node = tree.find_node(current_node.get_position())
                tree_dict = tree.to_dict()
                print(tree_dict)
                #tree.print_tree()
                return final_node.get_path(), visit_order

            visited_nodes.add(current_node.get_position())
            children = self.obtener_nodos_adyacentes(current_node)

            for child in children:
                tentative_g_cost = g_costs[current_node.get_position()] + 1  # Coste uniforme
                if child.get_position() in visited_nodes and tentative_g_cost >= g_costs.get(child.get_position(), float('inf')):
                    continue

                if tentative_g_cost < g_costs.get(child.get_position(), float('inf')) or child.get_position() not in [i[1].get_position() for i in open_list]:
                    g_costs[child.get_position()] = tentative_g_cost
                    f_cost = tentative_g_cost + self.heuristic(child, objetivo)
                    heapq.heappush(open_list, (f_cost, child))
                    tree.add_node(child.get_position(), current_node.get_position())
                    
        tree_dict = tree.to_dict()
        print(tree_dict)
        #tree.print_tree()
        return None, visit_order

    def hill_climbing(self, inicio, objetivo):
        print("Hill Climbing")
        tree = TreeG(inicio.get_position())
        current_node = inicio
        visited_nodes = set()
        visited_nodes.add(current_node.get_position())
        visit_order = {}
        visit_counter = 1
        visit_order[current_node.get_position()] = visit_counter

        while current_node.get_position() != objetivo.get_position():
            visit_counter += 1
            neighbors = self.obtener_nodos_adyacentes(current_node)
            next_node = min(neighbors, key=lambda node: self.heuristic(node, objetivo))

            if self.heuristic(next_node, objetivo) >= self.heuristic(current_node, objetivo):
                tree_dict = tree.to_dict()
                print(tree_dict)
                #tree.print_tree()
                return None, visit_order  # No se encontró una mejora

            next_node.parent = current_node  # Asigna manualmente el padre
            current_node = next_node


            current_node = next_node
            visited_nodes.add(current_node.get_position())
            visit_order[current_node.get_position()] = visit_counter
            tree.add_node(current_node.get_position(), current_node.parent.get_position())

        final_node = tree.find_node(current_node.get_position())
        tree_dict = tree.to_dict()
        print(tree_dict)
        #tree.print_tree()
        return final_node.get_path(), visit_order
    
    
    
    
    def heuristic(self, node, objetivo):
        if self.heuristic_type == 'manhattan':
            return self.manhattan_distance(node, objetivo)
        else:
            return self.euclidean_distance(node, objetivo)

    def manhattan_distance(self, node, objetivo):
        x1, y1 = node.get_position()
        x2, y2 = objetivo.get_position()
        return abs(x1 - x2) + abs(y1 - y2)

    def euclidean_distance(self, node, objetivo):
        x1, y1 = node.get_position()
        x2, y2 = objetivo.get_position()
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def obtener_nodos_adyacentes(self, nodo):
        adyacentes = []
        for dx, dy in [(1, 0),(0, -1),(-1, 0), (0, 1)]:
            x, y = nodo.x + dx, nodo.y + dy
            if 0 <= x < len(self.matriz[0]) and 0 <= y < len(self.matriz):
                if self.matriz[y][x] in ["C", "C_b", "C_g", "S", "R_s"]:
                    adyacentes.append(Node(x, y))
        return adyacentes
