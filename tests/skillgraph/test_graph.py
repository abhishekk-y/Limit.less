import pytest
import networkx as nx

def test_graph_algorithms():
    G = nx.DiGraph()
    G.add_edge("Python", "ML", weight=1)
    G.add_edge("ML", "Deep Learning", weight=1)
    
    path = nx.shortest_path(G, "Python", "Deep Learning")
    assert path == ["Python", "ML", "Deep Learning"]
    assert nx.shortest_path_length(G, "Python", "Deep Learning") == 2
