import java.util.*;
import java.util.stream.Collectors;

/*
 * Bellman-Ford Enterprise Graph Analysis Engine
 *
 * Java 17 implementation featuring:
 * - Immutable domain records
 * - Graph validation
 * - Directed weighted edges
 * - Negative-edge support
 * - Relaxation policies
 * - Negative-cycle detection
 * - Downstream impact analysis
 * - Shortest-path reconstruction
 * - Enterprise-style service separation
 * - Automated validation
 *
 * Compile:
 * javac BellmanFordEnterprise.java
 *
 * Run:
 * java BellmanFordEnterprise
 */

public class BellmanFordEnterprise {

    private static final long INF = Long.MAX_VALUE / 4;

    enum VertexState {
        SOURCE,
        REACHABLE,
        UNREACHABLE,
        NEGATIVE_CYCLE_AFFECTED
    }

    enum AnalysisStatus {
        COMPLETED,
        NEGATIVE_CYCLE_DETECTED
    }

    record Edge(int source, int destination, long weight) {

        Edge {
            if (weight >= INF || weight <= -INF) {
                throw new IllegalArgumentException(
                    "Edge weight exceeds supported range."
                );
            }
        }
    }

    record VertexDistance(
        int vertex,
        long distance,
        Integer predecessor,
        VertexState state
    ) {}

    record GraphSnapshot(
        int vertexCount,
        List<Edge> edges,
        List<List<Integer>> adjacency,
        long version
    ) {
        GraphSnapshot {
            edges = List.copyOf(edges);

            adjacency = adjacency.stream()
                .map(List::copyOf)
                .toList();
        }
    }

    record AnalysisResult(
        int source,
        long graphVersion,
        Map<Integer, VertexDistance> vertices,
        List<Integer> negativeCycle,
        int relaxationPasses,
        AnalysisStatus status
    ) {
        AnalysisResult {
            vertices = Collections.unmodifiableMap(
                new LinkedHashMap<>(vertices)
            );

            negativeCycle = List.copyOf(negativeCycle);
        }

        boolean hasNegativeCycle() {
            return status == AnalysisStatus.NEGATIVE_CYCLE_DETECTED;
        }

        VertexDistance getVertex(int vertex) {
            VertexDistance result = vertices.get(vertex);

            if (result == null) {
                throw new IllegalArgumentException("Unknown vertex.");
            }

            return result;
        }
    }

    static class GraphValidationException extends RuntimeException {
        GraphValidationException(String message) {
            super(message);
        }
    }

    static class NegativeCycleException extends RuntimeException {
        private final List<Integer> cycle;

        NegativeCycleException(List<Integer> cycle) {
            super("Shortest path is undefined due to a reachable negative cycle.");
            this.cycle = List.copyOf(cycle);
        }

        List<Integer> getCycle() {
            return cycle;
        }
    }

    static class WeightedGraph {
        private final int vertexCount;
        private final List<Edge> edges = new ArrayList<>();
        private final List<List<Integer>> adjacency;
        private long version = 0;

        WeightedGraph(int vertexCount) {
            if (vertexCount <= 0) {
                throw new GraphValidationException(
                    "Graph must contain at least one vertex."
                );
            }

            this.vertexCount = vertexCount;
            this.adjacency = new ArrayList<>();

            for (int i = 0; i < vertexCount; i++) {
                adjacency.add(new ArrayList<>());
            }
        }

        private void validateVertex(int vertex) {
            if (vertex < 0 || vertex >= vertexCount) {
                throw new GraphValidationException(
                    "Invalid vertex: " + vertex
                );
            }
        }

        synchronized void addEdge(int source, int destination, long weight) {
            validateVertex(source);
            validateVertex(destination);

            if (weight >= INF || weight <= -INF) {
                throw new GraphValidationException(
                    "Weight exceeds supported range."
                );
            }

            edges.add(new Edge(source, destination, weight));
            adjacency.get(source).add(destination);
            version++;
        }

