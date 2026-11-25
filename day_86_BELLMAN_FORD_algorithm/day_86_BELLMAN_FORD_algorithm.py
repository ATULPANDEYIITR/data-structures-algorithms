#!/usr/bin/env python3
"""
Bellman-Ford Algorithm
----------------------
Demonstrates:
- Weighted directed graphs
- Edge relaxation
- Negative edge weights
- Shortest-path reconstruction
- Unreachable vertices
- Negative-cycle detection and reconstruction
- Vertices affected by reachable negative cycles
- Complexity analysis
- Input validation and automated tests

Run:
    python bellman_ford.py
"""

from dataclasses import dataclass
from typing import Optional
from math import inf
from collections import deque


@dataclass(frozen=True)
class Edge:
    source: int
    destination: int
    weight: int


@dataclass
class BellmanFordResult:
    source: int
    distances: dict[int, float]
    predecessors: dict[int, Optional[int]]
    negative_cycle: list[int]
    affected_vertices: set[int]
    relaxation_passes: int

    @property
    def has_negative_cycle(self) -> bool:
        return bool(self.negative_cycle)


class Graph:
    def __init__(self, vertices: int):
        if not isinstance(vertices, int) or isinstance(vertices, bool):
            raise TypeError("Vertex count must be an integer.")

        if vertices <= 0:
            raise ValueError("Graph must contain at least one vertex.")

        self.vertices = vertices
        self.edges: list[Edge] = []

        # Adjacency lists support efficient cycle-impact propagation.
        self.adjacency: dict[int, list[int]] = {
            vertex: [] for vertex in range(vertices)
        }

    def _validate_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int) or isinstance(vertex, bool):
            raise TypeError("Vertex identifiers must be integers.")

        if not 0 <= vertex < self.vertices:
            raise ValueError(f"Invalid vertex: {vertex}")

    def add_edge(self, source: int, destination: int, weight: int) -> None:
        self._validate_vertex(source)
        self._validate_vertex(destination)

        if not isinstance(weight, int) or isinstance(weight, bool):
            raise TypeError("Edge weight must be an integer.")

        edge = Edge(source, destination, weight)
        self.edges.append(edge)
        self.adjacency[source].append(destination)

    def bellman_ford(self, source: int) -> BellmanFordResult:
        self._validate_vertex(source)

        # Initialization: only the source has a finite distance.
        distances = {v: inf for v in range(self.vertices)}
        predecessors: dict[int, Optional[int]] = {
            v: None for v in range(self.vertices)
        }

        distances[source] = 0
        passes = 0

        # At most V-1 passes are required for a shortest simple path.
        for iteration in range(self.vertices - 1):
            updated = False

            for edge in self.edges:
                u = edge.source
                v = edge.destination

                if distances[u] == inf:
                    continue

                candidate = distances[u] + edge.weight

                if candidate < distances[v]:
                    distances[v] = candidate
                    predecessors[v] = u
                    updated = True

            passes += 1

            # Early termination when an entire pass makes no changes.
            if not updated:
                break

        # Detect a reachable negative cycle.
        cycle_vertex: Optional[int] = None

        for edge in self.edges:
            u = edge.source
            v = edge.destination

            if distances[u] != inf:
                if distances[u] + edge.weight < distances[v]:
                    predecessors[v] = u
                    cycle_vertex = v
                    break

        negative_cycle: list[int] = []

        if cycle_vertex is not None:
            current = cycle_vertex

            # Move V times to enter the actual cycle.
            for _ in range(self.vertices):
                current = predecessors[current]

                if current is None:
                    raise RuntimeError("Negative-cycle reconstruction failed.")

            start = current
            negative_cycle = [start]
            current = predecessors[start]

            while current != start:
                if current is None or len(negative_cycle) > self.vertices:
                    raise RuntimeError("Invalid negative-cycle predecessor chain.")

                negative_cycle.append(current)
                current = predecessors[current]

            negative_cycle.append(start)
            negative_cycle.reverse()

        # Identify all vertices reachable from a detected negative cycle.
        affected: set[int] = set()

        if cycle_vertex is not None:
            queue = deque()

            # Every relaxable edge identifies a vertex affected by a cycle.
            for edge in self.edges:
                u = edge.source
                v = edge.destination

                if distances[u] != inf:
                    if distances[u] + edge.weight < distances[v]:
                        if v not in affected:
                            affected.add(v)
                            queue.append(v)

            # Negative-cycle effects propagate through outgoing edges.
            while queue:
                current = queue.popleft()

                for neighbor in self.adjacency[current]:
                    if neighbor not in affected:
                        affected.add(neighbor)
                        queue.append(neighbor)

        return BellmanFordResult(
            source=source,
            distances=distances,
            predecessors=predecessors,
            negative_cycle=negative_cycle,
            affected_vertices=affected,
            relaxation_passes=passes
        )

    def reconstruct_path(
        self,
        result: BellmanFordResult,
        destination: int
    ) -> Optional[list[int]]:
        self._validate_vertex(destination)

        if destination in result.affected_vertices:
            raise ValueError(
                "Shortest path is undefined due to a reachable negative cycle."
            )

        if result.distances[destination] == inf:
            return None

        path = []
        current: Optional[int] = destination

        while current is not None:
            path.append(current)

            if current == result.source:
                break

            current = result.predecessors[current]

        if not path or path[-1] != result.source:
            return None

        path.reverse()
        return path


