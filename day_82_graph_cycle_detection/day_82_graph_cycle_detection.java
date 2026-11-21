import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public class GraphCycleDetection {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    enum DetectionStatus {
        CYCLE_DETECTED,
        ACYCLIC
    }

    record Edge(int source, int destination) {}

    record CycleResult(
        DetectionStatus status,
        String algorithm,
        List<Integer> cycle,
        List<Integer> topologicalOrder
    ) {
        CycleResult {
            cycle = List.copyOf(cycle);
            topologicalOrder = List.copyOf(topologicalOrder);
        }

        boolean hasCycle() {
            return status == DetectionStatus.CYCLE_DETECTED;
        }
    }

    record RepositoryPolicy(
        int minimumVertices,
        int maximumVertices,
        int maximumEdges,
        boolean allowSelfLoops,
        boolean allowParallelEdges
    ) {
        RepositoryPolicy {
            if (minimumVertices < 0 ||
                maximumVertices < minimumVertices ||
                maximumEdges < 0) {
                throw new IllegalArgumentException(
                    "Invalid graph policy."
                );
            }
        }
    }

    static class GraphValidationException extends RuntimeException {
        GraphValidationException(String message) {
            super(message);
        }
    }

    static class GraphCycleException extends RuntimeException {
        private final CycleResult result;

        GraphCycleException(CycleResult result) {
            super(
                "Graph rejected because a cycle was detected: "
                + result.algorithm()
            );

            this.result = result;
        }

        CycleResult getResult() {
            return result;
        }
    }

    static final class DisjointSet {
        private final int[] parent;
        private final int[] size;
        private int components;

        DisjointSet(int count) {
            if (count < 0) {
                throw new IllegalArgumentException(
                    "Negative vertex count."
                );
            }

            parent = new int[count];
            size = new int[count];

            for (int i = 0; i < count; i++) {
                parent[i] = i;
                size[i] = 1;
            }

            components = count;
        }

        private void validate(int vertex) {
            if (vertex < 0 || vertex >= parent.length) {
                throw new GraphValidationException(
                    "Invalid vertex: " + vertex
                );
            }
        }

        int find(int vertex) {
            validate(vertex);

            int root = vertex;

            while (parent[root] != root) {
                root = parent[root];
            }

            while (parent[vertex] != vertex) {
                int next = parent[vertex];
                parent[vertex] = root;
                vertex = next;
            }

            return root;
        }

        boolean union(int first, int second) {
            int rootFirst = find(first);
            int rootSecond = find(second);

            if (rootFirst == rootSecond) {
                return false;
            }

            if (size[rootFirst] < size[rootSecond]) {
                int temporary = rootFirst;
                rootFirst = rootSecond;
                rootSecond = temporary;
            }

            parent[rootSecond] = rootFirst;
            size[rootFirst] += size[rootSecond];
            components--;

            return true;
        }

        int components() {
            return components;
        }
    }

    static final class Graph {
        private final int vertexCount;
        private final GraphType type;
        private final List<List<Integer>> adjacency;
        private final List<Edge> edges;

        Graph(int vertexCount, GraphType type) {
            if (vertexCount < 0) {
                throw new IllegalArgumentException(
                    "Vertex count cannot be negative."
                );
            }

            this.vertexCount = vertexCount;
            this.type = Objects.requireNonNull(type);

            adjacency = new ArrayList<>(vertexCount);

            for (int i = 0; i < vertexCount; i++) {
                adjacency.add(new ArrayList<>());
            }

            edges = new ArrayList<>();
        }

        void addEdge(int source, int destination) {
            validateVertex(source);
            validateVertex(destination);

            adjacency.get(source).add(destination);

            if (type == GraphType.UNDIRECTED) {
                adjacency.get(destination).add(source);
            }

            edges.add(new Edge(source, destination));
        }

        private void validateVertex(int vertex) {
            if (vertex < 0 || vertex >= vertexCount) {
                throw new GraphValidationException(
                    "Invalid vertex: " + vertex
                );
            }
        }

        private void requireType(GraphType expected) {
            if (type != expected) {
                throw new IllegalStateException(
                    "Expected " + expected + " graph."
                );
            }
        }

        CycleResult directedDFS() {
            requireType(GraphType.DIRECTED);

            int[] state = new int[vertexCount];
            int[] parent = new int[vertexCount];

            Arrays.fill(parent, -1);

            for (int start = 0; start < vertexCount; start++) {
                if (state[start] == 0) {
                    List<Integer> cycle =
                        dfsDirected(start, state, parent);

                    if (cycle != null) {
                        return new CycleResult(
                            DetectionStatus.CYCLE_DETECTED,
                            "Directed DFS",
                            cycle,
                            List.of()
                        );
                    }
                }
            }

            return new CycleResult(
                DetectionStatus.ACYCLIC,
                "Directed DFS",
                List.of(),
                List.of()
            );
        }

        private List<Integer> dfsDirected(
            int vertex,
            int[] state,
            int[] parent
        ) {
            state[vertex] = 1;

            for (int neighbor : adjacency.get(vertex)) {
                if (state[neighbor] == 0) {
                    parent[neighbor] = vertex;

                    List<Integer> cycle =
                        dfsDirected(neighbor, state, parent);

                    if (cycle != null) {
                        return cycle;
                    }
                } else if (state[neighbor] == 1) {
                    List<Integer> path = new ArrayList<>();

                    int current = vertex;
                    path.add(current);

                    while (current != neighbor) {
                        current = parent[current];

                        if (current == -1) {
                            throw new IllegalStateException(
                                "Invalid DFS parent relationship."
                            );
                        }

                        path.add(current);
                    }

                    Collections.reverse(path);
                    path.add(neighbor);

                    return path;
                }
            }

            state[vertex] = 2;
            return null;
        }

        CycleResult directedBFS() {
            requireType(GraphType.DIRECTED);

            int[] indegree = new int[vertexCount];

            for (List<Integer> neighbors : adjacency) {
                for (int neighbor : neighbors) {
                    indegree[neighbor]++;
                }
            }

            Deque<Integer> queue = new ArrayDeque<>();

            for (int vertex = 0; vertex < vertexCount; vertex++) {
                if (indegree[vertex] == 0) {
                    queue.offer(vertex);
                }
            }

            List<Integer> order = new ArrayList<>();

            while (!queue.isEmpty()) {
                int vertex = queue.poll();
                order.add(vertex);

                for (int neighbor : adjacency.get(vertex)) {
                    indegree[neighbor]--;

                    if (indegree[neighbor] == 0) {
                        queue.offer(neighbor);
                    }
                }
            }

            DetectionStatus status =
                order.size() == vertexCount
                    ? DetectionStatus.ACYCLIC
                    : DetectionStatus.CYCLE_DETECTED;

            return new CycleResult(
                status,
                "Kahn BFS",
                List.of(),
                order
            );
        }

        CycleResult undirectedDFS() {
            requireType(GraphType.UNDIRECTED);

            boolean[] visited = new boolean[vertexCount];

            for (int start = 0; start < vertexCount; start++) {
                if (!visited[start] &&
                    dfsUndirected(start, -1, visited)) {

                    return new CycleResult(
                        DetectionStatus.CYCLE_DETECTED,
                        "Undirected DFS",
                        List.of(),
                        List.of()
                    );
                }
            }

            return new CycleResult(
                DetectionStatus.ACYCLIC,
                "Undirected DFS",
                List.of(),
                List.of()
            );
        }

        private boolean dfsUndirected(
            int vertex,
            int parent,
            boolean[] visited
        ) {
            visited[vertex] = true;

            for (int neighbor : adjacency.get(vertex)) {
                if (!visited[neighbor]) {
                    if (dfsUndirected(neighbor, vertex, visited)) {
                        return true;
                    }
                } else if (neighbor != parent) {
                    return true;
                }
            }

            return false;
        }

        CycleResult undirectedBFS() {
            requireType(GraphType.UNDIRECTED);

            boolean[] visited = new boolean[vertexCount];

            for (int start = 0; start < vertexCount; start++) {
                if (visited[start]) {
                    continue;
                }

                Deque<int[]> queue = new ArrayDeque<>();

                queue.offer(new int[]{start, -1});
                visited[start] = true;

                while (!queue.isEmpty()) {
                    int[] current = queue.poll();

                    int vertex = current[0];
                    int parent = current[1];

                    for (int neighbor : adjacency.get(vertex)) {
                        if (!visited[neighbor]) {
                            visited[neighbor] = true;

                            queue.offer(
                                new int[]{neighbor, vertex}
                            );
                        } else if (neighbor != parent) {
                            return new CycleResult(
                                DetectionStatus.CYCLE_DETECTED,
                                "Undirected BFS",
                                List.of(),
                                List.of()
                            );
                        }
                    }
                }
            }

            return new CycleResult(
                DetectionStatus.ACYCLIC,
                "Undirected BFS",
                List.of(),
                List.of()
            );
        }

        CycleResult undirectedDSU() {
            requireType(GraphType.UNDIRECTED);

            DisjointSet dsu = new DisjointSet(vertexCount);

            for (Edge edge : edges) {
                if (!dsu.union(
                    edge.source(),
                    edge.destination()
                )) {
                    return new CycleResult(
                        DetectionStatus.CYCLE_DETECTED,
                        "Disjoint Set Union",
                        List.of(),
                        List.of()
                    );
                }
            }

            return new CycleResult(
                DetectionStatus.ACYCLIC,
                "Disjoint Set Union",
                List.of(),
                List.of()
            );
        }

        int vertexCount() {
            return vertexCount;
        }

        int edgeCount() {
            return edges.size();
        }
    }

    /*
     * Enterprise service for validating graph submissions.
     *
     * A graph submission is accepted only when:
     * - its dimensions satisfy policy;
     * - its edge count satisfies policy;
     * - prohibited structures are absent;
     * - the configured cycle policy is satisfied.
     */

    static final class GraphGovernanceService {
        private final RepositoryPolicy policy;

        GraphGovernanceService(RepositoryPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        Graph validateSubmission(
            int vertices,
            GraphType type,
            List<Edge> submittedEdges,
            boolean requireAcyclic
        ) {
            if (vertices < policy.minimumVertices() ||
                vertices > policy.maximumVertices()) {
                throw new GraphValidationException(
                    "Vertex count violates repository policy."
                );
            }

            if (submittedEdges.size() > policy.maximumEdges()) {
                throw new GraphValidationException(
                    "Edge count exceeds policy."
                );
            }

            Set<Edge> uniqueEdges = new HashSet<>();

            Graph graph = new Graph(vertices, type);

            for (Edge edge : submittedEdges) {
                Objects.requireNonNull(edge);

                if (!policy.allowSelfLoops() &&
                    edge.source() == edge.destination()) {
                    throw new GraphValidationException(
                        "Self-loops are prohibited."
                    );
                }

                if (!policy.allowParallelEdges()) {
                    Edge normalized = type == GraphType.UNDIRECTED
                        ? new Edge(
                            Math.min(edge.source(), edge.destination()),
                            Math.max(edge.source(), edge.destination())
                        )
                        : edge;

                    if (!uniqueEdges.add(normalized)) {
                        throw new GraphValidationException(
                            "Parallel edges are prohibited."
                        );
                    }
                }

                graph.addEdge(
                    edge.source(),
                    edge.destination()
                );
            }

            if (requireAcyclic) {
                CycleResult result = type == GraphType.DIRECTED
                    ? graph.directedDFS()
                    : graph.undirectedDSU();

                if (result.hasCycle()) {
                    throw new GraphCycleException(result);
                }
            }

            return graph;
        }
    }

    private static void check(
        boolean condition,
        String description
    ) {
        if (!condition) {
            throw new AssertionError(
                "Failed test: " + description
            );
        }
    }

    private static void runTests() {
        Graph directed = new Graph(4, GraphType.DIRECTED);

        directed.addEdge(0, 1);
        directed.addEdge(1, 2);
        directed.addEdge(2, 3);
        directed.addEdge(3, 1);

        check(directed.directedDFS().hasCycle(),
              "Directed DFS");

        check(directed.directedBFS().hasCycle(),
              "Directed BFS");

        Graph dag = new Graph(5, GraphType.DIRECTED);

        dag.addEdge(0, 1);
        dag.addEdge(0, 2);
        dag.addEdge(1, 3);
        dag.addEdge(2, 3);
        dag.addEdge(3, 4);

        check(!dag.directedDFS().hasCycle(), "DAG DFS");
        check(!dag.directedBFS().hasCycle(), "DAG BFS");

        Graph undirected = new Graph(4, GraphType.UNDIRECTED);

        undirected.addEdge(0, 1);
        undirected.addEdge(1, 2);
        undirected.addEdge(2, 0);
        undirected.addEdge(2, 3);

        check(undirected.undirectedDFS().hasCycle(),
              "Undirected DFS");

        check(undirected.undirectedBFS().hasCycle(),
              "Undirected BFS");

        check(undirected.undirectedDSU().hasCycle(),
              "Undirected DSU");

        Graph tree = new Graph(5, GraphType.UNDIRECTED);

        tree.addEdge(0, 1);
        tree.addEdge(0, 2);
        tree.addEdge(1, 3);
        tree.addEdge(1, 4);

        check(!tree.undirectedDFS().hasCycle(), "Tree DFS");
        check(!tree.undirectedBFS().hasCycle(), "Tree BFS");
        check(!tree.undirectedDSU().hasCycle(), "Tree DSU");

        Graph loop = new Graph(1, GraphType.DIRECTED);
        loop.addEdge(0, 0);

        check(loop.directedDFS().hasCycle(), "Directed self-loop");

        Graph parallel = new Graph(2, GraphType.UNDIRECTED);
        parallel.addEdge(0, 1);
        parallel.addEdge(0, 1);

        check(parallel.undirectedDSU().hasCycle(),
              "Parallel edges");

        Graph empty = new Graph(0, GraphType.DIRECTED);

        check(!empty.directedDFS().hasCycle(), "Empty graph");
        check(!empty.directedBFS().hasCycle(), "Empty graph BFS");

        RepositoryPolicy policy = new RepositoryPolicy(
            1, 100, 500, false, false
        );

        GraphGovernanceService service =
            new GraphGovernanceService(policy);

        Graph accepted = service.validateSubmission(
            3,
            GraphType.DIRECTED,
            List.of(
                new Edge(0, 1),
                new Edge(1, 2)
            ),
            true
        );

        check(accepted.vertexCount() == 3,
              "Governance acceptance");

        boolean cycleRejected = false;

        try {
            service.validateSubmission(
                3,
                GraphType.DIRECTED,
                List.of(
                    new Edge(0, 1),
                    new Edge(1, 2),
                    new Edge(2, 0)
                ),
                true
            );
        } catch (GraphCycleException exception) {
            cycleRejected = true;
        }

        check(cycleRejected, "Governance cycle rejection");

        boolean selfLoopRejected = false;

        try {
            service.validateSubmission(
                2,
                GraphType.DIRECTED,
                List.of(new Edge(0, 0)),
                false
            );
        } catch (GraphValidationException exception) {
            selfLoopRejected = true;
        }

        check(selfLoopRejected, "Self-loop policy");

        System.out.println("All Java 17 tests passed.");
    }

    private static void demonstrate() {
        System.out.println("\nDIRECTED GRAPH");

        Graph directed = new Graph(5, GraphType.DIRECTED);

        directed.addEdge(0, 1);
        directed.addEdge(1, 2);
        directed.addEdge(2, 3);
        directed.addEdge(3, 1);
        directed.addEdge(3, 4);

        System.out.println(directed.directedDFS());
        System.out.println(directed.directedBFS());

        System.out.println("\nUNDIRECTED GRAPH");

        Graph undirected = new Graph(4, GraphType.UNDIRECTED);

        undirected.addEdge(0, 1);
        undirected.addEdge(1, 2);
        undirected.addEdge(2, 0);
        undirected.addEdge(2, 3);

        System.out.println(undirected.undirectedDFS());
        System.out.println(undirected.undirectedBFS());
        System.out.println(undirected.undirectedDSU());

        System.out.println(
            "Vertices: " + undirected.vertexCount()
        );

        System.out.println(
            "Edges: " + undirected.edgeCount()
        );
    }

    public static void main(String[] args) {
        try {
            runTests();
            demonstrate();
        } catch (RuntimeException exception) {
            System.err.println(
                "Application error: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