        synchronized GraphSnapshot snapshot() {
            return new GraphSnapshot(
                vertexCount,
                edges,
                adjacency,
                version
            );
        }
    }

    interface DistancePolicy {
        boolean shouldRelax(long current, long candidate);
    }

    static class StandardDistancePolicy implements DistancePolicy {
        @Override
        public boolean shouldRelax(long current, long candidate) {
            return candidate < current;
        }
    }

    static class BellmanFordService {
        private final DistancePolicy policy;

        BellmanFordService(DistancePolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        private long safeAdd(long a, long b) {
            try {
                long result = Math.addExact(a, b);

                if (result >= INF || result <= -INF) {
                    throw new ArithmeticException();
                }

                return result;
            } catch (ArithmeticException exception) {
                throw new ArithmeticException(
                    "Distance calculation exceeds supported range."
                );
            }
        }

        AnalysisResult analyze(GraphSnapshot graph, int source) {
            Objects.requireNonNull(graph);

            int n = graph.vertexCount();

            if (source < 0 || source >= n) {
                throw new GraphValidationException(
                    "Source vertex does not exist."
                );
            }

            long[] distance = new long[n];
            int[] predecessor = new int[n];

            Arrays.fill(distance, INF);
            Arrays.fill(predecessor, -1);

            distance[source] = 0;

            int passes = 0;

            // Standard Bellman-Ford relaxation.
            for (int iteration = 0; iteration < n - 1; iteration++) {
                boolean updated = false;

                for (Edge edge : graph.edges()) {
                    int u = edge.source();
                    int v = edge.destination();

                    if (distance[u] == INF) {
                        continue;
                    }

                    long candidate = safeAdd(distance[u], edge.weight());

                    if (policy.shouldRelax(distance[v], candidate)) {
                        distance[v] = candidate;
                        predecessor[v] = u;
                        updated = true;
                    }
                }

                passes++;

                if (!updated) {
                    break;
                }
            }

            // Negative-cycle detection.
            int cycleVertex = -1;

            for (Edge edge : graph.edges()) {
                int u = edge.source();
                int v = edge.destination();

                if (distance[u] == INF) {
                    continue;
                }

                long candidate = safeAdd(distance[u], edge.weight());

                if (candidate < distance[v]) {
                    predecessor[v] = u;

                    if (cycleVertex == -1) {
                        cycleVertex = v;
                    }
                }
            }

            List<Integer> negativeCycle = cycleVertex == -1
                ? List.of()
                : reconstructCycle(cycleVertex, predecessor, n);

            // Propagate negative-cycle impact through outgoing edges.
            boolean[] affected = new boolean[n];
            Queue<Integer> queue = new ArrayDeque<>();

            for (Edge edge : graph.edges()) {
                int u = edge.source();
                int v = edge.destination();

                if (
                    distance[u] != INF &&
                    safeAdd(distance[u], edge.weight()) < distance[v] &&
                    !affected[v]
                ) {
                    affected[v] = true;
                    queue.add(v);
                }
            }

            while (!queue.isEmpty()) {
                int current = queue.remove();

                for (int neighbor : graph.adjacency().get(current)) {
                    if (!affected[neighbor]) {
                        affected[neighbor] = true;
                        queue.add(neighbor);
                    }
                }
            }

            Map<Integer, VertexDistance> vertexResults =
                new LinkedHashMap<>();

            for (int vertex = 0; vertex < n; vertex++) {
                VertexState state;

                if (affected[vertex]) {
                    state = VertexState.NEGATIVE_CYCLE_AFFECTED;
                } else if (distance[vertex] == INF) {
                    state = VertexState.UNREACHABLE;
                } else if (vertex == source) {
                    state = VertexState.SOURCE;
                } else {
                    state = VertexState.REACHABLE;
                }

                vertexResults.put(
                    vertex,
                    new VertexDistance(
                        vertex,
                        distance[vertex],
                        predecessor[vertex] == -1
                            ? null
                            : predecessor[vertex],
                        state
                    )
                );
            }

            AnalysisStatus status = negativeCycle.isEmpty()
                ? AnalysisStatus.COMPLETED
                : AnalysisStatus.NEGATIVE_CYCLE_DETECTED;

            return new AnalysisResult(
                source,
                graph.version(),
                vertexResults,
                negativeCycle,
                passes,
                status
            );
        }

        private List<Integer> reconstructCycle(
            int vertex,
            int[] predecessor,
            int n
        ) {
            for (int i = 0; i < n; i++) {
                vertex = predecessor[vertex];

                if (vertex == -1) {
                    return List.of();
                }
            }

            int start = vertex;
            List<Integer> cycle = new ArrayList<>();

            cycle.add(start);
            vertex = predecessor[start];

            while (vertex != start) {
                if (vertex == -1 || cycle.size() > n) {
                    return List.of();
                }

                cycle.add(vertex);
                vertex = predecessor[vertex];
            }

            cycle.add(start);
            Collections.reverse(cycle);

            return List.copyOf(cycle);
        }

        List<Integer> reconstructPath(
            AnalysisResult result,
            int destination
        ) {
            VertexDistance target = result.getVertex(destination);

            if (target.state() == VertexState.NEGATIVE_CYCLE_AFFECTED) {
                throw new NegativeCycleException(result.negativeCycle());
            }

            if (target.state() == VertexState.UNREACHABLE) {
                return List.of();
            }

            List<Integer> path = new ArrayList<>();
            Integer current = destination;

            while (current != null) {
                path.add(current);

                if (current == result.source()) {
                    Collections.reverse(path);
                    return List.copyOf(path);
                }

                current = result.getVertex(current).predecessor();
            }

            return List.of();
        }
    }

