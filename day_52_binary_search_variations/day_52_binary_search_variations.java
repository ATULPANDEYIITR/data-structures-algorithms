import java.util.Arrays;
import java.util.List;
import java.util.OptionalInt;

public class BinarySearchVariations {

    static final class SortedReleaseIndex {
        private final int[] releases;

        SortedReleaseIndex(int[] releases) {
            this.releases = Arrays.copyOf(releases, releases.length);

            if (!isSorted(this.releases)) {
                throw new IllegalArgumentException(
                    "Release index must be sorted in ascending order."
                );
            }
        }

        private static boolean isSorted(int[] values) {
            for (int i = 1; i < values.length; i++) {
                if (values[i - 1] > values[i]) {
                    return false;
                }
            }
            return true;
        }

        /*
         * lowerBound returns the first position whose value is >= target.
         * This is the foundation for first occurrence and insertion logic.
         */
        int lowerBound(int target) {
            int left = 0;
            int right = releases.length;

            while (left < right) {
                int mid = left + (right - left) / 2;

                if (releases[mid] < target) {
                    left = mid + 1;
                } else {
                    right = mid;
                }
            }

            return left;
        }

        /*
         * upperBound returns the first position whose value is > target.
         * The difference between upper and lower bounds is the duplicate count.
         */
        int upperBound(int target) {
            int left = 0;
            int right = releases.length;

            while (left < right) {
                int mid = left + (right - left) / 2;

                if (releases[mid] <= target) {
                    left = mid + 1;
                } else {
                    right = mid;
                }
            }

            return left;
        }

        OptionalInt exactSearch(int target) {
            int position = lowerBound(target);

            if (position < releases.length && releases[position] == target) {
                return OptionalInt.of(position);
            }

            return OptionalInt.empty();
        }

        OptionalInt firstOccurrence(int target) {
            return exactSearch(target);
        }

        OptionalInt lastOccurrence(int target) {
            int position = upperBound(target) - 1;

            if (position >= 0 && releases[position] == target) {
                return OptionalInt.of(position);
            }

            return OptionalInt.empty();
        }

        int insertionPosition(int target) {
            return lowerBound(target);
        }

        int occurrenceCount(int target) {
            return upperBound(target) - lowerBound(target);
        }

        String rangeDescription(int target) {
            OptionalInt first = firstOccurrence(target);

            if (first.isEmpty()) {
                return "absent";
            }

            return "[" + first.getAsInt() + ", "
                + lastOccurrence(target).getAsInt() + "]";
        }

        void printAnalysis(int target) {
            String exact = exactSearch(target)
                .stream()
                .mapToObj(String::valueOf)
                .findFirst()
                .orElse("absent");

            String first = firstOccurrence(target)
                .stream()
                .mapToObj(String::valueOf)
                .findFirst()
                .orElse("absent");

            String last = lastOccurrence(target)
                .stream()
                .mapToObj(String::valueOf)
                .findFirst()
                .orElse("absent");

            System.out.println("Target: " + target);
            System.out.println("  exact search:       " + exact);
            System.out.println("  first occurrence:   " + first);
            System.out.println("  last occurrence:    " + last);
            System.out.println("  lower bound:        " + lowerBound(target));
            System.out.println("  upper bound:        " + upperBound(target));
            System.out.println("  insertion position: " + insertionPosition(target));
            System.out.println("  occurrence count:   " + occurrenceCount(target));
            System.out.println("  duplicate range:    " + rangeDescription(target));
            System.out.println();
        }
    }

    private static void verify(
        SortedReleaseIndex index,
        int target,
        int expectedLower,
        int expectedUpper,
        int expectedCount,
        int expectedFirst,
        int expectedLast
    ) {
        if (index.lowerBound(target) != expectedLower) {
            throw new AssertionError("Lower-bound mismatch for " + target);
        }

        if (index.upperBound(target) != expectedUpper) {
            throw new AssertionError("Upper-bound mismatch for " + target);
        }

        if (index.occurrenceCount(target) != expectedCount) {
            throw new AssertionError("Count mismatch for " + target);
        }

        OptionalInt first = index.firstOccurrence(target);
        OptionalInt last = index.lastOccurrence(target);

        if (expectedFirst < 0 && first.isPresent()) {
            throw new AssertionError("Unexpected first occurrence.");
        }

        if (expectedFirst >= 0 &&
            (first.isEmpty() || first.getAsInt() != expectedFirst)) {
            throw new AssertionError("First occurrence mismatch.");
        }

        if (expectedLast < 0 && last.isPresent()) {
            throw new AssertionError("Unexpected last occurrence.");
        }

        if (expectedLast >= 0 &&
            (last.isEmpty() || last.getAsInt() != expectedLast)) {
            throw new AssertionError("Last occurrence mismatch.");
        }
    }

    private static void runTests() {
        SortedReleaseIndex index =
            new SortedReleaseIndex(new int[]{1, 1, 1, 3, 5, 5, 8});

        verify(index, 0, 0, 0, 0, -1, -1);
        verify(index, 1, 0, 3, 3, 0, 2);
        verify(index, 2, 3, 3, 0, -1, -1);
        verify(index, 3, 3, 4, 1, 3, 3);
        verify(index, 5, 4, 6, 2, 4, 5);
        verify(index, 9, 7, 7, 0, -1, -1);

        SortedReleaseIndex empty = new SortedReleaseIndex(new int[]{});
        verify(empty, 10, 0, 0, 0, -1, -1);

        boolean rejected = false;

        try {
            new SortedReleaseIndex(new int[]{5, 2, 7});
        } catch (IllegalArgumentException expected) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError("Unsorted input was accepted.");
        }

        System.out.println("All Java 17 verification tests passed.");
    }

    public static void main(String[] args) {
        SortedReleaseIndex releases = new SortedReleaseIndex(
            new int[]{1001, 1002, 1002, 1002, 1005, 1007, 1007, 1010}
        );

        List<Integer> targets = List.of(999, 1002, 1004, 1007, 1011);

        System.out.println("Enterprise release-index analysis");
        System.out.println();

        targets.forEach(releases::printAnalysis);

        runTests();
    }
}
