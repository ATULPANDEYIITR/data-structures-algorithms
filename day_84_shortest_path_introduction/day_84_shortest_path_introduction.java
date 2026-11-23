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

public class ShortestPathEnterprise {

    enum Algorithm {
        DIJKSTRA,
        BELLMAN_FORD
    }

    record Edge(String source, String target, double weight) {
        Edge {
            if (source == null || source.isBlank()
                    || target == null || target.isBlank()) {
                throw new IllegalArgumentException(
                    "Edge vertices must be nonempty."
                );
            }

            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Edge weight must be finite."
                );
            }
        }
    }

    record Route(
        String source,
        String target,
        double distance,
        List<String> path,
        Algorithm algorithm,
        long graphVersion
    ) {
        Route {
            path = List.copyOf(path);
        }

        boolean reachable() {
            return Double.isFinite(distance);
        }
    }

    record QueueEntry(String vertex, double distance) {}

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class NegativeCycleException extends GraphException {
        NegativeCycleException(String message) {
            super(message);
        }
    }

    static class WeightedGraph {
        private final Map<String, List<Edge>> adjacency =
            new HashMap<>();

        private final List<Edge> edges = new ArrayList<>();

        private long version = 0;

        public synchronized void addVertex(String vertex) {
            if (vertex == null || vertex.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex must be nonempty."
                );
            }

            if (!adjacency.containsKey(vertex)) {
                adjacency.put(vertex, new ArrayList<>());
                version++;
            }
        }

        public synchronized void addEdge(
            String source,
            String target,
            double weight,
            boolean bidirectional
        ) {
            Edge edge = new Edge(source, target, weight);

            addVertex(source);
            addVertex(target);

            adjacency.get(source).add(edge);
            edges.add(edge);

            if (bidirectional) {
                Edge reverse = new Edge(target, source, weight);
                adjacency.get(target).add(reverse);
                edges.add(reverse);
            }

            version++;
        }

        private void validate(String source, String target) {
            if (!adjacency.containsKey(source)) {
                throw new GraphException(
                    "Unknown source: " + source
                );
            }

            if (!adjacency.containsKey(target)) {
                throw new GraphException(
                    "Unknown target: " + target
                );
            }
        }

        private boolean hasNegativeEdges() {
            return edges.stream().anyMatch(
                edge -> edge.weight() < 0
            );
        }

        private List<String> reconstruct(
            Map<String, String> previous,
            String source,
            String target
        ) {
            List<String> path = new ArrayList<>();
            Set<String> visited = new HashSet<>();

            String current = target;

            while (current != null) {
                if (!visited.add(current)) {
                    throw new GraphException(
                        "Invalid predecessor cycle."
                    );
                }

                path.add(current);

                if (current.equals(source)) {
                    Collections.reverse(path);
                    return path;
                }

                current = previous.get(current);
            }

            return List.of();
        }

        private Route createRoute(
            String source,
            String target,
            Map<String, Double> distances,
            Map<String, String> previous,
            Algorithm algorithm
        ) {
            double distance = distances.get(target);

            List<String> path = Double.isInfinite(distance)
                ? List.of()
                : reconstruct(previous, source, target);

            return new Route(
                source,
                target,
                distance,
                path,
                algorithm,
                version
            );
        }

        public synchronized Route dijkstra(
            String source,
            String target
        ) {
            validate(source, target);

            if (hasNegativeEdges()) {
                throw new GraphException(
                    "Dijkstra requires nonnegative weights."
                );
            }

            Map<String, Double> distances = new HashMap<>();
            Map<String, String> previous = new HashMap<>();
            Set<String> settled = new HashSet<>();

            adjacency.keySet().forEach(
                vertex -> distances.put(vertex, Double.POSITIVE_INFINITY)
            );

            distances.put(source, 0.0);

            PriorityQueue<QueueEntry> queue =
                new PriorityQueue<>(
                    Comparator.comparingDouble(
                        QueueEntry::distance
                    )
                );

            queue.add(new QueueEntry(source, 0.0));

            while (!queue.isEmpty()) {
                QueueEntry current = queue.poll();

                String vertex = current.vertex();

                if (!settled.add(vertex)) {
                    continue;
                }

                if (vertex.equals(target)) {
                    break;
                }

                for (Edge edge : adjacency.get(vertex)) {
                    if (settled.contains(edge.target())) {
                        continue;
                    }

                    double candidate =
                        current.distance() + edge.weight();

                    if (candidate < distances.get(edge.target())) {
                        distances.put(edge.target(), candidate);
                        previous.put(edge.target(), vertex);

                        queue.add(
                            new QueueEntry(edge.target(), candidate)
                        );
                    }
                }
            }

            return createRoute(
                source,
                target,
                distances,
                previous,
                Algorithm.DIJKSTRA
            );
        }

        public synchronized Route bellmanFord(
            String source,
            String target
        ) {
            validate(source, target);

            Map<String, Double> distances = new HashMap<>();
            Map<String, String> previous = new HashMap<>();

            adjacency.keySet().forEach(
                vertex -> distances.put(vertex, Double.POSITIVE_INFINITY)
            );

            distances.put(source, 0.0);

            int vertexCount = adjacency.size();

            for (int iteration = 0;
                 iteration < vertexCount - 1;
                 iteration++) {

                boolean changed = false;

                for (Edge edge : edges) {
                    double sourceDistance =
                        distances.get(edge.source());

                    if (Double.isInfinite(sourceDistance)) {
                        continue;
                    }

                    double candidate =
                        sourceDistance + edge.weight();

                    if (candidate < distances.get(edge.target())) {
                        distances.put(edge.target(), candidate);
                        previous.put(edge.target(), edge.source());
                        changed = true;
                    }
                }

                if (!changed) {
                    break;
                }
            }

            for (Edge edge : edges) {
                double sourceDistance =
                    distances.get(edge.source());

                if (
                    !Double.isInfinite(sourceDistance)
                    && sourceDistance + edge.weight()
                        < distances.get(edge.target())
                ) {
                    throw new NegativeCycleException(
                        "Reachable negative-weight cycle detected."
                    );
                }
            }

            return createRoute(
                source,
                target,
                distances,
                previous,
                Algorithm.BELLMAN_FORD
            );
        }

        public synchronized Route shortestPath(
            String source,
            String target
        ) {
            return hasNegativeEdges()
                ? bellmanFord(source, target)
                : dijkstra(source, target);
        }

        public synchronized long version() {
            return version;
        }

        public synchronized int vertexCount() {
            return adjacency.size();
        }

        public synchronized int edgeCount() {
            return edges.size();
        }
    }

    interface RoutingPolicy {
        Algorithm choose(WeightedGraph graph);
    }

    static class SafeRoutingPolicy implements RoutingPolicy {
        @Override
        public Algorithm choose(WeightedGraph graph) {
            return graph.hasNegativeEdges()
                ? Algorithm.BELLMAN_FORD
                : Algorithm.DIJKSTRA;
        }
    }

    static class RoutingService {
        private final WeightedGraph graph;
        private final RoutingPolicy policy;

        RoutingService(
            WeightedGraph graph,
            RoutingPolicy policy
        ) {
            this.graph = Objects.requireNonNull(graph);
            this.policy = Objects.requireNonNull(policy);
        }

        public Route calculate(String source, String target) {
            Algorithm selected = policy.choose(graph);

            return switch (selected) {
                case DIJKSTRA -> graph.dijkstra(source, target);
                case BELLMAN_FORD ->
                    graph.bellmanFord(source, target);
            };
        }
    }

    private static WeightedGraph transportNetwork() {
        WeightedGraph graph = new WeightedGraph();

        graph.addEdge("Delhi", "Jaipur", 280, false);
        graph.addEdge("Delhi", "Agra", 230, false);
        graph.addEdge("Jaipur", "Mumbai", 1140, false);
        graph.addEdge("Agra", "Bhopal", 540, false);
        graph.addEdge("Bhopal", "Mumbai", 780, false);
        graph.addEdge("Jaipur", "Agra", 240, false);
        graph.addEdge("Agra", "Jaipur", 250, false);
        graph.addEdge("Delhi", "Chandigarh", 250, false);
        graph.addEdge("Chandigarh", "Jaipur", 480, false);

        return graph;
    }

    private static void display(Route route) {
        System.out.println("Algorithm: " + route.algorithm());

        if (!route.reachable()) {
            System.out.println("Destination unreachable.");
            return;
        }

        System.out.println("Distance: " + route.distance());
        System.out.println(
            "Path: " + String.join(" -> ", route.path())
        );

        System.out.println(
            "Graph version: " + route.graphVersion()
        );
    }

    public static void main(String[] args) {
        WeightedGraph transport = transportNetwork();

        RoutingService service = new RoutingService(
            transport,
            new SafeRoutingPolicy()
        );

        System.out.println("SHORTEST PATH ENTERPRISE ENGINE");
        System.out.println("================================");

        System.out.println("\n1. TRANSPORT NETWORK");

        display(service.calculate("Delhi", "Mumbai"));

        System.out.println("\n2. NEGATIVE EDGE WORKFLOW");

        WeightedGraph negative = new WeightedGraph();

        negative.addEdge("A", "B", 4, false);
        negative.addEdge("A", "C", 5, false);
        negative.addEdge("B", "C", -3, false);
        negative.addEdge("C", "D", 4, false);
        negative.addEdge("B", "D", 8, false);

        RoutingService negativeService = new RoutingService(
            negative,
            new SafeRoutingPolicy()
        );

        display(negativeService.calculate("A", "D"));

        System.out.println("\n3. ALGORITHM POLICY VALIDATION");

        try {
            negative.dijkstra("A", "D");
        } catch (GraphException exception) {
            System.out.println(
                "Rejected: " + exception.getMessage()
            );
        }

        System.out.println("\n4. UNREACHABLE DESTINATION");

        transport.addVertex("Kolkata");

        display(service.calculate("Delhi", "Kolkata"));

        System.out.println("\n5. NEGATIVE CYCLE");

        WeightedGraph cycle = new WeightedGraph();

        cycle.addEdge("A", "B", 2, false);
        cycle.addEdge("B", "C", -4, false);
        cycle.addEdge("C", "B", 1, false);
        cycle.addEdge("A", "D", 5, false);

        try {
            cycle.shortestPath("A", "D");
        } catch (NegativeCycleException exception) {
            System.out.println(
                "Detected: " + exception.getMessage()
            );
        }

        System.out.println("\n6. DOMAIN VALIDATION");

        try {
            service.calculate("Unknown", "Mumbai");
        } catch (GraphException exception) {
            System.out.println(
                "Rejected: " + exception.getMessage()
            );
        }

        System.out.println("\n7. GRAPH METADATA");

        System.out.println("Vertices: " + transport.vertexCount());
        System.out.println("Edges: " + transport.edgeCount());
        System.out.println("Version: " + transport.version());

        System.out.println("\nExecution completed.");
    }
}
