from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from math import inf
from pathlib import Path
import json
import logging
from typing import Any, Iterable


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("graph_introduction")


class GraphError(Exception):
    """Base exception for graph-related errors."""


class VertexNotFoundError(GraphError):
    """Raised when an operation references an unknown vertex."""


class NegativeWeightError(GraphError):
    """Raised when Dijkstra's algorithm encounters a negative weight."""


class GraphType(Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"


@dataclass(frozen=True)
class Edge:
    source: str
    destination: str
    weight: float = 1.0


@dataclass
class Graph:
    """
    Graph implementation using an adjacency list.

    Directed graph:
        A -> B represents one directed connection.

    Undirected graph:
        A -- B represents a bidirectional connection.

    Weighted graph:
        Each edge stores a numerical weight.
    """

    graph_type: GraphType = GraphType.UNDIRECTED
    weighted: bool = False
    adjacency: dict[str, dict[str, float]] = field(default_factory=dict)

    def add_vertex(self, vertex: str) -> None:
        self._validate_vertex(vertex)
        self.adjacency.setdefault(vertex, {})

    @staticmethod
    def _validate_vertex(vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise ValueError("Vertex must be a non-empty string.")

    def add_edge(
        self,
        source: str,
        destination: str,
        weight: float = 1.0
    ) -> None:
        self._validate_vertex(source)
        self._validate_vertex(destination)

        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError("Edge weight must be numeric.")

        if not float("-inf") < weight < float("inf"):
            raise ValueError("Edge weight must be finite.")

        if not self.weighted and weight != 1:
            raise ValueError("Unweighted graphs only accept weight 1.")

        self.add_vertex(source)
        self.add_vertex(destination)

        # A repeated edge updates its existing weight.
        self.adjacency[source][destination] = float(weight)

        if self.graph_type == GraphType.UNDIRECTED:
            self.adjacency[destination][source] = float(weight)

    def remove_edge(self, source: str, destination: str) -> None:
        self._require_vertex(source)
        self._require_vertex(destination)

        self.adjacency[source].pop(destination, None)

        if self.graph_type == GraphType.UNDIRECTED:
            self.adjacency[destination].pop(source, None)

    def remove_vertex(self, vertex: str) -> None:
        self._require_vertex(vertex)

        del self.adjacency[vertex]

        for neighbors in self.adjacency.values():
            neighbors.pop(vertex, None)

    def _require_vertex(self, vertex: str) -> None:
        if vertex not in self.adjacency:
            raise VertexNotFoundError(f"Unknown vertex: {vertex}")

    @property
    def vertices(self) -> list[str]:
        return sorted(self.adjacency)

    @property
    def vertex_count(self) -> int:
        return len(self.adjacency)

    @property
    def edge_count(self) -> int:
        total = sum(len(neighbors) for neighbors in self.adjacency.values())

        if self.graph_type == GraphType.UNDIRECTED:
            return total // 2

        return total

    def get_edges(self) -> list[Edge]:
        edges = []

        for source in self.vertices:
            for destination, weight in sorted(
                self.adjacency[source].items()
            ):
                if (
                    self.graph_type == GraphType.UNDIRECTED
                    and source > destination
                ):
                    continue

                edges.append(Edge(source, destination, weight))

        return edges

    def adjacency_list(self) -> dict[str, list[tuple[str, float]]]:
        return {
            vertex: sorted(neighbors.items())
            for vertex, neighbors in sorted(self.adjacency.items())
        }

    def adjacency_matrix(self) -> tuple[list[str], list[list[float | None]]]:
        """
        None means no edge.
        Zero remains a valid edge weight.
        """
        vertices = self.vertices
        index = {vertex: i for i, vertex in enumerate(vertices)}

        matrix = [
            [None for _ in vertices]
            for _ in vertices
        ]

        for source, neighbors in self.adjacency.items():
            for destination, weight in neighbors.items():
                matrix[index[source]][index[destination]] = weight

        return vertices, matrix

    def degree(self, vertex: str) -> int:
        self._require_vertex(vertex)

        if self.graph_type == GraphType.UNDIRECTED:
            return len(self.adjacency[vertex])

        return self.in_degree(vertex) + self.out_degree(vertex)

    def in_degree(self, vertex: str) -> int:
        self._require_vertex(vertex)

        return sum(
            vertex in neighbors
            for neighbors in self.adjacency.values()
        )

    def out_degree(self, vertex: str) -> int:
        self._require_vertex(vertex)
        return len(self.adjacency[vertex])

    def bfs(self, start: str) -> list[str]:
        """Breadth-first traversal using a queue."""
        self._require_vertex(start)

        visited = {start}
        queue = deque([start])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in sorted(self.adjacency[current]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return result

    def dfs(self, start: str) -> list[str]:
        """Depth-first traversal using an explicit stack."""
        self._require_vertex(start)

        visited = set()
        stack = [start]
        result = []

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            result.append(current)

            for neighbor in sorted(
                self.adjacency[current],
                reverse=True
            ):
                if neighbor not in visited:
                    stack.append(neighbor)

        return result

    def connected_components(self) -> list[list[str]]:
        if self.graph_type != GraphType.UNDIRECTED:
            raise GraphError(
                "Connected components in this implementation "
                "require an undirected graph."
            )

        visited = set()
        components = []

        for vertex in self.vertices:
            if vertex not in visited:
                component = self.bfs(vertex)
                visited.update(component)
                components.append(component)

        return components

    def dijkstra(self, start: str) -> dict[str, float]:
        """
        Calculate shortest distances from a starting vertex.

        Dijkstra's algorithm requires non-negative edge weights.
        """
        import heapq

        self._require_vertex(start)

        for edge in self.get_edges():
            if edge.weight < 0:
                raise NegativeWeightError(
                    "Dijkstra's algorithm does not support "
                    "negative edge weights."
                )

        distances = {vertex: inf for vertex in self.vertices}
        distances[start] = 0.0

        priority_queue = [(0.0, start)]

        while priority_queue:
            current_distance, current = heapq.heappop(priority_queue)

            if current_distance != distances[current]:
                continue

            for neighbor, weight in self.adjacency[current].items():
                candidate = current_distance + weight

                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    heapq.heappush(
                        priority_queue,
                        (candidate, neighbor)
                    )

        return distances

    def has_cycle(self) -> bool:
        """Cycle detection for directed and undirected graphs."""
        if self.graph_type == GraphType.DIRECTED:
            visited = set()
            active = set()

            def visit(vertex: str) -> bool:
                visited.add(vertex)
                active.add(vertex)

                for neighbor in self.adjacency[vertex]:
                    if neighbor not in visited:
                        if visit(neighbor):
                            return True
                    elif neighbor in active:
                        return True

                active.remove(vertex)
                return False

            return any(
                visit(vertex)
                for vertex in self.vertices
                if vertex not in visited
            )

        visited = set()

        def visit_undirected(vertex: str, parent: str | None) -> bool:
            visited.add(vertex)

            for neighbor in self.adjacency[vertex]:
                if neighbor not in visited:
                    if visit_undirected(neighbor, vertex):
                        return True
                elif neighbor != parent:
                    return True

            return False

        return any(
            visit_undirected(vertex, None)
            for vertex in self.vertices
            if vertex not in visited
        )

    def save_json(self, filename: str) -> None:
        """Save graph structure using JSON."""
        data = {
            "graph_type": self.graph_type.value,
            "weighted": self.weighted,
            "vertices": self.vertices,
            "edges": [
                {
                    "source": edge.source,
                    "destination": edge.destination,
                    "weight": edge.weight
                }
                for edge in self.get_edges()
            ]
        }

        path = Path(filename)
        path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )

    @classmethod
    def load_json(cls, filename: str) -> Graph:
        """Load and validate a previously saved graph."""
        path = Path(filename)
        data = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError("Graph document must be an object.")

        graph = cls(
            graph_type=GraphType(data["graph_type"]),
            weighted=data["weighted"]
        )

        for vertex in data["vertices"]:
            graph.add_vertex(vertex)

        for edge in data["edges"]:
            graph.add_edge(
                edge["source"],
                edge["destination"],
                edge["weight"]
            )

        return graph


def demonstrate_graphs() -> None:
    print("\nGRAPH INTRODUCTION")
    print("=" * 60)

    # 1. Undirected unweighted graph.
    social_network = Graph(
        graph_type=GraphType.UNDIRECTED,
        weighted=False
    )

    social_network.add_edge("Alice", "Bob")
    social_network.add_edge("Alice", "Charlie")
    social_network.add_edge("Bob", "David")
    social_network.add_edge("Charlie", "David")
    social_network.add_vertex("Eve")

    print("\n1. UNDIRECTED UNWEIGHTED GRAPH")
    print("Vertices:", social_network.vertices)
    print("Edges:", social_network.get_edges())
    print("Vertex count:", social_network.vertex_count)
    print("Edge count:", social_network.edge_count)
    print("Alice's degree:", social_network.degree("Alice"))
    print("BFS:", social_network.bfs("Alice"))
    print("DFS:", social_network.dfs("Alice"))
    print("Connected components:", social_network.connected_components())
    print("Contains cycle:", social_network.has_cycle())

    # 2. Directed graph.
    dependency_graph = Graph(
        graph_type=GraphType.DIRECTED,
        weighted=False
    )

    dependency_graph.add_edge("Requirements", "Design")
    dependency_graph.add_edge("Design", "Development")
    dependency_graph.add_edge("Development", "Testing")
    dependency_graph.add_edge("Testing", "Deployment")

    print("\n2. DIRECTED GRAPH")
    print("Edges:", dependency_graph.get_edges())
    print("Outgoing from Design:", dependency_graph.out_degree("Design"))
    print("Incoming to Testing:", dependency_graph.in_degree("Testing"))
    print("Traversal:", dependency_graph.bfs("Requirements"))
    print("Contains cycle:", dependency_graph.has_cycle())

    # 3. Weighted undirected graph.
    road_network = Graph(
        graph_type=GraphType.UNDIRECTED,
        weighted=True
    )

    road_network.add_edge("A", "B", 4)
    road_network.add_edge("A", "C", 2)
    road_network.add_edge("B", "C", 1)
    road_network.add_edge("B", "D", 5)
    road_network.add_edge("C", "D", 8)
    road_network.add_edge("C", "E", 10)
    road_network.add_edge("D", "E", 2)

    print("\n3. WEIGHTED GRAPH")
    print("Edges:", road_network.get_edges())
    print("Shortest distances from A:")
    print(road_network.dijkstra("A"))

    # 4. Graph representations.
    print("\n4. GRAPH REPRESENTATIONS")
    print("Adjacency list:")
    print(road_network.adjacency_list())

    vertices, matrix = road_network.adjacency_matrix()
    print("Matrix vertex order:", vertices)

    for row in matrix:
        print(row)

    # 5. Graph modification.
    road_network.add_edge("A", "E", 15)
    road_network.remove_edge("A", "E")

    print("\n5. GRAPH MODIFICATION")
    print("Updated edge count:", road_network.edge_count)

    # 6. Persistence.
    filename = "graph_example.json"
    road_network.save_json(filename)

    restored = Graph.load_json(filename)

    print("\n6. GRAPH PERSISTENCE")
    print("Restored vertices:", restored.vertices)
    print("Restored edges:", restored.edge_count)

    Path(filename).unlink(missing_ok=True)

    # 7. Validation and edge cases.
    print("\n7. VALIDATION")

    try:
        road_network.add_edge("A", "B", float("nan"))
    except ValueError as error:
        print("Invalid weight:", error)

    try:
        road_network.bfs("Unknown")
    except VertexNotFoundError as error:
        print("Unknown vertex:", error)

    negative_graph = Graph(
        graph_type=GraphType.DIRECTED,
        weighted=True
    )
    negative_graph.add_edge("X", "Y", -3)

    try:
        negative_graph.dijkstra("X")
    except NegativeWeightError as error:
        print("Invalid Dijkstra input:", error)

    cyclic_graph = Graph(GraphType.DIRECTED)
    cyclic_graph.add_edge("P", "Q")
    cyclic_graph.add_edge("Q", "R")
    cyclic_graph.add_edge("R", "P")

    assert cyclic_graph.has_cycle()
    assert road_network.edge_count == 7
    assert restored.vertices == road_network.vertices

    print("\nAll demonstration assertions passed.")


if __name__ == "__main__":
    demonstrate_graphs()
