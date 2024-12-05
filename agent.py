from mesa import Agent

class BombermanAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.avoiding_bomb = False
        self.waiting_for_explosion = False
        self.original_position = None
        self.escape_path = []
        self.return_path = []
        self.is_returning = False

    def step(self):
       pass

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
    def __init__(self, unique_id, model, difficulty_level=0):
        super().__init__(unique_id, model)
        self.difficulty_level = difficulty_level
        self.search_depth = 0 if difficulty_level == 0 else (3 if difficulty_level == 1 else 6)

    def step(self):
       pass

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
        self.timer = 1  # Tiempo de vida de la explosión en pasos

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