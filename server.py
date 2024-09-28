from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import BombermanModel  # Importamos tu modelo de Bomberman
from agent import BombermanAgent, Bomb  # Importamos los agentes

# Definir cómo se visualizan los agentes
def agent_portrayal(agent):
    if isinstance(agent, BombermanAgent):
        portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5, "Color": "blue"}
        portrayal["Layer"] = 1  # Definir la capa para Bomberman
    elif isinstance(agent, Bomb):
        portrayal = {"Shape": "circle", "Filled": "true", "r": 0.3, "Color": "red"}
        portrayal["Layer"] = 0  # Definir la capa para las bombas
    return portrayal


# Dimensiones del mapa
width, height = 10, 10

# Crear la grilla para visualizar los agentes
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

# Crear el servidor modular para ejecutar la simulación
server = ModularServer(
    BombermanModel,
    [grid],  # Agregar el módulo de visualización
    "Bomberman Simulation",
    {"width": width, "height": height, "N": 5}  # Parámetros del modelo
)

server.port = 8521  # El puerto para la interfaz
server.launch()
