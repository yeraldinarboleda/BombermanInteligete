from collections import deque
from controllers.Tree import TreeG
import heapq  # Para usar una cola de prioridad


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

    
    def RecorridoEnProfundidad(self, inicio, objetivo):
        # Crear un árbol para seguir el camino explorado
        tree = TreeG(inicio.get_position())  # Crear un árbol con el nodo raíz en la posición inicial

        self.pila = [inicio]  # Usar una pila en lugar de una cola
        self.nodos_visitados = set()
        self.nodos_visitados.add(inicio.get_position())

        while self.pila:
            nodo_actual = self.pila.pop()  # Sacar el último nodo de la pila
            if nodo_actual.get_position() == objetivo.get_position():
                # Si encontramos el objetivo, reconstruir el camino usando el árbol
                final_node = tree.find_node(nodo_actual.get_position())
                return final_node.get_path()

            hijos = self.obtener_nodos_adyacentes(nodo_actual)
            for hijo in hijos:
                if hijo.get_position() not in self.nodos_visitados:
                    self.pila.append(hijo)  # Añadir los nodos hijos a la pila
                    self.nodos_visitados.add(hijo.get_position())
                    # Agregar el nodo hijo al árbol
                    tree.add_node(hijo.get_position(), nodo_actual.get_position())

        return None
    

    def RecorridoCostoUniforme(self, inicio, objetivo):
        # Crear un árbol para seguir el camino explorado
        tree = TreeG(inicio.get_position())  # Crear un árbol con el nodo raíz en la posición inicial

        # Cola de prioridad (heap), donde cada elemento es una tupla (costo, id_unico, nodo)
        self.cola_prioridad = []
        heapq.heappush(self.cola_prioridad, (0, 0, inicio))  # El costo inicial es 0 y asignamos un ID único 0
        self.nodos_visitados = set()
        self.costos_acumulados = {inicio.get_position(): 0}  # Guardar los costos acumulados
        contador_nodos = 0  # Para garantizar un id único para cada nodo

        while self.cola_prioridad:
            # Extraer el nodo con el menor costo
            costo_actual, id_nodo, nodo_actual = heapq.heappop(self.cola_prioridad)
            
            # Si el nodo actual es el objetivo, reconstruir el camino usando el árbol
            if nodo_actual.get_position() == objetivo.get_position():
                final_node = tree.find_node(nodo_actual.get_position())
                return final_node.get_path()

            # Si el nodo no ha sido visitado aún
            if nodo_actual.get_position() not in self.nodos_visitados:
                self.nodos_visitados.add(nodo_actual.get_position())
                
                # Obtener los nodos adyacentes (vecinos)
                hijos = self.obtener_nodos_adyacentes(nodo_actual)
                for hijo in hijos:
                    hijo_pos = hijo.get_position()
                    nuevo_costo = costo_actual + self.obtener_costo(nodo_actual, hijo)  # Sumar el costo del nodo hijo
                    
                    # Si el hijo no ha sido visitado o si encontramos un camino más barato hacia ese hijo
                    if hijo_pos not in self.costos_acumulados or nuevo_costo < self.costos_acumulados[hijo_pos]:
                        self.costos_acumulados[hijo_pos] = nuevo_costo
                        contador_nodos += 1  # Incrementamos el contador de nodos para el identificador único
                        heapq.heappush(self.cola_prioridad, (nuevo_costo, contador_nodos, hijo))  # Añadir el hijo con su costo y un ID único
                        tree.add_node(hijo_pos, nodo_actual.get_position())  # Agregar el nodo hijo al árbol

        return None  # Si no se encuentra el objetivo
    
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
