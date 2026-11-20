from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable
import json
import time


class GraphType(Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"


@dataclass
class Graph:
    graph_type: GraphType = GraphType.UNDIRECTED
    adjacency: dict[int, list[int]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_vertex(self, vertex: int) -> None:
        self.adjacency[vertex]

    def add_edge(self, source: int, destination: int) -> None:
        if not isinstance(source, int) or not isinstance(destination, int):
            raise TypeError("Vertices must be integers.")

        self.add_vertex(source)
        self.add_vertex(destination)

        if destination not in self.adjacency[source]:
            self.adjacency[source].append(destination)

        if self.graph_type == GraphType.UNDIRECTED:
            if source not in self.adjacency[destination]:
                self.adjacency[destination].append(source)

    def neighbors(self, vertex: int) -> list[int]:
        if vertex not in self.adjacency:
            raise ValueError(f"Unknown vertex: {vertex}")
        return self.adjacency[vertex]

    def vertices(self) -> list[int]:
        return list(self.adjacency)

    def validate(self) -> None:
        for vertex, neighbors in self.adjacency.items():
            if len(neighbors) != len(set(neighbors)):
                raise ValueError(f"Duplicate edges at vertex {vertex}")

            for neighbor in neighbors:
                if neighbor not in self.adjacency:
                    raise ValueError(f"Unknown neighbor: {neighbor}")


class DepthFirstSearch:
    """Recursive and iterative depth-first graph traversal."""

    @staticmethod
    def recursive(
        graph: Graph,
        start: int,
        max_depth: int | None = None
    ) -> list[int]:
        if start not in graph.adjacency:
            raise ValueError("Starting vertex does not exist.")

        if max_depth is not None and max_depth < 0:
            raise ValueError("Maximum depth cannot be negative.")

        visited: set[int] = set()
        traversal: list[int] = []

        def explore(vertex: int, depth: int) -> None:
            visited.add(vertex)
            traversal.append(vertex)

            if max_depth is not None and depth >= max_depth:
                return

            for neighbor in graph.neighbors(vertex):
                if neighbor not in visited:
                    explore(neighbor, depth + 1)

        explore(start, 0)
        return traversal

    @staticmethod
    def iterative(graph: Graph, start: int) -> list[int]:
        if start not in graph.adjacency:
            raise ValueError("Starting vertex does not exist.")

        visited: set[int] = {start}
        traversal: list[int] = []
        stack = [start]

        while stack:
            vertex = stack.pop()
            traversal.append(vertex)

            # Reverse insertion preserves recursive DFS neighbor order.
            for neighbor in reversed(graph.neighbors(vertex)):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

        return traversal

    @staticmethod
    def connected_components(graph: Graph) -> list[list[int]]:
        if graph.graph_type != GraphType.UNDIRECTED:
            raise ValueError(
                "Connected components require an undirected graph."
            )

        visited: set[int] = set()
        components: list[list[int]] = []

        for start in graph.vertices():
            if start in visited:
                continue

            component = []
            stack = [start]
            visited.add(start)

            while stack:
                vertex = stack.pop()
                component.append(vertex)

                for neighbor in graph.neighbors(vertex):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)

            components.append(component)

        return components

    @staticmethod
    def has_path(graph: Graph, source: int, target: int) -> bool:
        if source not in graph.adjacency:
            raise ValueError("Source vertex does not exist.")

        if target not in graph.adjacency:
            raise ValueError("Target vertex does not exist.")

        visited = set()
        stack = [source]

        while stack:
            vertex = stack.pop()

            if vertex == target:
                return True

            if vertex in visited:
                continue

            visited.add(vertex)

            for neighbor in graph.neighbors(vertex):
                if neighbor not in visited:
                    stack.append(neighbor)

        return False

    @staticmethod
    def classify_edges(graph: Graph, start: int) -> dict:
        """Classify DFS tree and non-tree edges in a directed graph."""

        if start not in graph.adjacency:
            raise ValueError("Starting vertex does not exist.")

        visited = set()
        discovery = {}
        finish = {}
        tree_edges = []
        back_edges = []
        forward_edges = []
        cross_edges = []
        clock = 0

        def explore(vertex: int) -> None:
            nonlocal clock

            visited.add(vertex)
            clock += 1
            discovery[vertex] = clock

            for neighbor in graph.neighbors(vertex):
                if neighbor not in visited:
                    tree_edges.append((vertex, neighbor))
                    explore(neighbor)
                elif neighbor not in finish:
                    back_edges.append((vertex, neighbor))
                elif discovery[vertex] < discovery[neighbor]:
                    forward_edges.append((vertex, neighbor))
                else:
                    cross_edges.append((vertex, neighbor))

            clock += 1
            finish[vertex] = clock

        explore(start)

        return {
            "tree_edges": tree_edges,
            "back_edges": back_edges,
            "forward_edges": forward_edges,
            "cross_edges": cross_edges,
            "discovery": discovery,
            "finish": finish,
        }


def benchmark(graph: Graph, start: int) -> dict:
    results = {}

    for name, operation in (
        ("recursive", DepthFirstSearch.recursive),
        ("iterative", DepthFirstSearch.iterative),
    ):
        beginning = time.perf_counter()
        traversal = operation(graph, start)
        elapsed = time.perf_counter() - beginning

        results[name] = {
            "visited_vertices": len(traversal),
            "elapsed_seconds": round(elapsed, 8),
        }

    return results


def save_results(results: dict, filename: str) -> None:
    path = Path(filename)

    # Prevent accidental writes outside the current working directory.
    if path.name != filename or path.suffix.lower() != ".json":
        raise ValueError("Use a JSON filename in the current directory.")

    path.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8"
    )


