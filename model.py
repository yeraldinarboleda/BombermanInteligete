from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid  # Cambiamos Grid por MultiGrid
from agent import BombermanAgent, Bomb  # Importamos los agentes

class BombermanModel(Model):
    """Modelo que representa el juego de Bomberman."""
    def __init__(self, width, height, N):
        self.num_agents = N
        # Cambiamos Grid por MultiGrid
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # Crear agentes
        for i in range(self.num_agents):
            agent = BombermanAgent(i, self)
            self.grid.place_agent(agent, (i % width, i % height))
            self.schedule.add(agent)

        # Agregar una bomba
        bomb = Bomb(self.num_agents + 1, self)
        self.grid.place_agent(bomb, (width // 2, height // 2))
        self.schedule.add(bomb)

    def eliminar_agentes_almacenados(self, pos):
        # Obtener la grilla
        grid = self.grid

        # Obtener las posiciones de los agentes en la grilla
        agentes = grid.get_neighbors(pos, moore=True)

        # Eliminar a los bombermans que estén a un cuadrado a la redonda
        for agente in agentes:
            if isinstance(agente, BombermanAgent):
                grid.remove_agent(agente)
                self.schedule.remove(agente)

    def step(self):
        """Avanza un paso en la simulación."""
        self.schedule.step()

        # Verificar si hay bombas que explotaron
        for agente in self.schedule.agents:
            if isinstance(agente, Bomb):
                if agente.timer <= 0:
                    # Eliminar a los bombermans que estén a un cuadrado a la redonda
                    self.eliminar_agentes_almacenados(agente.pos)
                    # Eliminar la bomba
                    self.grid.remove_agent(agente)
                    self.schedule.remove(agente)