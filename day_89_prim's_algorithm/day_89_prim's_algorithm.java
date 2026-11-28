import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Prim's Algorithm: Enterprise Minimum Spanning Forest Engine.
 *
 * Java 17.
 *
 * Features:
 * - Immutable domain records.
 * - Adjacency-list graph storage.
 * - Priority queue based edge selection.
 * - Lazy deletion.
 * - Disconnected graph support.
 * - Explicit execution state.
 * - Validation and exception handling.
 * - Independent forest verification.
 */
public class PrimAlgorithm {

    enum ExecutionStatus {
        CREATED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    record Vertex(String id) {
        Vertex {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex identifier cannot be empty."
                );
            }
        }
    }

    record WeightedEdge(
        Vertex source,
        Vertex destination,
        double weight
    ) {
        WeightedEdge {
            Objects.requireNonNull(source);
            Objects.requireNonNull(destination);

            if (source.equals(destination)) {
                throw new IllegalArgumentException(
                    "Self-loops are not supported."
                );
            }

            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Weight must be finite."
                );
            }
        }
    }

    record SelectedEdge(
        Vertex source,
        Vertex destination,
        double weight
    ) {}

    record MSTResult(
        List<SelectedEdge> edges,
        double totalWeight,
        int components,
        int vertexCount,
        long examinedEdges,
        ExecutionStatus status
    ) {
        MSTResult {
            edges = List.copyOf(edges);
        }

        boolean isConnected() {
            return vertexCount == 0 || components == 1;
        }
    }

    record Candidate(
        Vertex source,
        Vertex destination,
        double weight,
        long sequence
    ) {}

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class WeightedGraph {
        private final Map<Vertex, List<WeightedEdge>> adjacency =
            new HashMap<>();

        public synchronized void addVertex(Vertex vertex) {
            Objects.requireNonNull(vertex);
            adjacency.computeIfAbsent(
                vertex,
                ignored -> new ArrayList<>()
            );
        }

        public synchronized void addEdge(WeightedEdge edge) {
            Objects.requireNonNull(edge);

            addVertex(edge.source());
            addVertex(edge.destination());

            adjacency.get(edge.source()).add(edge);
            adjacency.get(edge.destination()).add(
                new WeightedEdge(
                    edge.destination(),
                    edge.source(),
                    edge.weight()
                )
            );
        }

        public synchronized Map<Vertex, List<WeightedEdge>> snapshot() {
            Map<Vertex, List<WeightedEdge>> copy = new HashMap<>();

            adjacency.forEach((vertex, edges) ->
                copy.put(
                    vertex,
                    List.copyOf(edges)
                )
            );

            return Collections.unmodifiableMap(copy);
        }

        public int vertexCount() {
            return adjacency.size();
        }
    }

    static class PrimService {

        private final AtomicBoolean executing =
            new AtomicBoolean(false);

        private volatile ExecutionStatus status =
            ExecutionStatus.CREATED;

        private final Comparator<Candidate> candidateOrder =
            Comparator.comparingDouble(Candidate::weight)
                .thenComparingLong(Candidate::sequence);

        public ExecutionStatus getStatus() {
            return status;
        }

        public MSTResult calculate(WeightedGraph graph) {
            Objects.requireNonNull(graph);

            if (!executing.compareAndSet(false, true)) {
                throw new GraphException(
                    "This service is already executing."
                );
            }

            status = ExecutionStatus.RUNNING;

            try {
                MSTResult result = execute(graph.snapshot());

                status = ExecutionStatus.COMPLETED;

                return new MSTResult(
                    result.edges(),
                    result.totalWeight(),
                    result.components(),
                    result.vertexCount(),
                    result.examinedEdges(),
                    status
                );

            } catch (RuntimeException exception) {
                status = ExecutionStatus.FAILED;
                throw exception;

            } finally {
                executing.set(false);
            }
        }

        private MSTResult execute(
            Map<Vertex, List<WeightedEdge>> adjacency
        ) {
            Set<Vertex> visited = new HashSet<>();

            List<SelectedEdge> selected = new ArrayList<>();

            PriorityQueue<Candidate> queue =
                new PriorityQueue<>(candidateOrder);

            double totalWeight = 0.0;
            int components = 0;
            long examined = 0;
            long sequence = 0;

            for (Vertex root : adjacency.keySet()) {
                if (visited.contains(root)) {
                    continue;
                }

                components++;
                visited.add(root);

                // Each disconnected component receives its own root.
                for (WeightedEdge edge : adjacency.get(root)) {
                    examined++;

                    if (!visited.contains(edge.destination())) {
                        queue.offer(new Candidate(
                            root,
                            edge.destination(),
                            edge.weight(),
                            sequence++
                        ));
                    }
                }

                while (!queue.isEmpty()) {
                    Candidate current = queue.poll();

                    if (visited.contains(current.destination())) {
                        continue;
                    }

                    visited.add(current.destination());

                    selected.add(new SelectedEdge(
                        current.source(),
                        current.destination(),
                        current.weight()
                    ));

                    totalWeight += current.weight();

                    for (WeightedEdge edge :
                         adjacency.get(current.destination())) {

                        examined++;

                        if (!visited.contains(edge.destination())) {
                            queue.offer(new Candidate(
                                current.destination(),
                                edge.destination(),
                                edge.weight(),
                                sequence++
                            ));
                        }
                    }
                }
            }

            return new MSTResult(
                selected,
                totalWeight,
                components,
                adjacency.size(),
                examined,
                ExecutionStatus.COMPLETED
            );
        }
    }

    static class ForestVerifier {

        private final Map<Vertex, Vertex> parent =
            new HashMap<>();

        private final Map<Vertex, Integer> rank =
            new HashMap<>();

        private Vertex find(Vertex vertex) {
            Vertex current = parent.get(vertex);

            if (!current.equals(vertex)) {
                current = find(current);
                parent.put(vertex, current);
            }

            return current;
        }

        private boolean union(Vertex first, Vertex second) {
            Vertex rootA = find(first);
            Vertex rootB = find(second);

            if (rootA.equals(rootB)) {
                return false;
            }

            int rankA = rank.get(rootA);
            int rankB = rank.get(rootB);

            if (rankA < rankB) {
                Vertex temporary = rootA;
                rootA = rootB;
                rootB = temporary;
            }

            parent.put(rootB, rootA);

            if (rankA == rankB) {
                rank.put(rootA, rank.get(rootA) + 1);
            }

            return true;
        }

        public boolean verify(
            WeightedGraph graph,
            MSTResult result
        ) {
            Map<Vertex, List<WeightedEdge>> adjacency =
                graph.snapshot();

            if (
                result.edges().size() !=
                result.vertexCount() - result.components()
            ) {
                return false;
            }

            parent.clear();
            rank.clear();

            adjacency.keySet().forEach(vertex -> {
                parent.put(vertex, vertex);
                rank.put(vertex, 0);
            });

            double weight = 0.0;

            for (SelectedEdge selected : result.edges()) {
                boolean exists = adjacency
                    .get(selected.source())
                    .stream()
                    .anyMatch(edge ->
                        edge.destination().equals(
                            selected.destination()
                        ) &&
                        Double.compare(
                            edge.weight(),
                            selected.weight()
                        ) == 0
                    );

                if (
                    !exists ||
                    !union(
                        selected.source(),
                        selected.destination()
                    )
                ) {
                    return false;
                }

                weight += selected.weight();
            }

            Set<Vertex> roots = new HashSet<>();

            for (Vertex vertex : adjacency.keySet()) {
                roots.add(find(vertex));
            }

            return (
                roots.size() == result.components() &&
                Math.abs(weight - result.totalWeight()) < 1e-9
            );
        }
    }

    private static WeightedGraph createExample() {
        WeightedGraph graph = new WeightedGraph();

        String[][] edges = {
            {"A", "B", "4"},
            {"A", "C", "3"},
            {"B", "C", "1"},
            {"B", "D", "2"},
            {"C", "D", "4"},
            {"C", "E", "5"},
            {"D", "E", "2"},
            {"D", "F", "3"},
            {"E", "F", "1"},
            {"E", "G", "7"},
            {"F", "G", "2"},
            {"H", "I", "6"}
        };

        for (String[] edge : edges) {
            graph.addEdge(new WeightedEdge(
                new Vertex(edge[0]),
                new Vertex(edge[1]),
                Double.parseDouble(edge[2])
            ));
        }

        graph.addVertex(new Vertex("ISOLATED"));

        return graph;
    }

    private static void runTests() {
        // Negative weights.
        WeightedGraph graph = new WeightedGraph();

        graph.addEdge(new WeightedEdge(
            new Vertex("A"),
            new Vertex("B"),
            -5
        ));

        graph.addEdge(new WeightedEdge(
            new Vertex("B"),
            new Vertex("C"),
            -2
        ));

        graph.addEdge(new WeightedEdge(
            new Vertex("A"),
            new Vertex("C"),
            1
        ));

        PrimService service = new PrimService();
        MSTResult result = service.calculate(graph);

        if (result.totalWeight() != -7) {
            throw new AssertionError(
                "Negative-weight test failed."
            );
        }

        if (!new ForestVerifier().verify(graph, result)) {
            throw new AssertionError(
                "Negative-weight verification failed."
            );
        }

        // Disconnected graph with an isolated vertex.
        WeightedGraph disconnected = new WeightedGraph();

        disconnected.addEdge(new WeightedEdge(
            new Vertex("X"),
            new Vertex("Y"),
            4
        ));

        disconnected.addEdge(new WeightedEdge(
            new Vertex("P"),
            new Vertex("Q"),
            2
        ));

        disconnected.addVertex(new Vertex("Z"));

        MSTResult disconnectedResult =
            new PrimService().calculate(disconnected);

        if (
            disconnectedResult.components() != 3 ||
            disconnectedResult.edges().size() != 2 ||
            disconnectedResult.totalWeight() != 6
        ) {
            throw new AssertionError(
                "Disconnected graph test failed."
            );
        }

        // Parallel edges.
        WeightedGraph parallel = new WeightedGraph();

        parallel.addEdge(new WeightedEdge(
            new Vertex("M"),
            new Vertex("N"),
            10
        ));

        parallel.addEdge(new WeightedEdge(
            new Vertex("M"),
            new Vertex("N"),
            2
        ));

        if (
            new PrimService().calculate(parallel).totalWeight() != 2
        ) {
            throw new AssertionError(
                "Parallel-edge test failed."
            );
        }

        // Invalid input.
        try {
            new WeightedEdge(
                new Vertex("A"),
                new Vertex("A"),
                5
            );

            throw new AssertionError(
                "Self-loop validation failed."
            );

        } catch (IllegalArgumentException expected) {
            // Expected validation exception.
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            WeightedGraph graph = createExample();

            PrimService service = new PrimService();

            MSTResult result = service.calculate(graph);

            System.out.println("PRIM'S ALGORITHM");
            System.out.println("==============================");

            for (SelectedEdge edge : result.edges()) {
                System.out.printf(
                    "%s -> %s | Weight: %.2f%n",
                    edge.source().id(),
                    edge.destination().id(),
                    edge.weight()
                );
            }

            System.out.println("==============================");

            System.out.println(
                "Vertices: " + result.vertexCount()
            );

            System.out.println(
                "Components: " + result.components()
            );

            System.out.println(
                "Selected edges: " + result.edges().size()
            );

            System.out.printf(
                "Total weight: %.2f%n",
                result.totalWeight()
            );

            System.out.println(
                "Connected: " + result.isConnected()
            );

            System.out.println(
                "Execution status: " + service.getStatus()
            );

            if (!new ForestVerifier().verify(graph, result)) {
                throw new GraphException(
                    "Minimum spanning forest verification failed."
                );
            }

            System.out.println("Verification: PASSED");

            runTests();

        } catch (Exception exception) {
            System.err.println(
                "Execution failed: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
