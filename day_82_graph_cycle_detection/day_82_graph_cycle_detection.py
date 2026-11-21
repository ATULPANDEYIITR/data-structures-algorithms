from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class GraphType(Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"


@dataclass(frozen=True)
class CycleResult:
    has_cycle: bool
    algorithm: str
    cycle: tuple[int, ...] = ()


class Graph:
    """
    Graph supporting cycle detection in directed and undirected graphs.

    Vertices are integers in the range [0, vertex_count).
    Adjacency lists provide O(V + E) traversal complexity.
    """

    def __init__(
        self,
        vertex_count: int,
        graph_type: GraphType = GraphType.DIRECTED
    ):
        if not isinstance(vertex_count, int) or isinstance(vertex_count, bool):
            raise TypeError("Vertex count must be an integer.")

        if vertex_count < 0:
            raise ValueError("Vertex count cannot be negative.")

        self.vertex_count = vertex_count
        self.graph_type = graph_type
        self.adjacency: dict[int, list[int]] = {
            vertex: [] for vertex in range(vertex_count)
        }
        self.edges: list[tuple[int, int]] = []

    def _validate_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int) or isinstance(vertex, bool):
            raise TypeError("Vertex must be an integer.")

        if vertex not in self.adjacency:
            raise ValueError(f"Invalid vertex: {vertex}")

    def add_edge(self, source: int, destination: int) -> None:
        self._validate_vertex(source)
        self._validate_vertex(destination)

        self.adjacency[source].append(destination)

        if self.graph_type == GraphType.UNDIRECTED:
            self.adjacency[destination].append(source)

        self.edges.append((source, destination))

    def detect_directed_cycle_dfs(self) -> CycleResult:
        """
        DFS cycle detection using three vertex states.

        WHITE = 0: unvisited
        GRAY  = 1: currently in recursion path
        BLACK = 2: completely processed

        An edge to a GRAY vertex indicates a directed cycle.
        """

        if self.graph_type != GraphType.DIRECTED:
            raise ValueError("Algorithm requires a directed graph.")

        state = [0] * self.vertex_count
        parent = [-1] * self.vertex_count

        def reconstruct_cycle(vertex: int, ancestor: int) -> tuple[int, ...]:
            path = [vertex]

            while path[-1] != ancestor:
                previous = parent[path[-1]]

                if previous == -1:
                    raise RuntimeError("Invalid DFS parent relationship.")

                path.append(previous)

            path.reverse()
            path.append(ancestor)

            return tuple(path)

        def dfs(vertex: int) -> tuple[int, ...] | None:
            state[vertex] = 1

            for neighbor in self.adjacency[vertex]:
                if state[neighbor] == 0:
                    parent[neighbor] = vertex
                    result = dfs(neighbor)

                    if result is not None:
                        return result

                elif state[neighbor] == 1:
                    return reconstruct_cycle(vertex, neighbor)

            state[vertex] = 2
            return None

        for vertex in range(self.vertex_count):
            if state[vertex] == 0:
                cycle = dfs(vertex)

                if cycle is not None:
                    return CycleResult(True, "Directed DFS", cycle)

        return CycleResult(False, "Directed DFS")

    def detect_directed_cycle_bfs(self) -> CycleResult:
        """
        Kahn's topological sorting algorithm.

        A directed graph is acyclic if and only if every vertex
        can be processed through indegree-zero removal.
        """

        if self.graph_type != GraphType.DIRECTED:
            raise ValueError("Algorithm requires a directed graph.")

        indegree = [0] * self.vertex_count

        for source in range(self.vertex_count):
            for destination in self.adjacency[source]:
                indegree[destination] += 1

        queue = deque(
            vertex
            for vertex in range(self.vertex_count)
            if indegree[vertex] == 0
        )

        processed = 0
        topological_order = []

        while queue:
            vertex = queue.popleft()
            processed += 1
            topological_order.append(vertex)

            for neighbor in self.adjacency[vertex]:
                indegree[neighbor] -= 1

                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if processed != self.vertex_count:
            remaining = tuple(
                vertex
                for vertex in range(self.vertex_count)
                if indegree[vertex] > 0
            )

            return CycleResult(
                True,
                "Kahn BFS",
                remaining
            )

        return CycleResult(False, "Kahn BFS")

    def detect_undirected_cycle_dfs(self) -> CycleResult:
        """
        DFS cycle detection using parent tracking.

        An already visited neighbor that is not the current
        vertex's parent indicates a cycle.

        Self-loops and parallel edges are supported.
        """

        if self.graph_type != GraphType.UNDIRECTED:
            raise ValueError("Algorithm requires an undirected graph.")

        visited = [False] * self.vertex_count
        parent = [-1] * self.vertex_count

        def dfs(vertex: int) -> bool:
            visited[vertex] = True

            for neighbor in self.adjacency[vertex]:
                if not visited[neighbor]:
                    parent[neighbor] = vertex

                    if dfs(neighbor):
                        return True

                elif neighbor != parent[vertex]:
                    return True

            return False

        for vertex in range(self.vertex_count):
            if not visited[vertex]:
                if dfs(vertex):
                    return CycleResult(True, "Undirected DFS")

        return CycleResult(False, "Undirected DFS")

    def detect_undirected_cycle_bfs(self) -> CycleResult:
        """
        BFS cycle detection using parent information.
        """

        if self.graph_type != GraphType.UNDIRECTED:
            raise ValueError("Algorithm requires an undirected graph.")

        visited = [False] * self.vertex_count

        for start in range(self.vertex_count):
            if visited[start]:
                continue

            queue = deque([(start, -1)])
            visited[start] = True

            while queue:
                vertex, parent = queue.popleft()

                for neighbor in self.adjacency[vertex]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        queue.append((neighbor, vertex))

                    elif neighbor != parent:
                        return CycleResult(
                            True,
                            "Undirected BFS"
                        )

        return CycleResult(False, "Undirected BFS")


