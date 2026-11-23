from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import inf
from typing import Optional


class Algorithm(Enum):
    DIJKSTRA = "dijkstra"
    BELLMAN_FORD = "bellman_ford"


class GraphError(Exception):
    pass


class NegativeCycleError(GraphError):
    pass


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    weight: float


@dataclass
class PathResult:
    source: str
    target: str
    distance: float
    path: list[str]
    algorithm: str


class WeightedGraph:
    """Directed weighted graph using an adjacency-list representation."""

    def __init__(self):
        self.adjacency: dict[str, list[tuple[str, float]]] = {}
        self.edges: list[Edge] = set()
        self.directed = True

    def add_vertex(self, vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise ValueError("Vertex must be a nonempty string.")
        self.adjacency.setdefault(vertex, [])

    def add_edge(
        self,
        source: str,
        target: str,
        weight: float,
        bidirectional: bool = False
    ) -> None:
        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            raise ValueError("Edge weight must be numeric.")

        if weight != weight or weight in (inf, -inf):
            raise ValueError("Edge weight must be finite.")

        self.add_vertex(source)
        self.add_vertex(target)

        self.adjacency[source].append((target, float(weight)))
        self.edges.append(Edge(source, target, float(weight)))

        if bidirectional:
            self.adjacency[target].append((source, float(weight)))
            self.edges.append(Edge(target, source, float(weight)))

    def validate_vertices(self, source: str, target: str) -> None:
        if source not in self.adjacency:
            raise GraphError(f"Unknown source vertex: {source}")
        if target not in self.adjacency:
            raise GraphError(f"Unknown target vertex: {target}")

    def has_negative_edges(self) -> bool:
        return any(edge.weight < 0 for edge in self.edges)

    def reconstruct_path(
        self,
        predecessors: dict[str, Optional[str]],
        source: str,
        target: str
    ) -> list[str]:
        if predecessors[target] is None and source != target:
            return []

        path = []
        current = target

        while current is not None:
            path.append(current)
            if current == source:
                break
            current = predecessors[current]

        if path[-1] != source:
            return []

        path.reverse()
        return path

    def dijkstra(self, source: str, target: str) -> PathResult:
        """O((V + E) log V) using a binary heap."""
        import heapq

        self.validate_vertices(source, target)

        if self.has_negative_edges():
            raise GraphError(
                "Dijkstra cannot process negative-weight edges."
            )

        distances = {v: inf for v in self.adjacency}
        predecessors = {v: None for v in self.adjacency}

        distances[source] = 0.0
        queue = [(0.0, source)]
        visited = set()

        while queue:
            current_distance, vertex = heapq.heappop(queue)

            if vertex in visited:
                continue

            visited.add(vertex)

            if vertex == target:
                break

            for neighbor, weight in self.adjacency[vertex]:
                new_distance = current_distance + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = vertex
                    heapq.heappush(
                        queue,
                        (new_distance, neighbor)
                    )

        return PathResult(
            source,
            target,
            distances[target],
            self.reconstruct_path(
                predecessors, source, target
            ),
            Algorithm.DIJKSTRA.value
        )

    def bellman_ford(
        self,
        source: str,
        target: str
    ) -> PathResult:
        """O(VE); supports negative edges and detects reachable cycles."""
        self.validate_vertices(source, target)

        vertices = list(self.adjacency)
        distances = {v: inf for v in vertices}
        predecessors = {v: None for v in vertices}

        distances[source] = 0.0

        for _ in range(len(vertices) - 1):
            changed = False

            for edge in self.edges:
                if distances[edge.source] == inf:
                    continue

                candidate = distances[edge.source] + edge.weight

                if candidate < distances[edge.target]:
                    distances[edge.target] = candidate
                    predecessors[edge.target] = edge.source
                    changed = True

            if not changed:
                break

        # A reachable negative cycle makes shortest distances undefined.
        for edge in self.edges:
            if distances[edge.source] != inf:
                if (
                    distances[edge.source] + edge.weight
                    < distances[edge.target]
                ):
                    raise NegativeCycleError(
                        "A negative-weight cycle is reachable "
                        "from the source."
                    )

        return PathResult(
            source,
            target,
            distances[target],
            self.reconstruct_path(
                predecessors, source, target
            ),
            Algorithm.BELLMAN_FORD.value
        )

    def shortest_path(
        self,
        source: str,
        target: str,
        algorithm: Optional[Algorithm] = None
    ) -> PathResult:
        self.validate_vertices(source, target)

        if algorithm is None:
            algorithm = (
                Algorithm.BELLMAN_FORD
                if self.has_negative_edges()
                else Algorithm.DIJKSTRA
            )

        if algorithm == Algorithm.DIJKSTRA:
            return self.dijkstra(source, target)

        if algorithm == Algorithm.BELLMAN_FORD:
            return self.bellman_ford(source, target)

        raise ValueError("Unsupported shortest-path algorithm.")

    def floyd_warshall(self) -> dict[str, dict[str, float]]:
        """All-pairs shortest paths in O(V^3) time and O(V^2) space."""
        vertices = list(self.adjacency)
        distances = {
            u: {v: inf for v in vertices}
            for u in vertices
        }

        for vertex in vertices:
            distances[vertex][vertex] = 0.0

        for edge in self.edges:
            distances[edge.source][edge.target] = min(
                distances[edge.source][edge.target],
                edge.weight
            )

        for intermediate in vertices:
            for source in vertices:
                if distances[source][intermediate] == inf:
                    continue

                for target in vertices:
                    candidate = (
                        distances[source][intermediate]
                        + distances[intermediate][target]
                    )

                    if candidate < distances[source][target]:
                        distances[source][target] = candidate

        for vertex in vertices:
            if distances[vertex][vertex] < 0:
                raise NegativeCycleError(
                    "Graph contains a negative-weight cycle."
                )

        return distances

    def describe(self) -> None:
        print("\nGRAPH")
        for vertex, neighbors in self.adjacency.items():
            formatted = ", ".join(
                f"{neighbor}({weight})"
                for neighbor, weight in neighbors
            )
            print(f"{vertex}: {formatted or 'No outgoing edges'}")


def display_result(result: PathResult) -> None:
    print(f"\nAlgorithm: {result.algorithm}")
    print(f"Source: {result.source}")
    print(f"Target: {result.target}")

    if result.distance == inf:
        print("Distance: Unreachable")
        print("Path: None")
        return

    print(f"Distance: {result.distance:g}")
    print("Path:", " -> ".join(result.path))


def build_transport_graph() -> WeightedGraph:
    graph = WeightedGraph()

    graph.add_edge("Delhi", "Jaipur", 280)
    graph.add_edge("Delhi", "Agra", 230)
    graph.add_edge("Jaipur", "Mumbai", 1140)
    graph.add_edge("Agra", "Bhopal", 540)
    graph.add_edge("Bhopal", "Mumbai", 780)
    graph.add_edge("Jaipur", "Agra", 240)
    graph.add_edge("Agra", "Jaipur", 250)
    graph.add_edge("Delhi", "Chandigarh", 250)
    graph.add_edge("Chandigarh", "Jaipur", 480)

    return graph


def demonstrate_negative_edges() -> WeightedGraph:
    graph = WeightedGraph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 5)
    graph.add_edge("B", "C", -3)
    graph.add_edge("C", "D", 4)
    graph.add_edge("B", "D", 8)

    return graph


