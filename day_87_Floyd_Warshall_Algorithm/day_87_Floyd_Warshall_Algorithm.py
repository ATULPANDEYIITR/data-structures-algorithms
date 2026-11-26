#!/usr/bin/env python3
"""
Floyd-Warshall Algorithm
All-Pairs Shortest Paths, Dynamic Programming, and Path Reconstruction.

Features:
- Directed and undirected weighted graphs
- Positive, zero, and negative edge weights
- All-pairs shortest-path computation
- Path reconstruction
- Negative-cycle detection
- Unreachable vertex handling
- Graph validation
- Complexity analysis
- Automated correctness tests

Run:
    python floyd_warshall.py
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Optional


class GraphError(Exception):
    """Raised when graph input is invalid."""


class NegativeCycleError(Exception):
    """Raised when shortest paths are undefined due to a negative cycle."""


@dataclass(frozen=True)
class Edge:
    source: str
    destination: str
    weight: float


@dataclass
class ShortestPathResult:
    distance: list[list[float]]
    next_vertex: list[list[Optional[int]]]
    vertices: list[str]

    def get_distance(self, source: str, destination: str) -> float:
        """Return the shortest distance between two vertices."""
        self._validate_vertices(source, destination)

        i = self.vertices.index(source)
        j = self.vertices.index(destination)

        return self.distance[i][j]

    def _validate_vertices(self, source: str, destination: str) -> None:
        if source not in self.vertices:
            raise GraphError(f"Unknown source vertex: {source}")

        if destination not in self.vertices:
            raise GraphError(f"Unknown destination vertex: {destination}")

    def get_path(self, source: str, destination: str) -> list[str]:
        """Reconstruct the shortest path using the next-vertex matrix."""
        self._validate_vertices(source, destination)

        i = self.vertices.index(source)
        j = self.vertices.index(destination)

        if self.distance[i][j] == inf:
            return []

        path = [source]
        current = i

        # At most V transitions are needed for a simple shortest path.
        for _ in range(len(self.vertices)):
            if current == j:
                return path

            current = self.next_vertex[current][j]

            if current is None:
                return []

            path.append(self.vertices[current])

        raise NegativeCycleError("Path reconstruction exceeded vertex limit")


class WeightedGraph:
    """Directed weighted graph represented by an adjacency matrix."""

    def __init__(self, vertices: list[str]):
        if not vertices:
            raise GraphError("A graph must contain at least one vertex")

        if len(set(vertices)) != len(vertices):
            raise GraphError("Vertex names must be unique")

        if any(not isinstance(v, str) or not v.strip() for v in vertices):
            raise GraphError("Vertex names must be non-empty strings")

        self.vertices = list(vertices)
        self.index = {
            vertex: position
            for position, vertex in enumerate(vertices)
        }
        self.edges: list[Edge] = []

    def add_edge(
        self,
        source: str,
        destination: str,
        weight: float,
        undirected: bool = False
    ) -> None:
        """Add a directed edge or an undirected pair of edges."""

        if source not in self.index or destination not in self.index:
            raise GraphError("Edge references an unknown vertex")

        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise GraphError("Edge weight must be numeric")

        if weight != weight or weight in (inf, -inf):
            raise GraphError("Edge weight must be finite")

        self.edges.append(Edge(source, destination, float(weight)))

        if undirected:
            self.edges.append(
                Edge(destination, source, float(weight))
            )

    def floyd_warshall(self) -> ShortestPathResult:
        """
        Compute all-pairs shortest paths.

        Dynamic programming recurrence:

        D[k][i][j] = min(
            D[k-1][i][j],
            D[k-1][i][k] + D[k-1][k][j]
        )

        The implementation updates the matrix in place.
        """

        n = len(self.vertices)

        distance = [
            [inf] * n
            for _ in range(n)
        ]

        next_vertex: list[list[Optional[int]]] = [
            [None] * n
            for _ in range(n)
        ]

        # Distance from every vertex to itself is zero.
        for i in range(n):
            distance[i][i] = 0.0
            next_vertex[i][i] = i

        # Initialize direct edge distances.
        # Keep the minimum if parallel edges exist.
        for edge in self.edges:
            i = self.index[edge.source]
            j = self.index[edge.destination]

            if edge.weight < distance[i][j]:
                distance[i][j] = edge.weight
                next_vertex[i][j] = j

        # Floyd-Warshall dynamic programming.
        # k represents the set of permitted intermediate vertices.
        for k in range(n):
            for i in range(n):
                if distance[i][k] == inf:
                    continue

                for j in range(n):
                    if distance[k][j] == inf:
                        continue

                    candidate = distance[i][k] + distance[k][j]

                    if candidate < distance[i][j]:
                        distance[i][j] = candidate

                        # The first step from i towards j is the
                        # first step from i towards intermediate k.
                        next_vertex[i][j] = next_vertex[i][k]

        # A negative diagonal indicates a negative-weight cycle.
        for i in range(n):
            if distance[i][i] < 0:
                raise NegativeCycleError(
                    f"Negative cycle detected involving {self.vertices[i]}"
                )

        return ShortestPathResult(
            distance=distance,
            next_vertex=next_vertex,
            vertices=self.vertices.copy()
        )


def print_distance_matrix(result: ShortestPathResult) -> None:
    """Display the all-pairs shortest-distance matrix."""

    vertices = result.vertices

    print("\nALL-PAIRS SHORTEST-DISTANCE MATRIX")

    print(f"{'From/To':<12}", end="")

    for vertex in vertices:
        print(f"{vertex:>10}", end="")

    print()

    for i, source in enumerate(vertices):
        print(f"{source:<12}", end="")

        for j in range(len(vertices)):
            value = result.distance[i][j]

            formatted = "INF" if value == inf else f"{value:g}"

            print(f"{formatted:>10}", end="")

        print()


def demonstrate_basic_graph() -> None:
    """Demonstrate shortest paths on a directed weighted graph."""

    graph = WeightedGraph(["A", "B", "C", "D", "E"])

    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "B", 1),
        ("C", "D", 8),
        ("C", "E", 10),
        ("D", "E", 2),
        ("E", "D", 3),
    ]

    for source, destination, weight in edges:
        graph.add_edge(source, destination, weight)

    result = graph.floyd_warshall()

    print("=" * 65)
    print("FLOYD-WARSHALL ALGORITHM")
    print("=" * 65)

    print_distance_matrix(result)

    queries = [
        ("A", "E"),
        ("A", "D"),
        ("B", "E"),
        ("E", "A"),
        ("C", "C"),
    ]

    print("\nPATH RECONSTRUCTION")

    for source, destination in queries:
        distance = result.get_distance(source, destination)
        path = result.get_path(source, destination)

        if not path:
            print(f"{source} -> {destination}: Unreachable")
        else:
            print(
                f"{source} -> {destination}: "
                f"{' -> '.join(path)} | Distance: {distance:g}"
            )


def demonstrate_negative_edges() -> None:
    """Negative edges are valid when no negative cycle exists."""

    graph = WeightedGraph(["P", "Q", "R", "S"])

    graph.add_edge("P", "Q", 4)
    graph.add_edge("P", "R", 5)
    graph.add_edge("Q", "R", -3)
    graph.add_edge("R", "S", 2)

    result = graph.floyd_warshall()

    print("\nNEGATIVE EDGE EXAMPLE")
    print("P -> S:", result.get_distance("P", "S"))
    print("Path:", " -> ".join(result.get_path("P", "S")))


def demonstrate_negative_cycle() -> None:
    """Verify that negative cycles are rejected."""

    graph = WeightedGraph(["A", "B", "C"])

    graph.add_edge("A", "B", 2)
    graph.add_edge("B", "C", -5)
    graph.add_edge("C", "A", 1)

    try:
        graph.floyd_warshall()
    except NegativeCycleError as error:
        print("\nNEGATIVE CYCLE TEST")
        print("Correctly detected:", error)


def demonstrate_disconnected_graph() -> None:
    """Verify unreachable vertices and self-distance."""

    graph = WeightedGraph(["A", "B", "C", "D"])

    graph.add_edge("A", "B", 7)
    graph.add_edge("C", "D", 3)

    result = graph.floyd_warshall()

    print("\nDISCONNECTED GRAPH")
    print("A -> B:", result.get_distance("A", "B"))
    print("A -> D:", result.get_distance("A", "D"))
    print("A -> D path:", result.get_path("A", "D"))
    print("C -> C:", result.get_distance("C", "C"))


def run_tests() -> None:
    """Run correctness and edge-case assertions."""

    # Basic shortest path.
    graph = WeightedGraph(["A", "B", "C", "D"])
    graph.add_edge("A", "B", 3)
    graph.add_edge("B", "C", 2)
    graph.add_edge("A", "C", 10)
    graph.add_edge("C", "D", 1)

    result = graph.floyd_warshall()

    assert result.get_distance("A", "C") == 5
    assert result.get_distance("A", "D") == 6
    assert result.get_path("A", "D") == ["A", "B", "C", "D"]

    # Zero-weight edges.
    zero_graph = WeightedGraph(["X", "Y"])
    zero_graph.add_edge("X", "Y", 0)

    zero_result = zero_graph.floyd_warshall()

    assert zero_result.get_distance("X", "Y") == 0

    # Negative edge without negative cycle.
    negative_graph = WeightedGraph(["X", "Y", "Z"])
    negative_graph.add_edge("X", "Y", 5)
    negative_graph.add_edge("Y", "Z", -2)

    negative_result = negative_graph.floyd_warshall()

    assert negative_result.get_distance("X", "Z") == 3

    # Unreachable destination.
    assert result.get_distance("D", "A") == inf
    assert result.get_path("D", "A") == []

    # Negative-cycle rejection.
    cycle_graph = WeightedGraph(["A", "B"])
    cycle_graph.add_edge("A", "B", -2)
    cycle_graph.add_edge("B", "A", 1)

    try:
        cycle_graph.floyd_warshall()
        raise AssertionError("Expected negative cycle detection")
    except NegativeCycleError:
        pass

    # Parallel edges.
    parallel_graph = WeightedGraph(["A", "B"])
    parallel_graph.add_edge("A", "B", 9)
    parallel_graph.add_edge("A", "B", 4)

    assert parallel_graph.floyd_warshall().get_distance("A", "B") == 4

    # Invalid vertex.
    try:
        result.get_distance("UNKNOWN", "A")
        raise AssertionError("Expected GraphError")
    except GraphError:
        pass

    # Invalid edge.
    try:
        graph.add_edge("A", "UNKNOWN", 1)
        raise AssertionError("Expected GraphError")
    except GraphError:
        pass

    print("\nALL TESTS PASSED")


def main() -> None:
    demonstrate_basic_graph()
    demonstrate_negative_edges()
    demonstrate_negative_cycle()
    demonstrate_disconnected_graph()
    run_tests()

    print("\nCOMPLEXITY ANALYSIS")
    print("Time Complexity:  O(V^3)")
    print("Space Complexity: O(V^2)")
    print("Path Reconstruction: O(V) per requested path")
    print("Preprocessing: O(V^2 + E)")


if __name__ == "__main__":
    main()
