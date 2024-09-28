from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import BombermanModel
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon
from map_loader import MapLoader  # Importamos el nuevo cargador de mapas

# Definir cómo se visualizan los agentes con imágenes
def agent_portrayal(agent):
    portrayal = {"Shape": "image", "Layer": 1, "scale": 1.0}
    
    if isinstance(agent, BombermanAgent):
        portrayal["Shape"] = "iconos/bomberman.png"
    elif isinstance(agent, Bomb):
        portrayal["Shape"] = "iconos/bomba.png"
        portrayal["Layer"] = 2
    elif isinstance(agent, Rock):
        portrayal["Shape"] = "iconos/roca.png"
        portrayal["Layer"] = 2
    elif isinstance(agent, Metal):
        portrayal["Shape"] = "iconos/metal.png"
    elif isinstance(agent, Balloon):
        portrayal["Shape"] = "iconos/globo.png"
    elif isinstance(agent, Exit):
        portrayal["Shape"] = "iconos/salida.png"
        portrayal["Layer"] = 2
    elif isinstance(agent, Path):
        portrayal["Shape"] = "iconos/camino.png"
        portrayal["Layer"] = 0

    return portrayal

# Cargar el mapa desde el archivo
map_loader = MapLoader("mapas/mapa.txt")

map_data = map_loader.load_map()

# Dimensiones del mapa
grid_width = len(map_data[0])
grid_height = len(map_data)

# Crear la grilla para visualizar los agentes
grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)

# Crear el servidor modular para ejecutar la simulación
server = ModularServer(
    BombermanModel,
    [grid],  # Agregar el módulo de visualización
    "Bomberman Simulation",
    {"map_data": map_data}  # Pasar el mapa cargado al modelo
)

server.port = 8521  # El puerto para la interfaz
server.launch()