def demonstrate_negative_cycle() -> WeightedGraph:
    graph = WeightedGraph()

    graph.add_edge("A", "B", 2)
    graph.add_edge("B", "C", -4)
    graph.add_edge("C", "B", 1)
    graph.add_edge("A", "D", 5)

    return graph


def main() -> None:
    print("=" * 65)
    print("SHORTEST PATH ALGORITHM EXPLORER")
    print("=" * 65)

    # Example 1: Nonnegative transportation network.
    graph = build_transport_graph()
    graph.describe()

    print("\n1. AUTOMATIC ALGORITHM SELECTION")
    result = graph.shortest_path("Delhi", "Mumbai")
    display_result(result)

    # Example 2: Negative edges require Bellman-Ford.
    print("\n2. NEGATIVE EDGE SCENARIO")
    negative_graph = demonstrate_negative_edges()
    negative_result = negative_graph.shortest_path("A", "D")
    display_result(negative_result)

    # Example 3: Dijkstra rejects negative weights.
    print("\n3. DIJKSTRA VALIDATION")

    try:
        negative_graph.dijkstra("A", "D")
    except GraphError as error:
        print("Rejected:", error)

    # Example 4: Unreachable vertex.
    print("\n4. UNREACHABLE VERTEX")
    graph.add_vertex("Kolkata")
    display_result(graph.shortest_path("Delhi", "Kolkata"))

    # Example 5: All-pairs shortest paths.
    print("\n5. FLOYD-WARSHALL")
    distances = graph.floyd_warshall()

    for source, targets in distances.items():
        print(source, targets)

    # Example 6: Negative-cycle detection.
    print("\n6. NEGATIVE-CYCLE DETECTION")

    try:
        cycle_graph = demonstrate_negative_cycle()
        cycle_graph.shortest_path("A", "D")
    except NegativeCycleError as error:
        print("Detected:", error)

    # Example 7: Source equals target.
    print("\n7. SOURCE EQUALS TARGET")
    display_result(graph.shortest_path("Delhi", "Delhi"))

    # Example 8: Basic invariant checks.
    print("\n8. VALIDATION TESTS")

    assert graph.shortest_path("Delhi", "Delhi").distance == 0
    assert graph.shortest_path("Delhi", "Kolkata").distance == inf
    assert negative_result.distance == 5

    try:
        graph.dijkstra("Delhi", "Unknown")
        raise AssertionError("Unknown vertex was not rejected.")
    except GraphError:
        pass

    print("All validation tests passed.")


if __name__ == "__main__":
    main()
