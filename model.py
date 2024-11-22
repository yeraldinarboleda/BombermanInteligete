from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon, NumberedPath ,Explosion, Extra
from controllers.UninformedSearch import SearchFunctions, Node
from controllers.InformedSearch import InformedSearch
import os
import random

class BombermanModel(Model):
    def __init__(self, map_data, search_type, algorithm, heuristic, comodin):
        # Agregar variable para almacenar las posiciones visitadas
        self.path_positions = {}
        self.path_counter = 1  # Empezar la numeración desde 1
        
        # Almacena los parámetros iniciales
        self.initial_map_data = map_data
        self.initial_search_type = search_type
        self.initial_algorithm = algorithm
        self.initial_heuristic = heuristic
        
        self.visited_positions = []

        self.map_data = map_data
        self.grid_width = len(map_data[0])
        self.grid_height = len(map_data)
        self.grid = MultiGrid(self.grid_width, self.grid_height, torus=False)
        self.schedule = RandomActivation(self)
        self.exit_position = None
        self.current_id = 0
        self.exit_position = None

        self.running = True
        self.original_path = None  # Añadimos esta variable para guardar el camino original
        
        self.search_type = search_type
        self.algorithm = algorithm
        self.heuristic = heuristic

        self.current_path = None
        
        self.path = []
        
        
        # Inicializar el poder de destrucción y la probabilidad de comodines
        self.pd = 1  # Poder de destrucción inicial
        self.comodin_count = comodin

        self.load_agents_from_map(map_data)

        self.search_functions = SearchFunctions(self.get_walkable_nodes(), self.map_data)
        
        self.step_count = 0
        self.estados_folder = "estados"
        if not os.path.exists(self.estados_folder):
            os.makedirs(self.estados_folder)
            
        self.visit_order = {}  
        self.visit_counter = 1  
        
        # Llamar al método de configuración inicial
        self.setup_model()

        self.apply_search_algorithm()

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def place_agent_safely(self, agent, pos):
        cell_contents = self.grid.get_cell_list_contents(pos)

        # Permitir coexistencia de NumberedPath, Exit y Rock con otros agentes
        if isinstance(agent, (NumberedPath, Exit, Rock, Path)):
            self.grid.place_agent(agent, pos)
            self.schedule.add(agent)
        elif not any(isinstance(existing_agent, type(agent)) for existing_agent in cell_contents):
            self.grid.place_agent(agent, pos)
            self.schedule.add(agent)

    def load_agents_from_map(self, map_data):
        
        rock_positions = []
        
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
                    rock_positions.append(pos)
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
        # Colocar los comodines en posiciones de roca de forma aleatoria
        random.shuffle(rock_positions)
        for pos in rock_positions[:self.comodin_count]:
            self.place_agent_safely(Extra(self.next_id(), self), pos)
            
    def setup_model(self):
        # Inicializar la grilla y el schedule
        self.grid_width = len(self.initial_map_data[0])
        self.grid_height = len(self.initial_map_data)
        self.grid = MultiGrid(self.grid_width, self.grid_height, torus=False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.exit_position = None
        
        # Cargar agentes
        self.load_agents_from_map(self.initial_map_data)
        self.apply_search_algorithm()


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

    

    # Agregar método recalculate_path en model.py
    def recalculate_path(self, bomberman):
        start_node = Node(bomberman.pos[0], bomberman.pos[1])
        goal_node = Node(self.exit_position[0], self.exit_position[1])
        
        # Usar el mismo algoritmo de búsqueda que se usó inicialmente
        if self.search_type == "no-informada":
            if self.algorithm == "Anchura":
                path, _ = self.search_functions.RecorridoEnAnchura(start_node, goal_node)
            elif self.algorithm == "Profundidad":
                path, _ = self.search_functions.RecorridoEnProfundidad(start_node, goal_node)
            elif self.algorithm == "Costo Uniforme":
                path, _ = self.search_functions.RecorridoCostoUniforme(start_node, goal_node)
        else:  # búsqueda informada
            search_functions = InformedSearch(self.get_walkable_nodes(), self.map_data)
            if self.algorithm == "Beam Search":
                path, _ = search_functions.beam_search(start_node, goal_node)
            elif self.algorithm == "Hill Climbing":
                path, _ = search_functions.hill_climbing(start_node, goal_node)
            elif self.algorithm == "A*":
                path, _ = search_functions.a_star(start_node, goal_node)
        
        if path:
            self.path = [Node(pos[0], pos[1]) for pos in path[1:]]  # Excluir posición actual
            self.current_step = 0
        else:
            print("No se pudo encontrar un nuevo camino hacia la salida")
            
            
    def find_path(self, start_pos, goal_pos):
        """
        Recalcula el camino desde la posición actual hasta el objetivo
        """
        start_node = Node(start_pos[0], start_pos[1])
        goal_node = Node(goal_pos[0], goal_pos[1])
        
        # Crear matriz actual del estado del juego
        current_matrix = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        for (contents, (x, y)) in self.grid.coord_iter():
            if any(isinstance(agent, (Metal, Rock)) for agent in contents):
                current_matrix[y][x] = "M"
            else:
                current_matrix[y][x] = "C"
        
        # Usar el algoritmo de búsqueda apropiado
        if hasattr(self, 'search_type') and hasattr(self, 'algorithm'):
            if self.search_type == "no-informada":
                from controllers.UninformedSearch import SearchFunctions
                search = SearchFunctions([], current_matrix)
                if self.algorithm == "Anchura":
                    return search.RecorridoEnAnchura(start_node, goal_node)
                elif self.algorithm == "Profundidad":
                    return search.RecorridoEnProfundidad(start_node, goal_node)
                elif self.algorithm == "Costo Uniforme":
                    return search.RecorridoCostoUniforme(start_node, goal_node)
            else:  # informada
                from controllers.InformedSearch import InformedSearch
                search = InformedSearch([], current_matrix, heuristic_type="manhattan" if self.heuristic == "Manhattan" else "euclidean")
                if self.algorithm == "Beam Search":
                    return search.beam_search(start_node, goal_node)
                elif self.algorithm == "Hill Climbing":
                    return search.hill_climbing(start_node, goal_node)
                elif self.algorithm == "A*":
                    return search.a_star(start_node, goal_node)
        
        return None, None
    
    def is_bomb_exploded(self):
        # Devuelve True si alguna bomba ha explotado
        for agent in self.schedule.agents:
            if isinstance(agent, Bomb) and agent.timer <= 0:
                return True
        return False
         


    def check_and_collect_power(self, bomberman, pos):
        """
        Verifica y recoge poderes en la posición actual
        """
        contents = self.grid.get_cell_list_contents(pos)
        for agent in contents:
            if isinstance(agent, Extra):
                print(f"¡Poder recogido! Poder de destrucción aumentado de {self.pd} a {self.pd + 1}")
                self.pd += 1
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
                return True
        return False

    def get_safe_escape_position(self, bomberman_pos):
        """
        Encuentra una posición segura fuera del rango de la explosión.
        """
        # Calcular el área de peligro (rango de la explosión)
        danger_positions = set()
        # Añadir la posición central
        danger_positions.add(bomberman_pos)
        
        # Añadir posiciones en las cuatro direcciones considerando el pd actual
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            for distance in range(1, self.pd + 1):
                new_x = bomberman_pos[0] + (dx * distance)
                new_y = bomberman_pos[1] + (dy * distance)
                if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
                    danger_positions.add((new_x, new_y))
        
        # Buscar todas las posiciones seguras (fuera del área de peligro)
        safe_positions = []
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                pos = (x, y)
                if pos not in danger_positions:
                    # Verificar que la posición está libre
                    contents = self.grid.get_cell_list_contents(pos)
                    if not any(isinstance(agent, (Metal, Rock, Balloon, Bomb)) for agent in contents):
                        safe_positions.append(pos)
        
        if not safe_positions:
            return None
            
        # Encontrar la posición segura más cercana que sea alcanzable
        safe_positions.sort(key=lambda pos: abs(pos[0] - bomberman_pos[0]) + abs(pos[1] - bomberman_pos[1]))
        
        for safe_pos in safe_positions:
            path, _ = self.find_path(bomberman_pos, safe_pos)
            if path and len(path) > 1:  # Asegurarse de que hay un camino válido
                return safe_pos
                
        return None

    def handle_explosion(self, pos):
        # Inicializar lista de posiciones a afectar por la explosión
        explosion_positions = [(pos[0], pos[1])]
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Direcciones cardinales
        
        # Calcular el alcance de la explosión en cada dirección
        for dx, dy in directions:
            # Iterar por cada unidad de distancia hasta el poder de destrucción actual
            for distance in range(1, self.pd + 1):
                new_pos = (pos[0] + dx * distance, pos[1] + dy * distance)
                
                # Verificar que la posición está dentro de los límites de la grilla
                if 0 <= new_pos[0] < self.grid_width and 0 <= new_pos[1] < self.grid_height:
                    contents = self.grid.get_cell_list_contents(new_pos)
                    
                    # Si hay metal, detener la propagación en esta dirección
                    if any(isinstance(agent, Metal) for agent in contents):
                        break
                    
                    # Si hay roca, incluir esta posición pero detener la propagación en esta dirección
                    if any(isinstance(agent, Rock) for agent in contents):
                        explosion_positions.append(new_pos)
                        break
                    
                    # Si no hay obstáculos, continuar la propagación
                    explosion_positions.append(new_pos)

        # Procesar los efectos en todas las posiciones afectadas
        for explosion_pos in explosion_positions:
            cell_contents = list(self.grid.get_cell_list_contents(explosion_pos))
            for agent in cell_contents:
                if isinstance(agent, Rock):
                    self.grid.remove_agent(agent)
                    self.schedule.remove(agent)
                    print(f"Roca {agent.unique_id} destruida en {agent.pos}")
                elif isinstance(agent, BombermanAgent):
                    self.grid.remove_agent(agent)
                    self.schedule.remove(agent)
                    print(f"¡Bomberman murió en la explosión en {explosion_pos}!")
                    self.running = False
                    return
                elif isinstance(agent, Balloon):
                    self.grid.remove_agent(agent)
                    self.schedule.remove(agent)
                    print(f"Globo {agent.unique_id} destruido en {explosion_pos}")

            # Crear efecto visual de explosión
            explosion = Explosion(self.next_id(), self)
            self.grid.place_agent(explosion, explosion_pos)
            self.schedule.add(explosion)

    def step(self):
        """Maneja toda la lógica de pasos del modelo y los agentes."""
        self.schedule.step()
        
        # Manejar explosiones de bombas
        bombs_to_remove = []
        explosion_occurred = False
        
        for agent in self.schedule.agents:
            if isinstance(agent, Bomb):
                agent.timer -= 1
                if agent.timer <= 0:
                    self.handle_explosion(agent.pos)
                    bombs_to_remove.append(agent)
                    explosion_occurred = True
                    
        # Remover bombas explotadas
        for bomb in bombs_to_remove:
            self.grid.remove_agent(bomb)
            self.schedule.remove(bomb)
            
        # Obtener referencia a Bomberman
        bomberman = next((agent for agent in self.schedule.agents if isinstance(agent, BombermanAgent)), None)
        if not bomberman:
            return
            
        # Verificar y recoger poder en la posición actual
        self.check_and_collect_power(bomberman, bomberman.pos)
            
        # Actualizar la lista de posiciones visitadas
        if bomberman.pos not in self.visited_positions:
            self.visited_positions.append(bomberman.pos)
        
        # Verificar si Bomberman ha llegado a la salida
        if bomberman.pos == self.exit_position:
            print("¡Bomberman ha llegado a la salida! ¡Victoria!")
            self.running = False
            return
            
        # Verificar colisión con globo
        contents = self.grid.get_cell_list_contents(bomberman.pos)
        if any(isinstance(agent, Balloon) for agent in contents):
            print("¡Bomberman se encontró con un globo y ha muerto!")
            self.grid.remove_agent(bomberman)
            self.schedule.remove(bomberman)
            self.running = False
            return
            
        # Manejar el comportamiento de escape de la bomba
        if bomberman.avoiding_bomb:
            if bomberman.waiting_for_explosion:
                if explosion_occurred:
                    print("¡Explosión detectada! Recalculando ruta...")
                    bomberman.waiting_for_explosion = False
                    bomberman.avoiding_bomb = False
                    self.recalculate_path(bomberman)
                    return
                elif bomberman.escape_path and len(bomberman.escape_path) > 0:
                    next_pos = bomberman.escape_path.pop(0)
                    # Verificar y recoger poder antes de moverse
                    self.grid.move_agent(bomberman, next_pos)
                    self.check_and_collect_power(bomberman, next_pos)
                    return
            
        # Movimiento normal siguiendo el path
        if self.path and self.current_step < len(self.path):
            next_pos = self.path[self.current_step].get_position()
            contents = self.grid.get_cell_list_contents(next_pos)
            
            # Verificar si hay una roca en la siguiente posición
            if any(isinstance(agent, Rock) for agent in contents):
                # Solo colocar bomba si no estamos evitando otra
                if not bomberman.avoiding_bomb:
                    print("Encontrada roca. Colocando bomba...")
                    # Colocar bomba
                    bomberman.original_position = bomberman.pos
                    bomb = Bomb(self.next_id(), self)
                    self.place_agent_safely(bomb, bomberman.pos)
                    
                    # Buscar posición segura para escape
                    safe_pos = self.get_safe_escape_position(bomberman.pos)
                    if safe_pos:
                        print(f"Posición segura encontrada en {safe_pos}. Calculando ruta de escape...")
                        escape_path, _ = self.find_path(bomberman.pos, safe_pos)
                        if escape_path and len(escape_path) > 1:
                            bomberman.avoiding_bomb = True
                            bomberman.waiting_for_explosion = True
                            bomberman.escape_path = escape_path[1:]  # Excluir posición actual
                            print(f"Ruta de escape establecida con {len(bomberman.escape_path)} pasos")
                        else:
                            print("No se pudo encontrar una ruta hacia la posición segura")
                    else:
                        print("No se encontró una posición segura para escapar")
            else:
                # Mover normalmente si no hay obstáculos
                self.grid.move_agent(bomberman, next_pos)
                # Verificar y recoger poder después de moverse
                self.check_and_collect_power(bomberman, next_pos)
                self.current_step += 1
        elif self.path and self.current_step >= len(self.path):
            print("Recalculando ruta hacia la salida...")
            self.recalculate_path(bomberman)
            
            
        # Verificar colisión con globo
        cell_contents = self.grid.get_cell_list_contents(bomberman.pos)
        if any(isinstance(agent, Balloon) for agent in cell_contents):
            print("¡Bomberman se encontró con un globo y ha muerto!")
            self.grid.remove_agent(bomberman)
            self.schedule.remove(bomberman)
            self.running = False  # Pausar la ejecución del modelo
            return
                
        # Actualizar globos después del movimiento de Bomberman
        for agent in self.schedule.agents:
            if isinstance(agent, Balloon):
                agent.step()  # Llamar al método `step` del globo para actualizar su posición

        # Lógica adicional (verificación de poderes, explosiones, etc.)
        self.step_count += 1