    static void displayResult(
        AnalysisResult result,
        BellmanFordService service,
        int vertexCount
    ) {
        System.out.println("\nSource: " + result.source());

        System.out.printf(
            "%-10s %-18s %-16s %-30s%n",
            "VERTEX",
            "DISTANCE",
            "PREDECESSOR",
            "STATE"
        );

        for (int vertex = 0; vertex < vertexCount; vertex++) {
            VertexDistance entry = result.getVertex(vertex);

            String distance = switch (entry.state()) {
                case NEGATIVE_CYCLE_AFFECTED -> "UNDEFINED";
                case UNREACHABLE -> "INFINITY";
                default -> Long.toString(entry.distance());
            };

            System.out.printf(
                "%-10d %-18s %-16s %-30s%n",
                vertex,
                distance,
                entry.predecessor() == null
                    ? "-"
                    : entry.predecessor(),
                entry.state()
            );
        }

        System.out.println("\nStatus: " + result.status());
        System.out.println("Relaxation passes: " + result.relaxationPasses());

        if (result.hasNegativeCycle()) {
            System.out.println("Negative cycle: " + result.negativeCycle());
        }

        System.out.println("\nShortest paths:");

        for (int vertex = 0; vertex < vertexCount; vertex++) {
            System.out.print(result.source() + " -> " + vertex + ": ");

            try {
                List<Integer> path = service.reconstructPath(result, vertex);

                if (path.isEmpty()) {
                    System.out.println("UNREACHABLE");
                } else {
                    System.out.println(
                        path.stream()
                            .map(String::valueOf)
                            .collect(Collectors.joining(" -> "))
                        + " (cost: " + result.getVertex(vertex).distance() + ")"
                    );
                }
            } catch (NegativeCycleException exception) {
                System.out.println("UNDEFINED");
            }
        }
    }

