import java.time.Duration;
import java.time.Instant;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Consumer;

public class Main {

    enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    enum VertexState {
        UNVISITED,
        ACTIVE,
        FINISHED
    }

    record Edge(int source, int destination) {}

    record VisitEvent(int vertex, int depth, int discoveryTime) {}

    record TraversalResult(
        List<Integer> order,
        Map<Integer, Integer> parent,
        Map<Integer, Integer> depth,
        Map<Integer, Integer> discovery,
        Map<Integer, Integer> finish
    ) {
        TraversalResult {
            order = List.copyOf(order);
            parent = Map.copyOf(parent);
            depth = Map.copyOf(depth);
            discovery = Map.copyOf(discovery);
            finish = Map.copyOf(finish);
        }
    }

    static class GraphException extends RuntimeException {
        GraphException(String message) {
            super(message);
        }
    }

    static class CycleDetectedException extends GraphException {
        CycleDetectedException(String message) {
            super(message);
        }
    }

    static final class Graph {
        private final GraphType type;

        private final Map<Integer, LinkedHashSet<Integer>> adjacency =
            new LinkedHashMap<>();

        Graph(GraphType type) {
            this.type = Objects.requireNonNull(type);
        }

        void addVertex(int vertex) {
            adjacency.computeIfAbsent(
                vertex,
                ignored -> new LinkedHashSet<>()
            );
        }

        void addEdge(int source, int destination) {
            addVertex(source);
            addVertex(destination);

            adjacency.get(source).add(destination);

            if (type == GraphType.UNDIRECTED) {
                adjacency.get(destination).add(source);
            }
        }

        boolean contains(int vertex) {
            return adjacency.containsKey(vertex);
        }

        List<Integer> neighbors(int vertex) {
            if (!contains(vertex)) {
                throw new GraphException(
                    "Unknown vertex: " + vertex
                );
            }

            return List.copyOf(adjacency.get(vertex));
        }

        Set<Integer> vertices() {
            return Collections.unmodifiableSet(adjacency.keySet());
        }

        GraphType type() {
            return type;
        }

        void validate() {
            for (var entry : adjacency.entrySet()) {
                int vertex = entry.getKey();

                for (int neighbor : entry.getValue()) {
                    if (!contains(neighbor)) {
                        throw new GraphException(
                            "Unknown neighbor: " + neighbor
                        );
                    }

                    if (
                        type == GraphType.UNDIRECTED &&
                        !adjacency.get(neighbor).contains(vertex)
                    ) {
                        throw new GraphException(
                            "Undirected edge symmetry violation."
                        );
                    }
                }
            }
        }
    }

    interface TraversalStrategy {
        TraversalResult traverse(int start);
    }

    static final class DFSEngine implements TraversalStrategy {

        private final Graph graph;
        private final Consumer<VisitEvent> eventListener;

        private final Map<Integer, VertexState> states =
            new HashMap<>();

        private final List<Integer> order = new ArrayList<>();
        private final Map<Integer, Integer> parent = new HashMap<>();
        private final Map<Integer, Integer> depth = new HashMap<>();
        private final Map<Integer, Integer> discovery = new HashMap<>();
        private final Map<Integer, Integer> finish = new HashMap<>();

        private int clock;

        DFSEngine(Graph graph) {
            this(graph, event -> {});
        }

        DFSEngine(
            Graph graph,
            Consumer<VisitEvent> eventListener
        ) {
            this.graph = Objects.requireNonNull(graph);
            this.eventListener = Objects.requireNonNull(eventListener);
        }

        private void initialize(int start) {
            if (!graph.contains(start)) {
                throw new GraphException(
                    "Starting vertex does not exist."
                );
            }

            states.clear();
            order.clear();
            parent.clear();
            depth.clear();
            discovery.clear();
            finish.clear();
            clock = 0;

            for (int vertex : graph.vertices()) {
                states.put(vertex, VertexState.UNVISITED);
            }
        }

        private void explore(int vertex, int currentDepth) {
            states.put(vertex, VertexState.ACTIVE);

            depth.put(vertex, currentDepth);
            discovery.put(vertex, ++clock);
            order.add(vertex);

            eventListener.accept(
                new VisitEvent(vertex, currentDepth, clock)
            );

            for (int neighbor : graph.neighbors(vertex)) {
                if (states.get(neighbor) == VertexState.UNVISITED) {
                    parent.put(neighbor, vertex);
                    explore(neighbor, currentDepth + 1);
                }
            }

            states.put(vertex, VertexState.FINISHED);
            finish.put(vertex, ++clock);
        }

