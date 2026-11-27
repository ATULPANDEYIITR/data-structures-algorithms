import java.util.*;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Minimum Spanning Tree: Enterprise Infrastructure Planning
 *
 * Java 17 implementation.
 *
 * Features:
 * - Explicit domain types
 * - Immutable connection records
 * - Graph validation
 * - Kruskal and Prim algorithms
 * - Disjoint Set Union
 * - Network budget policies
 * - Mandatory and prohibited links
 * - Approval of infrastructure plans
 * - State transitions
 * - Independent plan verification
 * - Disconnected graph handling
 *
 * Run:
 * javac MinimumSpanningTree.java
 * java MinimumSpanningTree
 */

public class MinimumSpanningTree {

    enum PlanStatus {
        DRAFT,
        CALCULATED,
        VALIDATED,
        APPROVED,
        REJECTED
    }

    enum Algorithm {
        KRUSKAL,
        PRIM
    }

    enum PolicySeverity {
        ERROR,
        WARNING
    }

    static class NetworkException extends RuntimeException {
        NetworkException(String message) {
            super(message);
        }
    }

    static class PolicyViolationException extends RuntimeException {
        PolicyViolationException(String message) {
            super(message);
        }
    }

    record Vertex(String id, String region) {
        Vertex {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex ID is required."
                );
            }