def build_sample_graph() -> Graph:
    graph = Graph(GraphType.UNDIRECTED)

    edges = [
        (1, 2),
        (1, 3),
        (2, 4),
        (2, 5),
        (3, 6),
        (5, 6),
        (7, 8),
    ]

    for source, destination in edges:
        graph.add_edge(source, destination)

    graph.add_vertex(9)
    graph.validate()

    return graph


def run_tests() -> None:
    graph = build_sample_graph()

    recursive = DepthFirstSearch.recursive(graph, 1)
    iterative = DepthFirstSearch.iterative(graph, 1)

    assert recursive == [1, 2, 4, 5, 6, 3]
    assert iterative == recursive

    components = DepthFirstSearch.connected_components(graph)

    assert len(components) == 3
    assert sorted(map(len, components)) == [1, 2, 6]

    assert DepthFirstSearch.has_path(graph, 1, 6)
    assert not DepthFirstSearch.has_path(graph, 1, 8)
    assert DepthFirstSearch.has_path(graph, 9, 9)

    limited = DepthFirstSearch.recursive(graph, 1, max_depth=1)
    assert limited == [1, 2, 3]

    directed = Graph(GraphType.DIRECTED)
    directed.add_edge(1, 2)
    directed.add_edge(2, 3)
    directed.add_edge(3, 1)

    assert DepthFirstSearch.has_path(directed, 1, 3)

    try:
        DepthFirstSearch.connected_components(directed)
        raise AssertionError("Directed component validation failed.")
    except ValueError:
        pass

    try:
        DepthFirstSearch.iterative(graph, 100)
        raise AssertionError("Invalid start validation failed.")
    except ValueError:
        pass

    # Self-loops and cycles must not cause infinite traversal.
    cyclic = Graph()
    cyclic.add_edge(1, 1)
    cyclic.add_edge(1, 2)
    cyclic.add_edge(2, 3)
    cyclic.add_edge(3, 1)

    assert len(DepthFirstSearch.iterative(cyclic, 1)) == 3

    print("All DFS tests passed.")


def main() -> None:
    run_tests()

    graph = build_sample_graph()

    print("\nGraph adjacency list:")
    for vertex, neighbors in graph.adjacency.items():
        print(f"{vertex}: {neighbors}")

    print("\nRecursive DFS:", DepthFirstSearch.recursive(graph, 1))
    print("Iterative DFS:", DepthFirstSearch.iterative(graph, 1))

    print("\nConnected components:")
    for index, component in enumerate(
        DepthFirstSearch.connected_components(graph), 1
    ):
        print(f"Component {index}: {sorted(component)}")

    print("\nPath 1 -> 6:", DepthFirstSearch.has_path(graph, 1, 6))
    print("Path 1 -> 8:", DepthFirstSearch.has_path(graph, 1, 8))

    print("\nPerformance:")
    performance = benchmark(graph, 1)
    print(json.dumps(performance, indent=2))

    results = {
        "recursive_dfs": DepthFirstSearch.recursive(graph, 1),
        "iterative_dfs": DepthFirstSearch.iterative(graph, 1),
        "connected_components":
            DepthFirstSearch.connected_components(graph),
        "performance": performance,
    }

    save_results(results, "dfs_results.json")
    print("\nResults saved to dfs_results.json")


if __name__ == "__main__":
    main()
