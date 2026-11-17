import java.util.*;
import java.util.stream.Collectors;

/**
 * Graph Introduction
 *
 * Enterprise-oriented graph model with:
 * - Directed and undirected graphs.
 * - Weighted and unweighted edges.
 * - Immutable edge records.
 * - Adjacency-list and adjacency-matrix representations.
 * - Breadth-first and depth-first traversal.
 * - Dijkstra shortest paths.
 * - Cycle detection.
 * - Connected components.
 * - Domain validation and service-level operations.
 */
public class GraphIntroduction {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    enum Representation {
        ADJACENCY_LIST,
        ADJACENCY_MATRIX
    }

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class VertexNotFoundException extends GraphException {
        VertexNotFoundException(String vertex) {
            super("Unknown vertex: " + vertex);
        }
    }

    static class NegativeWeightException extends GraphException {
        NegativeWeightException() {
            super("Dijkstra requires non-negative edge weights.");
        }
    }

    record Edge(
        String source,
        String destination,
        double weight
    ) {
        Edge {
            if (
                source == null || source.isBlank() ||
                destination == null || destination.isBlank()
            ) {
                throw new IllegalArgumentException(
                    "Edge endpoints cannot be empty."
                );
            }

            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Edge weight must be finite."
                );
            }
        }
    }

    record GraphSnapshot(
        GraphType type,
        boolean weighted,
        Set<String> vertices,
        List<Edge> edges
    ) {}

    record MatrixRepresentation(
        List<String> vertices,
        List<List<Double>> matrix
    ) {}

    /**
     * Graph domain object.
     *
     * All modifications are synchronized so that individual
     * graph operations do not interleave unexpectedly.
     */
    static class Graph {

        private final GraphType type;
        private final boolean weighted;

        private final Map<String, Map<String, Double>> adjacency =
            new TreeMap<>();

        private long version = 0;

        Graph(GraphType type, boolean weighted) {
            this.type = Objects.requireNonNull(type);
            this.weighted = weighted;
        }

        private void validateVertex(String vertex) {
            if (vertex == null || vertex.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex must be non-empty."
                );
            }
        }

        private void requireVertex(String vertex) {
            if (!adjacency.containsKey(vertex)) {
                throw new VertexNotFoundException(vertex);
            }
        }

        public synchronized boolean addVertex(String vertex) {
            validateVertex(vertex);

            if (adjacency.containsKey(vertex)) {
                return false;
            }

            adjacency.put(vertex, new TreeMap<>());
            version++;

            return true;
        }

        public synchronized void addEdge(
            String source,
            String destination,
            double weight
        ) {
            validateVertex(source);
            validateVertex(destination);

            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Weight must be finite."
                );
            }

            if (!weighted && weight != 1.0) {
                throw new IllegalArgumentException(
                    "Unweighted graph only accepts weight 1."
                );
            }

            addVertex(source);
            addVertex(destination);

            adjacency.get(source).put(destination, weight);

            if (type == GraphType.UNDIRECTED) {
                adjacency.get(destination).put(source, weight);
            }

            version++;
        }

        public synchronized void removeEdge(
            String source,
            String destination
        ) {
            requireVertex(source);
            requireVertex(destination);

            adjacency.get(source).remove(destination);

            if (type == GraphType.UNDIRECTED) {
                adjacency.get(destination).remove(source);
            }

            version++;
        }

        public synchronized void removeVertex(String vertex) {
            requireVertex(vertex);

            adjacency.remove(vertex);

            adjacency.values().forEach(
                neighbors -> neighbors.remove(vertex)
            );

            version++;
        }

        public synchronized int vertexCount() {
            return adjacency.size();
        }

        public synchronized int edgeCount() {
            int count = adjacency.values()
                .stream()
                .mapToInt(Map::size)
                .sum();

            return type == GraphType.UNDIRECTED
                ? count / 2
                : count;
        }

        public synchronized long version() {
            return version;
        }

        public synchronized List<String> vertices() {
            return List.copyOf(adjacency.keySet());
        }

        public synchronized List<Edge> edges() {
            List<Edge> result = new ArrayList<>();

            for (var source : adjacency.entrySet()) {
                for (var destination : source.getValue().entrySet()) {

                    if (
                        type == GraphType.UNDIRECTED &&
                        source.getKey().compareTo(
                            destination.getKey()
                        ) > 0
                    ) {
                        continue;
                    }

                    result.add(new Edge(
                        source.getKey(),
                        destination.getKey(),
                        destination.getValue()
                    ));
                }
            }

            return List.copyOf(result);
        }

        public synchronized Map<String, Map<String, Double>>
        adjacencyList() {
            Map<String, Map<String, Double>> result =
                new LinkedHashMap<>();

            adjacency.forEach((vertex, neighbors) ->
                result.put(
                    vertex,
                    Collections.unmodifiableMap(
                        new TreeMap<>(neighbors)
                    )
                )
            );

            return Collections.unmodifiableMap(result);
        }

        public synchronized MatrixRepresentation
        adjacencyMatrix() {
            List<String> nodes = vertices();

            Map<String, Integer> index = new HashMap<>();

            for (int i = 0; i < nodes.size(); i++) {
                index.put(nodes.get(i), i);
            }

            List<List<Double>> matrix = new ArrayList<>();

            for (int i = 0; i < nodes.size(); i++) {
                List<Double> row = new ArrayList<>(
                    Collections.nCopies(nodes.size(), null)
                );

                matrix.add(row);
            }

            for (var source : adjacency.entrySet()) {
                for (var destination : source.getValue().entrySet()) {
                    matrix.get(index.get(source.getKey()))
                        .set(
                            index.get(destination.getKey()),
                            destination.getValue()
                        );
                }
            }

            List<List<Double>> immutableMatrix = matrix.stream()
                .map(List::copyOf)
                .collect(Collectors.toList());

            // List.copyOf rejects null values, so use unmodifiable
            // wrappers for rows containing absent-edge markers.
            immutableMatrix = matrix.stream()
                .map(row -> Collections.unmodifiableList(
                    new ArrayList<>(row)
                ))
                .toList();

            return new MatrixRepresentation(
                nodes,
                Collections.unmodifiableList(immutableMatrix)
            );
        }

        public synchronized int inDegree(String vertex) {
            requireVertex(vertex);

            return (int) adjacency.values()
                .stream()
                .filter(neighbors -> neighbors.containsKey(vertex))
                .count();
        }

        public synchronized int outDegree(String vertex) {
            requireVertex(vertex);
            return adjacency.get(vertex).size();
        }

        public synchronized List<String> bfs(String start) {
            requireVertex(start);

            Queue<String> queue = new ArrayDeque<>();
            Set<String> visited = new HashSet<>();
            List<String> result = new ArrayList<>();

            queue.add(start);
            visited.add(start);

            while (!queue.isEmpty()) {
                String current = queue.remove();
                result.add(current);

                for (
                    String neighbor :
                    adjacency.get(current).keySet()
                ) {
                    if (visited.add(neighbor)) {
                        queue.add(neighbor);
                    }
                }
            }

            return List.copyOf(result);
        }

        public synchronized List<String> dfs(String start) {
            requireVertex(start);

            Deque<String> stack = new ArrayDeque<>();
            Set<String> visited = new HashSet<>();
            List<String> result = new ArrayList<>();

            stack.push(start);

            while (!stack.isEmpty()) {
                String current = stack.pop();

                if (!visited.add(current)) {
                    continue;
                }

                result.add(current);

                List<String> neighbors = new ArrayList<>(
                    adjacency.get(current).keySet()
                );

                Collections.reverse(neighbors);

                for (String neighbor : neighbors) {
                    if (!visited.contains(neighbor)) {
                        stack.push(neighbor);
                    }
                }
            }

            return List.copyOf(result);
        }

        public synchronized Map<String, Double> dijkstra(
            String start
        ) {
            requireVertex(start);

            for (Edge edge : edges()) {
                if (edge.weight() < 0) {
                    throw new NegativeWeightException();
                }
            }

            Map<String, Double> distances = new TreeMap<>();

            for (String vertex : vertices()) {
                distances.put(vertex, Double.POSITIVE_INFINITY);
            }

            distances.put(start, 0.0);

            record State(String vertex, double distance) {}

            PriorityQueue<State> queue = new PriorityQueue<>(
                Comparator.comparingDouble(State::distance)
            );

            queue.add(new State(start, 0.0));

            while (!queue.isEmpty()) {
                State current = queue.poll();

                if (
                    current.distance() !=
                    distances.get(current.vertex())
                ) {
                    continue;
                }

                for (
                    var neighbor :
                    adjacency.get(current.vertex()).entrySet()
                ) {
                    double candidate =
                        current.distance() + neighbor.getValue();

                    if (candidate < distances.get(neighbor.getKey())) {
                        distances.put(neighbor.getKey(), candidate);

                        queue.add(new State(
                            neighbor.getKey(),
                            candidate
                        ));
                    }
                }
            }

            return Collections.unmodifiableMap(distances);
        }

        public synchronized boolean hasCycle() {
            Set<String> visited = new HashSet<>();

            if (type == GraphType.DIRECTED) {
                Set<String> active = new HashSet<>();

                for (String vertex : vertices()) {
                    if (
                        !visited.contains(vertex) &&
                        directedCycle(vertex, visited, active)
                    ) {
                        return true;
                    }
                }

                return false;
            }

            for (String vertex : vertices()) {
                if (
                    !visited.contains(vertex) &&
                    undirectedCycle(vertex, null, visited)
                ) {
                    return true;
                }
            }

            return false;
        }

        private boolean directedCycle(
            String vertex,
            Set<String> visited,
            Set<String> active
        ) {
            visited.add(vertex);
            active.add(vertex);

            for (String neighbor : adjacency.get(vertex).keySet()) {
                if (!visited.contains(neighbor)) {
                    if (directedCycle(neighbor, visited, active)) {
                        return true;
                    }
                } else if (active.contains(neighbor)) {
                    return true;
                }
            }

            active.remove(vertex);
            return false;
        }

        private boolean undirectedCycle(
            String vertex,
            String parent,
            Set<String> visited
        ) {
            visited.add(vertex);

            for (String neighbor : adjacency.get(vertex).keySet()) {
                if (!visited.contains(neighbor)) {
                    if (undirectedCycle(neighbor, vertex, visited)) {
                        return true;
                    }
                } else if (!neighbor.equals(parent)) {
                    return true;
                }
            }

            return false;
        }

        public synchronized List<List<String>>
        connectedComponents() {
            if (type != GraphType.UNDIRECTED) {
                throw new GraphException(
                    "Connected components require an undirected graph."
                );
            }

            Set<String> visited = new HashSet<>();
            List<List<String>> components = new ArrayList<>();

            for (String vertex : vertices()) {
                if (!visited.contains(vertex)) {
                    List<String> component = bfs(vertex);
                    visited.addAll(component);
                    components.add(component);
                }
            }

            return List.copyOf(components);
        }

        public synchronized GraphSnapshot snapshot() {
            return new GraphSnapshot(
                type,
                weighted,
                Collections.unmodifiableSet(
                    new LinkedHashSet<>(vertices())
                ),
                edges()
            );
        }
    }

    /**
     * Service layer separates graph operations from presentation.
     */
    static class GraphService {

        public Map<String, Double> calculateShortestPaths(
            Graph graph,
            String source
        ) {
            Objects.requireNonNull(graph);
            return graph.dijkstra(source);
        }

        public void printReport(Graph graph) {
            GraphSnapshot snapshot = graph.snapshot();

            System.out.println("Graph type: " + snapshot.type());
            System.out.println("Weighted: " + snapshot.weighted());
            System.out.println("Vertices: " + snapshot.vertices());
            System.out.println("Edges: " + snapshot.edges());
            System.out.println("Vertex count: " +
                snapshot.vertices().size());
            System.out.println("Edge count: " +
                snapshot.edges().size());
            System.out.println("Version: " + graph.version());
        }
    }

    public static void main(String[] args) {

        GraphService service = new GraphService();

        System.out.println("GRAPH INTRODUCTION");
        System.out.println("==============================");

        // Scenario 1: Enterprise transport network.
        Graph transport = new Graph(
            GraphType.UNDIRECTED,
            true
        );

        transport.addEdge("Delhi", "Agra", 230);
        transport.addEdge("Delhi", "Jaipur", 280);
        transport.addEdge("Agra", "Lucknow", 335);
        transport.addEdge("Agra", "Jaipur", 240);
        transport.addEdge("Lucknow", "Kanpur", 80);

        System.out.println("\n1. TRANSPORT GRAPH");
        service.printReport(transport);

        System.out.println("\n2. ADJACENCY LIST");
        System.out.println(transport.adjacencyList());

        System.out.println("\n3. ADJACENCY MATRIX");

        MatrixRepresentation matrix =
            transport.adjacencyMatrix();

        System.out.println("Vertex order: " + matrix.vertices());

        matrix.matrix().forEach(System.out::println);

        System.out.println("\n4. GRAPH TRAVERSAL");

        System.out.println("BFS: " + transport.bfs("Delhi"));
        System.out.println("DFS: " + transport.dfs("Delhi"));

        System.out.println("\n5. SHORTEST DISTANCES");

        service.calculateShortestPaths(
            transport,
            "Delhi"
        ).forEach((vertex, distance) ->
            System.out.println(vertex + " = " + distance)
        );

        System.out.println("\n6. DIRECTED DEPENDENCY GRAPH");

        Graph workflow = new Graph(
            GraphType.DIRECTED,
            false
        );

        workflow.addEdge("Analysis", "Design", 1);
        workflow.addEdge("Design", "Development", 1);
        workflow.addEdge("Development", "Testing", 1);
        workflow.addEdge("Testing", "Release", 1);

        System.out.println("BFS: " + workflow.bfs("Analysis"));
        System.out.println(
            "In-degree of Release: " +
            workflow.inDegree("Release")
        );

        System.out.println("\n7. CONNECTED COMPONENTS");

        Graph disconnected = new Graph(
            GraphType.UNDIRECTED,
            false
        );

        disconnected.addEdge("A", "B", 1);
        disconnected.addEdge("B", "C", 1);
        disconnected.addEdge("D", "E", 1);
        disconnected.addVertex("F");

        System.out.println(disconnected.connectedComponents());

        System.out.println("\n8. CYCLE DETECTION");

        Graph cyclic = new Graph(
            GraphType.DIRECTED,
            false
        );

        cyclic.addEdge("P", "Q", 1);
        cyclic.addEdge("Q", "R", 1);
        cyclic.addEdge("R", "P", 1);

        System.out.println(
            "Directed cycle: " + cyclic.hasCycle()
        );

        System.out.println("\n9. GRAPH MODIFICATION");

        transport.removeEdge("Delhi", "Jaipur");
        transport.removeVertex("Kanpur");

        service.printReport(transport);

        System.out.println("\n10. FAILURE HANDLING");

        try {
            transport.bfs("Unknown");
        } catch (GraphException error) {
            System.out.println(error.getMessage());
        }

        try {
            Graph negative = new Graph(
                GraphType.DIRECTED,
                true
            );

            negative.addEdge("X", "Y", -10);

            negative.dijkstra("X");
        } catch (NegativeWeightException error) {
            System.out.println(error.getMessage());
        }

        try {
            workflow.connectedComponents();
        } catch (GraphException error) {
            System.out.println(error.getMessage());
        }

        System.out.println("\n11. VALIDATION");

        if (
            transport.vertexCount() != 4 ||
            transport.edgeCount() != 3
        ) {
            throw new IllegalStateException(
                "Graph integrity verification failed."
            );
        }

        if (workflow.bfs("Analysis").size() != 5) {
            throw new IllegalStateException(
                "Traversal verification failed."
            );
        }

        System.out.println("All graph tests passed.");
    }
}