            if (region == null || region.isBlank()) {
                throw new IllegalArgumentException(
                    "Region is required."
                );
            }
        }
    }

    record Connection(
        String source,
        String destination,
        double weight,
        String provider
    ) {
        Connection {
            if (
                source == null ||
                destination == null ||
                source.isBlank() ||
                destination.isBlank()
            ) {
                throw new IllegalArgumentException(
                    "Connection endpoints are required."
                );
            }

            if (source.equals(destination)) {
                throw new IllegalArgumentException(
                    "Self-loops are not allowed."
                );
            }

            if (!Double.isFinite(weight) || weight < 0) {
                throw new IllegalArgumentException(
                    "Invalid connection cost."
                );
            }

            if (provider == null || provider.isBlank()) {
                throw new IllegalArgumentException(
                    "Provider is required."
                );
            }
        }

        String key() {
            return source.compareTo(destination) < 0
                ? source + "\u0000" + destination
                : destination + "\u0000" + source;
        }
    }

    record PolicyViolation(
        PolicySeverity severity,
        String message
    ) {}

    record PlanResult(
        String planId,
        Algorithm algorithm,
        List<Connection> selectedConnections,
        double totalCost,
        int vertexCount,
        int componentCount
    ) {
        PlanResult {
            selectedConnections = List.copyOf(
                selectedConnections
            );
        }

        boolean connected() {
            return componentCount <= 1;
        }

        int expectedEdgeCount() {
            return vertexCount - componentCount;
        }
    }

    static final class DisjointSet {
        private final Map<String, String> parent =
            new HashMap<>();

        private final Map<String, Integer> rank =
            new HashMap<>();

        private int components;

        DisjointSet(Collection<String> vertices) {
            for (String vertex : vertices) {
                parent.put(vertex, vertex);
                rank.put(vertex, 0);
            }

            components = parent.size();
        }

        String find(String vertex) {
            String p = parent.get(vertex);

            if (p == null) {
                throw new NetworkException(
                    "Unknown vertex: " + vertex
                );
            }

            if (!p.equals(vertex)) {
                parent.put(vertex, find(p));
            }

            return parent.get(vertex);
        }

        boolean union(String first, String second) {
            String a = find(first);
            String b = find(second);

            if (a.equals(b)) return false;

            int rankA = rank.get(a);
            int rankB = rank.get(b);

            if (rankA < rankB) {
                String temp = a;
                a = b;
                b = temp;
            }

            parent.put(b, a);

            if (rankA == rankB) {
                rank.put(a, rank.get(a) + 1);
            }

            components--;
            return true;
        }

        int components() {
            return components;
        }
    }

    static final class Network {
        private final String networkId;

        private final Map<String, Vertex> vertices =
            new LinkedHashMap<>();

        private final Map<String, Connection> connections =
            new LinkedHashMap<>();

        private long version = 0;

        Network(String networkId) {
            if (
                networkId == null ||
                networkId.isBlank()
            ) {
                throw new IllegalArgumentException(
                    "Network ID is required."
                );
            }

            this.networkId = networkId;
        }

        synchronized void addVertex(Vertex vertex) {
            if (vertices.putIfAbsent(
                vertex.id(),
                vertex
            ) != null) {
                throw new NetworkException(
                    "Duplicate vertex: " + vertex.id()
                );
            }

            version++;
        }

        synchronized void addConnection(Connection connection) {
            if (
                !vertices.containsKey(connection.source()) ||
                !vertices.containsKey(connection.destination())
            ) {
                throw new NetworkException(
                    "Both endpoints must be registered."
                );
            }

            if (
                connections.putIfAbsent(
                    connection.key(),
                    connection
                ) != null
            ) {
                throw new NetworkException(
                    "Duplicate undirected connection."
                );
            }

            version++;
        }

        synchronized long version() {
            return version;
        }

        synchronized List<Vertex> vertexSnapshot() {
            return List.copyOf(vertices.values());
        }

        synchronized List<Connection> connectionSnapshot() {
            return List.copyOf(connections.values());
        }

        String id() {
            return networkId;
        }
    }

    static final class NetworkPolicy {
        private final boolean requireConnected;
        private final double maximumTotalCost;
        private final double maximumConnectionCost;

        private final Set<String> mandatory;
        private final Set<String> forbidden;

        private final int minimumProviders;

        NetworkPolicy(
            boolean requireConnected,
            double maximumTotalCost,
            double maximumConnectionCost,
            Set<String> mandatory,
            Set<String> forbidden,
            int minimumProviders
        ) {
            if (
                maximumTotalCost < 0 ||
                maximumConnectionCost < 0 ||
                minimumProviders < 1
            ) {
                throw new IllegalArgumentException(
                    "Invalid policy configuration."
                );
            }

            this.requireConnected = requireConnected;
            this.maximumTotalCost = maximumTotalCost;
            this.maximumConnectionCost = maximumConnectionCost;

            this.mandatory = Set.copyOf(mandatory);
            this.forbidden = Set.copyOf(forbidden);
            this.minimumProviders = minimumProviders;
        }

        List<PolicyViolation> evaluate(
            PlanResult result
        ) {
            List<PolicyViolation> violations =
                new ArrayList<>();

            if (
                requireConnected &&
                !result.connected()
            ) {
                violations.add(new PolicyViolation(
                    PolicySeverity.ERROR,
                    "All network vertices must be connected."
                ));
            }

            if (result.totalCost() > maximumTotalCost) {
                violations.add(new PolicyViolation(
                    PolicySeverity.ERROR,
                    "Network budget exceeded."
                ));
            }

            Set<String> selected = result.selectedConnections()
                .stream()
                .map(Connection::key)
                .collect(Collectors.toSet());

            Set<String> providers = result.selectedConnections()
                .stream()
                .map(Connection::provider)
                .collect(Collectors.toSet());

            for (Connection connection : result.selectedConnections()) {
                if (
                    connection.weight() >
                    maximumConnectionCost
                ) {
                    violations.add(new PolicyViolation(
                        PolicySeverity.ERROR,
                        "Individual connection cost exceeded: " +
                        connection.key()
                    ));
                }

                if (forbidden.contains(connection.key())) {
                    violations.add(new PolicyViolation(
                        PolicySeverity.ERROR,
                        "Prohibited connection selected: " +
                        connection.key()
                    ));
                }
            }

            for (String required : mandatory) {
                if (!selected.contains(required)) {
                    violations.add(new PolicyViolation(
                        PolicySeverity.ERROR,
                        "Mandatory connection missing: " +
                        required
                    ));
                }
            }

            if (providers.size() < minimumProviders) {
                violations.add(new PolicyViolation(
                    PolicySeverity.WARNING,
                    "Provider diversity requirement not satisfied."
                ));
            }

            return List.copyOf(violations);
        }
    }

    static final class NetworkPlan {
        private final String planId;
        private final Network network;
        private final long sourceVersion;

        private PlanStatus status = PlanStatus.DRAFT;
        private PlanResult result;

        private List<PolicyViolation> violations =
            List.of();

        NetworkPlan(String planId, Network network) {
            this.planId = Objects.requireNonNull(planId);
            this.network = Objects.requireNonNull(network);
            this.sourceVersion = network.version();
        }

        synchronized void calculate(
            Algorithm algorithm,
            PlanningService service
        ) {
            if (status != PlanStatus.DRAFT) {
                throw new NetworkException(
                    "Only draft plans can be calculated."
                );
            }

            if (network.version() != sourceVersion) {
                throw new NetworkException(
                    "Network changed after plan creation."
                );
            }

            result = service.calculate(
                planId,
                network,
                algorithm
            );

            status = PlanStatus.CALCULATED;
        }

        synchronized void validate(
            NetworkPolicy policy
        ) {
            if (status != PlanStatus.CALCULATED) {
                throw new NetworkException(
                    "Plan must be calculated first."
                );
            }

            if (network.version() != sourceVersion) {
                status = PlanStatus.REJECTED;

                throw new NetworkException(
                    "Network changed during validation."
                );
            }

            violations = policy.evaluate(result);

            boolean hasError = violations.stream()
                .anyMatch(
                    v -> v.severity() == PolicySeverity.ERROR
                );

            status = hasError
                ? PlanStatus.REJECTED
                : PlanStatus.VALIDATED;
        }

        synchronized void approve() {
            if (status != PlanStatus.VALIDATED) {
                throw new NetworkException(
                    "Only validated plans can be approved."
                );
            }

            if (network.version() != sourceVersion) {
                status = PlanStatus.REJECTED;

                throw new NetworkException(
                    "Source network changed before approval."
                );
            }

            status = PlanStatus.APPROVED;
        }

        synchronized void reject(String reason) {
            if (reason == null || reason.isBlank()) {
                throw new IllegalArgumentException(
                    "Rejection reason is required."
                );
            }

            if (
                status == PlanStatus.APPROVED ||
                status == PlanStatus.REJECTED
            ) {
                throw new NetworkException(
                    "Terminal plan cannot be rejected again."
                );
            }

            status = PlanStatus.REJECTED;

            violations = List.of(
                new PolicyViolation(
                    PolicySeverity.ERROR,
                    reason
                )
            );
        }

        PlanStatus status() {
            return status;
        }

        PlanResult result() {
            if (result == null) {
                throw new NetworkException(
                    "Plan has not been calculated."
                );
            }

            return result;
        }

        List<PolicyViolation> violations() {
            return violations;
        }
    }

    static final class PlanningService {

        PlanResult calculate(
            String planId,
            Network network,
            Algorithm algorithm
        ) {
            List<Vertex> vertices =
                network.vertexSnapshot();

            List<Connection> edges =
                network.connectionSnapshot();

            if (vertices.isEmpty()) {
                throw new NetworkException(
                    "Cannot calculate an empty network."
                );
            }

            return switch (algorithm) {
                case KRUSKAL -> kruskal(
                    planId,
                    vertices,
                    edges
                );
                case PRIM -> prim(
                    planId,
                    vertices,
                    edges
                );
            };
        }

        private PlanResult kruskal(
            String planId,
            List<Vertex> vertices,
            List<Connection> edges
        ) {
            List<Connection> ordered = edges.stream()
                .sorted(
                    Comparator.comparingDouble(
                        Connection::weight
                    ).thenComparing(Connection::key)
                )
                .toList();

            Set<String> ids = vertices.stream()
                .map(Vertex::id)
                .collect(Collectors.toSet());

            DisjointSet dsu = new DisjointSet(ids);

            List<Connection> selected =
                new ArrayList<>();

            double total = 0;

            for (Connection edge : ordered) {
                if (dsu.union(
                    edge.source(),
                    edge.destination()
                )) {
                    selected.add(edge);
                    total += edge.weight();

                    if (dsu.components() <= 1) break;
                }
            }

            return new PlanResult(
                planId,
                Algorithm.KRUSKAL,
                selected,
                total,
                vertices.size(),
                dsu.components()
            );
        }

        private PlanResult prim(
            String planId,
            List<Vertex> vertices,
            List<Connection> edges
        ) {
            Map<String, List<Connection>> adjacency =
                new HashMap<>();

            for (Vertex vertex : vertices) {
                adjacency.put(
                    vertex.id(),
                    new ArrayList<>()
                );
            }

            for (Connection edge : edges) {
                adjacency.get(edge.source()).add(edge);
                adjacency.get(edge.destination()).add(edge);
            }

            PriorityQueue<Connection> queue =
                new PriorityQueue<>(
                    Comparator.comparingDouble(
                        Connection::weight
                    ).thenComparing(Connection::key)
                );

            Set<String> visited = new HashSet<>();
            List<Connection> selected = new ArrayList<>();

            int components = 0;
            double total = 0;

            for (Vertex vertex : vertices) {
                String start = vertex.id();

                if (!visited.add(start)) continue;

                components++;

                queue.addAll(adjacency.get(start));

                while (!queue.isEmpty()) {
                    Connection edge = queue.poll();

                    boolean sourceVisited =
                        visited.contains(edge.source());

                    boolean destinationVisited =
                        visited.contains(edge.destination());

                    if (
                        sourceVisited == destinationVisited
                    ) {
                        continue;
                    }

                    String next = sourceVisited
                        ? edge.destination()
                        : edge.source();

                    visited.add(next);
                    selected.add(edge);
                    total += edge.weight();

                    queue.addAll(adjacency.get(next));
                }
            }

            return new PlanResult(
                planId,
                Algorithm.PRIM,
                selected,
                total,
                vertices.size(),
                components
            );
        }

        boolean verify(
            PlanResult result,
            Network network
        ) {
            Set<String> vertices = network.vertexSnapshot()
                .stream()
                .map(Vertex::id)
                .collect(Collectors.toSet());

            DisjointSet dsu = new DisjointSet(vertices);

            double total = 0;

            for (Connection edge : result.selectedConnections()) {
                if (
                    !vertices.contains(edge.source()) ||
                    !vertices.contains(edge.destination())
                ) {
                    return false;
                }

                if (!dsu.union(
                    edge.source(),
                    edge.destination()
                )) {
                    return false;
                }

                total += edge.weight();
            }

            return (
                result.selectedConnections().size() ==
                    result.expectedEdgeCount() &&
                dsu.components() == result.componentCount() &&
                Math.abs(total - result.totalCost()) < 1e-9
            );
        }
    }

    static Network createSampleNetwork() {
        Network network = new Network("REGIONAL-NETWORK-01");

        for (String id : List.of("A", "B", "C", "D", "E", "F")) {
            network.addVertex(
                new Vertex(id, "North")
            );
        }

        network.addConnection(
            new Connection("A", "B", 4, "Provider-1")
        );

        network.addConnection(
            new Connection("A", "C", 3, "Provider-1")
        );

        network.addConnection(
            new Connection("B", "C", 1, "Provider-2")
        );

        network.addConnection(
            new Connection("B", "D", 2, "Provider-2")
        );

        network.addConnection(
            new Connection("C", "D", 4, "Provider-1")
        );

        network.addConnection(
            new Connection("C", "E", 5, "Provider-3")
        );

        network.addConnection(
            new Connection("D", "E", 2, "Provider-2")
        );

        network.addConnection(
            new Connection("D", "F", 6, "Provider-3")
        );

        network.addConnection(
            new Connection("E", "F", 3, "Provider-3")
        );

        network.addConnection(
            new Connection("A", "F", 10, "Provider-1")
        );

        return network;
    }

    static void runTests(
        PlanningService service
    ) {
        Network network = new Network("TEST");

        network.addVertex(new Vertex("A", "R1"));
        network.addVertex(new Vertex("B", "R1"));
        network.addVertex(new Vertex("C", "R2"));

        network.addConnection(
            new Connection("A", "B", 1, "P1")
        );

        network.addConnection(
            new Connection("B", "C", 2, "P2")
        );

        network.addConnection(
            new Connection("A", "C", 5, "P1")
        );

        PlanResult kruskal = service.calculate(
            "TEST-K",
            network,
            Algorithm.KRUSKAL
        );

        PlanResult prim = service.calculate(
            "TEST-P",
            network,
            Algorithm.PRIM
        );

        if (
            kruskal.totalCost() != 3 ||
            prim.totalCost() != 3
        ) {
            throw new AssertionError(
                "MST cost test failed."
            );
        }

        if (!service.verify(kruskal, network)) {
            throw new AssertionError(
                "Tree verification failed."
            );
        }

        NetworkPolicy budgetPolicy = new NetworkPolicy(
            true,
            4,
            3,
            Set.of(),
            Set.of(),
            1
        );

        if (!budgetPolicy.evaluate(kruskal).isEmpty()) {
            throw new AssertionError(
                "Valid policy was rejected."
            );
        }

        NetworkPolicy forbiddenPolicy = new NetworkPolicy(
            true,
            100,
            100,
            Set.of(),
            Set.of("A\u0000B"),
            1
        );

        if (forbiddenPolicy.evaluate(kruskal).stream()
            .noneMatch(v -> v.severity() == PolicySeverity.ERROR)) {
            throw new AssertionError(
                "Forbidden connection was accepted."
            );
        }

        Network disconnected = new Network("DISCONNECTED");
        disconnected.addVertex(new Vertex("X", "R1"));
        disconnected.addVertex(new Vertex("Y", "R1"));
        disconnected.addVertex(new Vertex("Z", "R2"));

        disconnected.addConnection(
            new Connection("X", "Y", 1, "P1")
        );

        PlanResult forest = service.calculate(
            "FOREST",
            disconnected,
            Algorithm.KRUSKAL
        );

        if (
            forest.connected() ||
            forest.componentCount() != 2
        ) {
            throw new AssertionError(
                "Forest test failed."
            );
        }

        // Detect modifications after plan creation.
        NetworkPlan stalePlan = new NetworkPlan(
            "STALE",
            network
        );

        network.addVertex(
            new Vertex("D", "R3")
        );

        try {
            stalePlan.calculate(
                Algorithm.KRUSKAL,
                service
            );

            throw new AssertionError(
                "Stale plan was accepted."
            );
        } catch (NetworkException expected) {
            // Expected state validation.
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            Network network = createSampleNetwork();

            PlanningService service =
                new PlanningService();

            NetworkPolicy policy = new NetworkPolicy(
                true,
                15,
                6,
                Set.of(),
                Set.of("A\u0000F"),
                2
            );

            NetworkPlan plan = new NetworkPlan(
                "PLAN-2026-001",
                network
            );

            plan.calculate(
                Algorithm.KRUSKAL,
                service
            );

            PlanResult result = plan.result();

            System.out.println(
                "ENTERPRISE NETWORK PLANNING"
            );

            System.out.println(
                "Network: " + network.id()
            );

            System.out.println(
                "Algorithm: " + result.algorithm()
            );

            System.out.println("\nSelected connections:");

            for (Connection edge : result.selectedConnections()) {
                System.out.printf(
                    "%s -- %s | Cost: %.2f | Provider: %s%n",
                    edge.source(),
                    edge.destination(),
                    edge.weight(),
                    edge.provider()
                );
            }

            System.out.printf(
                "%nTotal cost: %.2f%n",
                result.totalCost()
            );

            System.out.println(
                "Connected: " + result.connected()
            );

            if (!service.verify(result, network)) {
                throw new NetworkException(
                    "Integrity verification failed."
                );
            }

            plan.validate(policy);

            for (PolicyViolation violation : plan.violations()) {
                System.out.println(
                    violation.severity() + ": " +
                    violation.message()
                );
            }

            if (plan.status() == PlanStatus.VALIDATED) {
                plan.approve();
            }

            System.out.println(
                "\nFinal plan status: " + plan.status()
            );

            runTests(service);

        } catch (Exception exception) {
            System.err.println(
                "Planning failure: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
