from collections import deque
from controllers.Tree import TreeG

import queue


class SearchFunctions:
    def __init__(self, nodos, matriz):
        self.nodos = nodos
        self.matriz = matriz
    
    def RecorridoEnAnchura(self, inicio, objetivo):
        # Crear un árbol para seguir el camino explorado
        tree = TreeG(inicio.get_position())  # Crear un árbol con el nodo raíz en la posición inicial

        self.cola = deque([inicio])
        self.nodos_visitados = set()
        self.nodos_visitados.add(inicio.get_position())

        while self.cola:
            nodo_actual = self.cola.popleft()
            if nodo_actual.get_position() == objetivo.get_position():
                # Si encontramos el objetivo, reconstruir el camino usando el árbol
                final_node = tree.find_node(nodo_actual.get_position())
                return final_node.get_path()

            hijos = self.obtener_nodos_adyacentes(nodo_actual)
            for hijo in hijos:
                if hijo.get_position() not in self.nodos_visitados:
                    self.cola.append(hijo)
                    self.nodos_visitados.add(hijo.get_position())
                    # Agregar el nodo hijo al árbol
                    tree.add_node(hijo.get_position(), nodo_actual.get_position())

        return None

    
    def recorrido_en_profundidad(self, inicio, objetivo):
        self.nodos_visitados = set()
        self.pila = [inicio]
        self.padre = {inicio: None}
        self.nodos_visitados.add(inicio)
        print("Recorrido en profundidad:")
        
        while self.pila:
            nodo_actual = self.pila.pop()
            if nodo_actual == objetivo:
                return self.reconstruir_camino(nodo_actual)

            for vecino in self.obtener_nodos_adyacentes(nodo_actual):
                if vecino not in self.nodos_visitados:
                    self.nodos_visitados.add(vecino)
                    self.pila.append(vecino)
                    self.padre[vecino] = nodo_actual

        return None
    
    
    def recorrido_costo_uniforme(self, inicio, objetivo, heuristica):
        cola_prioridad = queue.PriorityQueue()
        cola_prioridad.put(self.NodoPrioridad(inicio, 0))
        visitados = set()
        padres = {inicio: None}

        while not cola_prioridad.empty():
            actual_prioridad = cola_prioridad.get()
            actual = actual_prioridad.nodo

            if actual.x == objetivo.x and actual.y == objetivo.y:
                camino = []
                while actual is not None:
                    camino.insert(0, actual)
                    actual = padres[actual]
                return camino

            visitados.add(actual)
            hijos = self.obtener_nodos_adyacentes(actual)

            for hijo in hijos:
                hijo.costo = int(hijo.calcular_heuristica(objetivo, heuristica) + 1)
                nuevo_costo = actual_prioridad.costo + hijo.costo
                if hijo not in visitados:
                    nodo_prioridad = self.NodoPrioridad(hijo, nuevo_costo)
                    cola_prioridad.put(nodo_prioridad)
                    padres[hijo] = actual

        return None
    
    class NodoPrioridad:
        def __init__(self, nodo, costo):
            self.nodo = nodo
            self.costo = costo

        def __lt__(self, other):
            return self.costo < other.costo
    """
        
         print("nodos visitados")
            for nodo in self.nodos_visitados:
                print(nodo.get_position())
            print("nodos visitados")
            for nodo in self.nodos_visitados:
                print(nodo.get_position())
                
                
        
        def RecorridoEnAnchura(self, inicio, objetivo):
        recorrido = []
        nodos_visitados = []
        cola = deque()

        cola.append(inicio)
        nodos_visitados.append(inicio)
        
        print("Recorrido en anchura:")
        print(self.nodos_visitados)
        print(self.cola)

        while cola:
            print(self.nodos_visitados)
            print(self.cola)
            recorrido.append(cola[0])
            if cola[0].x == objetivo.x and cola[0].y == objetivo.y:
                return self.reconstruir_camino(nodos_visitados, inicio, objetivo)
            nodo_actual = cola.popleft()
            adyacentes = self.obtener_nodos_adyacentes(nodo_actual)
            for adyacente in adyacentes:
                if not self.no_esta_en_lista(nodos_visitados, adyacente):
                    cola.append(adyacente)
                    nodos_visitados.append(adyacente)

        return None

    def recorrido_en_profundidad(self, inicio, objetivo):
        nodos_visitados = []
        pila = [inicio]
        nodos_visitados.append(inicio)
        
        print("Recorrido en profundidad:")
        print(self.nodos_visitados)
        print(self.pila)
        while pila:
            print(self.nodos_visitados)
            print(self.pila)
            nodo_actual = pila[-1]
            if nodo_actual.x == objetivo.x and nodo_actual.y == objetivo.y:
                return self.reconstruir_camino(nodos_visitados, inicio, objetivo)

            hijos = self.obtener_nodos_adyacentes(nodo_actual)
            contador = len(hijos)

            for nodo in hijos:
                if not self.no_esta_en_lista(nodos_visitados, nodo):
                    pila.append(nodo)
                    nodos_visitados.append(nodo)
                    break

                contador -= 1
                if contador == 0:
                    pila.pop()

        return None

        """
    
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
