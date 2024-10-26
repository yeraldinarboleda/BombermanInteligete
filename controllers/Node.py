class Node:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)
    
    def get_path(self):
        path = []
        node = self
        while node is not None:
            path.append(node.get_position())
            node = node.parent
        return path[::-1]
    
    def __lt__(self, other):
        return (self.x, self.y) < other.get_position()