import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/*
 * Recursion Trees: enterprise build-policy analysis
 *
 * The domain is a release validation service. A release candidate has
 * recursive validation stages. Each stage may require independent child
 * checks, and the execution tree is retained for auditability.
 *
 * Java-specific design:
 * - records provide immutable value objects for validation results;
 * - enums model explicit validation states;
 * - interfaces separate tree construction from policy evaluation;
 * - exceptions represent invalid state rather than silently accepting it;
 * - collections retain child relationships and cached recursive states.
 */
public class RecursionTrees {

    enum ValidationState {
        PENDING,
        PASSED,
        FAILED
    }

    record ValidationResult(
        String stage,
        ValidationState state,
        int localCost,
        String detail
    ) {
        ValidationResult {
            Objects.requireNonNull(stage);
            Objects.requireNonNull(state);
            Objects.requireNonNull(detail);

            if (localCost < 0) {
                throw new IllegalArgumentException(
                    "Validation cost cannot be negative"
                );
            }
        }
    }

    static final class ExecutionNode {
        private final ValidationResult result;
        private final List<ExecutionNode> children = new ArrayList<>();

        ExecutionNode(ValidationResult result) {
            this.result = Objects.requireNonNull(result);
        }

        void addChild(ExecutionNode child) {
            if (result.state() == ValidationState.PASSED) {
                throw new IllegalStateException(
                    "A completed validation node cannot gain new child work"
                );
            }

            children.add(Objects.requireNonNull(child));
        }

        ValidationResult result() {
            return result;
        }

        List<ExecutionNode> children() {
            return List.copyOf(children);
        }
    }

    interface RecursiveAnalyzer {
        ExecutionNode build(String state, int depth);
    }

    static final class ReleaseValidationAnalyzer
            implements RecursiveAnalyzer {

        @Override
        public ExecutionNode build(String state, int depth) {
            if (state == null || state.isBlank()) {
                throw new IllegalArgumentException(
                    "Validation state must not be blank"
                );
            }

            ValidationState terminal =
                depth == 0
                    ? ValidationState.PASSED
                    : ValidationState.PENDING;

            ExecutionNode node = new ExecutionNode(
                new ValidationResult(
                    state,
                    terminal,
                    depth == 0 ? 1 : 2,
                    depth == 0
                        ? "Terminal validation"
                        : "Waiting for recursive child validations"
                )
            );

            if (depth > 0) {
                ExecutionNode compile = build(
                    state + ".compile",
                    depth - 1
                );

                ExecutionNode integration = build(
                    state + ".integration",
                    depth - 1
                );

                node.addChild(compile);
                node.addChild(integration);
            }

            return node;
        }
    }

    static int nodeCount(ExecutionNode node) {
        return 1 + node.children().stream()
            .mapToInt(RecursionTrees::nodeCount)
            .sum();
    }

    static int leafCount(ExecutionNode node) {
        if (node.children().isEmpty()) {
            return 1;
        }

        return node.children().stream()
            .mapToInt(RecursionTrees::leafCount)
            .sum();
    }

    static int treeHeight(ExecutionNode node) {
        if (node.children().isEmpty()) {
            return 1;
        }

        return 1 + node.children().stream()
            .mapToInt(RecursionTrees::treeHeight)
            .max()
            .orElse(0);
    }

    static int accumulatedCost(ExecutionNode node) {
        return node.result().localCost()
            + node.children().stream()
                .mapToInt(RecursionTrees::accumulatedCost)
                .sum();
    }

    static void printTree(
        ExecutionNode node,
        String prefix,
        boolean last,
        boolean root
    ) {
        String connector =
            root ? "" : (last ? "└── " : "├── ");

        ValidationResult result = node.result();

        System.out.println(
            prefix
                + connector
                + result.stage()
                + " ["
                + result.state()
                + ", cost="
                + result.localCost()
                + "]"
        );

        String childPrefix = root
            ? prefix
            : prefix + (last ? "    " : "│   ");

        List<ExecutionNode> children = node.children();

        for (int i = 0; i < children.size(); i++) {
            printTree(
                children.get(i),
                childPrefix,
                i == children.size() - 1,
                false
            );
        }
    }

    /*
     * Fibonacci's raw tree is deliberately retained separately from the
     * enterprise validation tree because its primary purpose is to show
     * overlapping recursive states.
     */
    static ExecutionNode fibonacciTree(int n) {
        ExecutionNode node = new ExecutionNode(
            new ValidationResult(
                "fib(" + n + ")",
                ValidationState.PENDING,
                1,
                "Recursive arithmetic state"
            )
        );

        if (n <= 1) {
            return node;
        }

        node.addChild(fibonacciTree(n - 1));
        node.addChild(fibonacciTree(n - 2));

        return node;
    }

