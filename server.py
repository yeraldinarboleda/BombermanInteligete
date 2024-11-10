from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import BombermanModel
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon, NumberedPath, Explosion, Extra
from controllers.MapLoader import MapLoader
from mesa.visualization.UserParam import Choice


# Define la grilla
# En server.py
def agent_portrayal(agent):
    portrayal = {"Shape": "image", "Layer": 0, "scale": 1.0, "text": ""}
    if isinstance(agent, BombermanAgent):
        portrayal["Shape"] = "iconos/bomberman.png"
        portrayal["Layer"] = 4
    elif isinstance(agent, Bomb):
        portrayal["Shape"] = "iconos/bomba.png"
        portrayal["Layer"] = 3 
    elif isinstance(agent, Rock):
        portrayal["Shape"] = "iconos/roca.png"
        portrayal["Layer"] = 5
    elif isinstance(agent, Metal):
        portrayal["Shape"] = "iconos/metal.png"
        portrayal["Layer"] = 1
    elif isinstance(agent, Balloon):
        portrayal["Shape"] = "iconos/globo.png"
        portrayal["Layer"] = 6
    elif isinstance(agent, Exit):
        portrayal["Shape"] = "iconos/salida.png"
        portrayal["Layer"] = 7 
    elif isinstance(agent, Path):
        portrayal["Shape"] = "iconos/camino.png"
        portrayal["Layer"] = 0
    elif isinstance(agent, NumberedPath):
        portrayal["Shape"] = "iconos/camino.png"
        portrayal["Layer"] = 1
        portrayal["text"] = str(agent.number)
        portrayal["text_color"] = "black"    
    elif isinstance(agent, Explosion):
        portrayal["Shape"] = "iconos/explosion.png"
        portrayal["Layer"] = 8
    elif isinstance(agent, Extra):
        portrayal["Shape"] = "iconos/extra.png"
        portrayal["Layer"] = 9
    return portrayal


# Load the map
map_loader = MapLoader("mapas/mapa5.txt")
map_data = map_loader.load_map()

# Define user settable parameters
model_params = {
    "map_data": map_data,
    "search_type": Choice("Search Type", value="informada", choices=["no-informada", "informada"]),
    "algorithm": Choice("Algorithm", value="Hill Climbing", choices=["Anchura", "Profundidad", "Costo Uniforme", "Beam Search", "Hill Climbing", "A*"]),
    "heuristic": Choice("Heuristic", value="Manhattan", choices=["Manhattan", "Euclidiana"]),
    "comodin": Choice("Comodin", value=0, choices=list(range(21)))
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
server.model_cls.server = server
server.launch()