import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Queue;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

public class BreadthFirstSearch {

    public record Edge(String source, String destination) {
        public Edge {
            if (source == null || destination == null
                    || source.isBlank() || destination.isBlank()) {
                throw new IllegalArgumentException(
                    "Edge endpoints must be non-empty."
                );
            }
        }
    }

    public record PathResult(
        List<String> vertices,
        int distance
    ) {
        public PathResult {
            vertices = List.copyOf(vertices);

            if (distance < 0) {
                throw new IllegalArgumentException(
                    "Distance cannot be negative."
                );
            }
        }
    }

    public record GraphStatistics(
        int vertexCount,
        int edgeCount,
        int componentCount
    ) {}

    public static final class GraphException
            extends RuntimeException {
        public GraphException(String message) {
            super(message);
        }
    }

    public static final class Graph {

        private final Map<String, Set<String>> adjacency =
            new TreeMap<>();

        public synchronized void addVertex(String vertex) {
            validateName(vertex);
            adjacency.computeIfAbsent(
                vertex,
                key -> new TreeSet<>()
            );
        }

        public synchronized void addEdge(
                String source,
                String destination
        ) {
            addVertex(source);
            addVertex(destination);

            adjacency.get(source).add(destination);
            adjacency.get(destination).add(source);
        }

        public synchronized void removeEdge(
                String source,
                String destination
        ) {
            requireVertex(source);
            requireVertex(destination);

            adjacency.get(source).remove(destination);
            adjacency.get(destination).remove(source);
        }

        public synchronized void removeVertex(String vertex) {
            requireVertex(vertex);

            for (String neighbor : adjacency.get(vertex)) {
                adjacency.get(neighbor).remove(vertex);
            }

            adjacency.remove(vertex);
        }

        private void validateName(String vertex) {
            if (vertex == null || vertex.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex must be a non-empty string."
                );
            }
        }

        private void requireVertex(String vertex) {
            if (!adjacency.containsKey(vertex)) {
                throw new GraphException(
                    "Unknown vertex: " + vertex
                );
            }
        }

        /*
         * Creates an immutable snapshot so a traversal operates
         * against one consistent graph state.
         */
        private Map<String, List<String>> snapshot() {
            Map<String, List<String>> copy = new TreeMap<>();

            for (var entry : adjacency.entrySet()) {
                copy.put(
                    entry.getKey(),
                    List.copyOf(entry.getValue())
                );
            }

            return Collections.unmodifiableMap(copy);
        }

        public List<String> bfs(String start) {
            Map<String, List<String>> graph = snapshot();

            if (!graph.containsKey(start)) {
                throw new GraphException(
                    "Unknown starting vertex: " + start
                );
            }

            Set<String> visited = new HashSet<>();
            Queue<String> queue = new ArrayDeque<>();
            List<String> traversal = new ArrayList<>();

            visited.add(start);
            queue.offer(start);

            while (!queue.isEmpty()) {
                String current = queue.poll();
                traversal.add(current);

                for (String neighbor : graph.get(current)) {
                    if (visited.add(neighbor)) {
                        queue.offer(neighbor);
                    }
                }
            }

            return List.copyOf(traversal);
        }

        public Map<String, Integer> distancesFrom(String start) {
            Map<String, List<String>> graph = snapshot();

            if (!graph.containsKey(start)) {
                throw new GraphException(
                    "Unknown starting vertex: " + start
                );
            }

            Map<String, Integer> distances = new LinkedHashMap<>();
            Queue<String> queue = new ArrayDeque<>();

            distances.put(start, 0);
            queue.offer(start);

            while (!queue.isEmpty()) {
                String current = queue.poll();

                for (String neighbor : graph.get(current)) {
                    if (!distances.containsKey(neighbor)) {
                        distances.put(
                            neighbor,
                            distances.get(current) + 1
                        );

                        queue.offer(neighbor);
                    }
                }
            }

            return Collections.unmodifiableMap(distances);
        }

        public PathResult shortestPath(
                String start,
                String target
        ) {
            Map<String, List<String>> graph = snapshot();

            if (!graph.containsKey(start)
                    || !graph.containsKey(target)) {
                throw new GraphException(
                    "Source or destination does not exist."
                );
            }

            if (start.equals(target)) {
                return new PathResult(List.of(start), 0);
            }

            Map<String, String> parent = new HashMap<>();
            Map<String, Integer> distances = new HashMap<>();

            Queue<String> queue = new ArrayDeque<>();

            parent.put(start, null);
            distances.put(start, 0);
            queue.offer(start);

            boolean found = false;

            while (!queue.isEmpty() && !found) {
                String current = queue.poll();

                for (String neighbor : graph.get(current)) {
                    if (parent.containsKey(neighbor)) {
                        continue;
                    }

                    parent.put(neighbor, current);

                    distances.put(
                        neighbor,
                        distances.get(current) + 1
                    );

                    if (neighbor.equals(target)) {
                        found = true;
                        break;
                    }

                    queue.offer(neighbor);
                }
            }

            if (!found) {
                return null;
            }

            List<String> path = new ArrayList<>();
            String current = target;

            while (current != null) {
                path.add(current);
                current = parent.get(current);
            }

            Collections.reverse(path);

            return new PathResult(
                path,
                distances.get(target)
            );
        }

