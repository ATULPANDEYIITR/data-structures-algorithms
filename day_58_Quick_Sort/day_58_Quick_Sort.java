import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;
import java.util.Random;

public class QuickSortGovernance {

    enum PivotStrategy {
        FIRST,
        LAST,
        MIDDLE,
        MEDIAN_OF_THREE,
        RANDOM
    }

    enum PartitionStrategy {
        LOMUTO,
        HOARE
    }

    record SortStats(
        long comparisons,
        long swaps,
        long partitions,
        int maxStackDepth
    ) {}

    record Range(int low, int high) {}

    interface PivotPolicy {
        int choose(int[] values, int low, int high, SortStatsBuilder stats);
    }

    static final class SortStatsBuilder {
        long comparisons;
        long swaps;
        long partitions;
        int maxStackDepth;

        SortStats build() {
            return new SortStats(
                comparisons,
                swaps,
                partitions,
                maxStackDepth
            );
        }
    }

    static final class QuickSortService {
        private final PivotStrategy pivotStrategy;
        private final PartitionStrategy partitionStrategy;
        private final Random random;

        QuickSortService(
            PivotStrategy pivotStrategy,
            PartitionStrategy partitionStrategy,
            long seed
        ) {
            this.pivotStrategy = pivotStrategy;
            this.partitionStrategy = partitionStrategy;
            this.random = new Random(seed);
        }

        SortStats sort(int[] values) {
            if (values == null) {
                throw new IllegalArgumentException("Input cannot be null.");
            }

            SortStatsBuilder stats = new SortStatsBuilder();

            if (values.length < 2) {
                return stats.build();
            }

            Deque<Range> work = new ArrayDeque<>();
            work.push(new Range(0, values.length - 1));

            while (!work.isEmpty()) {
                stats.maxStackDepth =
                    Math.max(stats.maxStackDepth, work.size());

                Range current = work.pop();

                if (current.low() >= current.high()) {
                    continue;
                }

                stats.partitions++;

                if (partitionStrategy == PartitionStrategy.LOMUTO) {
                    int pivotIndex = choosePivot(
                        values,
                        current.low(),
                        current.high(),
                        stats
                    );

                    int split = lomuto(
                        values,
                        current.low(),
                        current.high(),
                        pivotIndex,
                        stats
                    );

                    Range left = new Range(
                        current.low(),
                        split - 1
                    );

                    Range right = new Range(
                        split + 1,
                        current.high()
                    );

                    pushSmallerFirst(work, left, right);
                } else {
                    int pivotIndex = choosePivot(
                        values,
                        current.low(),
                        current.high(),
                        stats
                    );

                    int split = hoare(
                        values,
                        current.low(),
                        current.high(),
                        values[pivotIndex],
                        stats
                    );

                    Range left = new Range(
                        current.low(),
                        split
                    );

                    Range right = new Range(
                        split + 1,
                        current.high()
                    );

                    pushSmallerFirst(work, left, right);
                }
            }

            return stats.build();
        }

        private void pushSmallerFirst(
            Deque<Range> work,
            Range left,
            Range right
        ) {
            int leftSize = rangeSize(left);
            int rightSize = rangeSize(right);

            // The larger partition is pushed first so the smaller one is
            // processed first. This limits the explicit stack size.
            if (leftSize < rightSize) {
                pushIfValid(work, right);
                pushIfValid(work, left);
            } else {
                pushIfValid(work, left);
                pushIfValid(work, right);
            }
        }

        private static int rangeSize(Range range) {
            if (range.low() > range.high()) {
                return 0;
            }

            return range.high() - range.low() + 1;
        }

        private static void pushIfValid(
            Deque<Range> work,
            Range range
        ) {
            if (range.low() < range.high()) {
                work.push(range);
            }
        }

        private int choosePivot(
            int[] values,
            int low,
            int high,
            SortStatsBuilder stats
        ) {
            return switch (pivotStrategy) {
                case FIRST -> low;
                case LAST -> high;
                case MIDDLE -> low + (high - low) / 2;
                case RANDOM -> low + random.nextInt(high - low + 1);
                case MEDIAN_OF_THREE -> {
                    int middle = low + (high - low) / 2;
                    int a = values[low];
                    int b = values[middle];
                    int c = values[high];

                    stats.comparisons += 3;

                    if ((a <= b && b <= c) || (c <= b && b <= a)) {
                        yield middle;
                    }

                    if ((b <= a && a <= c) || (c <= a && a <= b)) {
                        yield low;
                    }

                    yield high;
                }
            };
        }

