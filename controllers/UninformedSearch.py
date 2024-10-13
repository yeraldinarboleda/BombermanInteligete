from collections import deque
from controllers.Tree import TreeG
import heapq
#import random

class SearchFunctions:
    def __init__(self, nodos, matriz):
        self.nodos = nodos
        self.matriz = matriz
    
    def RecorridoEnAnchura(self, inicio, objetivo):
        print("Recorrido en anchura")
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
        print("Recorrido en Profundidad")
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

            hijos = self.obtener_nodos_adyacentes_profundidad(nodo_actual)
            for hijo in hijos:
                if hijo.get_position() not in self.nodos_visitados:
                    self.pila.append(hijo)
                    self.nodos_visitados.add(hijo.get_position())
                    tree.add_node(hijo.get_position(), nodo_actual.get_position())

        return None, visit_order

    def RecorridoCostoUniforme(self, inicio, objetivo):
        print("Recorrido costo uniforme")
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
                    nuevo_costo = costo_actual + self.obtener_costo()
                    
                    if hijo_pos not in self.costos_acumulados or nuevo_costo < self.costos_acumulados[hijo_pos]:
                        self.costos_acumulados[hijo_pos] = nuevo_costo
                        contador_nodos += 1
                        heapq.heappush(self.cola_prioridad, (nuevo_costo, contador_nodos, hijo))
                        tree.add_node(hijo_pos, nodo_actual.get_position())

        return None, visit_order
    
    def obtener_costo(self):
        # El costo entre cualquier nodo es un nurero random entre 1 y 10
        #return random.randint(1, 10)
        return 1
   
    
    def obtener_nodos_adyacentes_profundidad(self, nodo):
        adyacentes = []
        for dx, dy in [(0, -1), (0, 1),  (-1, 0),(1, 0)]:
            x, y = nodo.x + dx, nodo.y + dy
            if 0 <= x < len(self.matriz[0]) and 0 <= y < len(self.matriz):
                if self.matriz[y][x] in ["C", "C_b", "C_g","S","R_s"]:
                    adyacentes.append(Node(x, y))
                    
        return adyacentes
    
    def obtener_nodos_adyacentes(self, nodo):
        adyacentes = []
        for dx, dy in [(-1, 0),(0, 1), (1, 0), (0, -1)]:
            x, y = nodo.x + dx, nodo.y + dy
            if 0 <= x < len(self.matriz[0]) and 0 <= y < len(self.matriz):
                if self.matriz[y][x] in ["C", "C_b", "C_g","S","R_s"]:
                    adyacentes.append(Node(x, y))
                    
        return adyacentes

    def no_esta_en_lista(self, lista, nodo):
        for n in lista:
            if n.x == nodo.x and n.y == nodo.y:
                return False
        return True

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)
