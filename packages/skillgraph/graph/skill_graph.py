import networkx as nx
import numpy as np

class SkillGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_skill(self, skill) -> None:
        self.graph.add_node(skill.id, **skill.dict())

    def add_relation(self, source: str, target: str, rel_type: str, weight: float) -> None:
        self.graph.add_edge(source, target, rel_type=rel_type, weight=weight)

    def get_prerequisites(self, skill_id: str) -> list:
        return [u for u, v, d in self.graph.in_edges(skill_id, data=True) if d.get('rel_type') == 'prerequisite']

    def shortest_path(self, source: str, target: str) -> list:
        try:
            return nx.shortest_path(self.graph, source=source, target=target, weight='weight')
        except nx.NetworkXNoPath:
            return []
