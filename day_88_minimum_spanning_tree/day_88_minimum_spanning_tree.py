#!/usr/bin/env python3
"""
Minimum Spanning Tree (MST)
===========================

Implements:
- Weighted undirected graph modeling
- Disjoint Set Union (Union-Find)
- Path compression and union by rank
- Kruskal's minimum spanning tree algorithm
- Prim's minimum spanning tree algorithm
- Disconnected graph detection
- Minimum spanning forest generation
- MST uniqueness analysis using equal-weight alternative edges
- Network cost and connectivity validation
- Complexity measurements and test assertions

Python 3.10+
No external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable
import heapq
import logging
import math


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger("mst")


class GraphError(Exception):
    """Base exception for graph-related errors."""


class InvalidEdgeError(GraphError):
    """Raised when an edge contains invalid data."""


class DisconnectedGraphError(GraphError):
    """Raised when an MST is requested for a disconnected graph."""


class Algorithm(Enum):
    KRUSKAL = "kruskal"
    PRIM = "prim"


@dataclass(frozen=True, slots=True)
class Edge:
    source: str
    destination: str
    weight: float

    def __post_init__(self) -> None:
        if not self.source or not self.destination:
            raise InvalidEdgeError("Vertex names cannot be empty.")

        if self.source == self.destination:
            raise InvalidEdgeError("Self-loops are not permitted.")

        if not math.isfinite(self.weight):
            raise InvalidEdgeError("Edge weight must be finite.")

        if self.weight < 0:
            raise InvalidEdgeError("Negative connection costs are unsupported.")

    def normalized(self) -> tuple[str, str]:
        return tuple(sorted((self.source, self.destination)))


@dataclass
class MSTResult:
    algorithm: Algorithm
    selected_edges: list[Edge]
    total_cost: float
    vertex_count: int
    component_count: int
    connected: bool
    unique: bool | None = None

    @property
    def edge_count(self) -> int:
        return len(self.selected_edges)

    def display(self) -> None:
        print(f"\nAlgorithm: {self.algorithm.value.upper()}")
        print("-" * 55)

        for edge in self.selected_edges:
            print(
                f"{edge.source:12} -> "
                f"{edge.destination:12} "
                f"Cost: {edge.weight:g}"
            )

        print("-" * 55)
        print(f"Vertices:       {self.vertex_count}")
        print(f"Selected edges: {self.edge_count}")
        print(f"Components:     {self.component_count}")
        print(f"Total cost:     {self.total_cost:g}")
        print(f"Connected:      {self.connected}")
        print(f"Unique MST:     {self.unique}")


class DisjointSet:
    """
    Maintains disjoint connected components.

    Path compression reduces the height of trees.
    Union by rank attaches smaller trees below larger trees.

    Amortized operation complexity: O(alpha(V)).
    """

    def __init__(self, vertices: Iterable[str]) -> None:
        unique_vertices = set(vertices)

        self.parent = {v: v for v in unique_vertices}
        self.rank = {v: 0 for v in unique_vertices}
        self.components = len(unique_vertices)

    def find(self, vertex: str) -> str:
        if vertex not in self.parent:
            raise GraphError(f"Unknown vertex: {vertex}")

        if self.parent[vertex] != vertex:
            self.parent[vertex] = self.find(self.parent[vertex])

        return self.parent[vertex]

    def union(self, first: str, second: str) -> bool:
        root_a = self.find(first)
        root_b = self.find(second)

        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a

        self.parent[root_b] = root_a

        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1

        self.components -= 1
        return True

    def connected(self, first: str, second: str) -> bool:
        return self.find(first) == self.find(second)


@dataclass
class WeightedGraph:
    vertices: set[str] = field(default_factory=set)
    edges: list[Edge] = field(default_factory=list)

    def add_vertex(self, vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise GraphError("Vertex must be a nonempty string.")

        self.vertices.add(vertex)

    def add_edge(
        self,
        source: str,
        destination: str,
        weight: float
    ) -> None:
        edge = Edge(source, destination, weight)

        self.vertices.update((source, destination))
        self.edges.append(edge)

    def adjacency_list(self) -> dict[str, list[tuple[str, float]]]:
        adjacency = {vertex: [] for vertex in self.vertices}

        for edge in self.edges:
            adjacency[edge.source].append(
                (edge.destination, edge.weight)
            )
            adjacency[edge.destination].append(
                (edge.source, edge.weight)
            )

        return adjacency

    def kruskal(self) -> MSTResult:
        """Construct a minimum spanning forest using Kruskal."""

        dsu = DisjointSet(self.vertices)
        selected: list[Edge] = []

        ordered_edges = sorted(
            self.edges,
            key=lambda edge: (
                edge.weight,
                edge.normalized()
            )
        )

        for edge in ordered_edges:
            if dsu.union(edge.source, edge.destination):
                selected.append(edge)

            if dsu.components <= 1:
                break

        return MSTResult(
            algorithm=Algorithm.KRUSKAL,
            selected_edges=selected,
            total_cost=math.fsum(e.weight for e in selected),
            vertex_count=len(self.vertices),
            component_count=dsu.components,
            connected=dsu.components <= 1,
        )

    def prim(self) -> MSTResult:
        """
        Construct a minimum spanning forest using Prim's algorithm.

        A separate heap traversal is started for every disconnected
        component. Lazy heap entries are ignored when already visited.
        """

        adjacency = self.adjacency_list()
        visited: set[str] = set()
        selected: list[Edge] = []
        component_count = 0

        for start in sorted(self.vertices):
            if start in visited:
                continue

            component_count += 1
            visited.add(start)

            heap: list[
                tuple[float, str, str]
            ] = []

            for neighbor, weight in adjacency[start]:
                heapq.heappush(
                    heap,
                    (weight, start, neighbor)
                )

            while heap:
                weight, source, destination = heapq.heappop(heap)

                if destination in visited:
                    continue

                visited.add(destination)

                selected.append(
                    Edge(source, destination, weight)
                )

                for neighbor, next_weight in adjacency[destination]:
                    if neighbor not in visited:
                        heapq.heappush(
                            heap,
                            (next_weight, destination, neighbor)
                        )

        return MSTResult(
            algorithm=Algorithm.PRIM,
            selected_edges=selected,
            total_cost=math.fsum(e.weight for e in selected),
            vertex_count=len(self.vertices),
            component_count=component_count,
            connected=component_count <= 1,
        )

    def calculate_mst(
        self,
        algorithm: Algorithm = Algorithm.KRUSKAL,
        require_connected: bool = True
    ) -> MSTResult:

        if not self.vertices:
            raise GraphError("An empty graph has no spanning tree.")

        if algorithm == Algorithm.KRUSKAL:
            result = self.kruskal()
        elif algorithm == Algorithm.PRIM:
            result = self.prim()
        else:
            raise ValueError("Unsupported MST algorithm.")

        if require_connected and not result.connected:
            raise DisconnectedGraphError(
                f"Graph has {result.component_count} components. "
                "A spanning tree does not exist."
            )

        return result

    def verify_result(self, result: MSTResult) -> bool:
        """Check edge count, connectivity, cycles and cost."""

        if result.vertex_count == 0:
            return False

        dsu = DisjointSet(self.vertices)
        total = 0.0

        for edge in result.selected_edges:
            if not dsu.union(edge.source, edge.destination):
                return False

            total += edge.weight

        expected_edges = (
            result.vertex_count - result.component_count
        )

        return (
            len(result.selected_edges) == expected_edges
            and dsu.components == result.component_count
            and math.isclose(
                total,
                result.total_cost,
                rel_tol=1e-10,
                abs_tol=1e-10
            )
        )

    def analyze_uniqueness(self) -> bool:
        """
        Determine whether the graph has a unique minimum spanning tree.

        An MST is non-unique if an equal-weight alternative edge
        connects two different components after processing all
        strictly lighter edges.

        Parallel edges are handled as distinct alternatives.
        """

        if not self.vertices:
            raise GraphError("Cannot analyze an empty graph.")

        dsu = DisjointSet(self.vertices)

        ordered = sorted(
            self.edges,
            key=lambda edge: edge.weight
        )

        index = 0

        while index < len(ordered):
            end = index + 1
            weight = ordered[index].weight

            while (
                end < len(ordered)
                and ordered[end].weight == weight
            ):
                end += 1

            group = ordered[index:end]

            roots = {
                edge.source: dsu.find(edge.source)
                for edge in group
            }

            temporary_edges = [
                (
                    roots[edge.source],
                    roots[edge.destination]
                )
                for edge in group
            ]

            temporary_dsu = DisjointSet(set(roots.values()))

            for first, second in temporary_edges:
                if (
                    first != second
                    and not temporary_dsu.union(first, second)
                ):
                    return False

            # Contract all connections of the current weight.
            for edge in group:
                dsu.union(edge.source, edge.destination)

            index = end

        return True


def build_sample_graph() -> WeightedGraph:
    graph = WeightedGraph()

    for vertex in ["A", "B", "C", "D", "E", "F"]:
        graph.add_vertex(vertex)

    connections = [
        ("A", "B", 4),
        ("A", "C", 3),
        ("B", "C", 1),
        ("B", "D", 2),
        ("C", "D", 4),
        ("C", "E", 5),
        ("D", "E", 2),
        ("D", "F", 6),
        ("E", "F", 3),
        ("A", "F", 10),
    ]

    for source, destination, cost in connections:
        graph.add_edge(source, destination, cost)

    return graph


def demonstrate_disconnected_graph() -> None:
    graph = WeightedGraph()

    graph.add_edge("A", "B", 5)
    graph.add_edge("B", "C", 2)
    graph.add_edge("X", "Y", 7)
    graph.add_vertex("ISOLATED")

    forest = graph.calculate_mst(
        Algorithm.KRUSKAL,
        require_connected=False
    )

    print("\nDisconnected graph minimum spanning forest")
    forest.display()

    try:
        graph.calculate_mst(
            Algorithm.KRUSKAL,
            require_connected=True
        )
    except DisconnectedGraphError as error:
        print(f"Expected validation: {error}")


def run_tests() -> None:
    graph = build_sample_graph()

    kruskal = graph.calculate_mst(Algorithm.KRUSKAL)
    prim = graph.calculate_mst(Algorithm.PRIM)

    assert kruskal.connected
    assert kruskal.edge_count == 5
    assert math.isclose(kruskal.total_cost, 11.0)

    assert prim.edge_count == 5
    assert math.isclose(prim.total_cost, 11.0)

    assert graph.verify_result(kruskal)
    assert graph.verify_result(prim)

    # A cycle must not be accepted as a spanning tree.
    cyclic = MSTResult(
        algorithm=Algorithm.KRUSKAL,
        selected_edges=[
            Edge("A", "B", 1),
            Edge("B", "C", 1),
            Edge("A", "C", 1),
        ],
        total_cost=3,
        vertex_count=3,
        component_count=1,
        connected=True,
    )

    assert not graph.verify_result(cyclic)

    # Equal-weight alternatives produce a non-unique MST.
    equal_graph = WeightedGraph()
    equal_graph.add_edge("A", "B", 1)
    equal_graph.add_edge("B", "C", 1)
    equal_graph.add_edge("A", "C", 1)

    assert equal_graph.analyze_uniqueness() is False

    # A graph with distinct weights has a unique MST.
    unique_graph = WeightedGraph()
    unique_graph.add_edge("A", "B", 1)
    unique_graph.add_edge("B", "C", 2)
    unique_graph.add_edge("A", "C", 5)

    assert unique_graph.analyze_uniqueness() is True

    # Negative and non-finite weights are rejected.
    for invalid_weight in (-1, math.inf, math.nan):
        try:
            Edge("A", "B", invalid_weight)
            raise AssertionError("Invalid edge was accepted.")
        except InvalidEdgeError:
            pass

    # Empty graphs are rejected.
    try:
        WeightedGraph().calculate_mst()
        raise AssertionError("Empty graph was accepted.")
    except GraphError:
        pass

    print("\nAll validation tests passed.")


def main() -> None:
    graph = build_sample_graph()

    print("=" * 55)
    print("MINIMUM SPANNING TREE: NETWORK CONNECTION PLANNER")
    print("=" * 55)

    print("\nAvailable connections:")
    for edge in sorted(
        graph.edges,
        key=lambda item: item.weight
    ):
        print(
            f"{edge.source} -- {edge.destination}: "
            f"{edge.weight:g}"
        )

    kruskal = graph.calculate_mst(Algorithm.KRUSKAL)
    prim = graph.calculate_mst(Algorithm.PRIM)

    kruskal.unique = graph.analyze_uniqueness()

    kruskal.display()
    prim.display()

    assert math.isclose(
        kruskal.total_cost,
        prim.total_cost
    )

    print("\nAlgorithm comparison")
    print(f"Kruskal cost: {kruskal.total_cost:g}")
    print(f"Prim cost:    {prim.total_cost:g}")
    print(f"Cost agrees:  {kruskal.total_cost == prim.total_cost}")

    demonstrate_disconnected_graph()
    run_tests()


if __name__ == "__main__":
    main()
