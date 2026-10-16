import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class RecursionFundamentals {

    enum ComponentState {
        UNVISITED, VISITING, COMPLETE
    }

    record Service(String name, List<String> dependencies, int buildMinutes) {
        Service {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException("Service name is required");
            }
            if (buildMinutes < 0) {
                throw new IllegalArgumentException("Build duration cannot be negative");
            }
            dependencies = List.copyOf(dependencies);
        }
    }

    record BuildReport(List<String> dependencyFirstOrder, int criticalPathMinutes) {
        BuildReport {
            dependencyFirstOrder = List.copyOf(dependencyFirstOrder);
        }
    }

    static final class DependencyCycleException extends RuntimeException {
        DependencyCycleException(String message) {
            super(message);
        }
    }

    static final class ReleasePlanningService {
        private final Map<String, Service> services = new HashMap<>();

        void register(Service service) {
            Objects.requireNonNull(service, "service");
            if (services.putIfAbsent(service.name(), service) != null) {
                throw new IllegalArgumentException(
                    "Duplicate service: " + service.name()
                );
            }
        }

        BuildReport plan(String target) {
            if (!services.containsKey(target)) {
                throw new IllegalArgumentException("Unknown target: " + target);
            }

            Map<String, ComponentState> states = new HashMap<>();
            Map<String, Integer> durationCache = new HashMap<>();
            List<String> order = new ArrayList<>();

            int duration = visit(target, states, durationCache, order);
            return new BuildReport(order, duration);
        }

        private int visit(
            String name,
            Map<String, ComponentState> states,
            Map<String, Integer> durationCache,
            List<String> order
        ) {
            ComponentState state = states.getOrDefault(
                name, ComponentState.UNVISITED
            );

            if (state == ComponentState.VISITING) {
                throw new DependencyCycleException(
                    "Dependency cycle detected at " + name
                );
            }

            if (state == ComponentState.COMPLETE) {
                return durationCache.get(name);
            }

            Service service = services.get(name);
            if (service == null) {
                throw new IllegalArgumentException(
                    "Missing dependency registration: " + name
                );
            }

            states.put(name, ComponentState.VISITING);
            int longestDependency = 0;

            for (String dependency : service.dependencies()) {
                int duration = visit(
                    dependency, states, durationCache, order
                );
                longestDependency = Math.max(longestDependency, duration);
            }

            // The duration is a critical-path estimate, not the sum of all
            // build times, because independent dependencies may run in parallel.
            int total = Math.addExact(service.buildMinutes(), longestDependency);
            durationCache.put(name, total);
            states.put(name, ComponentState.COMPLETE);
            order.add(name);
            return total;
        }
    }

    static long sumNested(List<?> values) {
        long total = 0;
        for (Object value : values) {
            if (value instanceof Integer number) {
                total = Math.addExact(total, number.longValue());
            } else if (value instanceof List<?> nested) {
                total = Math.addExact(total, sumNested(nested));
            } else {
                throw new IllegalArgumentException(
                    "Expected an integer or nested list"
                );
            }
        }
        return total;
    }

    static long fibonacciMemoized(
        int n, Map<Integer, Long> cache
    ) {
        if (n < 0) {
            throw new IllegalArgumentException("n must be non-negative");
        }
        if (n <= 1) return n;

        Long cached = cache.get(n);
        if (cached != null) return cached;

        long value = Math.addExact(
            fibonacciMemoized(n - 1, cache),
            fibonacciMemoized(n - 2, cache)
        );
        cache.put(n, value);
        return value;
    }

    static long factorial(int n) {
        if (n < 0) {
            throw new IllegalArgumentException("n must be non-negative");
        }
        if (n <= 1) return 1;
        return Math.multiplyExact(n, factorial(n - 1));
    }

    static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        ReleasePlanningService planner = new ReleasePlanningService();
        planner.register(new Service("database", List.of(), 8));
        planner.register(new Service("cache", List.of(), 3));
        planner.register(new Service("identity", List.of("database"), 5));
        planner.register(new Service("api", List.of("database", "cache"), 12));
        planner.register(new Service("web-app", List.of("api", "identity"), 7));

        BuildReport report = planner.plan("web-app");
        System.out.println("Release dependency-first order: "
            + report.dependencyFirstOrder());
        System.out.println("Estimated critical path: "
            + report.criticalPathMinutes() + " minutes");

        List<?> configuration = List.of(
            120, List.of(55, List.of(13)), 8
        );
        System.out.println("Nested configuration total: "
            + sumNested(configuration));

        Map<Integer, Long> cache = new HashMap<>();
        System.out.println("Fibonacci(40): " + fibonacciMemoized(40, cache));
        System.out.println("Cached subproblems: " + cache.size());
        System.out.println("Factorial(10): " + factorial(10));

        ReleasePlanningService invalidPlanner = new ReleasePlanningService();
        invalidPlanner.register(new Service("service-a", List.of("service-b"), 2));
        invalidPlanner.register(new Service("service-b", List.of("service-a"), 4));

        try {
            invalidPlanner.plan("service-a");
            throw new AssertionError("A dependency cycle must fail");
        } catch (DependencyCycleException expected) {
            System.out.println("Rejected cyclic release plan: "
                + expected.getMessage());
        }

        try {
            factorial(100);
            throw new AssertionError("Overflow must be detected");
        } catch (ArithmeticException expected) {
            System.out.println("Rejected overflowing factorial");
        }

        require(report.dependencyFirstOrder().get(
            report.dependencyFirstOrder().size() - 1
        ).equals("web-app"), "Target must be built after its dependencies");
        require(sumNested(configuration) == 196, "Nested sum mismatch");
        require(fibonacciMemoized(10, new HashMap<>()) == 55,
            "Fibonacci result mismatch");

        System.out.println("Enterprise planning checks passed.");
    }
}
