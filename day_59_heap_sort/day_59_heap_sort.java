import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.Random;

public class HeapSortEnterprise {

    enum HeapType {
        MAX,
        MIN
    }

    enum SortStatus {
        ACCEPTED,
        REJECTED
    }

    record SortPolicy(
            HeapType heapType,
            boolean requireAscending,
            int maximumElements) {

        SortPolicy {
            Objects.requireNonNull(heapType, "heapType");
            if (maximumElements <= 0) {
                throw new IllegalArgumentException(
                        "maximumElements must be positive");
            }
        }
    }

    record SortResult(
            List<Long> values,
            long comparisons,
            long swaps,
            long elapsedNanos,
            SortStatus status) {
    }

    record RepositoryMetric(String metric, long value) {
    }

    static final class InvalidSortRequestException extends RuntimeException {
        InvalidSortRequestException(String message) {
            super(message);
        }
    }

    interface SortingStrategy {
        SortResult sort(List<Long> input, SortPolicy policy);
    }

    static final class HeapSortStrategy implements SortingStrategy {
        private long comparisons;
        private long swaps;

        @Override
        public SortResult sort(List<Long> input, SortPolicy policy) {
            validate(input, policy);

            comparisons = 0;
            swaps = 0;

            final List<Long> values = new ArrayList<>(input);
            final long started = System.nanoTime();

            if (values.size() < 2) {
                return new SortResult(
                        List.copyOf(values),
                        0,
                        0,
                        System.nanoTime() - started,
                        SortStatus.ACCEPTED);
            }

            /*
             * Bottom-up heap construction is O(n). The extraction phase
             * performs n-1 O(log n) root repairs.
             */
            for (int root = values.size() / 2 - 1; root >= 0; root--) {
                siftDown(values, root, values.size(), policy.heapType());
            }

            for (int end = values.size() - 1; end > 0; end--) {
                swap(values, 0, end);
                siftDown(values, 0, end, policy.heapType());
            }

            if (policy.heapType() == HeapType.MIN
                    && policy.requireAscending()) {
                values.sort(Comparator.naturalOrder());
            }

            return new SortResult(
                    List.copyOf(values),
                    comparisons,
                    swaps,
                    System.nanoTime() - started,
                    SortStatus.ACCEPTED);
        }

        private void validate(List<Long> input, SortPolicy policy) {
            if (input == null) {
                throw new InvalidSortRequestException("Input cannot be null.");
            }

            if (input.size() > policy.maximumElements()) {
                throw new InvalidSortRequestException(
                        "Input exceeds configured enterprise limit.");
            }

            if (input.stream().anyMatch(Objects::isNull)) {
                throw new InvalidSortRequestException(
                        "Null elements are not permitted.");
            }
        }

        private void siftDown(
                List<Long> values,
                int root,
                int size,
                HeapType heapType) {

            while (true) {
                int left = root * 2 + 1;
                int right = left + 1;
                int selected = root;

                if (left < size
                        && preferred(values.get(left),
                        values.get(selected), heapType)) {
                    selected = left;
                }

                if (right < size
                        && preferred(values.get(right),
                        values.get(selected), heapType)) {
                    selected = right;
                }

                if (selected == root) {
                    return;
                }

                swap(values, root, selected);
                root = selected;
            }
        }

        private boolean preferred(long first, long second, HeapType type) {
            comparisons++;
            return type == HeapType.MAX ? first > second : first < second;
        }

        private void swap(List<Long> values, int first, int second) {
            Long temporary = values.get(first);
            values.set(first, values.get(second));
            values.set(second, temporary);
            swaps++;
        }
    }

    static final class RepositorySortService {
        private final SortingStrategy strategy;

        RepositorySortService(SortingStrategy strategy) {
            this.strategy = Objects.requireNonNull(strategy);
        }

        SortResult execute(List<Long> commitSizes, SortPolicy policy) {
            if (commitSizes.stream().anyMatch(value -> value < 0)) {
                throw new InvalidSortRequestException(
                        "Commit-size metrics cannot be negative.");
            }

            return strategy.sort(commitSizes, policy);
        }

        List<RepositoryMetric> summarize(SortResult result) {
            return List.of(
                    new RepositoryMetric("comparisons", result.comparisons()),
                    new RepositoryMetric("swaps", result.swaps()),
                    new RepositoryMetric("elapsed_nanos", result.elapsedNanos()),
                    new RepositoryMetric("elements", result.values().size()));
        }
    }

    static void runTests() {
        SortingStrategy strategy = new HeapSortStrategy();
        RepositorySortService service = new RepositorySortService(strategy);

        List<List<Long>> cases = List.of(
                List.of(),
                List.of(1L),
                List.of(2L, 1L),
                List.of(5L, 5L, 5L),
                List.of(-4L, 9L, 0L, -2L, 9L),
                List.of(Long.MIN_VALUE, 0L, Long.MAX_VALUE)
        );

        SortPolicy policy = new SortPolicy(HeapType.MAX, true, 100_000);

        for (List<Long> input : cases) {
            SortResult result = service.execute(input, policy);

            List<Long> expected = new ArrayList<>(input);
            expected.sort(Comparator.naturalOrder());

            if (!result.values().equals(expected)) {
                throw new AssertionError(
                        "Heap sort failed for " + input);
            }
        }

        Random random = new Random(20261029);

        for (int trial = 0; trial < 100; trial++) {
            List<Long> input = new ArrayList<>();

            for (int i = 0; i < random.nextInt(200); i++) {
                input.add((long) random.nextInt(2001) - 1000);
            }

            List<Long> expected = new ArrayList<>(input);
            expected.sort(Comparator.naturalOrder());

            SortResult result = service.execute(input, policy);

            if (!result.values().equals(expected)) {
                throw new AssertionError("Randomized test failed.");
            }
        }

        try {
            service.execute(
                    Arrays.asList(1L, null, 3L),
                    policy);
            throw new AssertionError("Null validation failed.");
        } catch (InvalidSortRequestException expected) {
            // Expected failure state.
        }

        try {
            service.execute(
                    List.of(1L, -4L, 8L),
                    policy);
            throw new AssertionError("Negative metric validation failed.");
        } catch (InvalidSortRequestException expected) {
            // Expected failure state.
        }

        System.out.println("All Java 17 heap-sort tests passed.");
    }

    public static void main(String[] args) {
        runTests();

        List<Long> commits = List.of(
                120L, 35L, 900L, 12L, 450L, 75L, 18L, 300L);

        SortPolicy policy = new SortPolicy(
                HeapType.MAX,
                true,
                100_000);

        RepositorySortService service =
                new RepositorySortService(new HeapSortStrategy());

        SortResult result = service.execute(commits, policy);

        System.out.println("\nSorted repository-change metrics:");
        System.out.println(result.values());
        System.out.println("Comparisons: " + result.comparisons());
        System.out.println("Swaps: " + result.swaps());
        System.out.println("Elapsed ns: " + result.elapsedNanos());

        System.out.println("\nOperational metrics:");

        service.summarize(result)
                .stream()
                .forEach(metric ->
                        System.out.printf(
                                "%-18s %d%n",
                                metric.metric(),
                                metric.value()));

        /*
         * Heap sort is selected here because the service can guarantee
         * O(n log n) worst-case time without allocating an auxiliary
         * array proportional to the input size.
         *
         * The trade-off is that heap sort is not stable and often has
         * poorer cache locality than merge sort or well-engineered
         * quicksort implementations.
         */
    }
}
