from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import BombermanModel
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon, NumberedPath
from controllers.MapLoader import MapLoader
from mesa.visualization.UserParam import Choice


# Define la grilla
def agent_portrayal(agent):
    portrayal = {"Shape": "image", "Layer": 0, "scale": 1.0, "text": ""}
    if isinstance(agent, BombermanAgent):
        portrayal["Shape"] = "iconos/bomberman.png"
        portrayal["Layer"] = 2
    elif isinstance(agent, Bomb):
        portrayal["Shape"] = "iconos/bomba.png"
        portrayal["Layer"] = 1
    elif isinstance(agent, Rock):
        portrayal["Shape"] = "iconos/roca.png"
        portrayal["Layer"] = 1
    elif isinstance(agent, Metal):
        portrayal["Shape"] = "iconos/metal.png"
        portrayal["Layer"] = 1
    elif isinstance(agent, Balloon):
        portrayal["Shape"] = "iconos/globo.png"
        portrayal["Layer"] = 1
    elif isinstance(agent, Exit):
        portrayal["Shape"] = "iconos/salida.png"
        portrayal["Layer"] = 1
    elif isinstance(agent, Path):
        portrayal["Shape"] = "iconos/camino.png"
        portrayal["Layer"] = 0
    elif isinstance(agent, NumberedPath):
        portrayal["Shape"] = "iconos/camino.png"
        portrayal["Color"] = "white"
        portrayal["Layer"] = 3
        portrayal["text"] = str(agent.number)
        portrayal["text_color"] = "black"
    return portrayal

# Load the map
map_loader = MapLoader("mapas/mapa4.txt")
map_data = map_loader.load_map()

# Define user settable parameters
model_params = {
    "map_data": map_data,  # Include map_data as a parameter
    "search_type": Choice("Search Type", value="no-informada", choices=["no-informada", "informada"]),
    "algorithm": Choice("Algorithm", value="Anchura", choices=["Anchura", "Profundidad", "Costo Uniforme"]),
    "heuristic": Choice("Heuristic", value="Manhattan", choices=["Manhattan", "Euclidiana"])
}


grid_width = len(map_data[0])
grid_height = len(map_data)

grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)

server = ModularServer(
    BombermanModel,
    [grid],
    "Bomberman Simulation",
    model_params
)

server.port = 8521
server.launch()