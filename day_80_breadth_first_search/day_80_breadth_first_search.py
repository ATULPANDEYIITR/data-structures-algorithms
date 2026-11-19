from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class Graph:
    """Undirected, unweighted graph represented using adjacency sets."""

    adjacency: dict[str, set[str]] = field(default_factory=dict)

    def add_vertex(self, vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise ValueError("Vertex must be a non-empty string.")
        self.adjacency.setdefault(vertex, set())

    def add_edge(self, source: str, destination: str) -> None:
        if not source or not destination:
            raise ValueError("Both vertices are required.")

        self.add_vertex(source)
        self.add_vertex(destination)

        # Undirected edges are stored in both adjacency sets.
        self.adjacency[source].add(destination)
        self.adjacency[destination].add(source)

    def remove_edge(self, source: str, destination: str) -> None:
        if source not in self.adjacency or destination not in self.adjacency:
            raise KeyError("Vertex does not exist.")

        self.adjacency[source].discard(destination)
        self.adjacency[destination].discard(source)

    def remove_vertex(self, vertex: str) -> None:
        if vertex not in self.adjacency:
            raise KeyError(f"Unknown vertex: {vertex}")

        for neighbor in self.adjacency[vertex]:
            self.adjacency[neighbor].discard(vertex)

        del self.adjacency[vertex]

    def validate_vertex(self, vertex: str) -> None:
        if vertex not in self.adjacency:
            raise KeyError(f"Vertex '{vertex}' does not exist.")

    def bfs(self, start: str) -> list[str]:
        """Return vertices in breadth-first traversal order."""

        self.validate_vertex(start)

        visited = {start}
        queue = deque([start])
        traversal = []

        while queue:
            current = queue.popleft()
            traversal.append(current)

            # Sorting makes traversal output deterministic.
            for neighbor in sorted(self.adjacency[current]):
                if neighbor not in visited:
                    # Mark when enqueued to prevent duplicate queue entries.
                    visited.add(neighbor)
                    queue.append(neighbor)

        return traversal

    def bfs_levels(self, start: str) -> dict[str, int]:
        """Return the minimum number of edges from start to each reachable vertex."""

        self.validate_vertex(start)

        distances = {start: 0}
        queue = deque([start])

        while queue:
            current = queue.popleft()

            for neighbor in sorted(self.adjacency[current]):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)

        return distances

    def shortest_path(
        self, start: str, target: str
    ) -> list[str] | None:
        """Find a shortest path in an unweighted graph."""

        self.validate_vertex(start)
        self.validate_vertex(target)

        if start == target:
            return [start]

        queue = deque([start])
        parent: dict[str, str | None] = {start: None}

        while queue:
            current = queue.popleft()

            for neighbor in sorted(self.adjacency[current]):
                if neighbor in parent:
                    continue

                parent[neighbor] = current

                if neighbor == target:
                    path = []
                    node: str | None = target

                    while node is not None:
                        path.append(node)
                        node = parent[node]

                    return path[::-1]

                queue.append(neighbor)

        return None

    def connected_components(self) -> list[list[str]]:
        """Identify all connected components of an undirected graph."""

        visited = set()
        components = []

        for vertex in sorted(self.adjacency):
            if vertex in visited:
                continue

            component = []
            queue = deque([vertex])
            visited.add(vertex)

            while queue:
                current = queue.popleft()
                component.append(current)

                for neighbor in sorted(self.adjacency[current]):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            components.append(component)

        return components

    def is_connected(self) -> bool:
        if not self.adjacency:
            return True

        return len(self.connected_components()) == 1

    def display(self) -> None:
        for vertex in sorted(self.adjacency):
            neighbors = sorted(self.adjacency[vertex])
            print(f"{vertex}: {neighbors}")


def build_sample_graph() -> Graph:
    graph = Graph()

    edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("B", "E"),
        ("C", "F"),
        ("E", "F"),
        ("G", "H"),
    ]

    for source, destination in edges:
        graph.add_edge(source, destination)

    graph.add_vertex("I")
    return graph


def demonstrate_bfs() -> None:
    graph = build_sample_graph()

    print("=" * 55)
    print("BREADTH-FIRST SEARCH")
    print("=" * 55)

    print("\n1. Graph adjacency list")
    graph.display()

    print("\n2. BFS traversal from A")
    print(graph.bfs("A"))

    print("\n3. BFS levels from A")
    for vertex, distance in sorted(graph.bfs_levels("A").items()):
        print(f"{vertex}: {distance} edges")

    print("\n4. Shortest path from A to F")
    path = graph.shortest_path("A", "F")
    print(path)
    print("Distance:", len(path) - 1 if path else "Unreachable")

    print("\n5. Shortest path from A to H")
    print(graph.shortest_path("A", "H"))

    print("\n6. Connected components")
    for index, component in enumerate(
        graph.connected_components(), start=1
    ):
        print(f"Component {index}: {component}")

    print("\n7. Connectivity")
    print("Graph connected:", graph.is_connected())

    print("\n8. Single-vertex graph")
    single = Graph()
    single.add_vertex("X")
    print("Traversal:", single.bfs("X"))
    print("Components:", single.connected_components())

    print("\n9. Empty graph")
    empty = Graph()
    print("Connected:", empty.is_connected())

    print("\n10. Edge removal")
    graph.remove_edge("A", "B")
    print("Traversal after removing A-B:", graph.bfs("A"))

    print("\n11. Validation")
    try:
        graph.bfs("UNKNOWN")
    except KeyError as error:
        print("Expected error:", error)

    # Automated correctness checks.
    test_graph = build_sample_graph()

    assert test_graph.bfs("A") == [
        "A", "B", "C", "D", "E", "F"
    ]

    assert test_graph.bfs_levels("A")["F"] == 2

    assert test_graph.shortest_path("A", "F") == [
        "A", "C", "F"
    ]

    assert test_graph.shortest_path("A", "H") is None

    assert len(test_graph.connected_components()) == 3

    assert test_graph.shortest_path("A", "A") == ["A"]

    print("\nAll BFS tests passed successfully.")


if __name__ == "__main__":
    demonstrate_bfs()
