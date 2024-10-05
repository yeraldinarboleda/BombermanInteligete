from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import BombermanModel
from agent import BombermanAgent, Bomb, Rock, Metal, Path, Exit, Balloon , NumberedPath
from controllers.MapLoader import MapLoader
from menu import mostrar_menu

search_type, algorithm, heuristic = mostrar_menu()

def agent_portrayal(agent):
    portrayal = {"Shape": "image", "Layer": 0, "scale": 1.0}
    
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
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "black"
        portrayal["Layer"] = 3
        portrayal["text"] = str(agent.number)
        portrayal["text_color"] = "white"

    return portrayal

# Cargar el mapa
map_loader = MapLoader("mapas/mapa2.txt")
map_data = map_loader.load_map()

grid_width = len(map_data[0])
grid_height = len(map_data)

grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)


# Crear el servidor con los parámetros
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

server.port = 8521
server.launch()