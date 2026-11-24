import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

/*
 * Enterprise Transport Network Routing
 *
 * Java version: 17
 * Dependencies: Standard Java library only
 */

public class DijkstraEnterprise {

    enum NetworkType {
        DIRECTED,
        UNDIRECTED
    }

    record Edge(String destination, long weight) {
        Edge {
            if (destination == null || destination.isBlank()) {
                throw new IllegalArgumentException(
                    "Destination cannot be empty"
                );
            }

            if (weight < 0) {
                throw new IllegalArgumentException(
                    "Negative weights are not supported"
                );
            }
        }
    }

    record QueueEntry(String vertex, long distance) {
    }

    record Route(
        String source,
        String destination,
        long distance,
        List<String> path,
        boolean reachable
    ) {
        Route {
            path = List.copyOf(path);
        }
    }

    static class RoutingException extends RuntimeException {
        RoutingException(String message) {
            super(message);
        }
    }

    static class WeightedGraph {

        private final Map<String, List<Edge>> adjacency =
            new HashMap<>();

        private long version = 0;

        public synchronized void addVertex(String vertex) {
            validateVertex(vertex);

            if (!adjacency.containsKey(vertex)) {
                adjacency.put(vertex, new ArrayList<>());
                version++;
            }
        }

        public synchronized void addEdge(
            String source,
            String destination,
            long weight,
            NetworkType type
        ) {
            validateVertex(source);
            validateVertex(destination);

            if (weight < 0) {
                throw new IllegalArgumentException(
                    "Dijkstra requires non-negative weights"
                );
            }

            if (type == null) {
                throw new IllegalArgumentException(
                    "Network type is required"
                );
            }

            addVertex(source);
            addVertex(destination);

            adjacency.get(source).add(
                new Edge(destination, weight)
            );

            if (type == NetworkType.UNDIRECTED) {
                adjacency.get(destination).add(
                    new Edge(source, weight)
                );
            }

            version++;
        }

        private void validateVertex(String vertex) {
            if (vertex == null || vertex.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex must be a non-empty string"
                );
            }
        }

        public synchronized Set<String> vertices() {
            return Set.copyOf(adjacency.keySet());
        }

        public synchronized Map<String, List<Edge>> snapshot() {
            Map<String, List<Edge>> copy = new HashMap<>();

            adjacency.forEach(
                (vertex, edges) ->
                    copy.put(vertex, List.copyOf(edges))
            );

            return Collections.unmodifiableMap(copy);
        }

