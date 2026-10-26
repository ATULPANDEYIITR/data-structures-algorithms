import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;

public class ElementarySortingStudy {

    enum Algorithm {
        BUBBLE,
        SELECTION,
        INSERTION
    }

    record SortStats(
            long comparisons,
            long swaps,
            long writes,
            long nanoseconds
    ) {
        double milliseconds() {
            return nanoseconds / 1_000_000.0;
        }
    }

    record SortResult(
            List<Integer> values,
            SortStats stats
    ) {}

    static final class SortingException extends RuntimeException {
        SortingException(String message) {
            super(message);
        }
    }

    interface Sorter {
        SortResult sort(List<Integer> input);
    }

    static final class SortingService {
        private final Map<Algorithm, Sorter> sorters =
                new EnumMap<>(Algorithm.class);

        SortingService() {
            sorters.put(Algorithm.BUBBLE, this::bubbleSort);
            sorters.put(Algorithm.SELECTION, this::selectionSort);
            sorters.put(Algorithm.INSERTION, this::insertionSort);
        }

        SortResult sort(Algorithm algorithm, List<Integer> input) {
            Objects.requireNonNull(algorithm, "Algorithm is required.");
            return sorters.get(algorithm).sort(input);
        }

        private List<Integer> validateAndCopy(List<Integer> input) {
            if (input == null) {
                throw new SortingException("Input cannot be null.");
            }

            List<Integer> copy = new ArrayList<>(input);

            if (copy.stream().anyMatch(Objects::isNull)) {
                throw new SortingException(
                        "Null values are not supported."
                );
            }

            return copy;
        }

        private SortResult bubbleSort(List<Integer> input) {
            List<Integer> data = validateAndCopy(input);
            long comparisons = 0;
            long swaps = 0;
            long writes = 0;

            long start = System.nanoTime();

            for (int end = data.size() - 1; end > 0; end--) {
                boolean changed = false;

                for (int i = 0; i < end; i++) {
                    comparisons++;

                    if (data.get(i) > data.get(i + 1)) {
                        Collections.swap(data, i, i + 1);
                        swaps++;
                        writes += 2;
                        changed = true;
                    }
                }

                if (!changed) {
                    break;
                }
            }

            return result(
                    data,
                    comparisons,
                    swaps,
                    writes,
                    start
            );
        }

        private SortResult selectionSort(List<Integer> input) {
            List<Integer> data = validateAndCopy(input);
            long comparisons = 0;
            long swaps = 0;
            long writes = 0;

            long start = System.nanoTime();

            for (int i = 0; i < data.size() - 1; i++) {
                int minimum = i;

                for (int j = i + 1; j < data.size(); j++) {
                    comparisons++;

                    if (data.get(j) < data.get(minimum)) {
                        minimum = j;
                    }
                }

                if (minimum != i) {
                    Collections.swap(data, i, minimum);
                    swaps++;
                    writes += 2;
                }
            }

            return result(
                    data,
                    comparisons,
                    swaps,
                    writes,
                    start
            );
        }

        private SortResult insertionSort(List<Integer> input) {
            List<Integer> data = validateAndCopy(input);
            long comparisons = 0;
            long swaps = 0;
            long writes = 0;

            long start = System.nanoTime();

            for (int i = 1; i < data.size(); i++) {
                int key = data.get(i);
                writes++;

                int j = i - 1;

                while (j >= 0) {
                    comparisons++;

                    if (data.get(j) <= key) {
                        break;
                    }

                    data.set(j + 1, data.get(j));
                    writes++;
                    j--;
                }

                data.set(j + 1, key);
                writes++;
            }

            return result(
                    data,
                    comparisons,
                    swaps,
                    writes,
                    start
            );
        }

        private SortResult result(
                List<Integer> data,
                long comparisons,
                long swaps,
                long writes,
                long start
        ) {
            return new SortResult(
                    List.copyOf(data),
                    new SortStats(
                            comparisons,
                            swaps,
                            writes,
                            System.nanoTime() - start
                    )
            );
        }
    }

    static final class GovernanceStyleReport {
        private final SortingService service;

        GovernanceStyleReport(SortingService service) {
            this.service = service;
        }

        void print(String dataset, Algorithm algorithm, List<Integer> values) {
            SortResult result = service.sort(algorithm, values);
            SortStats s = result.stats();

            System.out.printf(
                    "%-16s %-17s %12d %10d %10d %12.3f%n",
                    dataset,
                    algorithm,
                    s.comparisons(),
                    s.swaps(),
                    s.writes(),
                    s.milliseconds()
            );
        }
    }

