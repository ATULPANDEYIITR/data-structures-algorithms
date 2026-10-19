import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/*
 * Enterprise case study: service deployment planning.
 *
 * A deployment request contains services that must be placed into available
 * zones. Each service has compatibility constraints and zone restrictions.
 * The DeploymentPlanner explores candidate assignments, rejects invalid
 * partial states early, and restores mutable state after each branch.
 *
 * Java records provide immutable domain values while the planner owns the
 * mutable search state. This separates domain representation from the
 * mechanics of recursive exploration.
 */
public class BacktrackingIntroduction {

    enum Environment {
        PRIMARY,
        SECONDARY,
        DR
    }

    record Service(
        String name,
        Set<Environment> allowedEnvironments,
        Set<String> incompatibleServices
    ) {
        Service {
            Objects.requireNonNull(name);
            allowedEnvironments = Set.copyOf(allowedEnvironments);
            incompatibleServices = Set.copyOf(incompatibleServices);
        }
    }

    record Deployment(
        String service,
        Environment environment
    ) {}

    record SearchMetrics(
        int visitedStates,
        int prunedBranches,
        int solutions
    ) {}

    static final class DeploymentPlanner {
        private final List<Service> services;
        private final List<Environment> environments;
        private final Map<String, Service> byName;

        private final Map<String, Environment> currentAssignment =
                new HashMap<>();

        private final List<Map<String, Environment>> solutions =
                new ArrayList<>();

        private int visitedStates;
        private int prunedBranches;

        DeploymentPlanner(
                List<Service> services,
                List<Environment> environments
        ) {
            if (services.isEmpty()) {
                throw new IllegalArgumentException(
                        "At least one service is required"
                );
            }

            this.services = List.copyOf(services);
            this.environments = List.copyOf(environments);

            this.byName = new HashMap<>();

            for (Service service : services) {
                if (byName.put(service.name(), service) != null) {
                    throw new IllegalArgumentException(
                            "Duplicate service: " + service.name()
                    );
                }
            }

            validateReferences();
        }

        private void validateReferences() {
            for (Service service : services) {
                for (String incompatible : service.incompatibleServices()) {
                    if (!byName.containsKey(incompatible)) {
                        throw new IllegalArgumentException(
                                "Unknown incompatible service: " + incompatible
                        );
                    }
                }
            }
        }

        private boolean violatesCompatibility(Service service) {
            for (String assignedService : currentAssignment.keySet()) {
                if (service.incompatibleServices().contains(assignedService)
                        || byName.get(assignedService)
                        .incompatibleServices()
                        .contains(service.name())) {
                    return true;
                }
            }

            return false;
        }

        private List<Environment> legalEnvironments(Service service) {
            List<Environment> result = new ArrayList<>();

            for (Environment environment : environments) {
                if (!service.allowedEnvironments().contains(environment)) {
                    continue;
                }

                /*
                 * The enterprise policy allows at most one service in each
                 * environment for this simplified deployment scenario.
                 * This is a state constraint rather than a final-result
                 * check, so illegal branches are stopped immediately.
                 */
                if (currentAssignment.containsValue(environment)) {
                    continue;
                }

                result.add(environment);
            }

            return result;
        }

        private Service chooseMostConstrainedService() {
            Service best = null;
            int smallestDomain = Integer.MAX_VALUE;

            for (Service service : services) {
                if (currentAssignment.containsKey(service.name())) {
                    continue;
                }

                int legalCount = legalEnvironments(service).size();

                if (legalCount < smallestDomain) {
                    smallestDomain = legalCount;
                    best = service;
                }
            }

            return best;
        }

        private void search() {
            visitedStates++;

            if (currentAssignment.size() == services.size()) {
                solutions.add(Map.copyOf(currentAssignment));
                return;
            }

            Service service = chooseMostConstrainedService();

            if (service == null) {
                prunedBranches++;
                return;
            }

            if (violatesCompatibility(service)) {
                prunedBranches++;
                return;
            }

            List<Environment> choices = legalEnvironments(service);

            if (choices.isEmpty()) {
                prunedBranches++;
                return;
            }

            for (Environment environment : choices) {
                currentAssignment.put(service.name(), environment);

                search();

                /*
                 * Removing the assignment restores the exact parent state.
                 * Forgetting this undo operation would cause sibling branches
                 * to incorrectly inherit decisions from earlier branches.
                 */
                currentAssignment.remove(service.name());
            }
        }

        List<Map<String, Environment>> solve() {
            currentAssignment.clear();
            solutions.clear();
            visitedStates = 0;
            prunedBranches = 0;

            search();
            return List.copyOf(solutions);
        }

        SearchMetrics metrics() {
            return new SearchMetrics(
                    visitedStates,
                    prunedBranches,
                    solutions.size()
            );
        }
    }

    static void printAssignments(
            List<Map<String, Environment>> solutions
    ) {
        for (Map<String, Environment> solution : solutions) {
            System.out.println(solution);
        }
    }

    public static void main(String[] args) {
        List<Service> services = List.of(
                new Service(
                        "identity",
                        EnumSet.of(Environment.PRIMARY, Environment.DR),
                        Set.of("billing")
                ),
                new Service(
                        "billing",
                        EnumSet.of(Environment.SECONDARY, Environment.DR),
                        Set.of("identity")
                ),
                new Service(
                        "catalog",
                        EnumSet.of(
                                Environment.PRIMARY,
                                Environment.SECONDARY
                        ),
                        Set.of()
                ),
                new Service(
                        "audit",
                        EnumSet.of(
                                Environment.PRIMARY,
                                Environment.SECONDARY,
                                Environment.DR
                        ),
                        Set.of()
                )
        );

        DeploymentPlanner planner = new DeploymentPlanner(
                services,
                List.of(
                        Environment.PRIMARY,
                        Environment.SECONDARY,
                        Environment.DR
                )
        );

        List<Map<String, Environment>> solutions = planner.solve();

        System.out.println("Valid deployment plans:");
        printAssignments(solutions);

        SearchMetrics metrics = planner.metrics();

        System.out.println();
        System.out.println("Visited states: " + metrics.visitedStates());
        System.out.println("Pruned branches: " + metrics.prunedBranches());
        System.out.println("Complete plans: " + metrics.solutions());

        /*
         * A key design decision is the most-constrained-service heuristic.
         * Choosing the service with the smallest legal domain exposes
         * contradictions early and can reduce the number of recursive calls.
         *
         * Worst-case search remains exponential because each unresolved
         * service can branch into multiple environments. Constraint pruning
         * improves practical performance but does not remove that worst case.
         */
    }
}
