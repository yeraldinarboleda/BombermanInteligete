from controllers.Tree import TreeG  

class AlphaBetaSearch:
    def __init__(self, matriz, heuristic=None):
        self.matriz = matriz
        self.heuristic = heuristic or self.heuristic
        self.tree = TreeG(None)  # Crear un árbol para visualizar la búsqueda
        self.node_counter = 0   # Para asignar identificadores únicos a cada nodo
    
    def alpha_beta(self, current_pos, target_pos, depth, alpha, beta, maximizing_player, salida_pos, visit_order=None):
        if visit_order is None:
            visit_order = {}

        if depth == 0 or current_pos == target_pos:
            score = self.heuristic(current_pos, target_pos, salida_pos, maximizing_player)
            node_id = f"Node{self.node_counter}"
            self.tree.add_node((current_pos, score), None if self.node_counter == 0 else "Parent")
            self.node_counter += 1
            tree_dict = self.tree.to_dict()
      
            return score, current_pos

        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        best_move = None
        parent_node_id = f"Node{self.node_counter}"

        if maximizing_player:
            max_eval = float('-inf')
            for move in possible_moves:
                new_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
                if self.is_valid_position(new_pos):
                    eval, _ = self.alpha_beta(new_pos, target_pos, depth - 1, alpha, beta, False, salida_pos, visit_order)
                    if eval > max_eval:
                        max_eval = eval
                        best_move = new_pos
                    alpha = max(alpha, eval)
                    if alpha >= beta:
                        # Nodo podado
                        break
            self.tree.add_node((current_pos, max_eval), parent_node_id)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in possible_moves:
                new_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
                if self.is_valid_position(new_pos):
                    eval, _ = self.alpha_beta(new_pos, target_pos, depth - 1, alpha, beta, True, salida_pos, visit_order)
                    if eval < min_eval:
                        min_eval = eval
                        best_move = new_pos
                    beta = min(beta, eval)
                    if alpha >= beta:
                        # Nodo podado
                        break
            self.tree.add_node((current_pos, min_eval), parent_node_id)
            return min_eval, best_move

    def is_valid_position(self, pos):
        return (0 <= pos[0] < len(self.matriz[0]) and
                0 <= pos[1] < len(self.matriz) and
                self.matriz[pos[1]][pos[0]] not in ["M", "R"])
        
    
    def heuristic(self, current_pos, target_pos, salida_pos, maximizing_player):
        bomberman_distance = abs(target_pos[0] - current_pos[0]) + abs(target_pos[1] - current_pos[1])
        salida_distance = abs(current_pos[0] - salida_pos[0]) + abs(current_pos[1] - salida_pos[1])

        # Ponderar dependiendo del jugador
        if maximizing_player:
            return -bomberman_distance  # Maximizar cercanía a la salida
        else:
            return  salida_distance # Minimizar distancia al Bomberman