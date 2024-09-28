import random
from mesa import Agent

class BombermanAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pos = (0, 0)  # Posición inicial; esta será asignada por el modelo
        self.bomb_cooldown = 10  # Cada 10 pasos puede soltar una bomba
        self.steps_since_last_bomb = 0

    def step(self):
        self.move()  # Movimiento aleatorio
        self.steps_since_last_bomb += 1
        self.drop_bomb_if_ready()  # Verifica si es momento de dejar una bomba

    def move(self):
        if self.pos is None:
            return
        
        # Movimiento aleatorio: arriba, abajo, izquierda, derecha
        move = random.choice(["up", "down", "left", "right"])
        
        # Obtener la posición actual
        x, y = self.pos
        
        # Calcular la nueva posición según la dirección elegida
        if move == "up" and y < self.model.grid.height - 1:
            new_pos = (x, y + 1)
        elif move == "down" and y > 0:
            new_pos = (x, y - 1)
        elif move == "left" and x > 0:
            new_pos = (x - 1, y)
        elif move == "right" and x < self.model.grid.width - 1:
            new_pos = (x + 1, y)
        else:
            return  # No moverse si la dirección no es válida

        # Verificar si la nueva posición tiene una roca o metal
        contents = self.model.grid.get_cell_list_contents([new_pos])
        if any(isinstance(obj, (Rock, Metal)) for obj in contents):
            return  # No moverse si hay una roca o metal en la nueva posición

        # Mover el agente a la nueva posición si está libre
        self.model.grid.move_agent(self, new_pos)

    def drop_bomb_if_ready(self):
        """
        Deja una bomba si han pasado suficientes pasos desde la última vez.
        """
        if self.steps_since_last_bomb >= self.bomb_cooldown:
            bomb = Bomb(self.model.next_id(), self.model)
            self.model.grid.place_agent(bomb, self.pos)
            self.model.schedule.add(bomb)
            self.steps_since_last_bomb = 0  # Reinicia el temporizador para la próxima bomba
            print(f"Bomberman {self.unique_id} dejó una bomba en {self.pos}")


class Bomb(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.timer = 10  # Tiempo antes de que la bomba explote

    def step(self):
        # Lógica para reducir el temporizador de la bomba
        self.timer -= 1
        if self.timer <= 0:
            # Verificar si la bomba tiene una posición antes de eliminarla
            if self.pos is not None:
                # Eliminar a los bombermans y rocas que estén a un cuadrado a la redonda
                self.model.eliminar_agentes_almacenados(self.pos)
                # Eliminar la bomba
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                print(f"Bomba {self.unique_id} explotó en {self.pos}")
            else:
                print(f"Bomba {self.unique_id} ya no está en la grilla.")

class Rock(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Metal(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
class Path(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

class Balloon(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

class Exit(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
