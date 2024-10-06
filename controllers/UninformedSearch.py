from collections import deque
from controllers.Tree import TreeG
import heapq

class SearchFunctions:
    def __init__(self, nodos, matriz):
        self.nodos = nodos
        self.matriz = matriz
    
    def RecorridoEnAnchura(self, inicio, objetivo):
        tree = TreeG(inicio.get_position())
        self.cola = deque([inicio])
        self.nodos_visitados = set()
        self.nodos_visitados.add(inicio.get_position())
        visit_order = {}
        visit_counter = 1

        while self.cola:
            nodo_actual = self.cola.popleft()
            visit_order[nodo_actual.get_position()] = visit_counter
            visit_counter += 1

            if nodo_actual.get_position() == objetivo.get_position():
                final_node = tree.find_node(nodo_actual.get_position())
                return final_node.get_path(), visit_order

            hijos = self.obtener_nodos_adyacentes(nodo_actual)
            for hijo in hijos:
                if hijo.get_position() not in self.nodos_visitados:
                    self.cola.append(hijo)
                    self.nodos_visitados.add(hijo.get_position())
                    tree.add_node(hijo.get_position(), nodo_actual.get_position())

        return None, visit_order

    def RecorridoEnProfundidad(self, inicio, objetivo):
        tree = TreeG(inicio.get_position())
        self.pila = [inicio]
        self.nodos_visitados = set()
        self.nodos_visitados.add(inicio.get_position())
        visit_order = {}
        visit_counter = 1

        while self.pila:
            nodo_actual = self.pila.pop()
            visit_order[nodo_actual.get_position()] = visit_counter
            visit_counter += 1

            if nodo_actual.get_position() == objetivo.get_position():
                final_node = tree.find_node(nodo_actual.get_position())
                return final_node.get_path(), visit_order

            hijos = self.obtener_nodos_adyacentes(nodo_actual)
            for hijo in hijos:
                if hijo.get_position() not in self.nodos_visitados:
                    self.pila.append(hijo)
                    self.nodos_visitados.add(hijo.get_position())
                    tree.add_node(hijo.get_position(), nodo_actual.get_position())

        return None, visit_order

    def RecorridoCostoUniforme(self, inicio, objetivo):
        tree = TreeG(inicio.get_position())
        self.cola_prioridad = []
        heapq.heappush(self.cola_prioridad, (0, 0, inicio))
        self.nodos_visitados = set()
        self.costos_acumulados = {inicio.get_position(): 0}
        contador_nodos = 0
        visit_order = {}
        visit_counter = 1

        while self.cola_prioridad:
            costo_actual, _, nodo_actual = heapq.heappop(self.cola_prioridad)
            visit_order[nodo_actual.get_position()] = visit_counter
            visit_counter += 1

            if nodo_actual.get_position() == objetivo.get_position():
                final_node = tree.find_node(nodo_actual.get_position())
                return final_node.get_path(), visit_order

            if nodo_actual.get_position() not in self.nodos_visitados:
                self.nodos_visitados.add(nodo_actual.get_position())
                
                hijos = self.obtener_nodos_adyacentes(nodo_actual)
                for hijo in hijos:
                    hijo_pos = hijo.get_position()
                    nuevo_costo = costo_actual + self.obtener_costo(nodo_actual, hijo)
                    
                    if hijo_pos not in self.costos_acumulados or nuevo_costo < self.costos_acumulados[hijo_pos]:
                        self.costos_acumulados[hijo_pos] = nuevo_costo
                        contador_nodos += 1
                        heapq.heappush(self.cola_prioridad, (nuevo_costo, contador_nodos, hijo))
                        tree.add_node(hijo_pos, nodo_actual.get_position())

        return None, visit_order
    
    def obtener_costo(self, nodo1, nodo2):
        # El costo entre cualquier nodo es siempre 1
        return 1
   
    
    def obtener_nodos_adyacentes(self, nodo):
        adyacentes = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = nodo.x + dx, nodo.y + dy
            if 0 <= x < len(self.matriz[0]) and 0 <= y < len(self.matriz):
                if self.matriz[y][x] in ["C", "C_b", "C_g","S"]:
                    adyacentes.append(Node(x, y))
                    
        return adyacentes

    def no_esta_en_lista(self, lista, nodo):
        for n in lista:
            if n.x == nodo.x and n.y == nodo.y:
                return False
        return True

    def reconstruir_camino(self, nodo_actual):
        camino = []
        while nodo_actual is not None:
            camino.append(nodo_actual)
            nodo_actual = self.padre[nodo_actual]
        return list(reversed(camino))

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)
