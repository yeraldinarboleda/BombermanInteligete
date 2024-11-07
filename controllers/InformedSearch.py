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
        print("Beam Search con retroceso")
        tree = TreeG(inicio.get_position())
        queue = deque([inicio])  # Cola inicial con el nodo de inicio
        visited_nodes = set()
        visited_nodes.add(inicio.get_position())
        visit_order = {}
        visit_counter = 1
        niveles_pendientes = {1: [inicio]}  # Guardar nodos pendientes por nivel, comenzando en nivel 1
        nivel_actual = 1

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
            if next_level:
                queue = deque(next_level[:self.beam_width])  # Sólo tomamos los mejores según beam_width
                niveles_pendientes[nivel_actual + 1] = next_level[:self.beam_width]  # Guardar nodos pendientes para retroceso
                nivel_actual += 1
            else:
                # Retroceso: Revisar niveles pendientes en orden ascendente
                print("No se encontró solución en este nivel, retrocediendo al primer nivel")
                encontrado_nodo_pendiente = False
                for nivel, nodos in sorted(niveles_pendientes.items()):
                    nodos_no_visitados = [nodo for nodo in nodos if nodo.get_position() not in visited_nodes]
                    if nodos_no_visitados:
                        queue = deque(nodos_no_visitados)
                        nivel_actual = nivel  # Actualizar el nivel actual al próximo nivel pendiente
                        encontrado_nodo_pendiente = True
                        print(f"Retrocediendo al nivel {nivel} y explorando nodos restantes.")
                        break

                if not encontrado_nodo_pendiente:
                    print("No hay más nodos por explorar. Objetivo no encontrado.")
                    break

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
        cost_counter = {}  

        while open_list:
            current_cost, current_node = heapq.heappop(open_list)
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
                tentative_g_cost = g_costs[current_node.get_position()] + 1  # Coste uniforme
                if child.get_position() in visited_nodes and tentative_g_cost >= g_costs.get(child.get_position(), float('inf')):
                    continue

                if tentative_g_cost < g_costs.get(child.get_position(), float('inf')) or child.get_position() not in [i[1].get_position() for i in open_list]:
                    g_costs[child.get_position()] = tentative_g_cost
                    f_cost = tentative_g_cost + self.heuristic(child, objetivo)
                    print(f"Nodo: {child.get_position()} Costo :{f_cost}")
                    heapq.heappush(open_list, (f_cost, child))
                    tree.add_node(child.get_position(), current_node.get_position())
                    
                    if f_cost not in cost_counter:
                        cost_counter[f_cost] = []
                    cost_counter[f_cost].append(child.get_position())
                    
        tree_dict = tree.to_dict()
        print(tree_dict)
        return None, visit_order


    def hill_climbing(self, inicio, objetivo):
        print("Hill Climbing")
        tree = TreeG(inicio.get_position())
        pila = [(inicio, 0)]  # Empezamos desde el nivel 1, evitando el nivel 0
        visitados = set()
        visit_order = {}  # Diccionario para almacenar todos los nodos visitados
        visit_counter = 1
        niveles_pendientes = {1: [(inicio, 1)]}  # Guardamos nodos pendientes por nivel, comenzando en nivel 1

        while pila:
            current_node, nivel_actual = pila.pop()

            # Verificar si el nodo ya fue visitado para evitar duplicados en visit_order
            if current_node.get_position() in visitados:
                continue

            # Marcar el nodo como visitado y registrar el orden de visita
            print(f"Visitando nodo: {current_node.get_position()} en el nivel {nivel_actual}")
            visitados.add(current_node.get_position())
            visit_order[current_node.get_position()] = visit_counter  # Registramos el nodo visitado en visit_order
            visit_counter += 1

            # Verificar si es el nodo objetivo
            if current_node.get_position() == objetivo.get_position():
                final_node = tree.find_node(current_node.get_position())
                tree_dict = tree.to_dict()
                print(tree_dict)
                return final_node.get_path(), visit_order  # Retornamos el camino y todos los nodos visitados

            # Obtener los hijos no visitados
            hijos_no_visitados = [hijo for hijo in self.obtener_nodos_adyacentes(current_node)
                                if hijo.get_position() not in visitados]

            # Ordenar los hijos no visitados utilizando la heurística
            hijos_no_visitados.sort(key=lambda node: self.heuristic(node, objetivo))

            if hijos_no_visitados:
                # Añadir hijos a la pila en orden inverso y registrar en niveles pendientes
                for hijo in reversed(hijos_no_visitados):
                    pila.append((hijo, nivel_actual + 1))
                    tree.add_node(hijo.get_position(), current_node.get_position())
                # Guardar nodos pendientes en este nivel
                niveles_pendientes[nivel_actual + 1] = niveles_pendientes.get(nivel_actual + 1, []) + [(hijo, nivel_actual + 1) for hijo in hijos_no_visitados]
                print(f"Nivel {nivel_actual + 1}: Explorando los hijos de {current_node.get_position()} con heurística.")
            else:
                # Si llegamos a una hoja, explorar los niveles pendientes en orden ascendente, comenzando en nivel 1
                print(f"Llegamos a una hoja en el nivel {nivel_actual}. Iniciando retroceso a niveles pendientes.")
                encontrado_nodo_pendiente = False

                # Reiniciar desde el siguiente nivel pendiente con nodos no visitados
                for nivel, nodos_pendientes in sorted(niveles_pendientes.items()):
                    if nivel > 0:  # Evitar el nivel 0
                        nodos_no_visitados = [(nodo, nivel) for nodo, _ in nodos_pendientes if nodo.get_position() not in visitados]
                        if nodos_no_visitados:
                            pila.extend(nodos_no_visitados)
                            encontrado_nodo_pendiente = True
                            print(f"Explorando el siguiente nivel pendiente: Nivel {nivel}")
                            break

                if not encontrado_nodo_pendiente:
                    print("No hay más nodos por explorar. Objetivo no encontrado.")
                    break

        return None, visit_order  # Si no se encuentra el nodo objetivo, devolver todos los nodos visitados    
    
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
        direcciones = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Izquierda, arriba, derecha, abajo
        
        for dx, dy in direcciones:
            x, y = nodo.x + dx, nodo.y + dy
            # Asegurarse de que la posición es válida y transitable
            if 0 <= x < len(self.matriz[0]) and 0 <= y < len(self.matriz):
                if self.matriz[y][x] in ["C", "C_b", "C_g", "S", "R_s", "R"]:
                    adyacentes.append(Node(x, y))
                    
        return adyacentes
