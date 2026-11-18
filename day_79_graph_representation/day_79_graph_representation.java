import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

/*
 * Enterprise Graph Representation and Analysis System.
 *
 * Java 17
 * No third-party dependencies.
 *
 * Implementations:
 * - Adjacency Matrix
 * - Adjacency List
 * - Edge List
 *
 * Includes graph validation, immutable domain records, graph services,
 * shortest paths, traversal, performance measurements, and tests.
 */

public class GraphRepresentationEngine {

    enum Representation {
        MATRIX,
        LIST,
        EDGE_LIST
    }

    enum GraphDirection {
        DIRECTED,
        UNDIRECTED
    }

    record Edge(int source, int target, double weight) {
        Edge {
            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Weight must be finite."
                );
            }
        }
    }

    record GraphMetrics(
        String representation,
        int vertices,
        int edges,
        long estimatedMemoryBytes,
        double lookupMicroseconds,
        double neighborMicroseconds,
        double enumerationMicroseconds
    ) {}

    record PathResult(
        int source,
        Map<Integer, Double> distances
    ) {
        PathResult {
            distances = Collections.unmodifiableMap(
                new HashMap<>(distances)
            );
        }
    }

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class GraphValidationException extends GraphException {
        GraphValidationException(String message) {
            super(message);
        }
    }

    interface GraphStore {
        int vertexCount();

        GraphDirection direction();

        Representation representation();

        void addEdge(int source, int target, double weight);

        boolean removeEdge(int source, int target);

        boolean hasEdge(int source, int target);

        List<Edge> neighbors(int vertex);

        List<Edge> edges();

        long estimatedMemoryBytes();
    }

    abstract static class AbstractGraph implements GraphStore {

        protected final int vertices;
        protected final GraphDirection direction;

        AbstractGraph(int vertices, GraphDirection direction) {
            if (vertices < 0) {
                throw new GraphValidationException(
                    "Vertex count cannot be negative."
                );
            }

            this.vertices = vertices;
            this.direction = direction;
        }

        @Override
        public int vertexCount() {
            return vertices;
        }

        @Override
        public GraphDirection direction() {
            return direction;
        }

        protected void validateVertex(int vertex) {
            if (vertex < 0 || vertex >= vertices) {
                throw new GraphValidationException(
                    "Invalid vertex: " + vertex
                );
            }
        }

        protected void validateEdge(
            int source,
            int target,
            double weight
        ) {
            validateVertex(source);
            validateVertex(target);

            if (!Double.isFinite(weight)) {
                throw new GraphValidationException(
                    "Edge weight must be finite."
                );
            }
        }

        protected boolean directed() {
            return direction == GraphDirection.DIRECTED;
        }
    }

    static final class MatrixGraph extends AbstractGraph {

        private final double[][] matrix;
        private final boolean[][] present;

        MatrixGraph(int vertices, GraphDirection direction) {
            super(vertices, direction);

            matrix = new double[vertices][vertices];
            present = new boolean[vertices][vertices];
        }

        @Override
        public Representation representation() {
            return Representation.MATRIX;
        }

        @Override
        public void addEdge(int source, int target, double weight) {
            validateEdge(source, target, weight);

            matrix[source][target] = weight;
            present[source][target] = true;

            if (!directed()) {
                matrix[target][source] = weight;
                present[target][source] = true;
            }
        }

        @Override
        public boolean removeEdge(int source, int target) {
            validateVertex(source);
            validateVertex(target);

            boolean existed = present[source][target];

            present[source][target] = false;

            if (!directed()) {
                present[target][source] = false;
            }

            return existed;
        }

        @Override
        public boolean hasEdge(int source, int target) {
            validateVertex(source);
            validateVertex(target);

            return present[source][target];
        }

        @Override
        public List<Edge> neighbors(int vertex) {
            validateVertex(vertex);

            List<Edge> result = new ArrayList<>();

            for (int target = 0; target < vertices; target++) {
                if (present[vertex][target]) {
                    result.add(
                        new Edge(vertex, target, matrix[vertex][target])
                    );
                }
            }

            return List.copyOf(result);
        }

        @Override
        public List<Edge> edges() {
            List<Edge> result = new ArrayList<>();

            for (int source = 0; source < vertices; source++) {
                for (int target = 0; target < vertices; target++) {
                    if (
                        present[source][target] &&
                        (directed() || target >= source)
                    ) {
                        result.add(
                            new Edge(
                                source,
                                target,
                                matrix[source][target]
                            )
                        );
                    }
                }
            }

            return List.copyOf(result);
        }

        @Override
        public long estimatedMemoryBytes() {
            return (long) vertices * vertices * 9L;
        }
    }

    static final class ListGraph extends AbstractGraph {

        private final List<Map<Integer, Double>> adjacency;

        ListGraph(int vertices, GraphDirection direction) {
            super(vertices, direction);

            adjacency = new ArrayList<>();

            for (int i = 0; i < vertices; i++) {
                adjacency.add(new HashMap<>());
            }
        }

        @Override
        public Representation representation() {
            return Representation.LIST;
        }

        @Override
        public void addEdge(int source, int target, double weight) {
            validateEdge(source, target, weight);

            adjacency.get(source).put(target, weight);

            if (!directed()) {
                adjacency.get(target).put(source, weight);
            }
        }

        @Override
        public boolean removeEdge(int source, int target) {
            validateVertex(source);
            validateVertex(target);

            boolean existed =
                adjacency.get(source).remove(target) != null;

            if (!directed()) {
                adjacency.get(target).remove(source);
            }

            return existed;
        }

        @Override
        public boolean hasEdge(int source, int target) {
            validateVertex(source);
            validateVertex(target);

            return adjacency.get(source).containsKey(target);
        }

        @Override
        public List<Edge> neighbors(int vertex) {
            validateVertex(vertex);

            List<Edge> result = new ArrayList<>();

            adjacency.get(vertex).forEach(
                (target, weight) ->
                    result.add(new Edge(vertex, target, weight))
            );

            result.sort(Comparator.comparingInt(Edge::target));

            return List.copyOf(result);
        }

        @Override
        public List<Edge> edges() {
            List<Edge> result = new ArrayList<>();

            for (int source = 0; source < vertices; source++) {
                final int current = source;

                adjacency.get(source).forEach((target, weight) -> {
                    if (directed() || target >= current) {
                        result.add(
                            new Edge(current, target, weight)
                        );
                    }
                });
            }

            result.sort(
                Comparator.comparingInt(Edge::source)
                    .thenComparingInt(Edge::target)
            );

            return List.copyOf(result);
        }

        @Override
        public long estimatedMemoryBytes() {
            long total = vertices * 48L;

            for (Map<Integer, Double> neighbors : adjacency) {
                total += neighbors.size() * 64L;
            }

            return total;
        }
    }

    static final class EdgeListGraph extends AbstractGraph {

        private final Map<String, Edge> edgeMap = new HashMap<>();

        EdgeListGraph(int vertices, GraphDirection direction) {
            super(vertices, direction);
        }

        @Override
        public Representation representation() {
            return Representation.EDGE_LIST;
        }

        private String key(int source, int target) {
            if (!directed() && source > target) {
                int temporary = source;
                source = target;
                target = temporary;
            }

            return source + ":" + target;
        }

        @Override
        public void addEdge(int source, int target, double weight) {
            validateEdge(source, target, weight);

            edgeMap.put(
                key(source, target),
                new Edge(
                    Math.min(source, target),
                    Math.max(source, target),
                    weight
                )
            );

            if (directed()) {
                edgeMap.put(
                    key(source, target),
                    new Edge(source, target, weight)
                );
            }
        }

        @Override
        public boolean removeEdge(int source, int target) {
            validateVertex(source);
            validateVertex(target);

            return edgeMap.remove(key(source, target)) != null;
        }

        @Override
        public boolean hasEdge(int source, int target) {
            validateVertex(source);
            validateVertex(target);

            return edgeMap.containsKey(key(source, target));
        }

        @Override
        public List<Edge> neighbors(int vertex) {
            validateVertex(vertex);

            List<Edge> result = new ArrayList<>();

            for (Edge edge : edgeMap.values()) {
                if (edge.source() == vertex) {
                    result.add(edge);
                }

                if (
                    !directed() &&
                    edge.target() == vertex &&
                    edge.source() != vertex
                ) {
                    result.add(
                        new Edge(
                            vertex,
                            edge.source(),
                            edge.weight()
                        )
                    );
                }
            }

            result.sort(Comparator.comparingInt(Edge::target));

            return List.copyOf(result);
        }

        @Override
        public List<Edge> edges() {
            List<Edge> result = new ArrayList<>(edgeMap.values());

            result.sort(
                Comparator.comparingInt(Edge::source)
                    .thenComparingInt(Edge::target)
            );

            return List.copyOf(result);
        }

        @Override
        public long estimatedMemoryBytes() {
            return edgeMap.size() * 80L;
        }
    }

    static final class GraphFactory {

        private GraphFactory() {}

        static GraphStore create(
            Representation representation,
            int vertices,
            GraphDirection direction
        ) {
            return switch (representation) {
                case MATRIX -> new MatrixGraph(vertices, direction);
                case LIST -> new ListGraph(vertices, direction);
                case EDGE_LIST -> new EdgeListGraph(vertices, direction);
            };
        }
    }

    static final class GraphTraversalService {

        List<Integer> breadthFirst(GraphStore graph, int start) {
            validate(graph, start);

            Set<Integer> visited = new HashSet<>();
            ArrayDeque<Integer> queue = new ArrayDeque<>();
            List<Integer> result = new ArrayList<>();

            visited.add(start);
            queue.add(start);

            while (!queue.isEmpty()) {
                int current = queue.removeFirst();
                result.add(current);

                for (Edge edge : graph.neighbors(current)) {
                    int neighbor = edge.target();

                    if (visited.add(neighbor)) {
                        queue.addLast(neighbor);
                    }
                }
            }

            return List.copyOf(result);
        }

        List<Integer> depthFirst(GraphStore graph, int start) {
            validate(graph, start);

            Set<Integer> visited = new HashSet<>();
            ArrayDeque<Integer> stack = new ArrayDeque<>();
            List<Integer> result = new ArrayList<>();

            stack.push(start);

            while (!stack.isEmpty()) {
                int current = stack.pop();

                if (!visited.add(current)) {
                    continue;
                }

                result.add(current);

                List<Edge> adjacent = new ArrayList<>(
                    graph.neighbors(current)
                );

                adjacent.sort(
                    Comparator.comparingInt(Edge::target).reversed()
                );

                for (Edge edge : adjacent) {
                    if (!visited.contains(edge.target())) {
                        stack.push(edge.target());
                    }
                }
            }

            return List.copyOf(result);
        }

        private void validate(GraphStore graph, int start) {
            if (start < 0 || start >= graph.vertexCount()) {
                throw new GraphValidationException(
                    "Invalid traversal start vertex."
                );
            }
        }
    }

    static final class ShortestPathService {

        PathResult dijkstra(GraphStore graph, int start) {
            if (start < 0 || start >= graph.vertexCount()) {
                throw new GraphValidationException(
                    "Invalid source vertex."
                );
            }

            for (Edge edge : graph.edges()) {
                if (edge.weight() < 0) {
                    throw new GraphValidationException(
                        "Negative weights are not supported."
                    );
                }
            }

            Map<Integer, Double> distance = new HashMap<>();

            for (int vertex = 0; vertex < graph.vertexCount(); vertex++) {
                distance.put(vertex, Double.POSITIVE_INFINITY);
            }

            PriorityQueue<Map.Entry<Integer, Double>> queue =
                new PriorityQueue<>(
                    Comparator.comparingDouble(Map.Entry::getValue)
                );

            distance.put(start, 0.0);

            queue.add(Map.entry(start, 0.0));

            while (!queue.isEmpty()) {
                var current = queue.poll();

                int vertex = current.getKey();
                double currentDistance = current.getValue();

                if (
                    currentDistance >
                    distance.get(vertex)
                ) {
                    continue;
                }

                for (Edge edge : graph.neighbors(vertex)) {
                    int neighbor = edge.target();

                    double candidate =
                        currentDistance + edge.weight();

                    if (candidate < distance.get(neighbor)) {
                        distance.put(neighbor, candidate);

                        queue.add(
                            Map.entry(neighbor, candidate)
                        );
                    }
                }
            }

            return new PathResult(start, distance);
        }
    }

    static final class GraphBenchmarkService {

        GraphMetrics measure(GraphStore graph, int repetitions) {
            if (repetitions <= 0) {
                throw new IllegalArgumentException(
                    "Repetitions must be positive."
                );
            }

            if (graph.vertexCount() == 0) {
                throw new GraphException(
                    "Cannot benchmark an empty graph."
                );
            }

            int source = 0;
            int target = graph.vertexCount() - 1;

            AtomicLong sink = new AtomicLong();

            long start = System.nanoTime();

            for (int i = 0; i < repetitions; i++) {
                if (graph.hasEdge(source, target)) {
                    sink.incrementAndGet();
                }
            }

            double lookup = (System.nanoTime() - start) /
                (double) repetitions / 1000.0;

            start = System.nanoTime();

            for (int i = 0; i < repetitions; i++) {
                sink.addAndGet(graph.neighbors(source).size());
            }

            double neighbor = (System.nanoTime() - start) /
                (double) repetitions / 1000.0;

            start = System.nanoTime();

            for (int i = 0; i < repetitions; i++) {
                sink.addAndGet(graph.edges().size());
            }

            double enumeration = (System.nanoTime() - start) /
                (double) repetitions / 1000.0;

            if (sink.get() < 0) {
                throw new IllegalStateException("Invalid benchmark state.");
            }

            return new GraphMetrics(
                graph.representation().name(),
                graph.vertexCount(),
                graph.edges().size(),
                graph.estimatedMemoryBytes(),
                lookup,
                neighbor,
                enumeration
            );
        }
    }

    static final class GraphProcessingService {

        CompletableFuture<List<Integer>> processAsync(
            GraphStore graph,
            int start,
            ExecutorService executor
        ) {
            return CompletableFuture.supplyAsync(
                () -> new GraphTraversalService()
                    .breadthFirst(graph, start),
                executor
            );
        }
    }

    static GraphStore sampleGraph(Representation representation) {
        GraphStore graph = GraphFactory.create(
            representation,
            6,
            GraphDirection.UNDIRECTED
        );

        List<Edge> edges = List.of(
            new Edge(0, 1, 4),
            new Edge(0, 2, 2),
            new Edge(1, 2, 1),
            new Edge(1, 3, 5),
            new Edge(2, 3, 8),
            new Edge(2, 4, 10),
            new Edge(3, 4, 2),
            new Edge(4, 5, 3)
        );

        edges.forEach(
            edge -> graph.addEdge(
                edge.source(),
                edge.target(),
                edge.weight()
            )
        );

        return graph;
    }

    static void runTests() {
        GraphTraversalService traversal =
            new GraphTraversalService();

        ShortestPathService shortest =
            new ShortestPathService();

        for (Representation representation : Representation.values()) {
            GraphStore graph = sampleGraph(representation);

            if (graph.edges().size() != 8) {
                throw new AssertionError("Edge count mismatch.");
            }

            List<Integer> expected = List.of(0, 1, 2, 3, 4, 5);

            if (!traversal.breadthFirst(graph, 0).equals(expected)) {
                throw new AssertionError("BFS mismatch.");
            }

            Map<Integer, Double> distances =
                shortest.dijkstra(graph, 0).distances();

            List<Double> expectedDistances =
                List.of(0.0, 3.0, 2.0, 8.0, 10.0, 13.0);

            for (int i = 0; i < expectedDistances.size(); i++) {
                if (!distances.get(i).equals(expectedDistances.get(i))) {
                    throw new AssertionError("Distance mismatch.");
                }
            }

            graph.removeEdge(0, 1);

            if (graph.hasEdge(0, 1)) {
                throw new AssertionError("Edge removal failed.");
            }
        }

        GraphStore directed = GraphFactory.create(
            Representation.LIST,
            3,
            GraphDirection.DIRECTED
        );

        directed.addEdge(0, 1, 1);

        if (directed.hasEdge(1, 0)) {
            throw new AssertionError("Direction validation failed.");
        }

        GraphStore negative = GraphFactory.create(
            Representation.LIST,
            2,
            GraphDirection.DIRECTED
        );

        negative.addEdge(0, 1, -1);

        boolean rejected = false;

        try {
            shortest.dijkstra(negative, 0);
        } catch (GraphValidationException exception) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError("Negative weight accepted.");
        }

        System.out.println("All Java 17 graph tests passed.");
    }

    public static void main(String[] args) {
        runTests();

        GraphTraversalService traversal =
            new GraphTraversalService();

        ShortestPathService shortest =
            new ShortestPathService();

        GraphBenchmarkService benchmark =
            new GraphBenchmarkService();

        for (Representation representation : Representation.values()) {
            GraphStore graph = sampleGraph(representation);

            System.out.println(
                "\nRepresentation: " + representation
            );

            System.out.println("Vertices: " + graph.vertexCount());
            System.out.println("Edges: " + graph.edges().size());

            System.out.println(
                "BFS: " + traversal.breadthFirst(graph, 0)
            );

            System.out.println(
                "DFS: " + traversal.depthFirst(graph, 0)
            );

            System.out.println(
                "Shortest paths: " +
                shortest.dijkstra(graph, 0).distances()
            );

            System.out.println(
                "Performance: " +
                benchmark.measure(graph, 1000)
            );
        }

        ExecutorService executor =
            Executors.newFixedThreadPool(2);

        try {
            GraphProcessingService processing =
                new GraphProcessingService();

            GraphStore graph = sampleGraph(Representation.LIST);

            List<Integer> result = processing.processAsync(
                graph,
                0,
                executor
            ).join();

            System.out.println("\nAsynchronous traversal: " + result);

        } finally {
            executor.shutdown();

            try {
                if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                    executor.shutdownNow();
                }
            } catch (InterruptedException exception) {
                executor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }

        System.out.println("\nGraph processing completed.");
    }
}
