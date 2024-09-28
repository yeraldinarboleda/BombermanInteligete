import random
from mesa import Agent

class BombermanAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pos = (0, 0)  # Posición inicial; esta será asignada por el modelo

    def step(self):
        self.move()  # Llama a la función de movimiento

    def move(self):
        # Movimiento aleatorio: arriba, abajo, izquierda, derecha
        move = random.choice(["up", "down", "left", "right"])
        
        # Obtener la posición actual
        x, y = self.pos
        
        # Actualizar la posición según la dirección elegida
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

        # Mover el agente a la nueva posición
        self.model.grid.move_agent(self, new_pos)


class Bomb(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.timer = 3  # Tiempo antes de que la bomba explote

    def step(self):
        # Lógica para reducir el temporizador de la bomba
        self.timer -= 1
        if self.timer <= 0:
            # Verificar si la bomba tiene una posición antes de eliminarla
            if self.pos is not None:
                # Eliminar a los bombermans que estén a un cuadrado a la redonda
                self.model.eliminar_agentes_almacenados(self.pos)
                # Eliminar la bomba
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                print(f"Bomba {self.unique_id} explotó en {self.pos}")
            else:
                print(f"Bomba {self.unique_id} ya no está en la grilla.")