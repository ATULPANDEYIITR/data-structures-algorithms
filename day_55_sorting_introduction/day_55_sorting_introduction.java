import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.function.Function;

public class SortingEnterpriseDemo {

    record SortMetrics(
        String algorithm,
        long comparisons,
        long writes,
        boolean stable,
        boolean inPlace
    ) {}

    record Employee(String name, int departmentRank, int hireOrder) {}

    record SortResult<T>(List<T> values, SortMetrics metrics) {
        SortResult {
            values = List.copyOf(values);
            Objects.requireNonNull(metrics, "metrics");
        }
    }

    interface SortingStrategy<T> {
        SortResult<T> sort(
            List<T> input,
            Comparator<? super T> comparator
        );
    }

    static final class InsertionSort<T> implements SortingStrategy<T> {
        @Override
        public SortResult<T> sort(
            List<T> input,
            Comparator<? super T> comparator
        ) {
            Objects.requireNonNull(input, "input");
            Objects.requireNonNull(comparator, "comparator");

            List<T> values = new ArrayList<>(input);
            long comparisons = 0;
            long writes = 0;

            for (int i = 1; i < values.size(); i++) {
                T current = values.get(i);
                int j = i - 1;

                while (j >= 0) {
                    comparisons++;
                    if (comparator.compare(values.get(j), current) <= 0) {
                        break;
                    }
                    values.set(j + 1, values.get(j));
                    writes++;
                    j--;
                }

                values.set(j + 1, current);
                writes++;
            }

            return new SortResult<>(
                values,
                new SortMetrics(
                    "Insertion sort", comparisons, writes, true, true
                )
            );
        }
    }

    static final class MergeSort<T> implements SortingStrategy<T> {
        private long comparisons;
        private long writes;
        private Comparator<? super T> comparator;

        @Override
        public SortResult<T> sort(
            List<T> input,
            Comparator<? super T> comparator
        ) {
            Objects.requireNonNull(input, "input");
            this.comparator = Objects.requireNonNull(comparator, "comparator");
            this.comparisons = 0;
            this.writes = 0;

            List<T> values = new ArrayList<>(input);
            List<T> sorted = sortRange(values);

            return new SortResult<>(
                sorted,
                new SortMetrics(
                    "Merge sort", comparisons, writes, true, false
                )
            );
        }

        private List<T> sortRange(List<T> values) {
            if (values.size() < 2) {
                return values;
            }

            int middle = values.size() / 2;
            List<T> left = sortRange(
                new ArrayList<>(values.subList(0, middle))
            );
            List<T> right = sortRange(
                new ArrayList<>(values.subList(middle, values.size()))
            );

            List<T> merged = new ArrayList<>(values.size());
            int i = 0;
            int j = 0;

            while (i < left.size() && j < right.size()) {
                comparisons++;
                // Choosing the left item on equality makes the sort stable.
                if (comparator.compare(left.get(i), right.get(j)) <= 0) {
                    merged.add(left.get(i++));
                } else {
                    merged.add(right.get(j++));
                }
                writes++;
            }

            while (i < left.size()) {
                merged.add(left.get(i++));
                writes++;
            }

            while (j < right.size()) {
                merged.add(right.get(j++));
                writes++;
            }

            return merged;
        }
    }

    static final class QuickSort<T> implements SortingStrategy<T> {
        private long comparisons;
        private long writes;
        private Comparator<? super T> comparator;

        @Override
        public SortResult<T> sort(
            List<T> input,
            Comparator<? super T> comparator
        ) {
            Objects.requireNonNull(input, "input");
            this.comparator = Objects.requireNonNull(comparator, "comparator");
            this.comparisons = 0;
            this.writes = 0;

            List<T> values = new ArrayList<>(input);
            sortRange(values, 0, values.size() - 1);

            return new SortResult<>(
                values,
                new SortMetrics(
                    "Three-way quicksort", comparisons, writes, false, true
                )
            );
        }

        private void sortRange(List<T> values, int low, int high) {
            while (low < high) {
                T pivot = values.get(low + (high - low) / 2);
                int less = low;
                int current = low;
                int greater = high;

                while (current <= greater) {
                    T item = values.get(current);
                    comparisons++;

                    if (comparator.compare(item, pivot) < 0) {
                        swap(values, less++, current++);
                    } else {
                        comparisons++;
                        if (comparator.compare(item, pivot) > 0) {
                            swap(values, current, greater--);
                        } else {
                            current++;
                        }
                    }
                }

                // Recurse into the smaller side to constrain stack growth.
                if (less - low < high - greater) {
                    sortRange(values, low, less - 1);
                    low = greater + 1;
                } else {
                    sortRange(values, greater + 1, high);
                    high = less - 1;
                }
            }
        }

        private void swap(List<T> values, int i, int j) {
            if (i == j) {
                return;
            }
            T temporary = values.get(i);
            values.set(i, values.get(j));
            values.set(j, temporary);
            writes += 2;
        }
    }

    static <T> void verifySorted(
        List<T> values,
        Comparator<? super T> comparator
    ) {
        for (int i = 1; i < values.size(); i++) {
            if (comparator.compare(values.get(i - 1), values.get(i)) > 0) {
                throw new IllegalStateException("Output is not sorted.");
            }
        }
    }

    static <T> void printResult(
        SortResult<T> result,
        Comparator<? super T> comparator
    ) {
        verifySorted(result.values(), comparator);
        System.out.println(result.metrics());
        System.out.println(result.values());
    }

    public static void main(String[] args) {
        Comparator<Integer> natural = Comparator.naturalOrder();
        List<List<Integer>> samples = List.of(
            List.of(),
            List.of(1),
            List.of(5, 2, 4, 1, 3),
            List.of(4, 4, 4, 4),
            List.of(9, -2, 0, 7, -2)
        );

        List<SortingStrategy<Integer>> strategies = List.of(
            new InsertionSort<>(),
            new MergeSort<>(),
            new QuickSort<>()
        );

        for (List<Integer> sample : samples) {
            System.out.println("\nInput: " + sample);
            List<Integer> expected = new ArrayList<>(sample);
            expected.sort(natural);

            for (SortingStrategy<Integer> strategy : strategies) {
                SortResult<Integer> result = strategy.sort(sample, natural);
                if (!result.values().equals(expected)) {
                    throw new IllegalStateException(
                        "Incorrect result from " + result.metrics().algorithm()
                    );
                }
                printResult(result, natural);
            }
        }

        List<Employee> employees = List.of(
            new Employee("Asha", 2, 1),
            new Employee("Ravi", 1, 2),
            new Employee("Meera", 2, 3),
            new Employee("Kabir", 1, 4),
            new Employee("Isha", 2, 5)
        );

        Comparator<Employee> byDepartment =
            Comparator.comparingInt(Employee::departmentRank);

        SortResult<Employee> stable =
            new MergeSort<Employee>().sort(employees, byDepartment);

        System.out.println("\nStable department ordering:");
        printResult(stable, byDepartment);

        if (!stable.values().get(0).name().equals("Ravi")
            || !stable.values().get(1).name().equals("Kabir")) {
            throw new IllegalStateException(
                "Equal department ranks lost their original order."
            );
        }

        SortResult<Employee> quick =
            new QuickSort<Employee>().sort(employees, byDepartment);

        System.out.println("\nQuicksort department ordering:");
        printResult(quick, byDepartment);

        // The strategies copy their input, so callers retain their original list.
        if (!employees.equals(List.copyOf(employees))) {
            throw new IllegalStateException("Input was unexpectedly modified.");
        }

        System.out.println("\nAll sorting checks passed.");
    }
}
