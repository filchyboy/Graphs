from util import Stack, Queue  # These may come in handy

class Graph:

    """Represent a graph as a dictionary of vertices mapping labels to edges."""
    def __init__(self):
        self.vertices = {}

    def add_vertex(self, vertex_id):
        """
        Add a vertex to the graph.
        """
        if vertex_id not in self.vertices:
            self.vertices[vertex_id] = set()

    def add_edge(self, v1, v2):
        """
        Add a directed edge to the graph.
        """
        if v1 in self.vertices and v2 in self.vertices:
            self.vertices[v1].add(v2)
        else:
            raise IndexError("All vertices need to exist in the graph")

    def get_neighbors(self, vertex_id):
        """
        Get all neighbors (edges) of a vertex.
        """
        return self.vertices[vertex_id]


    def longest_path(self, starting_vertex):
        """
        Print each vertex in depth-first order
        beginning from starting_vertex.
        """
        res = None
        path_len = 0

        s = Stack()
        s.push([starting_vertex])

        visited = set()

        if len(self.get_neighbors(starting_vertex)) == 0:
            return res

        while s.size() > 0:
            path = s.pop()
            v = path[-1]

            if v not in visited:
                visited.add(v)

                if len(self.get_neighbors(v)) == 0:
                    if (path_len < len(path) or (path_len == len(path) and res > v)):
                        path_len = len(path)
                        res = v

                for next_vertex in self.get_neighbors(v):
                    s.push(path + [next_vertex])
        return res