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
        # Definir el orden de prioridad para desempate
        self.direcciones = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Izquierda, arriba, derecha, abajo

    def get_direction_priority(self, current_node, next_node):
        """Determina la prioridad de dirección entre dos nodos"""
        dx = next_node.x - current_node.x
        dy = next_node.y - current_node.y
        try:
            return self.direcciones.index((dx, dy))
        except ValueError:
            return len(self.direcciones)  # Si no se encuentra, dar la prioridad más baja

    def beam_search(self, inicio, objetivo):
        print("Beam Search con retroceso")
        tree = TreeG(inicio.get_position())
        queue = deque([inicio])
        visited_nodes = set()
        visited_nodes.add(inicio.get_position())
        visit_order = {}
        visit_counter = 1
        niveles_pendientes = {1: [inicio]}
        nivel_actual = 1

        while queue:
            next_level = []

            while queue:
                current_node = queue.popleft()
                visit_order[current_node.get_position()] = visit_counter
                visit_counter += 1

                if current_node.get_position() == objetivo.get_position():
                    final_node = tree.find_node(current_node.get_position())
                    tree_dict = tree.to_dict()
                    print(tree_dict)
                    return final_node.get_path(), visit_order

                children = self.obtener_nodos_adyacentes(current_node)
                for child in children:
                    if child.get_position() not in visited_nodes:
                        next_level.append((child, current_node))

            # Sort next_level by heuristic and direction priority before adding to visited_nodes and queue
            next_level.sort(key=lambda x: (
                self.heuristic(x[0], objetivo),
                self.get_direction_priority(x[1], x[0])
            ))

            if next_level:
                queue = deque(node[0] for node in next_level[:self.beam_width])
                for node, parent in next_level[:self.beam_width]:
                    visited_nodes.add(node.get_position())  # Add to visited by sorted order
                    tree.add_node(node.get_position(), parent.get_position())
                niveles_pendientes[nivel_actual + 1] = [node[0] for node in next_level[:self.beam_width]]
                nivel_actual += 1
            else:
                print("No se encontró solución en este nivel, retrocediendo al primer nivel")
                encontrado_nodo_pendiente = False
                for nivel, nodos in sorted(niveles_pendientes.items()):
                    nodos_no_visitados = [nodo for nodo in nodos if nodo.get_position() not in visited_nodes]
                    if nodos_no_visitados:
                        queue = deque(nodos_no_visitados)
                        nivel_actual = nivel
                        encontrado_nodo_pendiente = True
                        print(f"Retrocediendo al nivel {nivel} y explorando nodos restantes.")
                        break

                if not encontrado_nodo_pendiente:
                    print("No hay más nodos por explorar. Objetivo no encontrado.")
                    break

        return None, visit_order


    def a_star(self, inicio, objetivo):
        print("A* Search")
        tree = TreeG(inicio.get_position())
        open_list = []
        entry_count = 0  # Contador para desempate secundario
        heapq.heappush(open_list, (0, entry_count, inicio, inicio))  # Añadido el nodo padre
        g_costs = {inicio.get_position(): 0}
        visited_nodes = set()
        visit_order = {}
        visit_counter = 1
        cost_counter = {}

        while open_list:
            current_cost, _, current_node, parent_node = heapq.heappop(open_list)
            
            if current_node.get_position() in visited_nodes:
                continue

            visit_order[current_node.get_position()] = visit_counter
            visit_counter += 1

            if current_node.get_position() == objetivo.get_position():
                final_node = tree.find_node(current_node.get_position())
                tree_dict = tree.to_dict()
                print(tree_dict)
                
                masReprtido = max(cost_counter, key=cost_counter.get)
                nodoMasRepetido = cost_counter[masReprtido]
                
                print(f"El costo más repetido es: {masReprtido}")
                print(f"Nodos con el costo {masReprtido}: {nodoMasRepetido}")
                
                return final_node.get_path(), visit_order

            visited_nodes.add(current_node.get_position())
            children = self.obtener_nodos_adyacentes(current_node)

            for child in children:
                tentative_g_cost = g_costs[current_node.get_position()] + 1

                if child.get_position() in visited_nodes and tentative_g_cost >= g_costs.get(child.get_position(), float('inf')):
                    continue

                if tentative_g_cost < g_costs.get(child.get_position(), float('inf')):
                    g_costs[child.get_position()] = tentative_g_cost
                    f_cost = tentative_g_cost + self.heuristic(child, objetivo)
                    entry_count += 1
                    direction_priority = self.get_direction_priority(current_node, child)
                    
                    # Usar f_cost como primera prioridad y direction_priority como segunda
                    heapq.heappush(open_list, (f_cost, direction_priority, child, current_node))
                    tree.add_node(child.get_position(), current_node.get_position())
                    
                    if f_cost not in cost_counter:
                        cost_counter[f_cost] = []
                    cost_counter[f_cost].append(child.get_position())

        return None, visit_order

    def hill_climbing(self, inicio, objetivo):
        print("Hill Climbing")
        tree = TreeG(inicio.get_position())
        pila = [(inicio, None, 1)]  # Añadido None como nodo padre
        visitados = set()
        visit_order = {}
        visit_counter = 1
        nivel_maximo = 1
        niveles_pendientes = {1: [(inicio, None, 1)]}

        while pila:
            current_node, parent_node, nivel_actual = pila.pop()

            if current_node.get_position() in visitados:
                continue

            print(f"Visitando nodo: {current_node.get_position()} en el nivel {nivel_actual}")
            visitados.add(current_node.get_position())
            visit_order[current_node.get_position()] = visit_counter
            visit_counter += 1

            if current_node.get_position() == objetivo.get_position():
                final_node = tree.find_node(current_node.get_position())
                tree_dict = tree.to_dict()
                print(tree_dict)
                return final_node.get_path(), visit_order

            hijos = self.obtener_nodos_adyacentes(current_node)
            hijos_no_visitados = [(hijo, current_node) for hijo in hijos 
                                if hijo.get_position() not in visitados]
            
            # Ordenar por heurística y desempatar por dirección
            hijos_no_visitados.sort(key=lambda x: (
                self.heuristic(x[0], objetivo),
                self.get_direction_priority(x[1], x[0])
            ))

            if hijos_no_visitados:
                nivel_maximo += 1
                for hijo, padre in reversed(hijos_no_visitados):
                    pila.append((hijo, padre, nivel_maximo))
                    tree.add_node(hijo.get_position(), padre.get_position())

                niveles_pendientes[nivel_maximo] = [(hijo, padre, nivel_maximo) 
                                                for hijo, padre in hijos_no_visitados]
                print(f"Nivel {nivel_maximo}: Explorando los hijos de {current_node.get_position()} con heurística.")
            else:
                print(f"Llegamos a una hoja en el nivel {nivel_actual}. Iniciando retroceso a niveles pendientes.")
                encontrado_nodo_pendiente = False

                for nivel in sorted(niveles_pendientes.keys()):
                    if nivel > 0:
                        nodos_no_visitados = [(nodo, padre, nivel_maximo + 1) 
                                            for nodo, padre, _ in niveles_pendientes[nivel] 
                                            if nodo.get_position() not in visitados]
                        if nodos_no_visitados:
                            nivel_maximo += 1
                            pila.extend(nodos_no_visitados)
                            encontrado_nodo_pendiente = True
                            print(f"Explorando el siguiente nivel pendiente: Nivel {nivel_maximo}")
                            break

                if not encontrado_nodo_pendiente:
                    print("No hay más nodos por explorar. Objetivo no encontrado.")
                    break

        return None, visit_order

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
        # Define el orden de expansión: izquierda, arriba, derecha, abajo
        for dx, dy in self.direcciones:
            x, y = nodo.x + dx, nodo.y + dy
            if 0 <= x < len(self.matriz[0]) and 0 <= y < len(self.matriz):
                if self.matriz[y][x] in ["C", "C_b", "C_g", "S", "R_s", "R"]:
                    adyacentes.append(Node(x, y))
        return adyacentes
    