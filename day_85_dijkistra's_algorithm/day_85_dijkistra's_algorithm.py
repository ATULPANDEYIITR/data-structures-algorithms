from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from itertools import count
from typing import Optional


@dataclass(frozen=True)
class Edge:
    destination: str
    weight: float


@dataclass
class PathResult:
    source: str
    distances: dict[str, float]
    predecessors: dict[str, Optional[str]]

    def path_to(self, destination: str) -> Optional[list[str]]:
        if destination not in self.distances:
            raise ValueError(f"Unknown destination: {destination}")

        if math.isinf(self.distances[destination]):
            return None

        path = []
        current = destination

        while current is not None:
            path.append(current)
            current = self.predecessors[current]

        path.reverse()
        return path

    def distance_to(self, destination: str) -> float:
        if destination not in self.distances:
            raise ValueError(f"Unknown destination: {destination}")
        return self.distances[destination]


@dataclass
class WeightedGraph:
    adjacency: dict[str, list[Edge]] = field(default_factory=dict)

    def add_vertex(self, vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise ValueError("Vertex must be a non-empty string")
        self.adjacency.setdefault(vertex, [])

    def add_edge(
        self,
        source: str,
        destination: str,
        weight: float,
        directed: bool = False
    ) -> None:
        self.add_vertex(source)
        self.add_vertex(destination)

        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise TypeError("Weight must be numeric")

        if not math.isfinite(weight) or weight < 0:
            raise ValueError("Dijkstra requires finite, non-negative weights")

        self.adjacency[source].append(Edge(destination, weight))

        if not directed:
            self.adjacency[destination].append(Edge(source, weight))

    def dijkstra(self, source: str) -> PathResult:
        if source not in self.adjacency:
            raise ValueError(f"Unknown source vertex: {source}")

        distances = {
            vertex: math.inf for vertex in self.adjacency
        }

        predecessors = {
            vertex: None for vertex in self.adjacency
        }

        distances[source] = 0.0

        # A counter makes equal-priority entries safe even if vertex
        # objects are not directly comparable.
        sequence = count()
        priority_queue = [(0.0, next(sequence), source)]

        settled = set()

        while priority_queue:
            current_distance, _, current = heapq.heappop(
                priority_queue
            )

            # Ignore obsolete entries created by earlier relaxations.
            if current_distance != distances[current]:
                continue

            if current in settled:
                continue

            settled.add(current)

            for edge in self.adjacency[current]:
                neighbor = edge.destination

                if neighbor in settled:
                    continue

                new_distance = current_distance + edge.weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current

                    heapq.heappush(
                        priority_queue,
                        (
                            new_distance,
                            next(sequence),
                            neighbor
                        )
                    )

        return PathResult(
            source=source,
            distances=distances,
            predecessors=predecessors
        )

    def shortest_path(
        self,
        source: str,
        destination: str
    ) -> tuple[Optional[list[str]], float]:
        result = self.dijkstra(source)

        return (
            result.path_to(destination),
            result.distance_to(destination)
        )

    def display(self) -> None:
        print("\nGraph adjacency list")

        for vertex, edges in sorted(self.adjacency.items()):
            connections = ", ".join(
                f"{edge.destination}({edge.weight:g})"
                for edge in edges
            )
            print(f"{vertex}: {connections or 'No outgoing edges'}")


def print_results(result: PathResult) -> None:
    print(f"\nShortest paths from {result.source}")
    print("-" * 65)
    print(f"{'Destination':<15}{'Distance':<15}{'Path'}")
    print("-" * 65)

    for vertex in sorted(result.distances):
        distance = result.distance_to(vertex)
        path = result.path_to(vertex)

        if path is None:
            print(f"{vertex:<15}{'Unreachable':<15}{'-'}")
        else:
            print(
                f"{vertex:<15}"
                f"{distance:<15g}"
                f"{' -> '.join(path)}"
            )


def build_transport_network() -> WeightedGraph:
    graph = WeightedGraph()

    connections = [
        ("Delhi", "Agra", 230),
        ("Delhi", "Jaipur", 280),
        ("Delhi", "Lucknow", 550),
        ("Agra", "Lucknow", 330),
        ("Agra", "Jaipur", 240),
        ("Jaipur", "Ahmedabad", 660),
        ("Lucknow", "Varanasi", 320),
        ("Lucknow", "Patna", 540),
        ("Varanasi", "Patna", 250),
        ("Patna", "Kolkata", 580),
        ("Ahmedabad", "Mumbai", 530),
        ("Mumbai", "Pune", 150),
        ("Kolkata", "Mumbai", 1900),
    ]

    for source, destination, distance in connections:
        graph.add_edge(
            source,
            destination,
            distance,
            directed=False
        )

    graph.add_vertex("Chennai")
    return graph


def run_tests() -> None:
    graph = WeightedGraph()

    graph.add_edge("A", "B", 4, directed=True)
    graph.add_edge("A", "C", 1, directed=True)
    graph.add_edge("C", "B", 2, directed=True)
    graph.add_edge("B", "D", 1, directed=True)
    graph.add_edge("C", "D", 5, directed=True)

    result = graph.dijkstra("A")

    assert result.distance_to("A") == 0
    assert result.distance_to("B") == 3
    assert result.distance_to("C") == 1
    assert result.distance_to("D") == 4

    assert result.path_to("D") == ["A", "C", "B", "D"]

    graph.add_vertex("ISOLATED")
    assert result.path_to("ISOLATED") is None

    # Zero-weight edges are valid.
    zero_graph = WeightedGraph()
    zero_graph.add_edge("X", "Y", 0, directed=True)

    assert zero_graph.dijkstra("X").distance_to("Y") == 0

    # Parallel edges must produce the minimum distance.
    parallel = WeightedGraph()
    parallel.add_edge("P", "Q", 10, directed=True)
    parallel.add_edge("P", "Q", 3, directed=True)

    assert parallel.dijkstra("P").distance_to("Q") == 3

    # Negative weights are rejected.
    try:
        parallel.add_edge("P", "R", -1, directed=True)
        raise AssertionError("Negative weight was accepted")
    except ValueError:
        pass

    # Infinite weights are rejected.
    try:
        parallel.add_edge("P", "R", math.inf, directed=True)
        raise AssertionError("Infinite weight was accepted")
    except ValueError:
        pass

    # Unknown sources are rejected.
    try:
        parallel.dijkstra("UNKNOWN")
        raise AssertionError("Unknown source was accepted")
    except ValueError:
        pass

    print("All tests passed.")


def main() -> None:
    print("=" * 65)
    print("DIJKSTRA'S SHORTEST PATH ALGORITHM")
    print("=" * 65)

    run_tests()

    graph = build_transport_network()
    graph.display()

    source = "Delhi"
    result = graph.dijkstra(source)

    print_results(result)

    destination = "Mumbai"
    path, distance = graph.shortest_path(
        source,
        destination
    )

    print("\nSpecific route query")

    if path is None:
        print(f"No route exists from {source} to {destination}")
    else:
        print("Route:", " -> ".join(path))
        print(f"Total distance: {distance:g} km")

    print("\nAlgorithm characteristics")
    print("Data structure: Binary min-heap priority queue")
    print("Relaxation: Update distance when a shorter path is found")
    print("Stale entries: Ignored when extracted from the heap")
    print("Negative weights: Not supported")
    print("Time complexity: O((V + E) log V)")
    print("Space complexity: O(V + E)")


if __name__ == "__main__":
    main()