class DisjointSet:
    """
    Disjoint Set Union with path compression and union by rank.

    Supports efficient connectivity and cycle detection
    in undirected graphs.
    """

    def __init__(self, vertex_count: int):
        if vertex_count < 0:
            raise ValueError("Vertex count cannot be negative.")

        self.parent = list(range(vertex_count))
        self.rank = [0] * vertex_count
        self.components = vertex_count

    def _validate(self, vertex: int) -> None:
        if not isinstance(vertex, int) or isinstance(vertex, bool):
            raise TypeError("Vertex must be an integer.")

        if not 0 <= vertex < len(self.parent):
            raise ValueError(f"Invalid vertex: {vertex}")

    def find(self, vertex: int) -> int:
        self._validate(vertex)

        if self.parent[vertex] != vertex:
            self.parent[vertex] = self.find(self.parent[vertex])

        return self.parent[vertex]

    def union(self, first: int, second: int) -> bool:
        """
        Returns False when both vertices already belong
        to the same component.
        """

        root_first = self.find(first)
        root_second = self.find(second)

        if root_first == root_second:
            return False

        if self.rank[root_first] < self.rank[root_second]:
            root_first, root_second = root_second, root_first

        self.parent[root_second] = root_first

        if self.rank[root_first] == self.rank[root_second]:
            self.rank[root_first] += 1

        self.components -= 1
        return True


def detect_undirected_cycle_dsu(
    vertex_count: int,
    edges: Iterable[tuple[int, int]]
) -> CycleResult:
    """
    Detects an undirected cycle by processing edges.

    If an edge connects vertices already in the same
    connected component, that edge creates a cycle.
    """

    dsu = DisjointSet(vertex_count)

    for source, destination in edges:
        if not dsu.union(source, destination):
            return CycleResult(True, "Disjoint Set Union")

    return CycleResult(False, "Disjoint Set Union")


def detect_directed_cycle_from_edges(
    vertex_count: int,
    edges: Iterable[tuple[int, int]]
) -> CycleResult:
    graph = Graph(vertex_count, GraphType.DIRECTED)

    for source, destination in edges:
        graph.add_edge(source, destination)

    return graph.detect_directed_cycle_dfs()


