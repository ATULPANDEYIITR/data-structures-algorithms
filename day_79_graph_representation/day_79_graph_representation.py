#!/usr/bin/env python3
"""
Graph Representation: Adjacency Matrix, Adjacency List, and Edge List.

Demonstrates:
- Directed and undirected graphs
- Weighted and unweighted edges
- Graph construction and validation
- Neighbor lookup and edge lookup
- BFS and DFS traversal
- Dijkstra's shortest-path algorithm
- Memory estimation and performance comparison
- Sparse and dense graph behavior
- Serialization and file handling
- Automated correctness tests

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import json
import random
import sys
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterator


class GraphError(Exception):
    """Base exception for graph operations."""


class InvalidVertexError(GraphError):
    """Raised when a vertex does not exist."""


class InvalidEdgeError(GraphError):
    """Raised when an edge is invalid."""


class Representation(Enum):
    MATRIX = "adjacency_matrix"
    LIST = "adjacency_list"
    EDGE_LIST = "edge_list"


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    weight: float = 1.0


class Graph(ABC):
    """Common graph interface."""

    def __init__(
        self,
        vertex_count: int,
        directed: bool = False
    ):
        if not isinstance(vertex_count, int) or isinstance(vertex_count, bool):
            raise ValueError("Vertex count must be an integer.")

        if vertex_count < 0:
            raise ValueError("Vertex count cannot be negative.")

        self.vertex_count = vertex_count
        self.directed = directed

    def validate_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int) or isinstance(vertex, bool):
            raise InvalidVertexError("Vertex must be an integer.")

        if not 0 <= vertex < self.vertex_count:
            raise InvalidVertexError(
                f"Vertex {vertex} is outside [0, {self.vertex_count - 1}]."
            )

    def validate_edge(self, source: int, target: int, weight: float) -> None:
        self.validate_vertex(source)
        self.validate_vertex(target)

        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise InvalidEdgeError("Weight must be numeric.")

        if not float("-inf") < float(weight) < float("inf"):
            raise InvalidEdgeError("Weight must be finite.")

    @abstractmethod
    def add_edge(self, source: int, target: int, weight: float = 1.0):
        pass

    @abstractmethod
    def remove_edge(self, source: int, target: int):
        pass

    @abstractmethod
    def has_edge(self, source: int, target: int) -> bool:
        pass

    @abstractmethod
    def neighbors(self, vertex: int) -> list[tuple[int, float]]:
        pass

    @abstractmethod
    def edges(self) -> list[Edge]:
        pass

    @abstractmethod
    def memory_estimate(self) -> int:
        pass

    def bfs(self, start: int) -> list[int]:
        """Breadth-first traversal using a queue."""
        self.validate_vertex(start)

        visited = {start}
        queue = deque([start])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for neighbor, _ in self.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def dfs(self, start: int) -> list[int]:
        """Iterative depth-first traversal."""
        self.validate_vertex(start)

        visited = set()
        stack = [start]
        order = []

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            adjacent = sorted(
                self.neighbors(current),
                key=lambda item: item[0],
                reverse=True
            )

            for neighbor, _ in adjacent:
                if neighbor not in visited:
                    stack.append(neighbor)

        return order

    def dijkstra(self, start: int) -> dict[int, float]:
        """
        Dijkstra's shortest-path algorithm.

        Negative weights are rejected because Dijkstra's algorithm
        does not correctly handle negative-weight edges.
        """
        import heapq

        self.validate_vertex(start)

        for edge in self.edges():
            if edge.weight < 0:
                raise GraphError(
                    "Dijkstra requires non-negative edge weights."
                )

        distances = {
            vertex: float("inf")
            for vertex in range(self.vertex_count)
        }

        distances[start] = 0.0
        priority_queue = [(0.0, start)]

        while priority_queue:
            distance, current = heapq.heappop(priority_queue)

            if distance != distances[current]:
                continue

            for neighbor, weight in self.neighbors(current):
                candidate = distance + weight

                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    heapq.heappush(
                        priority_queue,
                        (candidate, neighbor)
                    )

        return distances

    def to_dict(self) -> dict:
        return {
            "vertex_count": self.vertex_count,
            "directed": self.directed,
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "weight": edge.weight
                }
                for edge in self.edges()
            ]
        }


class AdjacencyMatrix(Graph):
    """
    Matrix representation.

    matrix[u][v] stores the weight of edge u -> v.
    None represents the absence of an edge.
    """

    def __init__(self, vertex_count: int, directed: bool = False):
        super().__init__(vertex_count, directed)

        self.matrix = [
            [None] * vertex_count
            for _ in range(vertex_count)
        ]

    def add_edge(self, source: int, target: int, weight: float = 1.0):
        self.validate_edge(source, target, weight)

        self.matrix[source][target] = float(weight)

        if not self.directed:
            self.matrix[target][source] = float(weight)

    def remove_edge(self, source: int, target: int):
        self.validate_vertex(source)
        self.validate_vertex(target)

        self.matrix[source][target] = None

        if not self.directed:
            self.matrix[target][source] = None

    def has_edge(self, source: int, target: int) -> bool:
        self.validate_vertex(source)
        self.validate_vertex(target)

        return self.matrix[source][target] is not None

    def neighbors(self, vertex: int) -> list[tuple[int, float]]:
        self.validate_vertex(vertex)

        return [
            (neighbor, weight)
            for neighbor, weight in enumerate(self.matrix[vertex])
            if weight is not None
        ]

    def edges(self) -> list[Edge]:
        result = []

        for source in range(self.vertex_count):
            for target in range(self.vertex_count):
                weight = self.matrix[source][target]

                if weight is not None:
                    if not self.directed and target < source:
                        continue

                    result.append(Edge(source, target, weight))

        return result

    def memory_estimate(self) -> int:
        return (
            sys.getsizeof(self.matrix)
            + sum(sys.getsizeof(row) for row in self.matrix)
            + sum(
                sys.getsizeof(value)
                for row in self.matrix
                for value in row
            )
        )


class AdjacencyList(Graph):
    """
    Adjacency-list representation.

    Each vertex maps to a dictionary of neighbors and edge weights.
    """

    def __init__(self, vertex_count: int, directed: bool = False):
        super().__init__(vertex_count, directed)

        self.adjacency = [
            {} for _ in range(vertex_count)
        ]

    def add_edge(self, source: int, target: int, weight: float = 1.0):
        self.validate_edge(source, target, weight)

        self.adjacency[source][target] = float(weight)

        if not self.directed:
            self.adjacency[target][source] = float(weight)

    def remove_edge(self, source: int, target: int):
        self.validate_vertex(source)
        self.validate_vertex(target)

        self.adjacency[source].pop(target, None)

        if not self.directed:
            self.adjacency[target].pop(source, None)

    def has_edge(self, source: int, target: int) -> bool:
        self.validate_vertex(source)
        self.validate_vertex(target)

        return target in self.adjacency[source]

    def neighbors(self, vertex: int) -> list[tuple[int, float]]:
        self.validate_vertex(vertex)

        return sorted(self.adjacency[vertex].items())

    def edges(self) -> list[Edge]:
        result = []

        for source, adjacent in enumerate(self.adjacency):
            for target, weight in adjacent.items():
                if not self.directed and target < source:
                    continue

                result.append(Edge(source, target, weight))

        return result

    def memory_estimate(self) -> int:
        total = sys.getsizeof(self.adjacency)

        for adjacent in self.adjacency:
            total += sys.getsizeof(adjacent)

            for vertex, weight in adjacent.items():
                total += sys.getsizeof(vertex)
                total += sys.getsizeof(weight)

        return total


class EdgeList(Graph):
    """
    Edge-list representation.

    Stores each edge as a separate record.
    """

    def __init__(self, vertex_count: int, directed: bool = False):
        super().__init__(vertex_count, directed)

        self.edge_data: dict[tuple[int, int], float] = {}

    def _key(self, source: int, target: int) -> tuple[int, int]:
        if self.directed or source <= target:
            return source, target

        return target, source

    def add_edge(self, source: int, target: int, weight: float = 1.0):
        self.validate_edge(source, target, weight)

        self.edge_data[self._key(source, target)] = float(weight)

    def remove_edge(self, source: int, target: int):
        self.validate_vertex(source)
        self.validate_vertex(target)

        self.edge_data.pop(self._key(source, target), None)

    def has_edge(self, source: int, target: int) -> bool:
        self.validate_vertex(source)
        self.validate_vertex(target)

        return self._key(source, target) in self.edge_data

    def neighbors(self, vertex: int) -> list[tuple[int, float]]:
        self.validate_vertex(vertex)

        result = []

        for (source, target), weight in self.edge_data.items():
            if source == vertex:
                result.append((target, weight))

            if not self.directed and target == vertex and source != vertex:
                result.append((source, weight))

        return sorted(result)

    def edges(self) -> list[Edge]:
        return [
            Edge(source, target, weight)
            for (source, target), weight in sorted(self.edge_data.items())
        ]

    def memory_estimate(self) -> int:
        total = sys.getsizeof(self.edge_data)

        for key, weight in self.edge_data.items():
            total += sys.getsizeof(key)
            total += sys.getsizeof(weight)

        return total


def create_graph(
    representation: Representation,
    vertex_count: int,
    directed: bool = False
) -> Graph:

    implementations = {
        Representation.MATRIX: AdjacencyMatrix,
        Representation.LIST: AdjacencyList,
        Representation.EDGE_LIST: EdgeList
    }

    return implementations[representation](vertex_count, directed)


def benchmark(graph: Graph, repetitions: int = 1000) -> dict:
    """Measure representative graph operations."""

    if repetitions <= 0:
        raise ValueError("Repetitions must be positive.")

    if graph.vertex_count == 0:
        raise GraphError("Benchmark requires at least one vertex.")

    source = 0
    target = graph.vertex_count - 1

    start = time.perf_counter()

    for _ in range(repetitions):
        graph.has_edge(source, target)

    lookup_time = time.perf_counter() - start

    start = time.perf_counter()

    for _ in range(repetitions):
        graph.neighbors(source)

    neighbor_time = time.perf_counter() - start

    start = time.perf_counter()

    for _ in range(repetitions):
        graph.edges()

    enumeration_time = time.perf_counter() - start

    return {
        "representation": type(graph).__name__,
        "vertices": graph.vertex_count,
        "edges": len(graph.edges()),
        "estimated_memory_bytes": graph.memory_estimate(),
        "edge_lookup_seconds": lookup_time,
        "neighbor_lookup_seconds": neighbor_time,
        "edge_enumeration_seconds": enumeration_time
    }


def build_sample_graph() -> list[Graph]:
    """Construct the same weighted graph in three representations."""

    specifications = [
        (0, 1, 4),
        (0, 2, 2),
        (1, 2, 1),
        (1, 3, 5),
        (2, 3, 8),
        (2, 4, 10),
        (3, 4, 2),
        (4, 5, 3)
    ]

    graphs = []

    for representation in Representation:
        graph = create_graph(representation, 6)

        for source, target, weight in specifications:
            graph.add_edge(source, target, weight)

        graphs.append(graph)

    return graphs


def generate_random_graph(
    vertex_count: int,
    edge_count: int,
    seed: int = 42
) -> Graph:
    """Generate a simple undirected graph for performance experiments."""

    if vertex_count < 0:
        raise ValueError("Vertex count cannot be negative.")

    maximum_edges = vertex_count * (vertex_count - 1) // 2

    if not 0 <= edge_count <= maximum_edges:
        raise ValueError("Invalid edge count for a simple undirected graph.")

    graph = AdjacencyList(vertex_count)
    generator = random.Random(seed)

    possible_edges = [
        (source, target)
        for source in range(vertex_count)
        for target in range(source + 1, vertex_count)
    ]

    for source, target in generator.sample(possible_edges, edge_count):
        graph.add_edge(source, target, generator.randint(1, 20))

    return graph


def save_graph(graph: Graph, filename: str) -> None:
    """Persist graph data as JSON."""

    path = Path(filename)

    payload = graph.to_dict()

    temporary = path.with_suffix(path.suffix + ".tmp")

    try:
        temporary.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8"
        )
        temporary.replace(path)

    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise GraphError(f"Unable to save graph: {error}") from error


def load_graph(filename: str, representation: Representation) -> Graph:
    """Load and validate a graph from JSON."""

    try:
        payload = json.loads(
            Path(filename).read_text(encoding="utf-8")
        )

        if not isinstance(payload, dict):
            raise GraphError("Graph document must be a JSON object.")

        vertex_count = payload["vertex_count"]
        directed = payload["directed"]
        edge_records = payload["edges"]

        if not isinstance(directed, bool):
            raise GraphError("Directed must be a boolean.")

        if not isinstance(edge_records, list):
            raise GraphError("Edges must be a list.")

        graph = create_graph(representation, vertex_count, directed)

        for record in edge_records:
            if not isinstance(record, dict):
                raise GraphError("Each edge must be an object.")

            graph.add_edge(
                record["source"],
                record["target"],
                record["weight"]
            )

        return graph

    except (OSError, KeyError, TypeError, ValueError) as error:
        raise GraphError(f"Invalid graph file: {error}") from error


def run_tests() -> None:
    """Verify representation-independent behavior."""

    graphs = build_sample_graph()

    for graph in graphs:
        assert graph.vertex_count == 6
        assert len(graph.edges()) == 8
        assert graph.has_edge(0, 1)
        assert not graph.has_edge(0, 5)

        assert graph.neighbors(0) == [(1, 4.0), (2, 2.0)]

        assert graph.bfs(0) == [0, 1, 2, 3, 4, 5]

        distances = graph.dijkstra(0)

        assert distances[0] == 0
        assert distances[1] == 3
        assert distances[2] == 2
        assert distances[3] == 8
        assert distances[4] == 10
        assert distances[5] == 13

        graph.remove_edge(0, 1)
        assert not graph.has_edge(0, 1)

        graph.add_edge(0, 1, 4)
        assert graph.has_edge(0, 1)

    directed = AdjacencyList(3, directed=True)
    directed.add_edge(0, 1)

    assert directed.has_edge(0, 1)
    assert not directed.has_edge(1, 0)

    try:
        directed.add_edge(0, 4)
        raise AssertionError("Invalid vertex was accepted.")
    except InvalidVertexError:
        pass

    try:
        directed.add_edge(0, 1, float("nan"))
        raise AssertionError("Invalid weight was accepted.")
    except InvalidEdgeError:
        pass

    negative = AdjacencyList(2, directed=True)
    negative.add_edge(0, 1, -1)

    try:
        negative.dijkstra(0)
        raise AssertionError("Negative weight was accepted.")
    except GraphError:
        pass

    empty = AdjacencyList(0)

    assert empty.edges() == []

    print("All graph representation tests passed.")


def main() -> None:
    print("=" * 72)
    print("GRAPH REPRESENTATION ENGINE")
    print("=" * 72)

    run_tests()

    graphs = build_sample_graph()

    for graph in graphs:
        print(f"\nRepresentation: {type(graph).__name__}")
        print(f"Vertices: {graph.vertex_count}")
        print(f"Edges: {graph.edges()}")
        print(f"BFS from vertex 0: {graph.bfs(0)}")
        print(f"DFS from vertex 0: {graph.dfs(0)}")
        print(f"Shortest distances: {graph.dijkstra(0)}")
        print(f"Estimated memory: {graph.memory_estimate():,} bytes")

        print("Benchmark:")
        print(json.dumps(benchmark(graph, 1000), indent=2))

    sparse = generate_random_graph(100, 150)

    print("\nSparse graph experiment:")
    print(f"Vertices: {sparse.vertex_count}")
    print(f"Edges: {len(sparse.edges())}")

    try:
        save_graph(graphs[1], "graph_data.json")
        restored = load_graph(
            "graph_data.json",
            Representation.LIST
        )

        assert restored.edges() == graphs[1].edges()

        print("Graph serialization test passed.")

    except GraphError as error:
        print(f"Serialization error: {error}")

    print("\nComplexity reference:")
    print("Adjacency Matrix: O(V^2) space, O(1) edge lookup.")
    print("Adjacency List:   O(V + E) space, O(degree) neighbor iteration.")
    print("Edge List:        O(E) space, O(E) edge lookup.")

    print("\nExecution completed.")


if __name__ == "__main__":
    main()
