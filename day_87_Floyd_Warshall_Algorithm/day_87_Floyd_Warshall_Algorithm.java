import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Floyd-Warshall Algorithm
 *
 * Enterprise-oriented all-pairs shortest-path service.
 *
 * Java version: 17
 *
 * Features:
 * - Immutable domain records
 * - Graph validation
 * - Weighted directed graph
 * - Dynamic programming
 * - Path reconstruction
 * - Negative-cycle detection
 * - Computation versioning
 * - Service-level exception handling
 * - Automated tests
 */

public class Main {

    private static final double INF = Double.POSITIVE_INFINITY;

    enum ComputationStatus {
        SUCCESS,
        NEGATIVE_CYCLE
    }

    record Vertex(String id, String description) {
        Vertex {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex identifier is required"
                );
            }

            description = description == null ? "" : description;
        }
    }

    record Edge(String source, String destination, double weight) {
        Edge {
            if (source == null || destination == null) {
                throw new IllegalArgumentException(
                    "Edge endpoints are required"
                );
            }

            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Edge weight must be finite"
                );
            }
        }
    }

    record Route(
        boolean reachable,
        double distance,
        List<String> vertices
    ) {
        Route {
            vertices = List.copyOf(vertices);
        }
    }

    record ComputationReport(
        ComputationStatus status,
        int vertexCount,
        int edgeCount,
        long graphVersion,
        String message
    ) {}

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class NegativeCycleException extends RuntimeException {
        NegativeCycleException(String message) {
            super(message);
        }
    }

    static class WeightedGraph {

        private final Map<String, Vertex> vertices =
            new HashMap<>();

        private final List<Edge> edges =
            new ArrayList<>();

        private final AtomicLong version =
            new AtomicLong(0);

        public synchronized void addVertex(Vertex vertex) {
            Objects.requireNonNull(vertex);

            if (vertices.containsKey(vertex.id())) {
                throw new GraphException(
                    "Duplicate vertex: " + vertex.id()
                );
            }

            vertices.put(vertex.id(), vertex);
            version.incrementAndGet();
        }

        public synchronized void addEdge(
            Edge edge,
            boolean bidirectional
        ) {
            Objects.requireNonNull(edge);

            if (!vertices.containsKey(edge.source()) ||
                !vertices.containsKey(edge.destination())) {
                throw new GraphException(
                    "Edge references an unknown vertex"
                );
            }

            edges.add(edge);

            if (bidirectional) {
                edges.add(
                    new Edge(
                        edge.destination(),
                        edge.source(),
                        edge.weight()
                    )
                );
            }

            version.incrementAndGet();
        }

        public synchronized GraphSnapshot snapshot() {
            return new GraphSnapshot(
                List.copyOf(vertices.keySet()),
                List.copyOf(edges),
                version.get()
            );
        }

        public long getVersion() {
            return version.get();
        }
    }

    record GraphSnapshot(
        List<String> vertices,
        List<Edge> edges,
        long version
    ) {
        GraphSnapshot {
            vertices = List.copyOf(vertices);
            edges = List.copyOf(edges);
        }
    }

    static class ShortestPathResult {

        private final List<String> vertices;
        private final Map<String, Integer> indices;
        private final double[][] distance;
        private final int[][] nextVertex;
        private final long graphVersion;

        ShortestPathResult(
            List<String> vertices,
            double[][] distance,
            int[][] nextVertex,
            long graphVersion
        ) {
            this.vertices = List.copyOf(vertices);
            this.distance = distance;
            this.nextVertex = nextVertex;
            this.graphVersion = graphVersion;

            this.indices = new HashMap<>();

            for (int i = 0; i < vertices.size(); i++) {
                indices.put(vertices.get(i), i);
            }
        }

        public double getDistance(
            String source,
            String destination
        ) {
            int i = indexOf(source);
            int j = indexOf(destination);

            return distance[i][j];
        }

        private int indexOf(String vertex) {
            Integer index = indices.get(vertex);

            if (index == null) {
                throw new GraphException(
                    "Unknown vertex: " + vertex
                );
            }

            return index;
        }

        public Route getRoute(
            String source,
            String destination
        ) {
            int i = indexOf(source);
            int j = indexOf(destination);

            if (Double.isInfinite(distance[i][j])) {
                return new Route(false, INF, List.of());
            }

            List<String> path = new ArrayList<>();

            int current = i;
            path.add(vertices.get(current));

            for (int step = 0; step < vertices.size(); step++) {

                if (current == j) {
                    return new Route(
                        true,
                        distance[i][j],
                        path
                    );
                }

                current = nextVertex[current][j];

                if (current == -1) {
                    return new Route(false, INF, List.of());
                }

                path.add(vertices.get(current));
            }

            throw new NegativeCycleException(
                "Path reconstruction exceeded vertex limit"
            );
        }

        public List<String> getVertices() {
            return vertices;
        }

        public long getGraphVersion() {
            return graphVersion;
        }

        public double[][] getDistanceMatrix() {
            double[][] copy =
                new double[distance.length][distance.length];

            for (int i = 0; i < distance.length; i++) {
                copy[i] = distance[i].clone();
            }

            return copy;
        }
    }

    interface ShortestPathService {
        ShortestPathResult compute(GraphSnapshot snapshot);
    }

    static class FloydWarshallService
        implements ShortestPathService {

        @Override
        public ShortestPathResult compute(GraphSnapshot snapshot) {

            int n = snapshot.vertices().size();

            if (n == 0) {
                throw new GraphException(
                    "Graph must contain at least one vertex"
                );
            }

            Map<String, Integer> index = new HashMap<>();

            for (int i = 0; i < n; i++) {
                index.put(snapshot.vertices().get(i), i);
            }

            double[][] distance = new double[n][n];
            int[][] next = new int[n][n];

            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    distance[i][j] = INF;
                    next[i][j] = -1;
                }

                distance[i][i] = 0;
                next[i][i] = i;
            }

            // Initialize direct connections.
            for (Edge edge : snapshot.edges()) {
                int u = index.get(edge.source());
                int v = index.get(edge.destination());

                if (edge.weight() < distance[u][v]) {
                    distance[u][v] = edge.weight();
                    next[u][v] = v;
                }
            }

            /*
             * Dynamic programming recurrence:
             *
             * D_k(i,j) = min(
             *     D_(k-1)(i,j),
             *     D_(k-1)(i,k) + D_(k-1)(k,j)
             * )
             *
             * k is the permitted intermediate vertex.
             */

            for (int k = 0; k < n; k++) {

                for (int i = 0; i < n; i++) {

                    if (Double.isInfinite(distance[i][k])) {
                        continue;
                    }

                    for (int j = 0; j < n; j++) {

                        if (Double.isInfinite(distance[k][j])) {
                            continue;
                        }

                        double candidate =
                            distance[i][k] + distance[k][j];

                        if (!Double.isFinite(candidate)) {
                            throw new ArithmeticException(
                                "Distance arithmetic overflow"
                            );
                        }

                        if (candidate < distance[i][j]) {
                            distance[i][j] = candidate;
                            next[i][j] = next[i][k];
                        }
                    }
                }
            }

            // Negative diagonal means a negative cycle exists.
            for (int i = 0; i < n; i++) {
                if (distance[i][i] < 0) {
                    throw new NegativeCycleException(
                        "Negative cycle detected at " +
                        snapshot.vertices().get(i)
                    );
                }
            }

            return new ShortestPathResult(
                snapshot.vertices(),
                distance,
                next,
                snapshot.version()
            );
        }
    }

    static class RoutingApplication {

        private final WeightedGraph graph;

        private final ShortestPathService service;

        private ShortestPathResult currentResult;

        RoutingApplication(
            WeightedGraph graph,
            ShortestPathService service
        ) {
            this.graph = Objects.requireNonNull(graph);
            this.service = Objects.requireNonNull(service);
        }

        public synchronized ComputationReport refresh() {

            GraphSnapshot snapshot = graph.snapshot();

            try {
                ShortestPathResult candidate =
                    service.compute(snapshot);

                // Publish only a completely validated result.
                currentResult = candidate;

                return new ComputationReport(
                    ComputationStatus.SUCCESS,
                    snapshot.vertices().size(),
                    snapshot.edges().size(),
                    snapshot.version(),
                    "Shortest-path matrix computed successfully"
                );

            } catch (NegativeCycleException error) {

                return new ComputationReport(
                    ComputationStatus.NEGATIVE_CYCLE,
                    snapshot.vertices().size(),
                    snapshot.edges().size(),
                    snapshot.version(),
                    error.getMessage()
                );
            }
        }

        private void ensureFresh() {
            if (currentResult == null ||
                currentResult.getGraphVersion() != graph.getVersion()) {
                refresh();
            }

            if (currentResult == null ||
                currentResult.getGraphVersion() != graph.getVersion()) {
                throw new GraphException(
                    "No valid result for current graph version"
                );
            }
        }

        public double distance(String source, String destination) {
            ensureFresh();
            return currentResult.getDistance(source, destination);
        }

        public Route route(String source, String destination) {
            ensureFresh();
            return currentResult.getRoute(source, destination);
        }

        public ShortestPathResult getResult() {
            ensureFresh();
            return currentResult;
        }
    }

    static void printMatrix(ShortestPathResult result) {

        List<String> vertices = result.getVertices();
        double[][] matrix = result.getDistanceMatrix();

        System.out.printf("%-12s", "From/To");

        for (String vertex : vertices) {
            System.out.printf("%12s", vertex);
        }

        System.out.println();

        for (int i = 0; i < vertices.size(); i++) {

            System.out.printf("%-12s", vertices.get(i));

            for (int j = 0; j < vertices.size(); j++) {

                if (Double.isInfinite(matrix[i][j])) {
                    System.out.printf("%12s", "INF");
                } else {
                    System.out.printf("%12.2f", matrix[i][j]);
                }
            }

            System.out.println();
        }
    }

    static void testCorrectness() {

        WeightedGraph graph = new WeightedGraph();

        for (String vertex : List.of("A", "B", "C", "D")) {
            graph.addVertex(new Vertex(vertex, "Test vertex"));
        }

        graph.addEdge(new Edge("A", "B", 3), false);
        graph.addEdge(new Edge("B", "C", 2), false);
        graph.addEdge(new Edge("A", "C", 10), false);
        graph.addEdge(new Edge("C", "D", 1), false);

        RoutingApplication application =
            new RoutingApplication(
                graph,
                new FloydWarshallService()
            );

        ComputationReport report = application.refresh();

        if (report.status() != ComputationStatus.SUCCESS) {
            throw new AssertionError("Computation failed");
        }

        if (application.distance("A", "C") != 5 ||
            application.distance("A", "D") != 6) {
            throw new AssertionError("Distance test failed");
        }

        List<String> expected = List.of("A", "B", "C", "D");

        if (!application.route("A", "D").vertices().equals(expected)) {
            throw new AssertionError("Path reconstruction failed");
        }

        if (!Double.isInfinite(application.distance("D", "A"))) {
            throw new AssertionError("Unreachable-path test failed");
        }

        // Negative edge without a negative cycle.
        WeightedGraph negative = new WeightedGraph();

        for (String vertex : List.of("X", "Y", "Z")) {
            negative.addVertex(new Vertex(vertex, ""));
        }

        negative.addEdge(new Edge("X", "Y", 5), false);
        negative.addEdge(new Edge("Y", "Z", -2), false);

        RoutingApplication negativeApp =
            new RoutingApplication(
                negative,
                new FloydWarshallService()
            );

        negativeApp.refresh();

        if (negativeApp.distance("X", "Z") != 3) {
            throw new AssertionError("Negative edge test failed");
        }

        // Negative cycle.
        WeightedGraph cycle = new WeightedGraph();

        cycle.addVertex(new Vertex("P", ""));
        cycle.addVertex(new Vertex("Q", ""));

        cycle.addEdge(new Edge("P", "Q", -2), false);
        cycle.addEdge(new Edge("Q", "P", 1), false);

        RoutingApplication cycleApp =
            new RoutingApplication(
                cycle,
                new FloydWarshallService()
            );

        if (cycleApp.refresh().status() !=
            ComputationStatus.NEGATIVE_CYCLE) {
            throw new AssertionError("Negative-cycle test failed");
        }

        System.out.println("\nALL JAVA TESTS PASSED");
    }

    public static void main(String[] args) {

        WeightedGraph graph = new WeightedGraph();

        Map<String, String> locations = Map.of(
            "Delhi", "National Capital",
            "Agra", "Uttar Pradesh",
            "Jaipur", "Rajasthan",
            "Lucknow", "Uttar Pradesh",
            "Kanpur", "Uttar Pradesh",
            "Mumbai", "Maharashtra"
        );

        locations.forEach((id, description) ->
            graph.addVertex(new Vertex(id, description))
        );

        List<Edge> connections = List.of(
            new Edge("Delhi", "Agra", 2),
            new Edge("Delhi", "Jaipur", 5),
            new Edge("Agra", "Jaipur", 1),
            new Edge("Agra", "Lucknow", 4),
            new Edge("Jaipur", "Lucknow", 2),
            new Edge("Lucknow", "Kanpur", 1),
            new Edge("Kanpur", "Mumbai", 8),
            new Edge("Jaipur", "Mumbai", 12),
            new Edge("Delhi", "Kanpur", 15)
        );

        for (Edge edge : connections) {
            graph.addEdge(edge, false);
        }

        RoutingApplication application =
            new RoutingApplication(
                graph,
                new FloydWarshallService()
            );

        System.out.println("ENTERPRISE ROUTING SERVICE");

        ComputationReport report = application.refresh();

        System.out.println(report.message());

        printMatrix(application.getResult());

        System.out.println("\nROUTE QUERIES");

        for (String[] query : List.of(
            new String[]{"Delhi", "Mumbai"},
            new String[]{"Delhi", "Kanpur"},
            new String[]{"Agra", "Mumbai"},
            new String[]{"Mumbai", "Delhi"}
        )) {

            Route route = application.route(query[0], query[1]);

            System.out.print(
                query[0] + " -> " + query[1] + ": "
            );

            if (!route.reachable()) {
                System.out.println("Unreachable");
                continue;
            }

            System.out.println(
                String.join(" -> ", route.vertices()) +
                " | Distance: " + route.distance()
            );
        }

        // The application detects the graph version change.
        graph.addEdge(
            new Edge("Delhi", "Mumbai", 3),
            false
        );

        System.out.println("\nUPDATED ROUTING NETWORK");

        System.out.println(
            "Delhi -> Mumbai: " +
            application.distance("Delhi", "Mumbai")
        );

        testCorrectness();

        System.out.println("\nCOMPLEXITY");
        System.out.println("Time: O(V^3)");
        System.out.println("Space: O(V^2)");
        System.out.println("Path reconstruction: O(V)");
    }
}
