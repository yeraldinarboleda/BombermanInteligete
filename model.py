from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon
from random import choice

class BombermanModel(Model):
    """Modelo que representa el juego de Bomberman."""
    
    def __init__(self, map_data, search_type=None, algorithm=None, heuristic=None):
        self.map_data = map_data
        self.grid_width = len(map_data[0])
        self.grid_height = len(map_data)
        self.grid = MultiGrid(self.grid_width, self.grid_height, torus=False)
        self.schedule = RandomActivation(self)
        self.exit_position = None
        self.current_id = 0
        
        # Nuevos atributos para los parámetros de búsqueda
        self.search_type = search_type
        self.algorithm = algorithm
        self.heuristic = heuristic

        # Crear el mapa basado en la información proporcionada por el archivo
        self.load_agents_from_map(map_data)

    def next_id(self):
        """
        Retorna un nuevo identificador único para los agentes.
        """
        self.current_id += 1
        return self.current_id

    def load_agents_from_map(self, map_data):
        """
        Crea los agentes Bomberman, rocas, metales y caminos según el mapa cargado.
        Si no se asigna una salida en el archivo de mapa, se asigna aleatoriamente en una roca.
        """
        rocks = []
        exit_assigned = False
        
        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                if cell == "C":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                elif cell == "C_b":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    bomberman = BombermanAgent(self.next_id(), self)
                    self.grid.place_agent(bomberman, (x, y))
                    self.schedule.add(bomberman)
                elif cell == "R":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    rock = Rock(self.next_id(), self)
                    self.grid.place_agent(rock, (x, y))
                    rocks.append((x, y))
                elif cell == "M":
                    metal = Metal(self.next_id(), self)
                    self.grid.place_agent(metal, (x, y))
                elif cell == "C_g":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    balloon = Balloon(self.next_id(), self)
                    self.grid.place_agent(balloon, (x, y))
                    self.schedule.add(balloon)
                elif cell == "R_s":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    rock = Rock(self.next_id(), self)
                    exit = Exit(self.next_id(), self)
                    self.grid.place_agent(rock, (x, y))
                    self.grid.place_agent(exit, (x, y))
                    exit_assigned = True
                    self.exit_position = (x, y)
        
        if not exit_assigned and rocks:
            random_rock_pos = choice(rocks)
            exit = Exit(self.next_id(), self)
            self.grid.place_agent(exit, random_rock_pos)
            self.exit_position = random_rock_pos
            print(f"Salida asignada aleatoriamente en {random_rock_pos}")

    def eliminar_agentes_almacenados(self, pos):
        """
        Elimina agentes que estén en las posiciones adyacentes a la posición de la bomba,
        pero solo afecta a los Bomberman y las Rocas.
        """
        agentes = self.grid.get_neighbors(pos, moore=True, include_center=True)

        for agente in agentes:
            if isinstance(agente, BombermanAgent):
                self.grid.remove_agent(agente)
                if agente in self.schedule.agents:
                    self.schedule.remove(agente)
                print(f"Bomberman {agente.unique_id} eliminado en {agente.pos}")
            elif isinstance(agente, Rock):
                self.grid.remove_agent(agente)
                if agente in self.schedule.agents:
                    self.schedule.remove(agente)
                print(f"Roca {agente.unique_id} destruida en {agente.pos}")
            elif isinstance(agente, Metal):
                print(f"Metal {agente.unique_id} en {agente.pos} es indestructible")

    def step(self):
        """Avanza un paso en la simulación."""
        self.schedule.step()

        # Verificar si hay bombas que explotaron
        for agente in self.schedule.agents:
            if isinstance(agente, Bomb) and agente.timer <= 0:
                self.eliminar_agentes_almacenados(agente.pos)
                self.grid.remove_agent(agente)
                self.schedule.remove(agente)
                
        # Verificar si el bomberman sigue vivo
        bomberman_vivo = any(isinstance(agente, BombermanAgent) for agente in self.schedule.agents)
        
        if not bomberman_vivo:
            # Reiniciar la simulación
            self.__init__(map_data=self.map_data, search_type=self.search_type, algorithm=self.algorithm, heuristic=self.heuristic)
            print("Simulación reiniciada")

        # Aquí puedes implementar la lógica para usar el algoritmo de búsqueda seleccionado
        if self.search_type and self.algorithm:
            self.apply_search_algorithm()

    def apply_search_algorithm(self):
        """
        Aplica el algoritmo de búsqueda seleccionado.
        Esta es una función placeholder que deberás implementar.
        """
        print(f"Aplicando búsqueda {self.search_type} con algoritmo {self.algorithm}")
        if self.search_type == "informada":
            print(f"Usando heurística: {self.heuristic}")
        # Implementa aquí la lógica real de los algoritmos de búsqueda