        public TraversalResult traverse(int start) {
            initialize(start);
            explore(start, 0);
            return result();
        }

        TraversalResult traverseIterative(int start) {
            initialize(start);

            Deque<Integer> stack = new ArrayDeque<>();
            stack.push(start);

            states.put(start, VertexState.ACTIVE);
            depth.put(start, 0);

            while (!stack.isEmpty()) {
                int vertex = stack.pop();

                if (states.get(vertex) == VertexState.FINISHED) {
                    continue;
                }

                states.put(vertex, VertexState.ACTIVE);
                discovery.put(vertex, ++clock);
                order.add(vertex);

                eventListener.accept(
                    new VisitEvent(vertex, depth.get(vertex), clock)
                );

                List<Integer> neighbors = graph.neighbors(vertex);

                for (int i = neighbors.size() - 1; i >= 0; i--) {
                    int neighbor = neighbors.get(i);

                    if (states.get(neighbor) == VertexState.UNVISITED) {
                        states.put(neighbor, VertexState.ACTIVE);
                        parent.put(neighbor, vertex);
                        depth.put(
                            neighbor,
                            depth.get(vertex) + 1
                        );
                        stack.push(neighbor);
                    }
                }

                states.put(vertex, VertexState.FINISHED);
                finish.put(vertex, ++clock);
            }

            return result();
        }

        private TraversalResult result() {
            return new TraversalResult(
                order,
                parent,
                depth,
                discovery,
                finish
            );
        }

        List<List<Integer>> connectedComponents() {
            if (graph.type() != GraphType.UNDIRECTED) {
                throw new GraphException(
                    "Connected components require an undirected graph."
                );
            }

            Set<Integer> visited = new HashSet<>();
            List<List<Integer>> components = new ArrayList<>();

            for (int start : graph.vertices()) {
                if (visited.contains(start)) {
                    continue;
                }

                List<Integer> component = new ArrayList<>();
                Deque<Integer> stack = new ArrayDeque<>();

                stack.push(start);
                visited.add(start);

                while (!stack.isEmpty()) {
                    int vertex = stack.pop();
                    component.add(vertex);

                    for (int neighbor : graph.neighbors(vertex)) {
                        if (visited.add(neighbor)) {
                            stack.push(neighbor);
                        }
                    }
                }

                components.add(List.copyOf(component));
            }

            return List.copyOf(components);
        }

        boolean hasPath(int source, int target) {
            if (!graph.contains(source) || !graph.contains(target)) {
                throw new GraphException("Invalid path endpoint.");
            }

            Set<Integer> visited = new HashSet<>();
            Deque<Integer> stack = new ArrayDeque<>();

            stack.push(source);

            while (!stack.isEmpty()) {
                int vertex = stack.pop();

                if (vertex == target) {
                    return true;
                }

                if (!visited.add(vertex)) {
                    continue;
                }

                for (int neighbor : graph.neighbors(vertex)) {
                    if (!visited.contains(neighbor)) {
                        stack.push(neighbor);
                    }
                }
            }

            return false;
        }

        List<Integer> topologicalSort() {
            if (graph.type() != GraphType.DIRECTED) {
                throw new GraphException(
                    "Topological sorting requires a directed graph."
                );
            }

            Map<Integer, VertexState> state = new HashMap<>();
            List<Integer> result = new ArrayList<>();

            for (int vertex : graph.vertices()) {
                state.put(vertex, VertexState.UNVISITED);
            }

            for (int vertex : graph.vertices()) {
                if (state.get(vertex) == VertexState.UNVISITED) {
                    topologicalExplore(vertex, state, result);
                }
            }

            Collections.reverse(result);
            return List.copyOf(result);
        }

        private void topologicalExplore(
            int vertex,
            Map<Integer, VertexState> state,
            List<Integer> result
        ) {
            state.put(vertex, VertexState.ACTIVE);

            for (int neighbor : graph.neighbors(vertex)) {
                if (state.get(neighbor) == VertexState.ACTIVE) {
                    throw new CycleDetectedException(
                        "Cycle detected at vertex " + neighbor
                    );
                }

                if (state.get(neighbor) == VertexState.UNVISITED) {
                    topologicalExplore(neighbor, state, result);
                }
            }

            state.put(vertex, VertexState.FINISHED);
            result.add(vertex);
        }
    }

