import java.util.Arrays;
import java.util.List;
import java.util.OptionalInt;

public class AdvancedBinarySearch {

    record SearchResult(
            String algorithm,
            OptionalInt index,
            OptionalInt value,
            int comparisons) {

        static SearchResult found(
                String algorithm,
                int index,
                int value,
                int comparisons) {
            return new SearchResult(
                    algorithm,
                    OptionalInt.of(index),
                    OptionalInt.of(value),
                    comparisons);
        }

        static SearchResult notFound(
                String algorithm,
                int comparisons) {
            return new SearchResult(
                    algorithm,
                    OptionalInt.empty(),
                    OptionalInt.empty(),
                    comparisons);
        }
    }

    static class SearchException extends IllegalArgumentException {
        SearchException(String message) {
            super(message);
        }
    }

    interface SearchPolicy {
        SearchResult search(int[] values, int target);
    }

    static final class StandardBinarySearch
            implements SearchPolicy {

        @Override
        public SearchResult search(
                int[] values,
                int target) {

            int left = 0;
            int right = values.length - 1;
            int comparisons = 0;

            while (left <= right) {
                int mid = left + (right - left) / 2;
                comparisons++;

                if (values[mid] == target) {
                    return SearchResult.found(
                            "standardBinarySearch",
                            mid,
                            values[mid],
                            comparisons);
                }

                if (values[mid] < target) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }

            return SearchResult.notFound(
                    "standardBinarySearch",
                    comparisons);
        }
    }

    static final class RotatedSearch
            implements SearchPolicy {

        @Override
        public SearchResult search(
                int[] values,
                int target) {

            int left = 0;
            int right = values.length - 1;
            int comparisons = 0;

            while (left <= right) {
                int mid = left + (right - left) / 2;
                comparisons++;

                if (values[mid] == target) {
                    return SearchResult.found(
                            "rotatedSearch",
                            mid,
                            values[mid],
                            comparisons);
                }

                if (values[left] <= values[mid]) {
                    if (values[left] <= target &&
                            target < values[mid]) {
                        right = mid - 1;
                    } else {
                        left = mid + 1;
                    }
                } else {
                    if (values[mid] < target &&
                            target <= values[right]) {
                        left = mid + 1;
                    } else {
                        right = mid - 1;
                    }
                }
            }

            return SearchResult.notFound(
                    "rotatedSearch",
                    comparisons);
        }
    }

    static final class RotatedSearchWithDuplicates
            implements SearchPolicy {

        @Override
        public SearchResult search(
                int[] values,
                int target) {

            int left = 0;
            int right = values.length - 1;
            int comparisons = 0;

            while (left <= right) {
                int mid = left + (right - left) / 2;
                comparisons++;

                if (values[mid] == target) {
                    return SearchResult.found(
                            "rotatedSearchWithDuplicates",
                            mid,
                            values[mid],
                            comparisons);
                }

                if (values[left] == values[mid] &&
                        values[mid] == values[right]) {
                    left++;
                    right--;
                    continue;
                }

                if (values[left] <= values[mid]) {
                    if (values[left] <= target &&
                            target < values[mid]) {
                        right = mid - 1;
                    } else {
                        left = mid + 1;
                    }
                } else {
                    if (values[mid] < target &&
                            target <= values[right]) {
                        left = mid + 1;
                    } else {
                        right = mid - 1;
                    }
                }
            }

            return SearchResult.notFound(
                    "rotatedSearchWithDuplicates",
                    comparisons);
        }
    }

    static final class BitonicSearch {

        private SearchResult findPeak(int[] values) {
            if (values.length == 0) {
                throw new SearchException(
                        "Bitonic array cannot be empty.");
            }

            int left = 0;
            int right = values.length - 1;
            int comparisons = 0;

            while (left < right) {
                int mid = left + (right - left) / 2;
                comparisons++;

                if (values[mid] < values[mid + 1]) {
                    left = mid + 1;
                } else {
                    right = mid;
                }
            }

            return SearchResult.found(
                    "bitonicPeak",
                    left,
                    values[left],
                    comparisons);
        }

        SearchResult search(int[] values, int target) {
            if (values.length == 0) {
                return SearchResult.notFound(
                        "bitonicSearch",
                        0);
            }

            SearchResult peak = findPeak(values);
            int peakIndex = peak.index().orElseThrow();
            int comparisons = peak.comparisons();

            int left = 0;
            int right = peakIndex;

            while (left <= right) {
                int mid = left + (right - left) / 2;
                comparisons++;

                if (values[mid] == target) {
                    return SearchResult.found(
                            "bitonicSearch",
                            mid,
                            values[mid],
                            comparisons);
                }

                if (values[mid] < target) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }

            left = peakIndex + 1;
            right = values.length - 1;

            while (left <= right) {
                int mid = left + (right - left) / 2;
                comparisons++;

                if (values[mid] == target) {
                    return SearchResult.found(
                            "bitonicSearch",
                            mid,
                            values[mid],
                            comparisons);
                }

                if (values[mid] > target) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }

            return SearchResult.notFound(
                    "bitonicSearch",
                    comparisons);
        }
    }

    static final class MatrixSearch {

        private void validate(int[][] matrix) {
            if (matrix == null) {
                throw new SearchException(
                        "Matrix cannot be null.");
            }

            if (matrix.length == 0) {
                return;
            }

            int columns = matrix[0].length;

            for (int[] row : matrix) {
                if (row.length != columns) {
                    throw new SearchException(
                            "Matrix must be rectangular.");
                }
            }
        }

