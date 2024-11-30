from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon, NumberedPath ,Explosion, Extra
from controllers.UninformedSearch import SearchFunctions, Node
from controllers.InformedSearch import InformedSearch
from controllers.podaAlfhaBeta import AlphaBetaSearch
import os
import random

class BombermanModel(Model):
    def __init__(self, map_data, search_type, algorithm, heuristic, comodin, balloon_difficulty, search_depth):
        self.search_depth = search_depth
        self.balloon_difficulty = balloon_difficulty 
        # Agregar variable para almacenar las posiciones visitadas
        self.path_positions = {}
        self.path_counter = 1  # Empezar la numeración desde 1
        
        self.current_step = 0 
        
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
        
        self.search = AlphaBetaSearch(map_data)

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
                    self.place_agent_safely(Balloon(self.next_id(), self, self.balloon_difficulty), pos)
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

        elif self.search_type == "informada":
            search_functions = InformedSearch(self.get_walkable_nodes(), self.map_data)
            if self.algorithm == "Beam Search":
                path, self.visit_order = search_functions.beam_search(start_node, goal_node)
            elif self.algorithm == "Hill Climbing":
                path, self.visit_order = search_functions.hill_climbing(start_node, goal_node)
            elif self.algorithm == "A*":
                path, self.visit_order = search_functions.a_star(start_node, goal_node)

        # Validar y convertir el camino en nodos
        if path and isinstance(path, list) and all(isinstance(pos, tuple) and len(pos) == 2 for pos in path):
            # Convierte las posiciones en objetos Node
            self.path = [Node(pos[0], pos[1]) for pos in path]
            self.current_step = 0  # Inicializa el paso actual
        else:
            print(f"Error: El camino obtenido no es válido. Path: {path}")
            self.path = None
            self.current_step = 0

    

    # Agregar método recalculate_path en model.py
    def recalculate_path(self, bomberman):
        start_node = Node(bomberman.pos[0], bomberman.pos[1])
        goal_node = Node(self.exit_position[0], self.exit_position[1])
        path = None  # Inicializar la variable path

        if self.algorithm == "Poda Alfa Beta":
            # Usar alpha-beta directamente para calcular el próximo movimiento
            _, best_move = self.search.alpha_beta(
                bomberman.pos,
                self.exit_position,
                self.search_depth,
                float('-inf'),
                float('inf'),
                True,  # Maximizing player para Bomberman
                self.exit_position
            )
            if best_move:
                # Si hay un movimiento válido, actualizar el camino con un único paso
                self.path = [bomberman.pos, best_move]
                self.current_step = 0
            else:
                print("Error: No se pudo encontrar un movimiento válido con poda alfa-beta")
                self.path = None
                self.current_step = 0
            return

        # Lógica para otros algoritmos de búsqueda
        if self.search_type == "no-informada":
            if self.algorithm == "Anchura":
                path, _ = self.search_functions.RecorridoEnAnchura(start_node, goal_node)
            elif self.algorithm == "Profundidad":
                path, _ = self.search_functions.RecorridoEnProfundidad(start_node, goal_node)
            elif self.algorithm == "Costo Uniforme":
                path, _ = self.search_functions.RecorridoCostoUniforme(start_node, goal_node)
        else:
            search_functions = InformedSearch(self.get_walkable_nodes(), self.map_data)
            if self.algorithm == "Beam Search":
                path, _ = search_functions.beam_search(start_node, goal_node)
            elif self.algorithm == "Hill Climbing":
                path, _ = search_functions.hill_climbing(start_node, goal_node)
            elif self.algorithm == "A*":
                path, _ = search_functions.a_star(start_node, goal_node)

        # Actualizar el camino para otros algoritmos
        if path:
            self.path = [Node(pos[0], pos[1]) for pos in path[1:]]  # Excluir posición actual
            self.current_step = 0  # Reiniciar el paso actual
        else:
            print("No se pudo encontrar un nuevo camino hacia la salida")
            self.path = None
            self.current_step = 0

            
    def find_path(self, start_pos, goal_pos):
        start_node = Node(start_pos[0], start_pos[1])
        goal_node = Node(goal_pos[0], goal_pos[1])

        # Verificar si las posiciones son válidas
        if not self.grid.is_cell_empty(start_pos) or not self.grid.is_cell_empty(goal_pos):
            print(f"Error: Posiciones inválidas para encontrar camino. Start: {start_pos}, Goal: {goal_pos}")
            return None, None
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
        # Calculate explosion danger zone
        danger_positions = set([bomberman_pos])
        
        # Add danger positions in all directions based on destruction power
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            for distance in range(1, self.pd + 1):
                new_x = bomberman_pos[0] + (dx * distance)
                new_y = bomberman_pos[1] + (dy * distance)
                
                if (0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height):
                    danger_positions.add((new_x, new_y))

        # Find safe positions
        safe_positions = []
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                pos = (x, y)
                if pos not in danger_positions:
                    contents = self.grid.get_cell_list_contents(pos)
                    if not any(isinstance(agent, (Metal, Rock, Balloon, Bomb)) for agent in contents):
                        safe_positions.append(pos)

        if not safe_positions:
            return None

        # Sort safe positions by distance from current position
        safe_positions.sort(key=lambda pos: abs(pos[0] - bomberman_pos[0]) + abs(pos[1] - bomberman_pos[1]))

        # Find the first reachable safe position
        for safe_pos in safe_positions:
            path, _ = self.find_path(bomberman_pos, safe_pos)
            if path and len(path) > 1:
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
            
    def move_bomberman(self, bomberman):
        if not self.path:  # Si no hay un camino calculado, calcula uno nuevo
            self.recalculate_path(bomberman)
        
        if self.algorithm == "Poda Alfa Beta":
            # Recalcular el camino en cada paso si es poda alfa-beta
            self.recalculate_path(bomberman)

        if self.path and self.current_step < len(self.path):
            # Validar si el elemento en path es un nodo o una tupla
            next_pos = None
            if isinstance(self.path[self.current_step], Node):
                next_pos = self.path[self.current_step].get_position()
            elif isinstance(self.path[self.current_step], tuple):
                next_pos = self.path[self.current_step]
            else:
                raise ValueError(f"Formato inesperado en self.path: {self.path[self.current_step]}")

            # Realizar las acciones necesarias
            self.grid.move_agent(bomberman, next_pos)
            self.check_and_collect_power(bomberman, next_pos)
            self.current_step += 1
        elif self.path and self.current_step >= len(self.path):
            print("Recalculando ruta hacia la salida...")
            self.recalculate_path(bomberman)
        
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
                    print(f"Bomberman se mueve a la posición de escape: {next_pos}")
                    self.grid.move_agent(bomberman, next_pos)
                    self.check_and_collect_power(bomberman, next_pos)
                    return
        
        # Eliminar bombas que han explotado
        for bomb in bombs_to_remove:
            self.schedule.remove(bomb)
            self.grid.remove_agent(bomb)

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

            
    def move_balloon(self, balloon):
        bomberman_pos = self.get_bomberman_position()
        salida_pos = self.exit_position

        if balloon.difficulty_level == 0:
            # Movimiento aleatorio para globos de nivel fácil
            new_position = self.get_random_valid_move(balloon.pos)
            if new_position:
                self.grid.move_agent(balloon, new_position)
                print(f"Globo {balloon.unique_id} se mueve aleatoriamente a {new_position}")
            else:
                print(f"Globo {balloon.unique_id} no tiene movimientos válidos.")
            
        else:
            # Movimiento estratégico con Alpha-Beta
            _, best_move = self.search.alpha_beta(
                balloon.pos, bomberman_pos, balloon.search_depth,
                float('-inf'), float('inf'),
                False,  # Maximizing player para el globo
                salida_pos
            )
            if best_move and self.search.is_valid_position(best_move):
                self.grid.move_agent(balloon, best_move)
                print(f"Globo {balloon.unique_id} se mueve estratégicamente a: {best_move}")

    def get_random_valid_move(self, current_position):
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(possible_moves)
        
        valid_moves = []
        for move in possible_moves:
            new_position = (current_position[0] + move[0], current_position[1] + move[1])
            if self.is_valid_position_for_balloon(new_position):
                valid_moves.append(new_position)
        
        print(f"Movimientos válidos para el globo en {current_position}: {valid_moves}")
        return random.choice(valid_moves) if valid_moves else None

    def is_valid_position_for_balloon(self, position):
        """
        Verifica si una posición es válida para que un globo se mueva.
        """
        x, y = position
        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
            return False

        # Verificar si la celda está vacía o transitable
        contents = self.grid.get_cell_list_contents(position)
        return not any(isinstance(agent, (Metal, Rock, Balloon, Bomb)) for agent in contents)

        

    def get_bomberman_position(self):
        for agent in self.schedule.agents:
            if isinstance(agent, BombermanAgent):
                return agent.pos
        return None
    
    def step(self):
        """Maneja toda la lógica de pasos del modelo y los agentes."""
        
        # Mover Bomberman
        bomberman = next((agent for agent in self.schedule.agents if isinstance(agent, BombermanAgent)), None)
        if bomberman:
            self.move_bomberman(bomberman)

        # Mover globos
        for agent in self.schedule.agents:
            if isinstance(agent, Balloon):
                self.move_balloon(agent)

        bomberman_pos = self.get_bomberman_position()
        salida_pos = self.exit_position
        
        if bomberman_pos == salida_pos:
            print("¡Bomberman se encontró con la salida")
            self.running = False  # Detiene la simulación
            return
        
        # Verificar si Bomberman colisiona con un globo
        if bomberman:
            bomberman_pos = bomberman.pos
            contents = self.grid.get_cell_list_contents(bomberman_pos)
            if any(isinstance(agent, Balloon) for agent in contents):
                print("¡Bomberman se encontró con un globo y ha muerto!")
                self.running = False  # Detiene la simulación
                return
        
        # Incrementar contador de pasos
        self.step_count += 1

        # Avanzar el reloj del modelo
        self.schedule.step()


