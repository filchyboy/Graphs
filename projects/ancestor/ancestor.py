
from graph import Graph


def earliest_ancestor(ancestors, starting_node):
    graph = Graph()

    for ancestor in ancestors:
        graph.add_vertex(ancestor[0])
        graph.add_vertex(ancestor[1])

        graph.add_edge(ancestor[1], ancestor[0])
    e_a = graph.longest_path(starting_node)
    if e_a: return e_a
    else: return -1