    private static Graph createSampleGraph() {
        Graph graph = new Graph(GraphType.UNDIRECTED);

        List<Edge> edges = List.of(
            new Edge(1, 2),
            new Edge(1, 3),
            new Edge(2, 4),
            new Edge(2, 5),
            new Edge(3, 6),
            new Edge(5, 6),
            new Edge(7, 8)
        );

        edges.forEach(
            edge -> graph.addEdge(edge.source(), edge.destination())
        );

        graph.addVertex(9);
        graph.validate();

        return graph;
    }

    private static void runTests() {
        Graph graph = createSampleGraph();
        DFSEngine engine = new DFSEngine(graph);

        TraversalResult recursive = engine.traverse(1);
        TraversalResult iterative = engine.traverseIterative(1);

        if (!recursive.order().equals(iterative.order())) {
            throw new AssertionError("Traversal mismatch.");
        }

        if (engine.connectedComponents().size() != 3) {
            throw new AssertionError("Component test failed.");
        }

        if (!engine.hasPath(1, 6)) {
            throw new AssertionError("Path test failed.");
        }

        if (engine.hasPath(1, 8)) {
            throw new AssertionError("Disconnected path test failed.");
        }

        if (!engine.hasPath(9, 9)) {
            throw new AssertionError("Self-path test failed.");
        }

        Graph directed = new Graph(GraphType.DIRECTED);
        directed.addEdge(10, 11);
        directed.addEdge(11, 12);
        directed.addEdge(10, 13);

        List<Integer> topological =
            new DFSEngine(directed).topologicalSort();

        if (topological.size() != 4) {
            throw new AssertionError("Topological sorting failed.");
        }

        Graph cyclic = new Graph(GraphType.DIRECTED);
        cyclic.addEdge(20, 21);
        cyclic.addEdge(21, 22);
        cyclic.addEdge(22, 20);

        try {
            new DFSEngine(cyclic).topologicalSort();
            throw new AssertionError("Cycle detection failed.");
        } catch (CycleDetectedException expected) {
            // Expected behavior.
        }

        try {
            engine.traverseIterative(100);
            throw new AssertionError("Invalid vertex test failed.");
        } catch (GraphException expected) {
            // Expected behavior.
        }

        System.out.println("All Java 17 DFS tests passed.");
    }

    public static void main(String[] args) {
        try {
            runTests();

            Graph graph = createSampleGraph();

            DFSEngine engine = new DFSEngine(
                graph,
                event -> System.out.printf(
                    "Visited vertex %d at depth %d%n",
                    event.vertex(),
                    event.depth()
                )
            );

            System.out.println("\nRecursive DFS:");
            TraversalResult recursive = engine.traverse(1);
            System.out.println(recursive.order());

            System.out.println("\nIterative DFS:");
            TraversalResult iterative = engine.traverseIterative(1);
            System.out.println(iterative.order());

            System.out.println("\nParent relationships:");
            recursive.parent().forEach(
                (vertex, parent) ->
                    System.out.println(parent + " -> " + vertex)
            );

            System.out.println("\nConnected components:");
            engine.connectedComponents().forEach(
                System.out::println
            );

            System.out.println("\nPath 1 -> 6: " + engine.hasPath(1, 6));
            System.out.println("Path 1 -> 8: " + engine.hasPath(1, 8));

            Graph directed = new Graph(GraphType.DIRECTED);
            directed.addEdge(1, 2);
            directed.addEdge(1, 3);
            directed.addEdge(2, 4);
            directed.addEdge(3, 4);

            System.out.println("\nTopological ordering:");
            System.out.println(
                new DFSEngine(directed).topologicalSort()
            );

            Instant beginning = Instant.now();
            TraversalResult benchmark = engine.traverseIterative(1);
            Instant ending = Instant.now();

            System.out.println("\nBenchmark:");
            System.out.println(
                "Visited vertices: " + benchmark.order().size()
            );
            System.out.println(
                "Elapsed: " +
                Duration.between(beginning, ending).toNanos() +
                " ns"
            );

        } catch (GraphException exception) {
            System.err.println("Graph error: " + exception.getMessage());
            System.exit(1);
        }
    }
}
