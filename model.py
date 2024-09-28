from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid  # Cambiamos Grid por MultiGrid
from agent import BombermanAgent, Bomb, Rock, Metal  # Importamos los agentes

class BombermanModel(Model):
    """Modelo que representa el juego de Bomberman."""
    def __init__(self, width, height):
        self.num_agents = 1  # Solo un Bomberman
        # Cambiamos Grid por MultiGrid
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # Crear el Bomberman
        bomberman = BombermanAgent(1, self)
        self.grid.place_agent(bomberman, (0, 0))
        self.schedule.add(bomberman)

        # Agregar una bomba
        bomb = Bomb(self.num_agents + 1, self)
        self.grid.place_agent(bomb, (width // 2, height // 2))
        self.schedule.add(bomb)

        # Agregar rocas y metales al azar en el mapa
        for i in range(5):  # Crear 5 rocas
            rock = Rock(self.num_agents + 2 + i, self)
            x, y = self.random_position(width, height)
            self.grid.place_agent(rock, (x, y))
            self.schedule.add(rock)

        for i in range(3):  # Crear 3 metales
            metal = Metal(self.num_agents + 7 + i, self)
            x, y = self.random_position(width, height)
            self.grid.place_agent(metal, (x, y))
            self.schedule.add(metal)

    def random_position(self, width, height):
        return (self.random.randint(0, width - 1), self.random.randint(0, height - 1))

    def eliminar_agentes_almacenados(self, pos):
        """
        Elimina agentes que estén en las posiciones adyacentes a la posición de la bomba,
        pero solo afecta a los Bomberman y las Rocas.
        """
        # Obtener los vecinos de la bomba (vecinos de Moore)
        agentes = self.grid.get_neighbors(pos, moore=True, include_center=True)

        for agente in agentes:
            if isinstance(agente, BombermanAgent):
                # Eliminar a los bombermans en la vecindad
                self.grid.remove_agent(agente)
                self.schedule.remove(agente)
                print(f"Bomberman {agente.unique_id} eliminado en {agente.pos}")
            elif isinstance(agente, Rock):
                # Eliminar las rocas en la vecindad
                self.grid.remove_agent(agente)
                self.schedule.remove(agente)
                print(f"Roca {agente.unique_id} destruida en {agente.pos}")
            elif isinstance(agente, Metal):
                # No se elimina el metal, solo se imprime un mensaje
                print(f"Metal {agente.unique_id} en {agente.pos} es indestructible")

    def step(self):
        """Avanza un paso en la simulación."""
        self.schedule.step()

        # Verificar si hay bombas que explotaron
        for agente in self.schedule.agents:
            if isinstance(agente, Bomb) and agente.timer <= 0:
                self.eliminar_agentes_almacenados(agente.pos)
                self.grid.remove_agent(agente)
                self.schedule.remove(agente)
