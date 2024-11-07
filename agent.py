from mesa import Agent
import random

class BombermanAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pos = (0, 0)
        self.path = None
        self.current_step = 0
        self.avoiding_bomb = False
        self.waiting_for_explosion = True
        self.original_position = None
        self.escape_path = []  # Almacenar el camino de escape
        self.return_path = []  # Almacenar el camino de regreso
        self.is_returning = False  # Bandera para indicar si está regresando

    def place_bomb_and_escape(self):
        """Coloca una bomba y genera una ruta de escape basada en el poder de destrucción (pd)."""
        self.original_position = self.pos
        self.avoiding_bomb = True
        self.waiting_for_explosion = True
        self.escape_path = []
        self.return_path = []
        self.is_returning = False

        # Calcular el camino de escape basado en el poder de destrucción
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        current_pos = self.pos
        self.escape_path.append(current_pos)

        # Aumentar la distancia de escape en función de `pd`
        for _ in range(self.model.pd + 2):  # Escape `pd` casillas + 1 de seguridad
            found_safe_step = False
            for dx, dy in directions:
                next_pos = (current_pos[0] + dx, current_pos[1] + dy)
                if self.is_position_transitable(next_pos) and next_pos != self.original_position:
                    self.escape_path.append(next_pos)
                    current_pos = next_pos
                    found_safe_step = True
                    break
            if not found_safe_step:
                break  # Salir si no hay más pasos seguros

        # Crear el camino de regreso invirtiendo el camino de escape
        self.return_path = list(reversed(self.escape_path))

    # Método para verificar si una posición es transitable
    def is_position_transitable(self, pos):
        """Verifica si una posición es transitable (sin roca ni metal)."""
        if 0 <= pos[0] < self.model.grid.width and 0 <= pos[1] < self.model.grid.height:
            contents = self.model.grid.get_cell_list_contents(pos)
            return not any(isinstance(agent, (Rock, Metal)) for agent in contents)
        return False

    def step(self):
        
        contents = self.model.grid.get_cell_list_contents(self.pos)
        for agent in contents:
            if isinstance(agent, Extra):
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
                print("¡Bomberman ha recogido un comodín! Aumenta el poder de destrucción.")
                self.model.pd += 1 
                
        # Verificar si ha llegado a la salida
        if self.pos == self.model.exit_position:
            print("¡Bomberman ha llegado a la salida! Terminando la simulación.")
            self.model.running = False
            return
        
        """# Verificar colisión con un globo
        contents = self.model.grid.get_cell_list_contents(self.pos)
        if any(isinstance(agent, Balloon) for agent in contents):
            print("¡Bomberman se encontró con un globo y ha muerto!")
            # reiniciar la libreria mesa 
            return"""

        # Si está escapando de la bomba
        if self.avoiding_bomb and self.waiting_for_explosion:
            if self.escape_path:
                next_pos = self.escape_path.pop(0)  # Tomar el siguiente paso de escape
                self.model.grid.move_agent(self, next_pos)
            elif not self.waiting_for_explosion:
                self.is_returning = True  # Prepararse para el regreso
                self.waiting_for_explosion = False

        # Si está regresando después de la explosión
        elif self.avoiding_bomb and  not self.waiting_for_explosion:
            if self.return_path:
                next_pos = self.return_path.pop(0)  # Tomar el siguiente paso de regreso
                self.model.grid.move_agent(self, next_pos)
            else:
                # Ha regresado completamente
                self.avoiding_bomb = False
                self.is_returning = False
                self.original_position = None

        # Movimiento normal siguiendo el path
        elif not self.avoiding_bomb:
            if self.path and self.current_step < len(self.path):
                next_pos = self.path[self.current_step].get_position()
                if self.is_position_transitable(next_pos):
                    self.model.grid.move_agent(self, next_pos)
                    self.current_step += 1


# En agent.py
class Bomb(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.timer = model.pd * 2 + 10

    def step(self):
        self.timer -= 1
        if self.timer <= 0:
            # Llama a handle_explosion solo cuando el temporizador llega a 0
            if self.pos is not None:
                self.model.handle_explosion(self.pos)
            self.model.schedule.remove(self)
            print(f"Bomba {self.unique_id} explotó en {self.pos}")


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

class Explosion(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.timer = 2  # Tiempo de vida de la explosión en pasos

    def step(self):
        self.timer -= 1
        if self.timer <= 0:
            # Elimina la explosión del grid y del scheduler
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

class Extra(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pos = (0, 0)