def display_result(
    graph: Graph,
    result: BellmanFordResult
) -> None:
    print("\nSOURCE:", result.source)
    print("-" * 65)

    print(f"{'VERTEX':<12}{'DISTANCE':<18}{'PREDECESSOR':<18}")

    for vertex in range(graph.vertices):
        distance = result.distances[vertex]

        if vertex in result.affected_vertices:
            distance_text = "UNDEFINED"
        elif distance == inf:
            distance_text = "INFINITY"
        else:
            distance_text = str(distance)

        predecessor = result.predecessors[vertex]
        predecessor_text = (
            str(predecessor) if predecessor is not None else "-"
        )

        print(f"{vertex:<12}{distance_text:<18}{predecessor_text:<18}")

    print("\nRelaxation passes:", result.relaxation_passes)

    if result.has_negative_cycle:
        print("Negative cycle detected:", result.negative_cycle)
        print("Affected vertices:", sorted(result.affected_vertices))
    else:
        print("No reachable negative cycle detected.")

    print("\nShortest paths:")

    for destination in range(graph.vertices):
        if destination in result.affected_vertices:
            print(f"{result.source} -> {destination}: Undefined")
            continue

        path = graph.reconstruct_path(result, destination)

        if path is None:
            print(f"{result.source} -> {destination}: Unreachable")
        else:
            print(
                f"{result.source} -> {destination}: "
                f"{' -> '.join(map(str, path))} "
                f"(cost: {result.distances[destination]})"
            )


def demonstrate_basic_graph() -> None:
    print("\n========== BASIC BELLMAN-FORD ==========")

    graph = Graph(5)

    edges = [
        (0, 1, 6),
        (0, 2, 7),
        (1, 2, 8),
        (1, 3, 5),
        (1, 4, -4),
        (2, 3, -3),
        (2, 4, 9),
        (3, 1, -2),
        (4, 0, 2),
        (4, 3, 7),
    ]

    for source, destination, weight in edges:
        graph.add_edge(source, destination, weight)

    result = graph.bellman_ford(0)
    display_result(graph, result)


def demonstrate_negative_cycle() -> None:
    print("\n========== NEGATIVE CYCLE ==========")

    graph = Graph(6)

    edges = [
        (0, 1, 4),
        (1, 2, 3),
        (2, 3, -8),
        (3, 1, 2),
        (3, 4, 5),
        (4, 5, 2),
    ]

    for source, destination, weight in edges:
        graph.add_edge(source, destination, weight)

    result = graph.bellman_ford(0)
    display_result(graph, result)


def demonstrate_unreachable_cycle() -> None:
    print("\n========== UNREACHABLE NEGATIVE CYCLE ==========")

    graph = Graph(5)

    edges = [
        (0, 1, 5),
        (1, 2, 3),
        (3, 4, -5),
        (4, 3, 2),
    ]

    for source, destination, weight in edges:
        graph.add_edge(source, destination, weight)

    result = graph.bellman_ford(0)
    display_result(graph, result)


def demonstrate_disconnected_vertices() -> None:
    print("\n========== DISCONNECTED GRAPH ==========")

    graph = Graph(5)

    graph.add_edge(0, 1, 10)
    graph.add_edge(1, 2, -2)

    result = graph.bellman_ford(0)
    display_result(graph, result)


def run_tests() -> None:
    # Negative edges without negative cycles.
    graph = Graph(4)
    graph.add_edge(0, 1, 4)
    graph.add_edge(0, 2, 5)
    graph.add_edge(1, 2, -2)
    graph.add_edge(2, 3, 3)

    result = graph.bellman_ford(0)

    assert result.distances[0] == 0
    assert result.distances[1] == 4
    assert result.distances[2] == 2
    assert result.distances[3] == 5
    assert not result.has_negative_cycle
    assert graph.reconstruct_path(result, 3) == [0, 1, 2, 3]

    # Reachable negative cycle.
    graph = Graph(3)
    graph.add_edge(0, 1, 1)
    graph.add_edge(1, 2, -2)
    graph.add_edge(2, 1, -2)

    result = graph.bellman_ford(0)

    assert result.has_negative_cycle
    assert 1 in result.affected_vertices
    assert 2 in result.affected_vertices

    # Unreachable negative cycle must not invalidate source distances.
    graph = Graph(4)
    graph.add_edge(0, 1, 2)
    graph.add_edge(2, 3, -3)
    graph.add_edge(3, 2, 1)

    result = graph.bellman_ford(0)

    assert not result.has_negative_cycle
    assert result.distances[1] == 2
    assert result.distances[2] == inf

    # Self-loop with negative weight.
    graph = Graph(2)
    graph.add_edge(0, 0, -1)

    result = graph.bellman_ford(0)

    assert result.has_negative_cycle
    assert 0 in result.affected_vertices

    # Zero-weight self-loop is not a negative cycle.
    graph = Graph(2)
    graph.add_edge(0, 0, 0)
    graph.add_edge(0, 1, 7)

    result = graph.bellman_ford(0)

    assert not result.has_negative_cycle
    assert result.distances[1] == 7

    # Invalid input.
    try:
        Graph(0)
        raise AssertionError("Invalid graph size was accepted.")
    except ValueError:
        pass

    try:
        graph.add_edge(0, 5, 1)
        raise AssertionError("Invalid vertex was accepted.")
    except ValueError:
        pass

    print("\nAll automated tests passed.")


def main() -> None:
    demonstrate_basic_graph()
    demonstrate_negative_cycle()
    demonstrate_unreachable_cycle()
    demonstrate_disconnected_vertices()
    run_tests()


if __name__ == "__main__":
    main()