    static void demonstrateNormalGraph() {
        System.out.println("\n========== NORMAL GRAPH ==========");

        WeightedGraph graph = new WeightedGraph(5);

        graph.addEdge(0, 1, 6);
        graph.addEdge(0, 2, 7);
        graph.addEdge(1, 2, 8);
        graph.addEdge(1, 3, 5);
        graph.addEdge(1, 4, -4);
        graph.addEdge(2, 3, -3);
        graph.addEdge(2, 4, 9);
        graph.addEdge(3, 1, -2);
        graph.addEdge(4, 0, 2);
        graph.addEdge(4, 3, 7);

        BellmanFordService service =
            new BellmanFordService(new StandardDistancePolicy());

        AnalysisResult result = service.analyze(graph.snapshot(), 0);

        displayResult(result, service, 5);
    }

    static void demonstrateNegativeCycle() {
        System.out.println("\n========== NEGATIVE CYCLE ==========");

        WeightedGraph graph = new WeightedGraph(6);

        graph.addEdge(0, 1, 4);
        graph.addEdge(1, 2, 3);
        graph.addEdge(2, 3, -8);
        graph.addEdge(3, 1, 2);
        graph.addEdge(3, 4, 5);
        graph.addEdge(4, 5, 2);

        BellmanFordService service =
            new BellmanFordService(new StandardDistancePolicy());

        AnalysisResult result = service.analyze(graph.snapshot(), 0);

        displayResult(result, service, 6);
    }

    static void demonstrateUnreachableCycle() {
        System.out.println("\n========== UNREACHABLE NEGATIVE CYCLE ==========");

        WeightedGraph graph = new WeightedGraph(5);

        graph.addEdge(0, 1, 5);
        graph.addEdge(1, 2, 3);
        graph.addEdge(3, 4, -5);
        graph.addEdge(4, 3, 2);

        BellmanFordService service =
            new BellmanFordService(new StandardDistancePolicy());

        AnalysisResult result = service.analyze(graph.snapshot(), 0);

        displayResult(result, service, 5);
    }

    static void runTests() {
        BellmanFordService service =
            new BellmanFordService(new StandardDistancePolicy());

        WeightedGraph graph = new WeightedGraph(4);

        graph.addEdge(0, 1, 4);
        graph.addEdge(1, 2, -2);
        graph.addEdge(2, 3, 3);

        AnalysisResult result = service.analyze(graph.snapshot(), 0);

        if (result.getVertex(3).distance() != 5) {
            throw new AssertionError("Distance test failed.");
        }

        if (!service.reconstructPath(result, 3).equals(
            List.of(0, 1, 2, 3)
        )) {
            throw new AssertionError("Path test failed.");
        }

        WeightedGraph cycleGraph = new WeightedGraph(3);

        cycleGraph.addEdge(0, 1, 1);
        cycleGraph.addEdge(1, 2, -3);
        cycleGraph.addEdge(2, 1, 1);

        AnalysisResult cycleResult =
            service.analyze(cycleGraph.snapshot(), 0);

        if (!cycleResult.hasNegativeCycle()) {
            throw new AssertionError("Negative-cycle test failed.");
        }

        WeightedGraph isolatedGraph = new WeightedGraph(4);

        isolatedGraph.addEdge(0, 1, 2);
        isolatedGraph.addEdge(2, 3, -4);
        isolatedGraph.addEdge(3, 2, 1);

        AnalysisResult isolatedResult =
            service.analyze(isolatedGraph.snapshot(), 0);

        if (isolatedResult.hasNegativeCycle()) {
            throw new AssertionError("Unreachable-cycle test failed.");
        }

        boolean rejected = false;

        try {
            graph.addEdge(0, 9, 1);
        } catch (GraphValidationException exception) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError("Validation test failed.");
        }

        System.out.println("\nAll Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            demonstrateNormalGraph();
            demonstrateNegativeCycle();
            demonstrateUnreachableCycle();
            runTests();
        } catch (RuntimeException exception) {
            System.err.println("Execution failed: " + exception.getMessage());
            System.exit(1);
        }
    }
}