        SearchResult globallySorted(
                int[][] matrix,
                int target) {

            validate(matrix);

            if (matrix.length == 0 ||
                    matrix[0].length == 0) {
                return SearchResult.notFound(
                        "globalMatrixSearch",
                        0);
            }

            int columns = matrix[0].length;
            int left = 0;
            int right = matrix.length * columns - 1;
            int comparisons = 0;

            while (left <= right) {
                int mid = left + (right - left) / 2;
                int row = mid / columns;
                int column = mid % columns;
                int value = matrix[row][column];
                comparisons++;

                if (value == target) {
                    return SearchResult.found(
                            "globalMatrixSearch",
                            mid,
                            value,
                            comparisons);
                }

                if (value < target) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }

            return SearchResult.notFound(
                    "globalMatrixSearch",
                    comparisons);
        }

        SearchResult rowColumnSorted(
                int[][] matrix,
                int target) {

            validate(matrix);

            if (matrix.length == 0 ||
                    matrix[0].length == 0) {
                return SearchResult.notFound(
                        "rowColumnMatrixSearch",
                        0);
            }

            int row = 0;
            int column = matrix[0].length - 1;
            int comparisons = 0;

            while (row < matrix.length && column >= 0) {
                int value = matrix[row][column];
                comparisons++;

                if (value == target) {
                    return SearchResult.found(
                            "rowColumnMatrixSearch",
                            row * matrix[0].length + column,
                            value,
                            comparisons);
                }

                if (value > target) {
                    column--;
                } else {
                    row++;
                }
            }

            return SearchResult.notFound(
                    "rowColumnMatrixSearch",
                    comparisons);
        }
    }

    static int lowerBound(int[] values, int target) {
        int left = 0;
        int right = values.length;

        while (left < right) {
            int mid = left + (right - left) / 2;

            if (values[mid] < target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        return left;
    }

    static int upperBound(int[] values, int target) {
        int left = 0;
        int right = values.length;

        while (left < right) {
            int mid = left + (right - left) / 2;

            if (values[mid] <= target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        return left;
    }

    static int[] findRange(int[] values, int target) {
        int first = lowerBound(values, target);
        int end = upperBound(values, target);

        if (first == end) {
            return new int[]{-1, -1};
        }

        return new int[]{first, end - 1};
    }

    static void print(SearchResult result) {
        if (result.index().isPresent()) {
            System.out.printf(
                    "%s: index=%d, value=%d, comparisons=%d%n",
                    result.algorithm(),
                    result.index().getAsInt(),
                    result.value().getAsInt(),
                    result.comparisons());
        } else {
            System.out.printf(
                    "%s: not found, comparisons=%d%n",
                    result.algorithm(),
                    result.comparisons());
        }
    }

    public static void main(String[] args) {
        try {
            int[] sorted = {
                    2, 5, 8, 12, 17, 21, 29
            };

            int[] rotated = {
                    13, 18, 25, 2, 8, 10
            };

            int[] duplicateRotated = {
                    2, 5, 6, 0, 0, 1, 2
            };

            int[] bitonic = {
                    2, 5, 9, 14, 19, 16, 11, 4
            };

            int[][] globalMatrix = {
                    {1, 3, 5, 7},
                    {10, 12, 14, 16},
                    {20, 22, 24, 26}
            };

            int[][] rowColumnMatrix = {
                    {1, 4, 7, 11},
                    {2, 5, 8, 13},
                    {3, 6, 9, 15},
                    {10, 12, 14, 18}
            };

            List<SearchPolicy> policies = List.of(
                    new StandardBinarySearch(),
                    new RotatedSearch(),
                    new RotatedSearchWithDuplicates()
            );

            SearchResult standard =
                    policies.get(0).search(sorted, 17);
            assert standard.index().orElse(-1) == 4;

            SearchResult rotatedResult =
                    policies.get(1).search(rotated, 8);
            assert rotatedResult.index().orElse(-1) == 4;

            SearchResult duplicateResult =
                    policies.get(2).search(
                            duplicateRotated,
                            0);

            assert duplicateResult.index().orElse(-1) == 3 ||
                    duplicateResult.index().orElse(-1) == 4;

            BitonicSearch bitonicSearch = new BitonicSearch();

            SearchResult bitonicResult =
                    bitonicSearch.search(bitonic, 11);
            assert bitonicResult.index().orElse(-1) == 6;

            MatrixSearch matrixSearch = new MatrixSearch();

            SearchResult matrixResult =
                    matrixSearch.globallySorted(
                            globalMatrix,
                            22);
            assert matrixResult.index().orElse(-1) == 9;

            SearchResult staircaseResult =
                    matrixSearch.rowColumnSorted(
                            rowColumnMatrix,
                            9);
            assert staircaseResult.index().orElse(-1) == 10;

            int[] range =
                    findRange(
                            new int[]{1, 2, 2, 2, 4, 7},
                            2);

            assert Arrays.equals(
                    range,
                    new int[]{1, 3});

            print(standard);
            print(rotatedResult);
            print(duplicateResult);
            print(bitonicResult);
            print(matrixResult);
            print(staircaseResult);

            System.out.printf(
                    "Range of 2: [%d, %d]%n",
                    range[0],
                    range[1]);

            System.out.println(
                    "All Java 17 checks passed.");
        } catch (SearchException error) {
            System.err.println(
                    "Validation failure: " +
                    error.getMessage());
            System.exit(1);
        }
    }
}
