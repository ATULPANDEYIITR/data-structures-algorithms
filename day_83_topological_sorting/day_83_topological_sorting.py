"""
Topological Sorting and Dependency Resolution
==============================================

Demonstrates:
1. Directed Acyclic Graphs (DAGs)
2. Graph representation using adjacency lists
3. DFS-based topological sorting
4. Kahn's algorithm using indegrees
5. Cycle detection and cycle reporting
6. Dependency resolution
7. Dependency-aware task execution
8. Graph validation and complexity analysis

Python 3.10+
No external dependencies.
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple


class GraphError(Exception):
    """Base exception for graph-related failures."""


class CycleDetectedError(GraphError):
    """Raised when a directed cycle prevents topological ordering."""


class TaskNotFoundError(GraphError):
    """Raised when a requested task does not exist."""


class TaskStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    task_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class DirectedGraph:
    """
    Directed graph represented using an adjacency list.

    An edge A -> B means A must execute before B.
    """

    adjacency: Dict[str, Set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )

    def add_vertex(self, vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise ValueError("Vertex must be a nonempty string.")

        self.adjacency[vertex]

    def add_edge(self, source: str, destination: str) -> None:
        if not source or not destination:
            raise ValueError("Source and destination are required.")

        self.add_vertex(source)
        self.add_vertex(destination)

        if source == destination:
            raise CycleDetectedError(
                f"Self-loop detected at vertex: {source}"
            )

        self.adjacency[source].add(destination)

    def vertices(self) -> List[str]:
        return sorted(self.adjacency)

    def edge_count(self) -> int:
        return sum(len(neighbors) for neighbors in self.adjacency.values())

    def reverse_graph(self) -> Dict[str, Set[str]]:
        reverse = {vertex: set() for vertex in self.adjacency}

        for source, destinations in self.adjacency.items():
            for destination in destinations:
                reverse[destination].add(source)

        return reverse

    def validate_vertices(self) -> None:
        for source, destinations in self.adjacency.items():
            for destination in destinations:
                if destination not in self.adjacency:
                    raise GraphError(
                        f"Undefined destination: {destination}"
                    )

    def topological_sort_dfs(self) -> List[str]:
        """
        DFS-based topological sorting.

        Three states:
        WHITE: unvisited
        GRAY: currently being explored
        BLACK: completely processed

        Encountering a GRAY vertex indicates a cycle.
        """

        WHITE, GRAY, BLACK = 0, 1, 2

        color = {vertex: WHITE for vertex in self.adjacency}
        result = []
        path = []

        def visit(vertex: str) -> None:
            color[vertex] = GRAY
            path.append(vertex)

            for neighbor in sorted(self.adjacency[vertex]):
                if color[neighbor] == GRAY:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]

                    raise CycleDetectedError(
                        "Cycle detected: " + " -> ".join(cycle)
                    )

                if color[neighbor] == WHITE:
                    visit(neighbor)

            path.pop()
            color[vertex] = BLACK
            result.append(vertex)

        for vertex in sorted(self.adjacency):
            if color[vertex] == WHITE:
                visit(vertex)

        result.reverse()
        return result

    def topological_sort_kahn(self) -> List[str]:
        """
        Kahn's algorithm.

        Repeatedly selects vertices having indegree zero.
        Removing a vertex decreases the indegree of its neighbors.

        A remaining vertex count smaller than V indicates a cycle.
        """

        indegree = {vertex: 0 for vertex in self.adjacency}

        for source in self.adjacency:
            for destination in self.adjacency[source]:
                indegree[destination] += 1

        queue = deque(
            sorted(
                vertex
                for vertex, degree in indegree.items()
                if degree == 0
            )
        )

        result = []

        while queue:
            vertex = queue.popleft()
            result.append(vertex)

            for neighbor in sorted(self.adjacency[vertex]):
                indegree[neighbor] -= 1

                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.adjacency):
            remaining = sorted(
                vertex
                for vertex, degree in indegree.items()
                if degree > 0
            )

            raise CycleDetectedError(
                f"Cycle detected; unresolved vertices: {remaining}"
            )

        return result

    def is_valid_topological_order(
        self, ordering: List[str]
    ) -> bool:
        if len(ordering) != len(self.adjacency):
            return False

        if len(set(ordering)) != len(ordering):
            return False

        if set(ordering) != set(self.adjacency):
            return False

        position = {
            vertex: index
            for index, vertex in enumerate(ordering)
        }

        return all(
            position[source] < position[destination]
            for source, destinations in self.adjacency.items()
            for destination in destinations
        )

    def dependency_levels(self) -> Dict[str, int]:
        """
        Calculates the earliest execution level of each vertex.

        Independent vertices can share an execution level.
        """

        order = self.topological_sort_kahn()
        levels = {vertex: 0 for vertex in self.adjacency}

        for vertex in order:
            for neighbor in self.adjacency[vertex]:
                levels[neighbor] = max(
                    levels[neighbor],
                    levels[vertex] + 1
                )

        return levels

    def dependencies_of(self, vertex: str) -> Set[str]:
        if vertex not in self.adjacency:
            raise TaskNotFoundError(vertex)

        reverse = self.reverse_graph()
        return reverse[vertex]


class DependencyResolver:
    """Resolves dependencies for a software build pipeline."""

    def __init__(self):
        self.graph = DirectedGraph()
        self.tasks: Dict[str, Task] = {}

    def register_task(self, task_id: str, description: str) -> None:
        if task_id in self.tasks:
            raise ValueError(f"Duplicate task: {task_id}")

        self.graph.add_vertex(task_id)

        self.tasks[task_id] = Task(
            task_id=task_id,
            description=description
        )

    def add_dependency(
        self, prerequisite: str, dependent: str
    ) -> None:
        if prerequisite not in self.tasks:
            raise TaskNotFoundError(prerequisite)

        if dependent not in self.tasks:
            raise TaskNotFoundError(dependent)

        self.graph.add_edge(prerequisite, dependent)

    def resolve(self) -> List[Task]:
        ordering = self.graph.topological_sort_kahn()

        return [self.tasks[task_id] for task_id in ordering]

    def execute(self) -> List[str]:
        """
        Simulates sequential execution in valid dependency order.
        """

        completed = set()
        execution_log = []

        for task in self.resolve():
            prerequisites = self.graph.dependencies_of(task.task_id)

            if not prerequisites.issubset(completed):
                raise GraphError(
                    f"Prerequisites incomplete for {task.task_id}"
                )

            task.status = TaskStatus.READY

            try:
                # Actual application work would execute here.
                task.status = TaskStatus.COMPLETED
                completed.add(task.task_id)
                execution_log.append(task.task_id)

            except Exception:
                task.status = TaskStatus.FAILED
                raise

        return execution_log


def build_sample_pipeline() -> DependencyResolver:
    resolver = DependencyResolver()

    tasks = {
        "source": "Retrieve source code",
        "validate": "Validate source files",
        "compile": "Compile application",
        "unit_test": "Execute unit tests",
        "security": "Perform security scanning",
        "package": "Create application package",
        "integration": "Run integration tests",
        "deploy": "Deploy application",
    }

    for task_id, description in tasks.items():
        resolver.register_task(task_id, description)

    dependencies = [
        ("source", "validate"),
        ("validate", "compile"),
        ("compile", "unit_test"),
        ("compile", "security"),
        ("unit_test", "package"),
        ("security", "package"),
        ("package", "integration"),
        ("integration", "deploy"),
    ]

    for prerequisite, dependent in dependencies:
        resolver.add_dependency(prerequisite, dependent)

    return resolver


def demonstrate_cycle_detection() -> None:
    graph = DirectedGraph()

    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")

    try:
        graph.topological_sort_dfs()
    except CycleDetectedError as error:
        print("\nDFS cycle detection:", error)

    try:
        graph.topological_sort_kahn()
    except CycleDetectedError as error:
        print("Kahn cycle detection:", error)


def demonstrate_edge_cases() -> None:
    # An isolated vertex is a valid DAG.
    graph = DirectedGraph()
    graph.add_vertex("isolated")

    assert graph.topological_sort_kahn() == ["isolated"]

    # An empty graph has an empty topological ordering.
    empty_graph = DirectedGraph()
    assert empty_graph.topological_sort_dfs() == []

    # Duplicate edges must not increase indegree.
    graph.add_edge("A", "B")
    graph.add_edge("A", "B")
    assert graph.edge_count() == 1

    # A self-loop is immediately rejected.
    try:
        graph.add_edge("C", "C")
    except CycleDetectedError:
        print("\nSelf-loop correctly rejected.")


def main() -> None:
    print("=" * 65)
    print("TOPOLOGICAL SORTING AND DEPENDENCY RESOLUTION")
    print("=" * 65)

    resolver = build_sample_pipeline()
    graph = resolver.graph

    print("\nVertices:", graph.vertices())
    print("Edges:", graph.edge_count())

    dfs_order = graph.topological_sort_dfs()
    kahn_order = graph.topological_sort_kahn()

    print("\nDFS topological ordering:")
    print(" -> ".join(dfs_order))

    print("\nKahn topological ordering:")
    print(" -> ".join(kahn_order))

    assert graph.is_valid_topological_order(dfs_order)
    assert graph.is_valid_topological_order(kahn_order)

    print("\nBoth orderings satisfy every dependency.")

    print("\nEarliest dependency levels:")
    for task, level in sorted(graph.dependency_levels().items()):
        print(f"{task:15} Level {level}")

    print("\nResolved dependency information:")
    for task in resolver.resolve():
        dependencies = sorted(
            graph.dependencies_of(task.task_id)
        )
        print(
            f"{task.task_id:15} "
            f"Prerequisites: {dependencies}"
        )

    print("\nExecution simulation:")
    execution_log = resolver.execute()

    for index, task_id in enumerate(execution_log, 1):
        print(f"{index}. {task_id}: completed")

    print("\nFinal task states:")
    for task_id, task in resolver.tasks.items():
        print(f"{task_id:15} {task.status.value}")

    demonstrate_cycle_detection()
    demonstrate_edge_cases()

    print("\nAll assertions passed.")


if __name__ == "__main__":
    main()