def run_tests() -> None:
    # Directed graph containing a cycle.
    directed_cycle = Graph(4, GraphType.DIRECTED)

    for edge in [(0, 1), (1, 2), (2, 3), (3, 1)]:
        directed_cycle.add_edge(*edge)

    result = directed_cycle.detect_directed_cycle_dfs()
    assert result.has_cycle
    assert result.cycle[0] == result.cycle[-1]

    assert directed_cycle.detect_directed_cycle_bfs().has_cycle

    # Directed acyclic graph.
    dag = Graph(5, GraphType.DIRECTED)

    for edge in [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]:
        dag.add_edge(*edge)

    assert not dag.detect_directed_cycle_dfs().has_cycle
    assert not dag.detect_directed_cycle_bfs().has_cycle

    # Directed self-loop.
    self_loop = Graph(2, GraphType.DIRECTED)
    self_loop.add_edge(1, 1)

    assert self_loop.detect_directed_cycle_dfs().has_cycle
    assert self_loop.detect_directed_cycle_bfs().has_cycle

    # Undirected tree.
    tree = Graph(5, GraphType.UNDIRECTED)

    for edge in [(0, 1), (0, 2), (1, 3), (1, 4)]:
        tree.add_edge(*edge)

    assert not tree.detect_undirected_cycle_dfs().has_cycle
    assert not tree.detect_undirected_cycle_bfs().has_cycle
    assert not detect_undirected_cycle_dsu(5, tree.edges).has_cycle

    # Undirected cycle.
    cyclic = Graph(4, GraphType.UNDIRECTED)

    for edge in [(0, 1), (1, 2), (2, 0), (2, 3)]:
        cyclic.add_edge(*edge)

    assert cyclic.detect_undirected_cycle_dfs().has_cycle
    assert cyclic.detect_undirected_cycle_bfs().has_cycle
    assert detect_undirected_cycle_dsu(4, cyclic.edges).has_cycle

    # Parallel edges form a cycle in a multigraph.
    assert detect_undirected_cycle_dsu(
        2, [(0, 1), (0, 1)]
    ).has_cycle

    # Self-loop forms a cycle.
    assert detect_undirected_cycle_dsu(
        2, [(1, 1)]
    ).has_cycle

    # Disconnected acyclic graph.
    assert not detect_undirected_cycle_dsu(
        6, [(0, 1), (2, 3), (4, 5)]
    ).has_cycle

    # Empty graph.
    empty = Graph(0, GraphType.DIRECTED)
    assert not empty.detect_directed_cycle_dfs().has_cycle
    assert not empty.detect_directed_cycle_bfs().has_cycle

    # Invalid vertices.
    try:
        tree.add_edge(0, 10)
        raise AssertionError("Invalid vertex was accepted.")
    except ValueError:
        pass

    # Wrong algorithm and graph-type combination.
    try:
        tree.detect_directed_cycle_dfs()
        raise AssertionError("Invalid graph type was accepted.")
    except ValueError:
        pass

    print("All graph cycle detection tests passed.")


def demonstrate() -> None:
    print("\nDIRECTED GRAPH")

    directed = Graph(5, GraphType.DIRECTED)

    for edge in [(0, 1), (1, 2), (2, 3), (3, 1), (3, 4)]:
        directed.add_edge(*edge)

    print("DFS:", directed.detect_directed_cycle_dfs())
    print("BFS:", directed.detect_directed_cycle_bfs())

    print("\nUNDIRECTED GRAPH")

    undirected_edges = [
        (0, 1),
        (1, 2),
        (2, 0),
        (2, 3)
    ]

    undirected = Graph(4, GraphType.UNDIRECTED)

    for edge in undirected_edges:
        undirected.add_edge(*edge)

    print("DFS:", undirected.detect_undirected_cycle_dfs())
    print("BFS:", undirected.detect_undirected_cycle_bfs())
    print(
        "DSU:",
        detect_undirected_cycle_dsu(4, undirected_edges)
    )


if __name__ == "__main__":
    run_tests()
    demonstrate()
