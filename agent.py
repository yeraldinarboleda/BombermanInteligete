from mesa import Agent
import random

class BombermanAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pos = (0, 0)
        self.path = None
        self.current_step = 0

    def set_path(self, path):
        self.path = path
        self.current_step = 0

    def step(self):
        pass  # El movimiento ahora es controlado por el modelo

class Bomb(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.timer = 10

    def step(self):
        self.timer -= 1
        if self.timer <= 0:
            if self.pos is not None:
                self.model.eliminar_agentes_almacenados(self.pos)
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                print(f"Bomba {self.unique_id} explotó en {self.pos}")
            else:
                print(f"Bomba {self.unique_id} ya no está en la grilla.")

class Rock(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pos = (0,0)

class Metal(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pos = (0,0)

class Path(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.visit_order = None

class Balloon(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        
    def step(self):
        # Define las posibles direcciones de movimiento: (dx, dy)
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # abajo, arriba, derecha, izquierda
        
        # Elige un movimiento aleatorio
        move = random.choice(possible_moves)
        
        # Calcula la nueva posición
        new_position = (self.pos[0] + move[0], self.pos[1] + move[1])
        
        # Verifica si la nueva posición está dentro de los límites del grid y es un espacio transitable
        if 0 <= new_position[0] < self.model.grid_width and 0 <= new_position[1] < self.model.grid_height:
            # Verifica si el nuevo espacio está libre (no tiene obstáculos)
            cell_contents = self.model.grid.get_cell_list_contents(new_position)
            if all(isinstance(agent, Path) for agent in cell_contents):  # solo se mueve si es una celda transitable
                # Mueve el globo a la nueva posición
                self.model.grid.move_agent(self, new_position)
                self.pos = new_position

class Exit(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        
class NumberedPath(Agent):
    """
    Clase que representa una celda con un número que indica el orden de visita.
    """
    def __init__(self, pos, model, number):
        super().__init__(pos, model)
        self.pos = pos
        self.number = number

    