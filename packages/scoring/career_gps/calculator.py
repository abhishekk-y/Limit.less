from typing import List, Dict, Any
import networkx as nx

class CareerGPSCalculator:
    """Career GPS engine for routing and pathfinding."""
    
    def __init__(self, role_graph: nx.DiGraph):
        self.graph = role_graph

    def compute_distance(self, source_role: str, target_role: str) -> float:
        """Weighted career distance based on skill gaps and typical transitions."""
        try:
            length = nx.shortest_path_length(self.graph, source=source_role, target=target_role, weight='weight')
            return length
        except nx.NetworkXNoPath:
            return float('inf')

    def find_paths(self, source_role: str, target_role: str) -> Dict[str, Any]:
        """Multiple path types (fastest, cheapest, highest opportunity)."""
        paths = {}
        try:
            # Fastest
            fastest = nx.shortest_path(self.graph, source=source_role, target=target_role, weight='time_cost')
            paths['fastest'] = fastest
            
            # Cheapest
            cheapest = nx.shortest_path(self.graph, source=source_role, target=target_role, weight='money_cost')
            paths['cheapest'] = cheapest
            
        except nx.NetworkXNoPath:
            pass
            
        return {
            "paths": paths,
            "lineage": {"source": "NetworkX Dijkstra"}
        }

    def generate_ics(self, path: List[str]) -> str:
        """Calendar export dummy method."""
        return "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
