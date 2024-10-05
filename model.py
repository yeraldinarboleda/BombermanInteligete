from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon, NumberedPath
from random import choice
from controllers.UninformedSearch import SearchFunctions, Node

class BombermanModel(Model):
    def __init__(self, map_data, search_type, algorithm, heuristic):
        # Agregar variable para almacenar las posiciones visitadas
        self.path_positions = {}
        self.path_counter = 1  # Empezar la numeración desde 1

        self.map_data = map_data
        self.grid_width = len(map_data[0])
        self.grid_height = len(map_data)
        self.grid = MultiGrid(self.grid_width, self.grid_height, torus=False)
        self.schedule = RandomActivation(self)
        self.exit_position = None
        self.current_id = 0

        self.search_type = search_type
        self.algorithm = algorithm
        self.heuristic = heuristic

        self.path = []

        self.load_agents_from_map(map_data)

        self.search_functions = SearchFunctions(self.get_walkable_nodes(), self.map_data)
        self.search_functions = SearchFunctions(self.get_walkable_nodes(), self.map_data)

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def load_agents_from_map(self, map_data):
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
                elif cell == "S":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    exit = Exit(self.next_id(), self)
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

    def get_walkable_nodes(self):
        walkable_nodes = []
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                if cell in ["C", "C_b", "C_g" ,"S"]:
                    walkable_nodes.append(Node(x, y))
        return walkable_nodes

    def apply_search_algorithm(self):
        bomberman = next((agent for agent in self.schedule.agents if isinstance(agent, BombermanAgent)), None)
        if not bomberman or not self.exit_position:
            return

        start_node = Node(bomberman.pos[0], bomberman.pos[1])
        goal_node = Node(self.exit_position[0], self.exit_position[1])

        path = None
        if self.search_type == "no-informada":
            if self.algorithm == "Anchura":
                path = self.search_functions.RecorridoEnAnchura(start_node, goal_node)
            elif self.algorithm == "Profundidad":
                path = self.search_functions.RecorridoEnProfundidad(start_node, goal_node)
            elif self.algorithm == "Costo Uniforme":
                path = self.search_functions.RecorridoCostoUniforme(start_node, goal_node)


        if path:
            # Convertir las tuplas en objetos Node
            path_nodes = [Node(pos[0], pos[1]) for pos in path]

            # Elimina el agente existente en la posición
            # ... (resto del código sin cambios)

            # Guarda el camino para que Bomberman lo siga
            self.path = path_nodes[1:]  # Elimina el nodo inicial
            self.current_step = 0
        else:
            print("No se encontró un camino desde Bomberman hasta la salida.")
    def step(self):
        self.schedule.step()

        for agente in self.schedule.agents:
            if isinstance(agente, Bomb) and agente.timer <= 0:
                self.eliminar_agentes_almacenados(agente.pos)
                self.grid.remove_agent(agente)
                self.schedule.remove(agente)
                
        bomberman_vivo = any(isinstance(agente, BombermanAgent) for agente in self.schedule.agents)
        
        if not bomberman_vivo:
            self.__init__(map_data=self.map_data, search_type=self.search_type, algorithm=self.algorithm, heuristic=self.heuristic)
            print("Simulación reiniciada")

        if self.path and self.current_step < len(self.path):
            bomberman = next((agent for agent in self.schedule.agents if isinstance(agent, BombermanAgent)), None)
            if bomberman:
                next_pos = self.path[self.current_step].get_position()
                self.grid.move_agent(bomberman, next_pos)
                self.current_step += 1
        elif self.path and self.current_step >= len(self.path):
            print("Bomberman ha llegado a la salida.")

        # Aplicar el algoritmo de búsqueda
        self.apply_search_algorithm()