        private static void swap(
            int[] values,
            int i,
            int j,
            SortStatsBuilder stats
        ) {
            if (i != j) {
                int temp = values[i];
                values[i] = values[j];
                values[j] = temp;
                stats.swaps++;
            }
        }

        private static int lomuto(
            int[] values,
            int low,
            int high,
            int pivotIndex,
            SortStatsBuilder stats
        ) {
            swap(values, pivotIndex, high, stats);
            int pivot = values[high];
            int store = low;

            for (int i = low; i < high; i++) {
                stats.comparisons++;

                if (values[i] <= pivot) {
                    swap(values, i, store, stats);
                    store++;
                }
            }

            swap(values, store, high, stats);
            return store;
        }

        private static int hoare(
            int[] values,
            int low,
            int high,
            int pivot,
            SortStatsBuilder stats
        ) {
            int i = low - 1;
            int j = high + 1;

            while (true) {
                do {
                    i++;
                    stats.comparisons++;
                } while (values[i] < pivot);

                do {
                    j--;
                    stats.comparisons++;
                } while (values[j] > pivot);

                if (i >= j) {
                    return j;
                }

                swap(values, i, j, stats);
            }
        }
    }

    record SortRequest(
        String name,
        int[] values,
        QuickSortService service
    ) {}

    static void execute(SortRequest request) {
        int[] expected = request.values().clone();
        Arrays.sort(expected);

        SortStats stats = request.service().sort(request.values());

        if (!Arrays.equals(request.values(), expected)) {
            throw new IllegalStateException(
                request.name() + ": sorting invariant failed"
            );
        }

        System.out.printf(
            "%s | size=%d | comparisons=%d | swaps=%d | " +
            "partitions=%d | maxStackDepth=%d%n",
            request.name(),
            request.values().length,
            stats.comparisons(),
            stats.swaps(),
            stats.partitions(),
            stats.maxStackDepth()
        );
    }

    public static void main(String[] args) {
        QuickSortService service = new QuickSortService(
            PivotStrategy.MEDIAN_OF_THREE,
            PartitionStrategy.HOARE,
            42
        );

        List<int[]> examples = List.of(
            new int[] {},
            new int[] {5},
            new int[] {3, 1, 4, 1, 5, 9, 2, 6},
            new int[] {7, 7, 7, 7},
            new int[] {5, 4, 3, 2, 1},
            new int[] {-4, 9, 0, -7, 3, 3, 1}
        );

        for (int i = 0; i < examples.size(); i++) {
            execute(new SortRequest(
                "example-" + (i + 1),
                examples.get(i),
                service
            ));
        }

        int[] randomValues = new Random(10)
            .ints(10_000, -100_000, 100_001)
            .toArray();

        execute(new SortRequest("random", randomValues, service));

        int[] sorted = new Random(1)
            .ints(10_000, 0, 10_000)
            .sorted()
            .toArray();

        execute(new SortRequest("sorted", sorted, service));

        int[] reverse = new int[10_000];
        for (int i = 0; i < reverse.length; i++) {
            reverse[i] = reverse.length - i;
        }

        execute(new SortRequest("reverse-sorted", reverse, service));

        int[] duplicates = new int[10_000];
        Arrays.fill(duplicates, 7);
        execute(new SortRequest("duplicates", duplicates, service));

        System.out.println("\nPivot policy comparison");

        for (PivotStrategy strategy : PivotStrategy.values()) {
            QuickSortService policy = new QuickSortService(
                strategy,
                PartitionStrategy.HOARE,
                42
            );

            int[] input = new int[10_000];
            for (int i = 0; i < input.length; i++) {
                input[i] = i;
            }

            SortStats stats = policy.sort(input);

            System.out.printf(
                "%-18s comparisons=%d maxStackDepth=%d%n",
                strategy,
                stats.comparisons(),
                stats.maxStackDepth()
            );
        }

        QuickSortService lomuto = new QuickSortService(
            PivotStrategy.MEDIAN_OF_THREE,
            PartitionStrategy.LOMUTO,
            42
        );

        execute(new SortRequest(
            "lomuto-policy",
            new int[] {10, 4, 8, 3, 7, 1, 9, 2, 6, 5},
            lomuto
        ));
    }
}
