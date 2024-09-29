from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon  # Importamos los agentes
from random import choice

class BombermanModel(Model):
    """Modelo que representa el juego de Bomberman."""
    
    def __init__(self, map_data):
        self.map_data = map_data
        self.grid_width = len(map_data[0])  # Basado en el archivo de texto
        self.grid_height = len(map_data)
        self.grid = MultiGrid(self.grid_width, self.grid_height, torus=False)
        self.schedule = RandomActivation(self)
        self.exit_position = None  # Posición de la salida
        self.current_id = 0  # Inicializa el contador de IDs para los agentes

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
        rocks = []  # Lista para almacenar todas las posiciones de rocas
        exit_assigned = False  # Bandera para verificar si ya se asignó la salida
        
        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                if cell == "C":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                elif cell == "C_b":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    bomberman = BombermanAgent(0, self)
                    self.grid.place_agent(bomberman, (x, y))
                    self.schedule.add(bomberman)
                elif cell == "R":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    rock = Rock((x, y), self)
                    self.grid.place_agent(rock, (x, y))
                    rocks.append((x, y))  # Añadir la roca a la lista
                elif cell == "M":
                    metal = Metal((x, y), self)
                    self.grid.place_agent(metal, (x, y))
                elif cell == "C_g":
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    balloon = Balloon((x, y), self)
                    self.grid.place_agent(balloon, (x, y))
                    self.schedule.add(balloon)
                elif cell == "R_s":
                    # Si ya hay una roca con salida
                    path = Path((x, y), self)
                    self.grid.place_agent(path, (x, y))
                    rock = Rock((x, y), self)
                    exit = Exit((x, y), self)
                    self.grid.place_agent(rock, (x, y))
                    self.grid.place_agent(exit, (x, y))
                    exit_assigned = True
                    self.exit_position = (x, y)  # Guardar la posición de la salida
        
        # Asignar salida aleatoria si no se especificó
        if not exit_assigned and rocks:
            random_rock_pos = choice(rocks)
            exit = Exit(random_rock_pos, self)
            self.grid.place_agent(exit, random_rock_pos)
            self.exit_position = random_rock_pos  # Guardar la posición de la salida
            print(f"Salida asignada aleatoriamente en {random_rock_pos}")
                

    def eliminar_agentes_almacenados(self, pos):
        """
        Elimina agentes que estén en las posiciones adyacentes a la posición de la bomba,
        pero solo afecta a los Bomberman y las Rocas.
        """
        # Obtener los vecinos de la bomba (vecinos de Moore)
        agentes = self.grid.get_neighbors(pos, moore=True, include_center=True)

        for agente in agentes:
            if isinstance(agente, BombermanAgent):
                # Eliminar a los bombermans en la vecindad
                self.grid.remove_agent(agente)
                if agente in self.schedule.agents:
                    self.schedule.remove(agente)
                print(f"Bomberman {agente.unique_id} eliminado en {agente.pos}")
            elif isinstance(agente, Rock):
                # Eliminar las rocas en la vecindad
                self.grid.remove_agent(agente)
                if agente in self.schedule.agents:
                    self.schedule.remove(agente)
                print(f"Roca {agente.unique_id} destruida en {agente.pos}")
            elif isinstance(agente, Metal):
                # No se elimina el metal, solo se imprime un mensaje
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
            self.__init__(map_data=self.map_data)
            print("Simulación reiniciada")
