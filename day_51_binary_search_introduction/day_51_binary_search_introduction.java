import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.OptionalInt;

public class BinarySearchEnterpriseDemo {

    enum SearchMethod {
        ITERATIVE,
        RECURSIVE
    }

    record SearchRequest(List<Integer> data, int target, SearchMethod method) {
        SearchRequest {
            Objects.requireNonNull(data, "data must not be null");
            Objects.requireNonNull(method, "method must not be null");

            if (!isSorted(data)) {
                throw new IllegalArgumentException(
                    "Binary search requires sorted non-decreasing data."
                );
            }
        }
    }

    record SearchResult(
        int target,
        OptionalInt index,
        int insertionPoint,
        boolean found,
        SearchMethod method
    ) {}

    static final class BinarySearchService {

        SearchResult execute(SearchRequest request) {
            List<Integer> data = request.data();

            OptionalInt index = switch (request.method()) {
                case ITERATIVE -> iterative(data, request.target());
                case RECURSIVE -> recursive(
                    data,
                    request.target(),
                    0,
                    data.size() - 1
                );
            };

            int insertionPoint = lowerBound(data, request.target());

            return new SearchResult(
                request.target(),
                index,
                insertionPoint,
                index.isPresent(),
                request.method()
            );
        }

        private OptionalInt iterative(List<Integer> data, int target) {
            int left = 0;
            int right = data.size() - 1;

            while (left <= right) {
                int middle = left + (right - left) / 2;
                int value = data.get(middle);

                if (value == target) {
                    return OptionalInt.of(middle);
                }

                if (value < target) {
                    left = middle + 1;
                } else {
                    right = middle - 1;
                }
            }

            return OptionalInt.empty();
        }

        private OptionalInt recursive(
            List<Integer> data,
            int target,
            int left,
            int right
        ) {
            if (left > right) {
                return OptionalInt.empty();
            }

            int middle = left + (right - left) / 2;
            int value = data.get(middle);

            if (value == target) {
                return OptionalInt.of(middle);
            }

            if (value < target) {
                return recursive(data, target, middle + 1, right);
            }

            return recursive(data, target, left, middle - 1);
        }

        private int lowerBound(List<Integer> data, int target) {
            int left = 0;
            int right = data.size();

            while (left < right) {
                int middle = left + (right - left) / 2;

                if (data.get(middle) < target) {
                    left = middle + 1;
                } else {
                    right = middle;
                }
            }

            return left;
        }
    }

    static final class RepositoryArtifactIndex {
        private final List<Integer> sortedKeys;
        private final BinarySearchService searchService;

        RepositoryArtifactIndex(List<Integer> keys) {
            Objects.requireNonNull(keys, "keys must not be null");

            if (!isSorted(keys)) {
                throw new IllegalArgumentException(
                    "Repository artifact keys must be sorted."
                );
            }

            this.sortedKeys = List.copyOf(keys);
            this.searchService = new BinarySearchService();
        }

        SearchResult find(int target, SearchMethod method) {
            return searchService.execute(
                new SearchRequest(sortedKeys, target, method)
            );
        }

        List<Integer> keys() {
            return sortedKeys;
        }
    }

    private static boolean isSorted(List<Integer> data) {
        for (int i = 1; i < data.size(); i++) {
            if (data.get(i - 1) > data.get(i)) {
                return false;
            }
        }
        return true;
    }

    private static void printResult(SearchResult result) {
        String index = result.index().isPresent()
            ? Integer.toString(result.index().getAsInt())
            : "not-found";

        System.out.printf(
            "method=%-9s target=%3d index=%-9s insertion=%d%n",
            result.method(),
            result.target(),
            index,
            result.insertionPoint()
        );
    }

    public static void main(String[] args) {
        List<Integer> keys = new ArrayList<>(
            List.of(-20, -10, -1, 0, 4, 4, 4, 9, 15, 21, 42)
        );

        // Sorting is a preprocessing operation. The service never silently
        // sorts caller data because doing so could hide a workflow defect.
        Collections.sort(keys);

        RepositoryArtifactIndex index = new RepositoryArtifactIndex(keys);

        System.out.println("Enterprise artifact lookup");
        System.out.println("Keys: " + index.keys());
        System.out.println();

        for (int target : List.of(-20, 4, 5, 42, 100)) {
            printResult(index.find(target, SearchMethod.ITERATIVE));
            printResult(index.find(target, SearchMethod.RECURSIVE));
            System.out.println();
        }

        try {
            new RepositoryArtifactIndex(List.of(9, 3, 7));
        } catch (IllegalArgumentException error) {
            System.out.println(
                "Validation failure handled: " + error.getMessage()
            );
        }

        RepositoryArtifactIndex empty =
            new RepositoryArtifactIndex(List.of());

        SearchResult emptyResult =
            empty.find(10, SearchMethod.ITERATIVE);

        System.out.println(
            "Empty index found target: " + emptyResult.found()
        );

        System.out.println(
            "Complexity: O(log n) comparisons; iterative search uses "
                + "constant auxiliary space, while recursive search uses "
                + "O(log n) stack space."
        );
    }
}
