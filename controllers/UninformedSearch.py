from collections import deque

class SearchFunctions:
    def __init__(self, nodos, matriz):
        self.nodos = nodos
        self.matriz = matriz

    def RecorridoEnAnchura(self, inicio, objetivo):
        recorrido = []
        nodos_visitados = []
        cola = deque()

        cola.append(inicio)
        nodos_visitados.append(inicio)

        while cola:
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

        while pila:
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

    def obtener_nodos_adyacentes(self, nodo):
        adyacentes = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = nodo.x + dx, nodo.y + dy
            if 0 <= x < len(self.matriz[0]) and 0 <= y < len(self.matriz):
                if self.matriz[y][x] in ["C", "C_b", "C_g"]:
                    adyacentes.append(Node(x, y))
        return adyacentes

    def no_esta_en_lista(self, lista, nodo):
        for n in lista:
            if n.x == nodo.x and n.y == nodo.y:
                return False
        return True

    def reconstruir_camino(self, nodos_visitados, inicio, objetivo):
        camino = []
        nodo_actual = objetivo
        while nodo_actual.x != inicio.x or nodo_actual.y != inicio.y:
            camino.append(nodo_actual)
            for nodo in nodos_visitados:
                if nodo.x == nodo_actual.x and nodo.y == nodo_actual.y:
                    nodo_actual = nodo
                    break
        camino.append(inicio)
        return list(reversed(camino))

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)