        public List<List<String>> connectedComponents() {
            Map<String, List<String>> graph = snapshot();

            Set<String> visited = new HashSet<>();
            List<List<String>> components = new ArrayList<>();

            for (String vertex : graph.keySet()) {
                if (!visited.add(vertex)) {
                    continue;
                }

                List<String> component = new ArrayList<>();
                Queue<String> queue = new ArrayDeque<>();

                queue.offer(vertex);

                while (!queue.isEmpty()) {
                    String current = queue.poll();
                    component.add(current);

                    for (String neighbor : graph.get(current)) {
                        if (visited.add(neighbor)) {
                            queue.offer(neighbor);
                        }
                    }
                }

                components.add(List.copyOf(component));
            }

            return List.copyOf(components);
        }

        public GraphStatistics statistics() {
            int vertices = adjacency.size();

            int directedEntries = adjacency.values()
                .stream()
                .mapToInt(Set::size)
                .sum();

            return new GraphStatistics(
                vertices,
                directedEntries / 2,
                connectedComponents().size()
            );
        }

        public synchronized void display() {
            adjacency.forEach((vertex, neighbors) ->
                System.out.println(vertex + ": " + neighbors)
            );
        }
    }

    public static final class GraphService {

        private final Graph graph;

        public GraphService(Graph graph) {
            this.graph = Objects.requireNonNull(graph);
        }

        public void processRoute(String source, String destination) {
            PathResult result =
                graph.shortestPath(source, destination);

            if (result == null) {
                System.out.println(
                    "No route exists between "
                    + source + " and " + destination
                );
                return;
            }

            System.out.println(
                "Route: " + String.join(" -> ", result.vertices())
            );

            System.out.println(
                "Minimum number of edges: " + result.distance()
            );
        }

        public void printComponentReport() {
            List<List<String>> components =
                graph.connectedComponents();

            System.out.println(
                "Connected component count: " + components.size()
            );

            for (int i = 0; i < components.size(); i++) {
                System.out.println(
                    "Component " + (i + 1) + ": " + components.get(i)
                );
            }
        }
    }

    private static Graph createSampleGraph() {
        Graph graph = new Graph();

        List<Edge> edges = List.of(
            new Edge("A", "B"),
            new Edge("A", "C"),
            new Edge("B", "D"),
            new Edge("B", "E"),
            new Edge("C", "F"),
            new Edge("E", "F"),
            new Edge("G", "H")
        );

        for (Edge edge : edges) {
            graph.addEdge(
                edge.source(),
                edge.destination()
            );
        }

        graph.addVertex("I");

        return graph;
    }

    private static void runTests() {
        Graph graph = createSampleGraph();

        assert graph.bfs("A").equals(
            List.of("A", "B", "C", "D", "E", "F")
        );

        assert graph.distancesFrom("A").get("F") == 2;

        PathResult result = graph.shortestPath("A", "F");

        assert result != null;
        assert result.distance() == 2;
        assert result.vertices().equals(
            List.of("A", "C", "F")
        );

        assert graph.shortestPath("A", "H") == null;

        assert graph.shortestPath("A", "A")
            .vertices().equals(List.of("A"));

        assert graph.connectedComponents().size() == 3;

        assert graph.statistics().vertexCount() == 9;
        assert graph.statistics().edgeCount() == 7;

        System.out.println("All Java tests passed.");
    }

    public static void main(String[] args) {
        try {
            Graph graph = createSampleGraph();
            GraphService service = new GraphService(graph);

            System.out.println("BREADTH-FIRST SEARCH");
            System.out.println("====================");

            System.out.println("\n1. Repository-style graph inventory");
            graph.display();

            System.out.println("\n2. BFS traversal from A");
            System.out.println(graph.bfs("A"));

            System.out.println("\n3. Distance report");
            graph.distancesFrom("A").forEach(
                (vertex, distance) ->
                    System.out.println(vertex + ": " + distance)
            );

            System.out.println("\n4. Shortest route");
            service.processRoute("A", "F");

            System.out.println("\n5. Unreachable route");
            service.processRoute("A", "H");

            System.out.println("\n6. Connected components");
            service.printComponentReport();

            System.out.println("\n7. Graph statistics");
            System.out.println(graph.statistics());

            System.out.println("\n8. Removing an edge");
            graph.removeEdge("A", "B");
            System.out.println(graph.bfs("A"));

            System.out.println("\n9. Validation");
            try {
                graph.bfs("UNKNOWN");
            } catch (GraphException exception) {
                System.out.println(
                    "Expected error: " + exception.getMessage()
                );
            }

            System.out.println("\n10. Automated tests");
            runTests();

        } catch (RuntimeException exception) {
            System.err.println(
                "Application failure: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
