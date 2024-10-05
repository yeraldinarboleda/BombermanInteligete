from mesa import Agent

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

    def step(self):
        # Actualizar la posición del agente en la grilla
        self.model.grid.move_agent(self, self.pos)
