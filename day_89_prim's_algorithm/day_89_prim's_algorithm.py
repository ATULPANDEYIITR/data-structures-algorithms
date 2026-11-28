#!/usr/bin/env python3
"""
Prim's Algorithm: Minimum Spanning Tree and Minimum Spanning Forest.

Implementation features:
- Adjacency-list graph representation.
- Priority queue using heapq.
- Lazy deletion of outdated heap entries.
- Weighted undirected graphs.
- Negative and zero edge weights.
- Disconnected graph support.
- Minimum spanning forest generation.
- Deterministic tie-breaking.
- Input validation and complexity reporting.
- Independent verification of the resulting forest.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Hashable, Iterable


Vertex = Hashable


class GraphError(Exception):
    """Base exception for graph-related errors."""


class InvalidGraphError(GraphError):
    """Raised when graph input is invalid."""


@dataclass(frozen=True)
class Edge:
    source: Vertex
    destination: Vertex
    weight: float


@dataclass
class MSTResult:
    edges: list[Edge]
    total_weight: float
    components: int
    vertices: int
    examined_edges: int

    @property
    def is_connected(self) -> bool:
        return self.vertices == 0 or self.components == 1

    def display(self) -> None:
        print("\nMinimum Spanning Forest")
        print("-" * 55)

        if not self.edges:
            print("No selected edges.")

        for edge in self.edges:
            print(
                f"{edge.source!s:12} -> "
                f"{edge.destination!s:12} "
                f"Weight: {edge.weight:g}"
            )

        print("-" * 55)
        print(f"Vertices          : {self.vertices}")
        print(f"Components        : {self.components}")
        print(f"Selected edges    : {len(self.edges)}")
        print(f"Total weight      : {self.total_weight:g}")
        print(f"Connected graph   : {self.is_connected}")
        print(f"Examined edges    : {self.examined_edges}")


class WeightedGraph:
    """Undirected weighted graph using adjacency lists."""

    def __init__(self) -> None:
        self.adjacency: dict[Vertex, list[tuple[Vertex, float]]] = {}

    def add_vertex(self, vertex: Vertex) -> None:
        try:
            hash(vertex)
        except TypeError as exc:
            raise InvalidGraphError("Vertices must be hashable.") from exc

        self.adjacency.setdefault(vertex, [])

    def add_edge(
        self,
        source: Vertex,
        destination: Vertex,
        weight: float,
    ) -> None:
        if source == destination:
            raise InvalidGraphError("Self-loops are not supported.")

        try:
            numeric_weight = float(weight)
        except (TypeError, ValueError, OverflowError) as exc:
            raise InvalidGraphError("Edge weight must be numeric.") from exc

        if not __import__("math").isfinite(numeric_weight):
            raise InvalidGraphError("Edge weight must be finite.")

        self.add_vertex(source)
        self.add_vertex(destination)

        self.adjacency[source].append((destination, numeric_weight))
        self.adjacency[destination].append((source, numeric_weight))

    @property
    def vertex_count(self) -> int:
        return len(self.adjacency)

    @property
    def edge_count(self) -> int:
        return sum(map(len, self.adjacency.values())) // 2

    def neighbors(self, vertex: Vertex) -> list[tuple[Vertex, float]]:
        return self.adjacency[vertex]


class PrimAlgorithm:
    """
    Prim's minimum spanning forest algorithm.

    The priority queue stores:
        (edge_weight, insertion_counter, source, destination)

    The insertion counter avoids comparing arbitrary vertex objects
    when two edges have equal weights.
    """

    @staticmethod
    def calculate(graph: WeightedGraph) -> MSTResult:
        if not isinstance(graph, WeightedGraph):
            raise InvalidGraphError("Expected a WeightedGraph instance.")

        adjacency = graph.adjacency
        visited: set[Vertex] = set()
        selected_edges: list[Edge] = []

        total_weight = 0.0
        components = 0
        examined_edges = 0
        counter = 0

        # Start a new Prim traversal for every disconnected component.
        for start in adjacency:
            if start in visited:
                continue

            components += 1
            visited.add(start)

            heap: list[
                tuple[float, int, Vertex, Vertex]
            ] = []

            def push_edges(vertex: Vertex) -> None:
                nonlocal counter, examined_edges

                for neighbor, weight in adjacency[vertex]:
                    examined_edges += 1

                    if neighbor not in visited:
                        heapq.heappush(
                            heap,
                            (weight, counter, vertex, neighbor),
                        )
                        counter += 1

            push_edges(start)

            while heap:
                weight, _, source, destination = heapq.heappop(heap)

                # Lazy deletion: another edge may have already reached
                # this vertex with a smaller weight.
                if destination in visited:
                    continue

                visited.add(destination)

                selected_edges.append(
                    Edge(source, destination, weight)
                )
                total_weight += weight

                push_edges(destination)

        return MSTResult(
            edges=selected_edges,
            total_weight=total_weight,
            components=components,
            vertices=graph.vertex_count,
            examined_edges=examined_edges,
        )


def verify_minimum_spanning_forest(
    graph: WeightedGraph,
    result: MSTResult,
) -> bool:
    """Verify forest structure, edge validity and component count."""

    if len(result.edges) != graph.vertex_count - result.components:
        return False

    parent = {vertex: vertex for vertex in graph.adjacency}
    rank = {vertex: 0 for vertex in graph.adjacency}

    def find(vertex: Vertex) -> Vertex:
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    def union(first: Vertex, second: Vertex) -> bool:
        root_a = find(first)
        root_b = find(second)

        if root_a == root_b:
            return False

        if rank[root_a] < rank[root_b]:
            root_a, root_b = root_b, root_a

        parent[root_b] = root_a

        if rank[root_a] == rank[root_b]:
            rank[root_a] += 1

        return True

    calculated_weight = 0.0

    for edge in result.edges:
        if edge.source not in parent or edge.destination not in parent:
            return False

        valid = any(
            neighbor == edge.destination and weight == edge.weight
            for neighbor, weight in graph.neighbors(edge.source)
        )

        if not valid or not union(edge.source, edge.destination):
            return False

        calculated_weight += edge.weight

    if abs(calculated_weight - result.total_weight) > 1e-9:
        return False

    graph_components = len({
        find(vertex) for vertex in graph.adjacency
    })

    return graph_components == result.components


def build_example_graph() -> WeightedGraph:
    graph = WeightedGraph()

    edges = [
        ("A", "B", 4),
        ("A", "C", 3),
        ("B", "C", 1),
        ("B", "D", 2),
        ("C", "D", 4),
        ("C", "E", 5),
        ("D", "E", 2),
        ("D", "F", 3),
        ("E", "F", 1),
        ("E", "G", 7),
        ("F", "G", 2),
        ("H", "I", 6),
    ]

    for source, destination, weight in edges:
        graph.add_edge(source, destination, weight)

    graph.add_vertex("ISOLATED")

    return graph


def run_tests() -> None:
    # Empty graph.
    empty = WeightedGraph()
    empty_result = PrimAlgorithm.calculate(empty)
    assert empty_result.total_weight == 0
    assert empty_result.components == 0

    # Single vertex.
    single = WeightedGraph()
    single.add_vertex("A")
    single_result = PrimAlgorithm.calculate(single)
    assert single_result.components == 1
    assert single_result.edges == []

    # Negative weights.
    negative = WeightedGraph()
    negative.add_edge("A", "B", -5)
    negative.add_edge("B", "C", -2)
    negative.add_edge("A", "C", 1)

    negative_result = PrimAlgorithm.calculate(negative)
    assert negative_result.total_weight == -7
    assert verify_minimum_spanning_forest(
        negative, negative_result
    )

    # Parallel edges.
    parallel = WeightedGraph()
    parallel.add_edge("A", "B", 10)
    parallel.add_edge("A", "B", 2)

    parallel_result = PrimAlgorithm.calculate(parallel)
    assert parallel_result.total_weight == 2

    # Disconnected graph.
    disconnected = WeightedGraph()
    disconnected.add_edge(1, 2, 5)
    disconnected.add_edge(3, 4, 2)
    disconnected.add_vertex(5)

    disconnected_result = PrimAlgorithm.calculate(disconnected)

    assert disconnected_result.components == 3
    assert len(disconnected_result.edges) == 2
    assert disconnected_result.total_weight == 7

    # Invalid inputs.
    try:
        disconnected.add_edge(1, 1, 5)
        raise AssertionError("Self-loop validation failed.")
    except InvalidGraphError:
        pass

    try:
        disconnected.add_edge(1, 2, float("inf"))
        raise AssertionError("Infinite weight validation failed.")
    except InvalidGraphError:
        pass

    assert verify_minimum_spanning_forest(
        disconnected, disconnected_result
    )

    print("All tests passed.")


def main() -> None:
    print("PRIM'S ALGORITHM")
    print("=" * 55)

    graph = build_example_graph()

    print(f"Vertices: {graph.vertex_count}")
    print(f"Edges: {graph.edge_count}")

    result = PrimAlgorithm.calculate(graph)
    result.display()

    if not verify_minimum_spanning_forest(graph, result):
        raise RuntimeError("Minimum spanning forest verification failed.")

    print("\nForest verification: PASSED")

    run_tests()


if __name__ == "__main__":
    main()
