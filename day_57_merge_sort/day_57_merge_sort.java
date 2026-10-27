import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.Random;

public class MergeSortEnterpriseDemo {

    enum SortOrder {
        ASCENDING,
        DESCENDING
    }

    enum ChangeStatus {
        READY,
        BLOCKED,
        PROCESSED
    }

    record DeploymentChange(
            String changeId,
            String service,
            int riskScore,
            ChangeStatus status
    ) {
        public DeploymentChange {
            if (changeId == null || changeId.isBlank()) {
                throw new IllegalArgumentException("changeId is required");
            }
            if (service == null || service.isBlank()) {
                throw new IllegalArgumentException("service is required");
            }
            if (riskScore < 0 || riskScore > 100) {
                throw new IllegalArgumentException(
                        "riskScore must be between 0 and 100"
                );
            }
            Objects.requireNonNull(status, "status is required");
        }
    }

    record SortMetrics(
            long comparisons,
            long merges,
            long elapsedNanoseconds
    ) {}

    static final class MergeSortException extends RuntimeException {
        MergeSortException(String message) {
            super(message);
        }
    }

    interface MergeObserver<T> {
        void afterMerge(List<T> values, int left, int middle, int right);
    }

    static final class MergeSortService<T> {
        private final Comparator<T> comparator;
        private final MergeObserver<T> observer;
        private long comparisons;
        private long merges;

        MergeSortService(
                Comparator<T> comparator,
                MergeObserver<T> observer
        ) {
            this.comparator = Objects.requireNonNull(comparator);
            this.observer = Objects.requireNonNull(observer);
        }

        List<T> sort(List<T> input) {
            if (input == null) {
                throw new MergeSortException("Input cannot be null.");
            }

            List<T> values = new ArrayList<>(input);

            if (values.size() < 2) {
                return values;
            }

            comparisons = 0;
            merges = 0;

            List<T> buffer = new ArrayList<>(values);

            long start = System.nanoTime();

            sortRange(values, buffer, 0, values.size() - 1);

            long elapsed = System.nanoTime() - start;

            System.out.printf(
                    "Sort metrics: comparisons=%d, merges=%d, time=%d ns%n",
                    comparisons,
                    merges,
                    elapsed
            );

            return List.copyOf(values);
        }

        SortMetrics sortWithMetrics(List<T> input) {
            if (input == null) {
                throw new MergeSortException("Input cannot be null.");
            }

            List<T> values = new ArrayList<>(input);
            comparisons = 0;
            merges = 0;

            if (values.size() < 2) {
                return new SortMetrics(0, 0, 0);
            }

            List<T> buffer = new ArrayList<>(values);
            long start = System.nanoTime();

            sortRange(values, buffer, 0, values.size() - 1);

            return new SortMetrics(
                    comparisons,
                    merges,
                    System.nanoTime() - start
            );
        }

        private void sortRange(
                List<T> values,
                List<T> buffer,
                int left,
                int right
        ) {
            if (left >= right) {
                return;
            }

            int middle = left + (right - left) / 2;

            sortRange(values, buffer, left, middle);
            sortRange(values, buffer, middle + 1, right);

            comparisons++;
            if (comparator.compare(values.get(middle + 1), values.get(middle)) >= 0) {
                return;
            }

            merge(values, buffer, left, middle, right);
        }

        private void merge(
                List<T> values,
                List<T> buffer,
                int left,
                int middle,
                int right
        ) {
            merges++;

            int i = left;
            int j = middle + 1;
            int k = left;

            while (i <= middle && j <= right) {
                comparisons++;

                // Equality selects the left side and therefore preserves
                // the relative order of equivalent records.
                if (comparator.compare(values.get(i), values.get(j)) <= 0) {
                    buffer.set(k++, values.get(i++));
                } else {
                    buffer.set(k++, values.get(j++));
                }
            }

            while (i <= middle) {
                buffer.set(k++, values.get(i++));
            }

            while (j <= right) {
                buffer.set(k++, values.get(j++));
            }

            for (int index = left; index <= right; index++) {
                values.set(index, buffer.get(index));
            }

            observer.afterMerge(values, left, middle, right);
        }
    }

    static final class GovernancePolicy {
        private final int maximumRiskForAutomaticProcessing;

