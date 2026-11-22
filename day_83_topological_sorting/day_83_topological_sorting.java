import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Set;

/*
 * Topological Sorting and Enterprise Dependency Management
 *
 * Java 17 implementation featuring:
 * - Typed dependency graph
 * - Immutable task definitions
 * - DFS and Kahn topological algorithms
 * - Cycle detection
 * - Enterprise dependency policies
 * - Approval-like prerequisite validation
 * - Execution state transitions
 * - Failure propagation
 * - Deterministic scheduling
 */

public class Main {

    enum TaskStatus {
        PENDING,
        READY,
        RUNNING,
        COMPLETED,
        FAILED,
        BLOCKED
    }

    enum DependencyType {
        BUILD,
        TEST,
        SECURITY,
        DEPLOYMENT
    }

    record TaskDefinition(
        String id,
        String description,
        DependencyType type
    ) {
        TaskDefinition {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Task ID cannot be empty."
                );
            }

            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException(
                    "Task description is required."
                );
            }

            Objects.requireNonNull(type);
        }
    }

    record ExecutionResult(
        String taskId,
        TaskStatus status,
        String message
    ) {}

    static class DependencyException extends RuntimeException {
        DependencyException(String message) {
            super(message);
        }
    }

    static class CycleException extends DependencyException {
        private final List<String> cycle;

        CycleException(String message, List<String> cycle) {
            super(message);
            this.cycle = List.copyOf(cycle);
        }

        public List<String> getCycle() {
            return cycle;
        }
    }

    static class DependencyPolicy {

        private final int maximumTasks;
        private final int maximumDependencies;

        DependencyPolicy(
            int maximumTasks,
            int maximumDependencies
        ) {
            if (maximumTasks < 1 || maximumDependencies < 0) {
                throw new IllegalArgumentException(
                    "Invalid dependency policy limits."
                );
            }

            this.maximumTasks = maximumTasks;
            this.maximumDependencies = maximumDependencies;
        }

        void validateTaskCount(int count) {
            if (count > maximumTasks) {
                throw new DependencyException(
                    "Maximum task limit exceeded."
                );
            }
        }

        void validateDependencyCount(int count) {
            if (count > maximumDependencies) {
                throw new DependencyException(
                    "Maximum dependency limit exceeded."
                );
            }
        }
    }

    static class DirectedAcyclicGraph {

        private final Map<String, Set<String>> adjacency =
            new LinkedHashMap<>();

        private final Map<String, Set<String>> reverse =
            new LinkedHashMap<>();

        private final DependencyPolicy policy;

        DirectedAcyclicGraph(DependencyPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        void addVertex(String id) {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Invalid vertex identifier."
                );
            }

            if (!adjacency.containsKey(id)) {
                policy.validateTaskCount(adjacency.size() + 1);

                adjacency.put(id, new LinkedHashSet<>());
                reverse.put(id, new LinkedHashSet<>());
            }
        }

        void addEdge(String source, String destination) {
            if (!adjacency.containsKey(source)) {
                throw new DependencyException(
                    "Unknown prerequisite: " + source
                );
            }

            if (!adjacency.containsKey(destination)) {
                throw new DependencyException(
                    "Unknown dependent: " + destination
                );
            }

            if (source.equals(destination)) {
                throw new CycleException(
                    "Self-dependency: " + source,
                    List.of(source, source)
                );
            }

            if (adjacency.get(source).contains(destination)) {
                return;
            }

            if (getEdgeCount() >= policy.maximumDependencies) {
                throw new DependencyException(
                    "Maximum dependency count reached."
                );
            }

            adjacency.get(source).add(destination);
            reverse.get(destination).add(source);
        }

        int getVertexCount() {
            return adjacency.size();
        }

        int getEdgeCount() {
            return adjacency.values()
                .stream()
                .mapToInt(Set::size)
                .sum();
        }

        private void dfs(
            String node,
            Map<String, Integer> state,
            Deque<String> path,
            List<String> result
        ) {
            state.put(node, 1);
            path.addLast(node);

            for (String neighbor : adjacency.get(node)) {
                int neighborState = state.get(neighbor);

                if (neighborState == 1) {
                    List<String> cycle = new ArrayList<>();
                    boolean collecting = false;

                    for (String element : path) {
                        if (element.equals(neighbor)) {
                            collecting = true;
                        }

                        if (collecting) {
                            cycle.add(element);
                        }
                    }

                    cycle.add(neighbor);

                    throw new CycleException(
                        "Cycle detected: " +
                            String.join(" -> ", cycle),
                        cycle
                    );
                }

                if (neighborState == 0) {
                    dfs(neighbor, state, path, result);
                }
            }

            path.removeLast();
            state.put(node, 2);
            result.add(node);
        }

        List<String> depthFirstOrdering() {
            Map<String, Integer> state = new HashMap<>();

            for (String node : adjacency.keySet()) {
                state.put(node, 0);
            }

            List<String> result = new ArrayList<>();
            Deque<String> path = new ArrayDeque<>();

            adjacency.keySet()
                .stream()
                .sorted()
                .forEach(node -> {
                    if (state.get(node) == 0) {
                        dfs(node, state, path, result);
                    }
                });

            Collections.reverse(result);

            return List.copyOf(result);
        }

        List<String> kahnOrdering() {
            Map<String, Integer> indegree = new HashMap<>();

            for (String node : adjacency.keySet()) {
                indegree.put(node, reverse.get(node).size());
            }

            PriorityQueue<String> ready = new PriorityQueue<>(
                Comparator.naturalOrder()
            );

            indegree.forEach((node, degree) -> {
                if (degree == 0) {
                    ready.add(node);
                }
            });

            List<String> result = new ArrayList<>();

            while (!ready.isEmpty()) {
                String current = ready.remove();
                result.add(current);

                for (String neighbor : adjacency.get(current)) {
                    int remaining = indegree.get(neighbor) - 1;

                    indegree.put(neighbor, remaining);

                    if (remaining == 0) {
                        ready.add(neighbor);
                    }
                }
            }

            if (result.size() != adjacency.size()) {
                List<String> unresolved = indegree.entrySet()
                    .stream()
                    .filter(entry -> entry.getValue() > 0)
                    .map(Map.Entry::getKey)
                    .sorted()
                    .toList();

                throw new CycleException(
                    "Unresolved cyclic dependencies: " + unresolved,
                    unresolved
                );
            }

            return List.copyOf(result);
        }

        Map<String, Integer> calculateLevels() {
            List<String> order = kahnOrdering();

            Map<String, Integer> levels = new LinkedHashMap<>();

            for (String node : adjacency.keySet()) {
                levels.put(node, 0);
            }

            for (String node : order) {
                for (String neighbor : adjacency.get(node)) {
                    levels.put(
                        neighbor,
                        Math.max(
                            levels.get(neighbor),
                            levels.get(node) + 1
                        )
                    );
                }
            }

            return Collections.unmodifiableMap(levels);
        }

        List<String> getPrerequisites(String id) {
            if (!reverse.containsKey(id)) {
                throw new DependencyException(
                    "Unknown task: " + id
                );
            }

            return reverse.get(id).stream().sorted().toList();
        }

        boolean isValidOrdering(List<String> ordering) {
            if (ordering.size() != adjacency.size()) {
                return false;
            }

            Map<String, Integer> positions = new HashMap<>();

            for (int i = 0; i < ordering.size(); i++) {
                if (
                    !adjacency.containsKey(ordering.get(i)) ||
                    positions.put(ordering.get(i), i) != null
                ) {
                    return false;
                }
            }

            for (var entry : adjacency.entrySet()) {
                for (String dependent : entry.getValue()) {
                    if (
                        positions.get(entry.getKey()) >=
                        positions.get(dependent)
                    ) {
                        return false;
                    }
                }
            }

            return true;
        }
    }

    static class TaskExecutionService {

        private final DirectedAcyclicGraph graph;

        private final Map<String, TaskDefinition> definitions =
            new LinkedHashMap<>();

        private final Map<String, TaskStatus> states =
            new LinkedHashMap<>();

        private final DependencyPolicy policy;

        TaskExecutionService(DependencyPolicy policy) {
            this.policy = policy;
            this.graph = new DirectedAcyclicGraph(policy);
        }

        void registerTask(TaskDefinition definition) {
            Objects.requireNonNull(definition);

            if (definitions.containsKey(definition.id())) {
                throw new DependencyException(
                    "Duplicate task: " + definition.id()
                );
            }

            graph.addVertex(definition.id());

            definitions.put(definition.id(), definition);
            states.put(definition.id(), TaskStatus.PENDING);
        }

        void addDependency(
            String prerequisite,
            String dependent
        ) {
            graph.addEdge(prerequisite, dependent);
        }

        DirectedAcyclicGraph getGraph() {
            return graph;
        }

        private void transition(
            String id,
            TaskStatus next
        ) {
            TaskStatus current = states.get(id);

            boolean allowed = switch (current) {
                case PENDING ->
                    next == TaskStatus.READY ||
                    next == TaskStatus.BLOCKED;

                case READY ->
                    next == TaskStatus.RUNNING;

                case RUNNING ->
                    next == TaskStatus.COMPLETED ||
                    next == TaskStatus.FAILED;

                default -> false;
            };

            if (!allowed) {
                throw new DependencyException(
                    "Invalid state transition for " +
                        id + ": " + current + " -> " + next
                );
            }

            states.put(id, next);
        }

        List<ExecutionResult> execute() {
            // Resolve cycles before performing any task operations.
            List<String> ordering = graph.kahnOrdering();

            Set<String> completed = new HashSet<>();
            Set<String> failed = new HashSet<>();

            List<ExecutionResult> results = new ArrayList<>();

            for (String id : ordering) {
                List<String> prerequisites =
                    graph.getPrerequisites(id);

                if (
                    prerequisites.stream()
                        .anyMatch(failed::contains)
                ) {
                    transition(id, TaskStatus.BLOCKED);
                    failed.add(id);

                    results.add(new ExecutionResult(
                        id,
                        TaskStatus.BLOCKED,
                        "A prerequisite failed."
                    ));

                    continue;
                }

                if (!completed.containsAll(prerequisites)) {
                    throw new DependencyException(
                        "Dependency invariant failed for " + id
                    );
                }

                transition(id, TaskStatus.READY);
                transition(id, TaskStatus.RUNNING);

                TaskDefinition definition = definitions.get(id);

                try {
                    // A production executor would invoke the task's
                    // registered operation at this point.
                    String message =
                        "Executed " + definition.description();

                    transition(id, TaskStatus.COMPLETED);
                    completed.add(id);

                    results.add(new ExecutionResult(
                        id,
                        TaskStatus.COMPLETED,
                        message
                    ));

                } catch (RuntimeException error) {
                    transition(id, TaskStatus.FAILED);
                    failed.add(id);

                    results.add(new ExecutionResult(
                        id,
                        TaskStatus.FAILED,
                        error.getMessage()
                    ));
                }
            }

            return List.copyOf(results);
        }

        Map<String, TaskStatus> getStates() {
            return Collections.unmodifiableMap(states);
        }
    }

    private static TaskExecutionService createPipeline() {
        DependencyPolicy policy = new DependencyPolicy(
            1000,
            5000
        );

        TaskExecutionService service =
            new TaskExecutionService(policy);

        List<TaskDefinition> tasks = List.of(
            new TaskDefinition(
                "source",
                "Retrieve source files",
                DependencyType.BUILD
            ),
            new TaskDefinition(
                "validate",
                "Validate source files",
                DependencyType.BUILD
            ),
            new TaskDefinition(
                "compile",
                "Compile application",
                DependencyType.BUILD
            ),
            new TaskDefinition(
                "unit",
                "Execute unit tests",
                DependencyType.TEST
            ),
            new TaskDefinition(
                "security",
                "Perform security analysis",
                DependencyType.SECURITY
            ),
            new TaskDefinition(
                "package",
                "Generate application package",
                DependencyType.BUILD
            ),
            new TaskDefinition(
                "integration",
                "Run integration tests",
                DependencyType.TEST
            ),
            new TaskDefinition(
                "deploy",
                "Deploy application",
                DependencyType.DEPLOYMENT
            )
        );

        tasks.forEach(service::registerTask);

        List<List<String>> dependencies = List.of(
            List.of("source", "validate"),
            List.of("validate", "compile"),
            List.of("compile", "unit"),
            List.of("compile", "security"),
            List.of("unit", "package"),
            List.of("security", "package"),
            List.of("package", "integration"),
            List.of("integration", "deploy")
        );

        dependencies.forEach(edge ->
            service.addDependency(edge.get(0), edge.get(1))
        );

        return service;
    }

    private static void demonstrateCycles() {
        DependencyPolicy policy = new DependencyPolicy(20, 50);

        DirectedAcyclicGraph graph =
            new DirectedAcyclicGraph(policy);

        graph.addVertex("A");
        graph.addVertex("B");
        graph.addVertex("C");

        graph.addEdge("A", "B");
        graph.addEdge("B", "C");
        graph.addEdge("C", "A");

        try {
            graph.depthFirstOrdering();
        } catch (CycleException error) {
            System.out.println(
                "\nDFS cycle detection: " + error.getMessage()
            );
        }

        try {
            graph.kahnOrdering();
        } catch (CycleException error) {
            System.out.println(
                "Kahn cycle detection: " + error.getMessage()
            );
        }
    }

    private static void demonstrateEdgeCases() {
        DependencyPolicy policy = new DependencyPolicy(20, 50);

        DirectedAcyclicGraph graph =
            new DirectedAcyclicGraph(policy);

        graph.addVertex("isolated");

        if (!graph.kahnOrdering().equals(List.of("isolated"))) {
            throw new IllegalStateException(
                "Isolated vertex validation failed."
            );
        }

        DirectedAcyclicGraph empty =
            new DirectedAcyclicGraph(policy);

        if (!empty.depthFirstOrdering().isEmpty()) {
            throw new IllegalStateException(
                "Empty graph validation failed."
            );
        }

        System.out.println("\nEdge-case validations passed.");
    }

    public static void main(String[] args) {
        try {
            System.out.println(
                "ENTERPRISE TOPOLOGICAL SORTING ENGINE"
            );

            System.out.println("=".repeat(55));

            TaskExecutionService service = createPipeline();

            DirectedAcyclicGraph graph = service.getGraph();

            System.out.println(
                "\nVertices: " + graph.getVertexCount()
            );

            System.out.println(
                "Edges: " + graph.getEdgeCount()
            );

            List<String> dfs = graph.depthFirstOrdering();
            List<String> kahn = graph.kahnOrdering();

            System.out.println("\nDFS ordering:");
            System.out.println(String.join(" -> ", dfs));

            System.out.println("\nKahn ordering:");
            System.out.println(String.join(" -> ", kahn));

            if (
                !graph.isValidOrdering(dfs) ||
                !graph.isValidOrdering(kahn)
            ) {
                throw new DependencyException(
                    "Generated ordering is invalid."
                );
            }

            System.out.println("\nExecution levels:");

            graph.calculateLevels().forEach(
                (id, level) ->
                    System.out.println(id + ": " + level)
            );

            System.out.println("\nTask execution:");

            for (ExecutionResult result : service.execute()) {
                System.out.println(
                    result.taskId() + " | " +
                    result.status() + " | " +
                    result.message()
                );
            }

            System.out.println("\nFinal task states:");

            service.getStates().forEach(
                (id, status) ->
                    System.out.println(id + ": " + status)
            );

            demonstrateCycles();
            demonstrateEdgeCases();

            System.out.println(
                "\nAll enterprise dependency validations passed."
            );

        } catch (RuntimeException error) {
            System.err.println(
                "Execution error: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