    public static void main(String[] args) {
        SortingService service = new SortingService();

        runCorrectnessTests(service);

        Map<String, List<Integer>> datasets = createDatasets(250);

        System.out.printf(
                "%-16s %-17s %12s %10s %10s %12s%n",
                "Dataset",
                "Algorithm",
                "Comparisons",
                "Swaps",
                "Writes",
                "Time ms"
        );

        System.out.println("-".repeat(82));

        GovernanceStyleReport report = new GovernanceStyleReport(service);

        for (Map.Entry<String, List<Integer>> entry : datasets.entrySet()) {
            for (Algorithm algorithm : Algorithm.values()) {
                report.print(
                        entry.getKey(),
                        algorithm,
                        entry.getValue()
                );
            }
        }

        List<Integer> example = List.of(5, 2, 4, 1, 3);

        System.out.println("\nExample input: " + example);

        for (Algorithm algorithm : Algorithm.values()) {
            System.out.println(
                    algorithm + ": " +
                    service.sort(algorithm, example).values()
            );
        }

        try {
            service.sort(Algorithm.INSERTION, Arrays.asList(3, null, 1));
        } catch (SortingException exception) {
            System.out.println(
                    "\nValidation failure: " + exception.getMessage()
            );
        }

        System.out.println("\nComplexity characteristics:");
        System.out.println(
                "Bubble Sort: best O(n) with early exit; average/worst O(n^2)."
        );
        System.out.println(
                "Selection Sort: O(n^2) regardless of input order."
        );
        System.out.println(
                "Insertion Sort: best O(n); average/worst O(n^2)."
        );
        System.out.println(
                "Each implementation uses O(1) auxiliary algorithmic space."
        );
        System.out.println(
                "Insertion Sort is useful when input is small or nearly sorted."
        );
    }

    private static void runCorrectnessTests(SortingService service) {
        List<List<Integer>> cases = List.of(
                List.of(),
                List.of(1),
                List.of(2, 1),
                List.of(1, 2, 3, 4),
                List.of(4, 3, 2, 1),
                List.of(3, 1, 3, 2, 1, 2),
                List.of(-4, 7, 0, -1, 5)
        );

        for (Algorithm algorithm : Algorithm.values()) {
            for (List<Integer> input : cases) {
                SortResult result = service.sort(algorithm, input);

                if (!isSorted(result.values())) {
                    throw new SortingException(
                            algorithm + " produced unsorted data."
                    );
                }

                if (!sameMultiset(input, result.values())) {
                    throw new SortingException(
                            algorithm + " changed the input values."
                    );
                }

                if (!input.equals(result.values()) && input.size() == 0) {
                    throw new SortingException(
                            "Empty input behavior is inconsistent."
                    );
                }
            }
        }

        System.out.println("Correctness suite: PASS");
    }

    private static boolean isSorted(List<Integer> values) {
        for (int i = 1; i < values.size(); i++) {
            if (values.get(i - 1) > values.get(i)) {
                return false;
            }
        }

        return true;
    }

    private static boolean sameMultiset(
            List<Integer> first,
            List<Integer> second
    ) {
        Map<Integer, Integer> counts = new LinkedHashMap<>();

        for (Integer value : first) {
            counts.merge(value, 1, Integer::sum);
        }

        for (Integer value : second) {
            Integer count = counts.get(value);

            if (count == null) {
                return false;
            }

            if (count == 1) {
                counts.remove(value);
            } else {
                counts.put(value, count - 1);
            }
        }

        return counts.isEmpty();
    }

    private static Map<String, List<Integer>> createDatasets(int size) {
        Map<String, List<Integer>> datasets = new LinkedHashMap<>();

        List<Integer> random = new ArrayList<>();
        long state = 42;

        for (int i = 0; i < size; i++) {
            state = (1664525L * state + 1013904223L) & 0xffffffffL;
            random.add((int) (state % (size * 4L)));
        }

        List<Integer> sorted = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            sorted.add(i);
        }

        List<Integer> reverse = new ArrayList<>(sorted);
        Collections.reverse(reverse);

        List<Integer> duplicates = new ArrayList<>();
        state = 99;

        for (int i = 0; i < size; i++) {
            state = (1664525L * state + 1013904223L) & 0xffffffffL;
            duplicates.add((int) (state % 10));
        }

        List<Integer> nearlySorted = new ArrayList<>(sorted);
        int step = Math.max(1, size / 20);

        for (int i = 0; i + 1 < size; i += step) {
            Collections.swap(nearlySorted, i, i + 1);
        }

        datasets.put("random", random);
        datasets.put("sorted", sorted);
        datasets.put("reverse", reverse);
        datasets.put("duplicates", duplicates);
        datasets.put("nearly sorted", nearlySorted);

        return datasets;
    }
}