        GovernancePolicy(int maximumRiskForAutomaticProcessing) {
            if (maximumRiskForAutomaticProcessing < 0
                    || maximumRiskForAutomaticProcessing > 100) {
                throw new IllegalArgumentException(
                        "Risk threshold must be between 0 and 100"
                );
            }

            this.maximumRiskForAutomaticProcessing =
                    maximumRiskForAutomaticProcessing;
        }

        boolean permits(DeploymentChange change) {
            return change.status() == ChangeStatus.READY
                    && change.riskScore() <= maximumRiskForAutomaticProcessing;
        }
    }

    static void validateAscending(List<Integer> values) {
        for (int i = 1; i < values.size(); i++) {
            if (values.get(i - 1) > values.get(i)) {
                throw new AssertionError("Values are not sorted.");
            }
        }
    }

    static void demonstrateRiskOrdering() {
        List<DeploymentChange> changes = List.of(
                new DeploymentChange("CHG-101", "identity", 80, ChangeStatus.READY),
                new DeploymentChange("CHG-102", "billing", 30, ChangeStatus.READY),
                new DeploymentChange("CHG-103", "audit", 80, ChangeStatus.READY),
                new DeploymentChange("CHG-104", "gateway", 20, ChangeStatus.BLOCKED),
                new DeploymentChange("CHG-105", "notifications", 30, ChangeStatus.READY)
        );

        GovernancePolicy policy = new GovernancePolicy(80);

        List<DeploymentChange> eligible = changes.stream()
                .filter(policy::permits)
                .toList();

        MergeSortService<DeploymentChange> service =
                new MergeSortService<>(
                        Comparator.comparingInt(DeploymentChange::riskScore),
                        (values, left, middle, right) -> {
                            // Observer is intentionally lightweight so merge
                            // performance is not dominated by logging.
                        }
                );

        List<DeploymentChange> sorted =
                service.sort(eligible);

        System.out.println("Risk-ordered eligible changes:");

        for (DeploymentChange change : sorted) {
            System.out.printf(
                    "  %s %s risk=%d%n",
                    change.changeId(),
                    change.service(),
                    change.riskScore()
            );
        }

        // CHG-102 must remain before CHG-105 because both have risk 30.
        if (!sorted.get(0).changeId().equals("CHG-102")
                || !sorted.get(1).changeId().equals("CHG-105")) {
            throw new AssertionError("Stable ordering failed.");
        }
    }

    static void demonstratePrimitiveOrdering() {
        List<Integer> values = new ArrayList<>(
                List.of(10, -2, 7, 4, 0, 10, 1)
        );

        MergeSortService<Integer> service =
                new MergeSortService<>(
                        Integer::compare,
                        (v, left, middle, right) -> {}
                );

        List<Integer> sorted = service.sort(values);

        validateAscending(sorted);

        System.out.println("Sorted integers: " + sorted);
    }

    static void demonstrateEdgeCases() {
        MergeSortService<Integer> service =
                new MergeSortService<>(
                        Integer::compare,
                        (v, left, middle, right) -> {}
                );

        if (!service.sort(List.of()).isEmpty()) {
            throw new AssertionError("Empty input failed.");
        }

        if (!service.sort(List.of(7)).equals(List.of(7))) {
            throw new AssertionError("Singleton input failed.");
        }

        if (!service.sort(List.of(4, 4, 4)).equals(List.of(4, 4, 4))) {
            throw new AssertionError("Duplicate handling failed.");
        }

        System.out.println("Edge cases: PASSED");
    }

    static void performanceTest() {
        Random random = new Random(42);
        List<Integer> values = new ArrayList<>();

        for (int i = 0; i < 50_000; i++) {
            values.add(random.nextInt(2_000_001) - 1_000_000);
        }

        MergeSortService<Integer> service =
                new MergeSortService<>(
                        Integer::compare,
                        (v, left, middle, right) -> {}
                );

        SortMetrics metrics = service.sortWithMetrics(values);

        List<Integer> sorted = service.sort(values);
        validateAscending(sorted);

        System.out.println(
                "Performance metrics: " +
                "comparisons=" + metrics.comparisons() +
                ", merges=" + metrics.merges() +
                ", time=" + metrics.elapsedNanoseconds() + " ns"
        );
    }

    public static void main(String[] args) {
        try {
            demonstratePrimitiveOrdering();
            demonstrateRiskOrdering();
            demonstrateEdgeCases();
            performanceTest();

            System.out.println("All Java 17 merge-sort tests passed.");
        } catch (RuntimeException | AssertionError error) {
            System.err.println("Failure: " + error.getMessage());
            System.exit(1);
        }
    }
}