    static final class MemoizedFibonacci {
        private final Map<Integer, Long> cache = new HashMap<>();
        private long invocations;

        long calculate(int n) {
            invocations++;

            if (cache.containsKey(n)) {
                return cache.get(n);
            }

            if (n <= 1) {
                cache.put(n, (long) n);
                return n;
            }

            long value =
                calculate(n - 1) +
                calculate(n - 2);

            cache.put(n, value);
            return value;
        }

        long invocations() {
            return invocations;
        }

        int uniqueStates() {
            return cache.size();
        }
    }

    /*
     * Recursive binary search is represented by one child per internal node.
     * This is important because recursion trees describe calls, not merely
     * algorithms with multiple branches.
     */
    static ExecutionNode binarySearchTree(
        List<Integer> values,
        int target,
        int low,
        int high
    ) {
        ExecutionNode node = new ExecutionNode(
            new ValidationResult(
                "binarySearch",
                ValidationState.PENDING,
                1,
                "range=[" + low + "," + high + "]"
            )
        );

        if (low > high) {
            return node;
        }

        int middle = low + (high - low) / 2;

        if (values.get(middle) == target) {
            return node;
        }

        if (target < values.get(middle)) {
            node.addChild(
                binarySearchTree(
                    values,
                    target,
                    low,
                    middle - 1
                )
            );
        } else {
            node.addChild(
                binarySearchTree(
                    values,
                    target,
                    middle + 1,
                    high
                )
            );
        }

        return node;
    }

    static void printRecurrenceTable() {
        System.out.println("\n=== Fibonacci tree measurements ===");
        System.out.printf(
            "%-6s %-10s %-10s %-10s%n",
            "n",
            "nodes",
            "leaves",
            "height"
        );

        for (int n = 0; n <= 9; n++) {
            ExecutionNode tree = fibonacciTree(n);

            System.out.printf(
                "%-6d %-10d %-10d %-10d%n",
                n,
                nodeCount(tree),
                leafCount(tree),
                treeHeight(tree)
            );
        }
    }

    public static void main(String[] args) {
        System.out.println("RECURSION TREES");
        System.out.println("================");

        /*
         * Enterprise scenario: a release validation service decomposes a
         * release into recursively smaller verification stages.
         */
        System.out.println(
            "\n=== Release validation execution tree ==="
        );

        RecursiveAnalyzer analyzer =
            new ReleaseValidationAnalyzer();

        ExecutionNode releaseTree =
            analyzer.build("release-2026.10", 3);

        printTree(releaseTree, "", true, true);

        System.out.println(
            "Height: " + treeHeight(releaseTree)
        );
        System.out.println(
            "Nodes: " + nodeCount(releaseTree)
        );
        System.out.println(
            "Leaves: " + leafCount(releaseTree)
        );
        System.out.println(
            "Accumulated local cost: "
                + accumulatedCost(releaseTree)
        );

        /*
         * A Fibonacci tree makes overlapping recursive state explicit.
         */
        System.out.println(
            "\n=== Overlapping recursive state ==="
        );

        ExecutionNode fibonacci = fibonacciTree(5);
        printTree(fibonacci, "", true, true);

        System.out.println(
            "Raw nodes: " + nodeCount(fibonacci)
        );

        MemoizedFibonacci memoized =
            new MemoizedFibonacci();

        long fibonacciValue =
            memoized.calculate(35);

        System.out.println(
            "fib(35): " + fibonacciValue
        );
        System.out.println(
            "Recursive invocations: "
                + memoized.invocations()
        );
        System.out.println(
            "Unique states: "
                + memoized.uniqueStates()
        );

        /*
         * Binary search demonstrates a recursion tree with one surviving
         * branch at each internal node.
         */
        System.out.println(
            "\n=== One-branch recursive tree ==="
        );

        List<Integer> sorted =
            java.util.stream.IntStream.range(0, 32)
                .boxed()
                .toList();

        ExecutionNode searchTree =
            binarySearchTree(
                sorted,
                23,
                0,
                sorted.size() - 1
            );

        printTree(searchTree, "", true, true);

        printRecurrenceTable();

        System.out.println(
            "\n=== Domain interpretation ==="
        );
        System.out.println(
            "The validation tree represents the execution structure, "
                + "while node-local cost represents work performed at "
                + "that recursive state."
        );
        System.out.println(
            "Branching determines how many child calls exist, shrinking "
                + "the input determines tree height, and repeated states "
                + "determine whether memoization can remove redundant work."
        );
    }
}
