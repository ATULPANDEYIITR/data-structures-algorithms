import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class BinaryTreeEnterpriseDemo {

    public static final class TreeNode {
        private final int value;
        private TreeNode left;
        private TreeNode right;

        public TreeNode(int value) {
            this.value = value;
        }

        public TreeNode(int value, TreeNode left, TreeNode right) {
            this.value = value;
            this.left = left;
            this.right = right;
        }

        public int value() {
            return value;
        }

        public TreeNode left() {
            return left;
        }

        public TreeNode right() {
            return right;
        }

        public void setLeft(TreeNode child) {
            this.left = child;
        }

        public void setRight(TreeNode child) {
            this.right = child;
        }
    }

    public record TreePolicy(
        long maximumNodes,
        int maximumDepth,
        boolean requireBalanced
    ) {
        public TreePolicy {
            if (maximumNodes < 1) {
                throw new IllegalArgumentException(
                    "maximumNodes must be positive."
                );
            }

            if (maximumDepth < 1) {
                throw new IllegalArgumentException(
                    "maximumDepth must be positive."
                );
            }
        }

        public static TreePolicy standard() {
            return new TreePolicy(1_000_000, 100_000, false);
        }

        public static TreePolicy balancedOnly() {
            return new TreePolicy(100_000, 10_000, true);
        }
    }

    public record TreeMetrics(
        int maxDepth,
        int minDepth,
        boolean hasPathSum,
        int diameterEdges,
        boolean balanced,
        long nodeCount
    ) {}

    private record LevelNode(TreeNode node, int depth) {}

    private record PathState(TreeNode node, long sum) {}

    private record Frame(TreeNode node, boolean expanded) {}

    private record SubtreeStats(
        int height,
        int minDepth,
        int diameter,
        boolean balanced,
        long count
    ) {
        private static SubtreeStats empty() {
            return new SubtreeStats(0, 0, 0, true, 0);
        }
    }

    private record ValidationResult(long nodeCount, int maximumDepth) {}

    public static final class InvalidTreeException extends RuntimeException {
        public InvalidTreeException(String message) {
            super(message);
        }
    }

    public static final class TreeLimitExceededException
        extends RuntimeException {

        public TreeLimitExceededException(String message) {
            super(message);
        }
    }

    public static final class PolicyViolationException
        extends RuntimeException {

        public PolicyViolationException(String message) {
            super(message);
        }
    }

    public static final class TreeAnalyticsService {
        private final TreePolicy policy;

        public TreeAnalyticsService(TreePolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        private ValidationResult validateStructure(TreeNode root) {
            if (root == null) {
                return new ValidationResult(0, 0);
            }

            IdentityHashMap<TreeNode, Boolean> visited =
                new IdentityHashMap<>();

            Deque<LevelNode> queue = new ArrayDeque<>();
            queue.addLast(new LevelNode(root, 1));

            long count = 0;
            int maximumDepth = 0;

            while (!queue.isEmpty()) {
                LevelNode entry = queue.removeFirst();
                TreeNode node = entry.node();

                if (visited.put(node, Boolean.TRUE) != null) {
                    throw new InvalidTreeException(
                        "The structure contains a cycle or shared child."
                    );
                }

                count++;
                maximumDepth = Math.max(maximumDepth, entry.depth());

                if (count > policy.maximumNodes()) {
                    throw new TreeLimitExceededException(
                        "The tree exceeds the configured node limit."
                    );
                }

                if (maximumDepth > policy.maximumDepth()) {
                    throw new TreeLimitExceededException(
                        "The tree exceeds the configured depth limit."
                    );
                }

                if (node.left() != null) {
                    queue.addLast(
                        new LevelNode(node.left(), entry.depth() + 1)
                    );
                }

                if (node.right() != null) {
                    queue.addLast(
                        new LevelNode(node.right(), entry.depth() + 1)
                    );
                }
            }

            return new ValidationResult(count, maximumDepth);
        }

        private boolean hasPathSum(TreeNode root, long target) {
            if (root == null) {
                return false;
            }

            Deque<PathState> stack = new ArrayDeque<>();
            stack.push(new PathState(root, 0));

            while (!stack.isEmpty()) {
                PathState state = stack.pop();
                TreeNode node = state.node();

                final long currentSum;
                try {
                    currentSum = Math.addExact(
                        state.sum(),
                        node.value()
                    );
                } catch (ArithmeticException exception) {
                    throw new TreeLimitExceededException(
                        "A root-to-leaf path sum exceeds the long integer range."
                    );
                }

                if (node.left() == null && node.right() == null) {
                    if (currentSum == target) {
                        return true;
                    }
                    continue;
                }

                if (node.right() != null) {
                    stack.push(new PathState(node.right(), currentSum));
                }

                if (node.left() != null) {
                    stack.push(new PathState(node.left(), currentSum));
                }
            }

            return false;
        }

        public TreeMetrics analyze(TreeNode root, long targetSum) {
            validateStructure(root);

            if (root == null) {
                return new TreeMetrics(0, 0, false, 0, true, 0);
            }

            Map<TreeNode, SubtreeStats> stats = new IdentityHashMap<>();
            Deque<Frame> stack = new ArrayDeque<>();
            stack.push(new Frame(root, false));

            while (!stack.isEmpty()) {
                Frame frame = stack.pop();
                TreeNode node = frame.node();

                if (!frame.expanded()) {
                    stack.push(new Frame(node, true));

                    if (node.right() != null) {
                        stack.push(new Frame(node.right(), false));
                    }

                    if (node.left() != null) {
                        stack.push(new Frame(node.left(), false));
                    }

                    continue;
                }

                SubtreeStats left = node.left() == null
                    ? SubtreeStats.empty()
                    : stats.get(node.left());

                SubtreeStats right = node.right() == null
                    ? SubtreeStats.empty()
                    : stats.get(node.right());

                int height = 1 + Math.max(
                    left.height(),
                    right.height()
                );

                int minimumDepth;

                if (node.left() == null && node.right() == null) {
                    minimumDepth = 1;
                } else if (node.left() == null) {
                    minimumDepth = 1 + right.minDepth();
                } else if (node.right() == null) {
                    minimumDepth = 1 + left.minDepth();
                } else {
                    minimumDepth = 1 + Math.min(
                        left.minDepth(),
                        right.minDepth()
                    );
                }

                int diameter = Math.max(
                    left.height() + right.height(),
                    Math.max(left.diameter(), right.diameter())
                );

                boolean balanced =
                    left.balanced()
                    && right.balanced()
                    && Math.abs(left.height() - right.height()) <= 1;

                long count = 1 + left.count() + right.count();

                stats.put(
                    node,
                    new SubtreeStats(
                        height,
                        minimumDepth,
                        diameter,
                        balanced,
                        count
                    )
                );
            }

            SubtreeStats rootStats = stats.get(root);

            if (policy.requireBalanced() && !rootStats.balanced()) {
                throw new PolicyViolationException(
                    "The configured policy requires a balanced tree."
                );
            }

            return new TreeMetrics(
                rootStats.height(),
                rootStats.minDepth(),
                hasPathSum(root, targetSum),
                rootStats.diameter(),
                rootStats.balanced(),
                rootStats.count()
            );
        }

        public int maximumDepth(TreeNode root) {
            return analyze(root, 0).maxDepth();
        }

        public int minimumDepth(TreeNode root) {
            return analyze(root, 0).minDepth();
        }

        public boolean containsPathSum(TreeNode root, long targetSum) {
            validateStructure(root);
            return hasPathSum(root, targetSum);
        }

        public int diameter(TreeNode root) {
            return analyze(root, 0).diameterEdges();
        }

        public boolean isBalanced(TreeNode root) {
            return analyze(root, 0).balanced();
        }

        public long countNodes(TreeNode root) {
            return validateStructure(root).nodeCount();
        }

        private boolean isCompleteAfterValidation(TreeNode root) {
            if (root == null) {
                return true;
            }

            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.addLast(root);

            boolean missingChildSeen = false;

            while (!queue.isEmpty()) {
                TreeNode node = queue.removeFirst();

                for (TreeNode child : new TreeNode[] {
                    node.left(),
                    node.right()
                }) {
                    if (child == null) {
                        missingChildSeen = true;
                    } else {
                        if (missingChildSeen) {
                            return false;
                        }
                        queue.addLast(child);
                    }
                }
            }

            return true;
        }

        private int leftmostHeight(TreeNode node) {
            int height = 0;

            while (node != null) {
                height++;
                node = node.left();
            }

            return height;
        }

        public long countCompleteNodes(TreeNode root, boolean verify) {
            validateStructure(root);

            if (root == null) {
                return 0;
            }

            if (verify && !isCompleteAfterValidation(root)) {
                throw new InvalidTreeException(
                    "Complete-tree counting cannot be applied to this tree."
                );
            }

            long total = 0;
            TreeNode current = root;

            while (current != null) {
                int leftHeight = leftmostHeight(current.left());
                int rightHeight = leftmostHeight(current.right());

                int shift = leftHeight == rightHeight
                    ? leftHeight
                    : rightHeight;

                if (shift >= 63) {
                    throw new TreeLimitExceededException(
                        "The complete-tree count exceeds the signed long range."
                    );
                }

                total += 1L << shift;

                if (leftHeight == rightHeight) {
                    current = current.right();
                } else {
                    current = current.left();
                }
            }

            return total;
        }

        public long countCompleteNodes(TreeNode root) {
            return countCompleteNodes(root, true);
        }
    }

    public static TreeNode fromLevelOrder(List<Integer> values) {
        Objects.requireNonNull(values, "Level-order values are required.");

        if (values.isEmpty()) {
            return null;
        }

        if (values.get(0) == null) {
            if (values.stream().anyMatch(Objects::nonNull)) {
                throw new IllegalArgumentException(
                    "A non-empty tree must have a root."
                );
            }
            return null;
        }

        TreeNode root = new TreeNode(values.get(0));
        Deque<TreeNode> queue = new ArrayDeque<>();
        queue.addLast(root);

        int index = 1;

        while (!queue.isEmpty() && index < values.size()) {
            TreeNode parent = queue.removeFirst();

            if (index < values.size()) {
                Integer value = values.get(index++);

                if (value != null) {
                    parent.setLeft(new TreeNode(value));
                    queue.addLast(parent.left());
                }
            }

            if (index < values.size()) {
                Integer value = values.get(index++);

                if (value != null) {
                    parent.setRight(new TreeNode(value));
                    queue.addLast(parent.right());
                }
            }
        }

        for (; index < values.size(); index++) {
            if (values.get(index) != null) {
                throw new IllegalArgumentException(
                    "Level-order input contains unreachable nodes."
                );
            }
        }

        return root;
    }

    private static void runTests() {
        TreeAnalyticsService service =
            new TreeAnalyticsService(TreePolicy.standard());

        TreeNode balanced = fromLevelOrder(
            Arrays.asList(10, 5, 15, 3, 7, 12, 18)
        );

        TreeMetrics metrics = service.analyze(balanced, 22);

        assert metrics.maxDepth() == 3;
        assert metrics.minDepth() == 3;
        assert metrics.hasPathSum();
        assert metrics.diameterEdges() == 4;
        assert metrics.balanced();
        assert metrics.nodeCount() == 7;
        assert service.countCompleteNodes(balanced) == 7;

        TreeNode skewed = fromLevelOrder(
            Arrays.asList(5, 4, null, 3, null, 2)
        );

        TreeMetrics skewedMetrics = service.analyze(skewed, 14);

        assert skewedMetrics.maxDepth() == 4;
        assert skewedMetrics.minDepth() == 4;
        assert skewedMetrics.diameterEdges() == 3;
        assert !skewedMetrics.balanced();
        assert skewedMetrics.nodeCount() == 4;

        TreeNode oneChild = new TreeNode(1, new TreeNode(2), null);
        assert service.minimumDepth(oneChild) == 2;

        TreeNode negative = fromLevelOrder(
            Arrays.asList(-2, -3, -4)
        );
        assert service.containsPathSum(negative, -5);

        TreeNode empty = null;
        TreeMetrics emptyMetrics = service.analyze(empty, 0);

        assert emptyMetrics.maxDepth() == 0;
        assert emptyMetrics.minDepth() == 0;
        assert emptyMetrics.diameterEdges() == 0;
        assert emptyMetrics.balanced();
        assert emptyMetrics.nodeCount() == 0;

        boolean incompleteRejected = false;
        try {
            service.countCompleteNodes(skewed);
        } catch (InvalidTreeException exception) {
            incompleteRejected = true;
        }
        assert incompleteRejected;

        boolean balancePolicyApplied = false;
        try {
            TreeAnalyticsService balancedOnly = new TreeAnalyticsService(
                TreePolicy.balancedOnly()
            );
            balancedOnly.analyze(skewed, 14);
        } catch (PolicyViolationException exception) {
            balancePolicyApplied = true;
        }
        assert balancePolicyApplied;

        TreeNode shared = new TreeNode(9);
        TreeNode invalid = new TreeNode(
            1,
            new TreeNode(2, shared, null),
            new TreeNode(3, shared, null)
        );

        boolean sharedNodeRejected = false;
        try {
            service.analyze(invalid, 0);
        } catch (InvalidTreeException exception) {
            sharedNodeRejected = true;
        }
        assert sharedNodeRejected;

        System.out.println("All Java 17 binary tree tests passed.");
    }

    public static void main(String[] args) {
        try {
            runTests();

            TreeAnalyticsService service =
                new TreeAnalyticsService(TreePolicy.standard());

            TreeNode tree = fromLevelOrder(
                Arrays.asList(10, 5, 15, 3, 7, 12, 18)
            );

            TreeMetrics metrics = service.analyze(tree, 22);

            System.out.println("\nEnterprise Tree Analysis");
            System.out.println("Maximum depth: " + metrics.maxDepth());
            System.out.println("Minimum depth: " + metrics.minDepth());
            System.out.println("Path sum 22 exists: " + metrics.hasPathSum());
            System.out.println("Diameter in edges: " + metrics.diameterEdges());
            System.out.println("Balanced: " + metrics.balanced());
            System.out.println("Node count: " + metrics.nodeCount());
            System.out.println(
                "Complete-tree node count: "
                + service.countCompleteNodes(tree)
            );

        } catch (RuntimeException exception) {
            System.err.println("Analysis failed: " + exception.getMessage());
            System.exitCode = 1;
        }
    }
}