        public synchronized long version() {
            return version;
        }
    }

    static class ShortestPathResult {

        private final String source;
        private final Map<String, Long> distances;
        private final Map<String, String> predecessors;
        private final Set<String> settled;

        ShortestPathResult(
            String source,
            Map<String, Long> distances,
            Map<String, String> predecessors,
            Set<String> settled
        ) {
            this.source = source;
            this.distances = Map.copyOf(distances);
            this.predecessors = Collections.unmodifiableMap(
                new HashMap<>(predecessors)
            );
            this.settled = Set.copyOf(settled);
        }

        public long distanceTo(String destination) {
            Long distance = distances.get(destination);

            if (distance == null) {
                throw new RoutingException(
                    "Unknown destination: " + destination
                );
            }

            return distance;
        }

        public List<String> pathTo(String destination) {
            long distance = distanceTo(destination);

            if (distance == Long.MAX_VALUE) {
                return List.of();
            }

            List<String> path = new ArrayList<>();
            Set<String> visited = new HashSet<>();

            String current = destination;

            while (current != null) {
                if (!visited.add(current)) {
                    throw new RoutingException(
                        "Cycle in predecessor chain"
                    );
                }

                path.add(current);

                if (current.equals(source)) {
                    break;
                }

                current = predecessors.get(current);
            }

            Collections.reverse(path);

            if (path.isEmpty() || !path.get(0).equals(source)) {
                throw new RoutingException(
                    "Invalid predecessor chain"
                );
            }

            return List.copyOf(path);
        }

        public Map<String, Long> allDistances() {
            return distances;
        }

        public Set<String> settledVertices() {
            return settled;
        }
    }

    static class ShortestPathService {

        private final WeightedGraph graph;

        ShortestPathService(WeightedGraph graph) {
            this.graph = graph;
        }

        public ShortestPathResult calculate(String source) {
            Map<String, List<Edge>> adjacency = graph.snapshot();

            if (!adjacency.containsKey(source)) {
                throw new RoutingException(
                    "Unknown source: " + source
                );
            }

            Map<String, Long> distances = new HashMap<>();
            Map<String, String> predecessors = new HashMap<>();
            Set<String> settled = new HashSet<>();

            for (String vertex : adjacency.keySet()) {
                distances.put(vertex, Long.MAX_VALUE);
                predecessors.put(vertex, null);
            }

            distances.put(source, 0L);

            PriorityQueue<QueueEntry> queue =
                new PriorityQueue<>(
                    Comparator.comparingLong(QueueEntry::distance)
                        .thenComparing(QueueEntry::vertex)
                );

            queue.add(new QueueEntry(source, 0L));

            while (!queue.isEmpty()) {
                QueueEntry current = queue.poll();

                String vertex = current.vertex();
                long currentDistance = current.distance();

                // Ignore stale priority queue entries.
                if (currentDistance != distances.get(vertex)) {
                    continue;
                }

                if (!settled.add(vertex)) {
                    continue;
                }

                for (Edge edge : adjacency.get(vertex)) {
                    String neighbor = edge.destination();

                    if (settled.contains(neighbor)) {
                        continue;
                    }

                    // Protect long arithmetic from overflow.
                    if (currentDistance >
                        Long.MAX_VALUE - edge.weight()) {
                        throw new ArithmeticException(
                            "Shortest-path distance overflow"
                        );
                    }

                    long candidate =
                        currentDistance + edge.weight();

                    if (candidate < distances.get(neighbor)) {
                        distances.put(neighbor, candidate);
                        predecessors.put(neighbor, vertex);

                        queue.add(
                            new QueueEntry(neighbor, candidate)
                        );
                    }
                }
            }

            return new ShortestPathResult(
                source,
                distances,
                predecessors,
                settled
            );
        }

        public Route route(String source, String destination) {
            ShortestPathResult result = calculate(source);

            long distance = result.distanceTo(destination);

            if (distance == Long.MAX_VALUE) {
                return new Route(
                    source,
                    destination,
                    distance,
                    List.of(),
                    false
                );
            }

            return new Route(
                source,
                destination,
                distance,
                result.pathTo(destination),
                true
            );
        }
    }

    static WeightedGraph createTransportNetwork() {
        WeightedGraph graph = new WeightedGraph();

        graph.addEdge("Delhi", "Agra", 230, NetworkType.UNDIRECTED);
        graph.addEdge("Delhi", "Jaipur", 280, NetworkType.UNDIRECTED);
        graph.addEdge("Delhi", "Lucknow", 550, NetworkType.UNDIRECTED);
        graph.addEdge("Agra", "Lucknow", 330, NetworkType.UNDIRECTED);
        graph.addEdge("Agra", "Jaipur", 240, NetworkType.UNDIRECTED);
        graph.addEdge("Jaipur", "Ahmedabad", 660, NetworkType.UNDIRECTED);
        graph.addEdge("Lucknow", "Varanasi", 320, NetworkType.UNDIRECTED);
        graph.addEdge("Lucknow", "Patna", 540, NetworkType.UNDIRECTED);
        graph.addEdge("Varanasi", "Patna", 250, NetworkType.UNDIRECTED);
        graph.addEdge("Patna", "Kolkata", 580, NetworkType.UNDIRECTED);
        graph.addEdge("Ahmedabad", "Mumbai", 530, NetworkType.UNDIRECTED);
        graph.addEdge("Mumbai", "Pune", 150, NetworkType.UNDIRECTED);
        graph.addEdge("Kolkata", "Mumbai", 1900, NetworkType.UNDIRECTED);

        graph.addVertex("Chennai");

        return graph;
    }

    static void runTests() {
        WeightedGraph graph = new WeightedGraph();

        graph.addEdge("A", "B", 4, NetworkType.DIRECTED);
        graph.addEdge("A", "C", 1, NetworkType.DIRECTED);
        graph.addEdge("C", "B", 2, NetworkType.DIRECTED);
        graph.addEdge("B", "D", 1, NetworkType.DIRECTED);
        graph.addEdge("C", "D", 5, NetworkType.DIRECTED);
        graph.addVertex("ISOLATED");

        ShortestPathService service =
            new ShortestPathService(graph);

        ShortestPathResult result = service.calculate("A");

        if (result.distanceTo("B") != 3 ||
            result.distanceTo("D") != 4) {
            throw new AssertionError("Distance test failed");
        }

        if (!result.pathTo("D").equals(
            List.of("A", "C", "B", "D"))) {
            throw new AssertionError("Path test failed");
        }

        if (!result.pathTo("ISOLATED").isEmpty()) {
            throw new AssertionError("Unreachable test failed");
        }

        WeightedGraph zeroGraph = new WeightedGraph();
        zeroGraph.addEdge(
            "X", "Y", 0, NetworkType.DIRECTED
        );

        if (new ShortestPathService(zeroGraph)
            .calculate("X").distanceTo("Y") != 0) {
            throw new AssertionError("Zero-weight test failed");
        }

        boolean negativeRejected = false;

        try {
            graph.addEdge(
                "A", "Z", -5, NetworkType.DIRECTED
            );
        } catch (IllegalArgumentException exception) {
            negativeRejected = true;
        }

        if (!negativeRejected) {
            throw new AssertionError("Negative weight accepted");
        }

        boolean unknownRejected = false;

        try {
            service.calculate("UNKNOWN");
        } catch (RoutingException exception) {
            unknownRejected = true;
        }

        if (!unknownRejected) {
            throw new AssertionError("Unknown source accepted");
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            runTests();

            WeightedGraph graph = createTransportNetwork();

            ShortestPathService service =
                new ShortestPathService(graph);

            ShortestPathResult result =
                service.calculate("Delhi");

            System.out.println(
                "\nEnterprise Transport Routing"
            );

            System.out.printf(
                "%-16s %-16s %s%n",
                "Destination",
                "Distance",
                "Route"
            );

            result.allDistances().entrySet()
                .stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> {
                    String destination = entry.getKey();
                    long distance = entry.getValue();

                    if (distance == Long.MAX_VALUE) {
                        System.out.printf(
                            "%-16s %-16s %s%n",
                            destination,
                            "Unreachable",
                            "-"
                        );
                    } else {
                        System.out.printf(
                            "%-16s %-16d %s%n",
                            destination,
                            distance,
                            String.join(
                                " -> ",
                                result.pathTo(destination)
                            )
                        );
                    }
                });

            Route route = service.route(
                "Delhi",
                "Mumbai"
            );

            System.out.println("\nSpecific route");

            if (route.reachable()) {
                System.out.println(
                    String.join(" -> ", route.path())
                );

                System.out.println(
                    "Distance: " + route.distance() + " km"
                );
            } else {
                System.out.println("No route available");
            }

            System.out.println("\nPerformance");
            System.out.println("Time: O((V + E) log V)");
            System.out.println("Space: O(V + E)");
            System.out.println("Priority queue: Binary min-heap");
            System.out.println("Graph snapshot: Immutable calculation input");
            System.out.println("Weights: Non-negative long integers");

        } catch (Exception exception) {
            System.err.println(
                "Routing error: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
