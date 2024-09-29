from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice
from model import BombermanModel
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon
from map_loader import MapLoader

# Definir cómo se visualizan los agentes con imágenes
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
map_loader = MapLoader("mapas/mapa2.txt")
map_data = map_loader.load_map()

# Dimensiones del mapa
grid_width = len(map_data[0])
grid_height = len(map_data)

# Crear la grilla para visualizar los agentes
grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)

# Definir los parámetros de usuario para el menú de selección de algoritmo
search_type = Choice(
    "Tipo de Búsqueda",
    value="no-informada",
    choices=["no-informada", "informada"]
)

algorithm = Choice(
    "Algoritmo",
    value="Anchura",
    choices=["Anchura", "Profundidad", "Costo Uniforme", "Beam Search", "Hill Climbing", "A*"]
)

heuristic = Choice(
    "Heurística",
    value="Manhattan",
    choices=["Manhattan", "Euclidiana"]
)

# Crear el servidor modular para ejecutar la simulación
server = ModularServer(
    BombermanModel,
    [grid],
    "Bomberman Simulation",
    {
        "map_data": map_data,
        "search_type": search_type,
        "algorithm": algorithm,
        "heuristic": heuristic
    }
)

server.port = 8521  # El puerto para la interfaz
server.launch()