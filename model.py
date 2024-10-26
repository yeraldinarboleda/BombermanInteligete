from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon, NumberedPath
from controllers.UninformedSearch import SearchFunctions, Node
from controllers.InformedSearch import InformedSearch
import os
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
        
        self.step_count = 0
        self.estados_folder = "estados"
        if not os.path.exists(self.estados_folder):
            os.makedirs(self.estados_folder)
            
        self.visit_order = {}  
        self.visit_counter = 1  

        self.apply_search_algorithm()

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def place_agent_safely(self, agent, pos):
        cell_contents = self.grid.get_cell_list_contents(pos)
        
        # Permitir la coexistencia de NumberedPath con otros agentes
        if isinstance(agent, NumberedPath):
            self.grid.place_agent(agent, pos)
            self.schedule.add(agent)
        elif not any(isinstance(existing_agent, type(agent)) for existing_agent in cell_contents):
            self.grid.place_agent(agent, pos)
            self.schedule.add(agent)
    

    def load_agents_from_map(self, map_data):
        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                pos = (x, y)
                if cell == "C":
                    self.place_agent_safely(Path(pos, self), pos)
                elif cell == "C_b":
                    self.place_agent_safely(Path(pos, self), pos)
                    self.place_agent_safely(BombermanAgent(self.next_id(), self), pos)
                elif cell == "R":
                    self.place_agent_safely(Path(pos, self), pos)
                    self.place_agent_safely(Rock(self.next_id(), self), pos)
                elif cell == "M":
                    self.place_agent_safely(Metal(self.next_id(), self), pos)
                elif cell == "C_g":
                    self.place_agent_safely(Path(pos, self), pos)
                    self.place_agent_safely(Balloon(self.next_id(), self), pos)
                elif cell == "R_s":
                    self.place_agent_safely(Path(pos, self), pos)
                    self.place_agent_safely(Rock(self.next_id(), self), pos)
                    self.place_agent_safely(Exit(self.next_id(), self), pos)
                    self.exit_position = pos
                elif cell == "S":
                    self.place_agent_safely(Path(pos, self), pos)
                    self.place_agent_safely(Exit(self.next_id(), self), pos)
                    self.exit_position = pos
        """
        
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
            elif isinstance(agente, Exit):
                print(f"Salida no debe ser eliminada en {agente.pos}")
            elif isinstance(agente, BombermanAgent):
                print(f"Bomberman no debe ser eliminado en {agente.pos}")
"""
    def get_walkable_nodes(self):
        walkable_nodes = []
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                if cell in ["C", "C_b", "C_g" ,"S"]:
                    walkable_nodes.append(Node(x, y))
        return walkable_nodes
    
    def export_game_state(self):
        state = []
        
        # Crear el directorio específico según el algoritmo de búsqueda
        if self.algorithm == "Profundidad":
            folder_path = os.path.join(self.estados_folder, "profundidad")
        elif self.algorithm == "Anchura":
            folder_path = os.path.join(self.estados_folder, "anchura")
        elif self.algorithm == "Costo Uniforme":
            folder_path = os.path.join(self.estados_folder, "costo_uniforme")
        elif self.algorithm == "Beam Search":
            folder_path = os.path.join(self.estados_folder, "beam_search")
        elif self.algorithm == "Hill Climbing":
            folder_path = os.path.join(self.estados_folder, "hill_climbing")
        elif self.algorithm == "A*":
            folder_path = os.path.join(self.estados_folder, "A*")
        else:
            folder_path = self.estados_folder  # Carpeta por defecto si no se especifica el algoritmo

        # Crear la carpeta si no existe
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Recorrer la grilla y obtener el estado actual
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                cell_agents = self.grid.get_cell_list_contents((x, y))
                cell_state = self.get_cell_state(cell_agents)
                row.append(cell_state)
            state.append(row)
        
        # Guardar el archivo de estado en la carpeta correspondiente
        filename = os.path.join(folder_path, f"state_{self.step_count}.txt")
        with open(filename, 'w') as f:
            for row in state:
                f.write(''.join(row) + '\n')


    def get_cell_state(self, cell_agents):
        state = " "
        for agent in cell_agents:
            if isinstance(agent, BombermanAgent):
                return "C_b"
            elif isinstance(agent, Bomb):
                return "B"
            elif isinstance(agent, Rock) and any(isinstance(a, Exit) for a in cell_agents):
                return "R_s"
            elif isinstance(agent, Rock):
                state = "R"
            elif isinstance(agent, Metal):
                return "M"
            elif isinstance(agent, Balloon):
                state = "C_g"
            elif isinstance(agent, Exit):
                state = "S"
            elif isinstance(agent, Path) and state == " ":
                state = "C"
        return state

    def apply_search_algorithm(self):
        bomberman = next((agent for agent in self.schedule.agents if isinstance(agent, BombermanAgent)), None)
        if not bomberman or not self.exit_position:
            return

        # Define los nodos de inicio y objetivo
        start_node = Node(bomberman.pos[0], bomberman.pos[1])
        goal_node = Node(self.exit_position[0], self.exit_position[1])

        path = None

        # Selección del algoritmo de búsqueda (informada o no informada)
        if self.search_type == "no-informada":
            if self.algorithm == "Anchura":
                path, self.visit_order = self.search_functions.RecorridoEnAnchura(start_node, goal_node)
            elif self.algorithm == "Profundidad":
                path, self.visit_order = self.search_functions.RecorridoEnProfundidad(start_node, goal_node)
            elif self.algorithm == "Costo Uniforme":
                path, self.visit_order = self.search_functions.RecorridoCostoUniforme(start_node, goal_node)

        if self.search_type == "informada":
            search_functions = InformedSearch(self.get_walkable_nodes(), self.map_data)
            if self.algorithm == "Beam Search":
                path, self.visit_order = search_functions.beam_search(start_node, goal_node)
            elif self.algorithm == "Hill Climbing":
                path, self.visit_order = search_functions.hill_climbing(start_node, goal_node)
            elif self.algorithm == "A*":
                path, self.visit_order = search_functions.a_star(start_node, goal_node)

        if path:
            # Crear los agentes NumberedPath que muestran el orden de visita en cada celda del camino
            for pos, order in self.visit_order.items():
                numbered_path_agent = NumberedPath(self.next_id(), self, order)
                self.place_agent_safely(numbered_path_agent, pos)

            # Guarda el camino para que Bomberman lo siga
            path_nodes = [Node(pos[0], pos[1]) for pos in path]  # Convierte las posiciones en objetos Node
            self.path = path_nodes[1:]  # Elimina el nodo inicial
            self.current_step = 0

        else:
            print("No se encontró un camino desde Bomberman hasta la salida.")

    
    def handle_explosion(self, pos):
        cell_contents = list(self.grid.get_cell_list_contents(pos))
        for agent in cell_contents:
            if isinstance(agent, Rock) and not any(isinstance(a, Exit) for a in cell_contents):
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
            elif isinstance(agent, Balloon):
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)   
            
    def step(self):
        self.schedule.step()
        
        for agent in self.schedule.agents:
            if isinstance(agent, Bomb) and agent.timer <= 0:
                self.handle_explosion(agent.pos)
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)

        """for agente in self.schedule.agents:
            if isinstance(agente, Bomb) and agente.timer <= 0:
                self.eliminar_agentes_almacenados(agente.pos)
                self.grid.remove_agent(agente)
                self.schedule.remove(agente)"""

        if self.path and self.current_step < len(self.path):
            bomberman = next((agent for agent in self.schedule.agents if isinstance(agent, BombermanAgent)), None)
            if bomberman:
                next_pos = self.path[self.current_step].get_position()
                # Mover a Bomberman sin eliminar otros agentes
                self.grid.move_agent(bomberman, next_pos)
                self.current_step += 1
        elif self.path and self.current_step >= len(self.path):
            self.running = False  # Pausa la simulación

        self.export_game_state()
        self.step_count += 1


