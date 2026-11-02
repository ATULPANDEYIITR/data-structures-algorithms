import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class BinaryTreeProperties {

    enum NodeKind {
        LEAF,
        INTERNAL
    }

    enum TreeState {
        VALID,
        EMPTY,
        UNBALANCED,
        INCOMPLETE,
        NON_FULL
    }

    static final class TreeNode {
        private final int value;
        private TreeNode left;
        private TreeNode right;

        TreeNode(int value) {
            this.value = value;
        }

        int value() {
            return value;
        }

        NodeKind kind() {
            return left == null && right == null
                    ? NodeKind.LEAF
                    : NodeKind.INTERNAL;
        }
    }

    record TreeProfile(
            int nodes,
            int leaves,
            int internalNodes,
            int heightEdges,
            int heightNodes,
            int diameterEdges,
            boolean balanced,
            boolean full,
            boolean complete,
            boolean perfect,
            Optional<Boolean> leafInternalIdentity
    ) {
        TreeProfile {
            if (nodes < 0 || leaves < 0 || internalNodes < 0) {
                throw new IllegalArgumentException("Counts cannot be negative");
            }
        }
    }

    record Policy(
            int maximumHeight,
            boolean requireBalanced,
            boolean requireComplete
    ) {
        Policy {
            if (maximumHeight < 0) {
                throw new IllegalArgumentException(
                        "Maximum height cannot be negative"
                );
            }
        }
    }

    record PolicyDecision(
            boolean eligible,
            List<String> violations
    ) {
        PolicyDecision {
            violations = List.copyOf(violations);
        }
    }

    interface TreePolicy {
        PolicyDecision evaluate(TreeProfile profile);
    }

    static final class StructuralPolicy implements TreePolicy {
        private final Policy policy;

        StructuralPolicy(Policy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        @Override
        public PolicyDecision evaluate(TreeProfile profile) {
            List<String> violations = new ArrayList<>();

            if (profile.heightEdges() > policy.maximumHeight()) {
                violations.add("height exceeds policy limit");
            }

            if (policy.requireBalanced() && !profile.balanced()) {
                violations.add("tree is not balanced");
            }

            if (policy.requireComplete() && !profile.complete()) {
                violations.add("tree is not complete");
            }

            return new PolicyDecision(
                    violations.isEmpty(),
                    violations
            );
        }
    }

    static final class TreeService {
        private TreeNode root;

        TreeService(TreeNode root) {
            this.root = root;
        }

        static TreeService fromLevelOrder(List<Integer> values) {
            if (values.isEmpty() || values.get(0) == null) {
                return new TreeService(null);
            }

            TreeNode root = new TreeNode(values.get(0));
            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.add(root);

            int index = 1;

            while (!queue.isEmpty() && index < values.size()) {
                TreeNode current = queue.remove();

                Integer leftValue = values.get(index++);
                if (leftValue != null) {
                    current.left = new TreeNode(leftValue);
                    queue.add(current.left);
                }

                if (index < values.size()) {
                    Integer rightValue = values.get(index++);
                    if (rightValue != null) {
                        current.right = new TreeNode(rightValue);
                        queue.add(current.right);
                    }
                }
            }

            if (index < values.size()) {
                throw new IllegalArgumentException(
                        "Input contains unreachable nodes"
                );
            }

            return new TreeService(root);
        }

        void validate() {
            if (root == null) {
                return;
            }

            Deque<TreeNode> stack = new ArrayDeque<>();
            List<TreeNode> seen = new ArrayList<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                TreeNode node = stack.pop();

                if (seen.stream().anyMatch(existing -> existing == node)) {
                    throw new IllegalStateException(
                            "Cycle or repeated node reference detected"
                    );
                }

                seen.add(node);

                if (node.left == node || node.right == node) {
                    throw new IllegalStateException(
                            "Self-reference detected"
                    );
                }

                if (node.left != null) stack.push(node.left);
                if (node.right != null) stack.push(node.right);
            }
        }

        int countNodes() {
            if (root == null) return 0;

            int count = 0;
            Deque<TreeNode> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                TreeNode node = stack.pop();
                count++;

                if (node.left != null) stack.push(node.left);
                if (node.right != null) stack.push(node.right);
            }

            return count;
        }

        int countLeaves() {
            if (root == null) return 0;

            int count = 0;
            Deque<TreeNode> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                TreeNode node = stack.pop();

                if (node.kind() == NodeKind.LEAF) {
                    count++;
                    continue;
                }

                if (node.left != null) stack.push(node.left);
                if (node.right != null) stack.push(node.right);
            }

            return count;
        }

        int heightEdges() {
            return height(root);
        }

        private int height(TreeNode node) {
            if (node == null) return -1;
            return 1 + Math.max(
                    height(node.left),
                    height(node.right)
            );
        }

        int diameterEdges() {
            return diameterAndHeight(root).diameter();
        }

        private record HeightDiameter(int height, int diameter) {}

        private HeightDiameter diameterAndHeight(TreeNode node) {
            if (node == null) {
                return new HeightDiameter(-1, 0);
            }

            HeightDiameter left = diameterAndHeight(node.left);
            HeightDiameter right = diameterAndHeight(node.right);

            int height = 1 + Math.max(
                    left.height(),
                    right.height()
            );

            int throughNode =
                    left.height() + right.height() + 2;

            int diameter = Math.max(
                    throughNode,
                    Math.max(left.diameter(), right.diameter())
            );

            return new HeightDiameter(height, diameter);
        }

        boolean isBalanced() {
            return balancedHeight(root) >= 0;
        }

        private int balancedHeight(TreeNode node) {
            if (node == null) return 0;

            int left = balancedHeight(node.left);
            if (left < 0) return -1;

            int right = balancedHeight(node.right);
            if (right < 0) return -1;

            if (Math.abs(left - right) > 1) return -1;

            return 1 + Math.max(left, right);
        }

        boolean isFull() {
            if (root == null) return true;

            Deque<TreeNode> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                TreeNode node = stack.pop();

                int children =
                        (node.left == null ? 0 : 1) +
                        (node.right == null ? 0 : 1);

                if (children == 1) return false;

                if (node.left != null) stack.push(node.left);
                if (node.right != null) stack.push(node.right);
            }

            return true;
        }

        boolean isComplete() {
            if (root == null) return true;

            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.add(root);
            boolean missingChild = false;

            while (!queue.isEmpty()) {
                TreeNode node = queue.remove();

                if (node.left != null) {
                    if (missingChild) return false;
                    queue.add(node.left);
                } else {
                    missingChild = true;
                }

                if (node.right != null) {
                    if (missingChild) return false;
                    queue.add(node.right);
                } else {
                    missingChild = true;
                }
            }

            return true;
        }

        boolean isPerfect() {
            if (root == null) return true;

            Optional<Integer> expectedDepth = Optional.empty();
            Deque<Map.Entry<TreeNode, Integer>> stack = new ArrayDeque<>();
            stack.push(Map.entry(root, 0));

            while (!stack.isEmpty()) {
                var entry = stack.pop();
                TreeNode node = entry.getKey();
                int depth = entry.getValue();

                boolean left = node.left != null;
                boolean right = node.right != null;

                if (!left && !right) {
                    if (expectedDepth.isEmpty()) {
                        expectedDepth = Optional.of(depth);
                    } else if (expectedDepth.get() != depth) {
                        return false;
                    }
                    continue;
                }

                if (!left || !right) return false;

                stack.push(Map.entry(node.left, depth + 1));
                stack.push(Map.entry(node.right, depth + 1));
            }

            return true;
        }

        TreeProfile profile() {
            validate();

            int nodes = countNodes();
            int leaves = countLeaves();
            int internal = nodes - leaves;
            int height = heightEdges();
            boolean full = isFull();

            return new TreeProfile(
                    nodes,
                    leaves,
                    internal,
                    height,
                    nodes == 0 ? 0 : height + 1,
                    diameterEdges(),
                    isBalanced(),
                    full,
                    isComplete(),
                    isPerfect(),
                    nodes > 0 && full
                            ? Optional.of(leaves == internal + 1)
                            : Optional.empty()
            );
        }
    }

    static final class ReportService {
        static String toText(TreeProfile profile) {
            return """
                    Binary Tree Structural Profile
                    nodes=%d
                    leaves=%d
                    internalNodes=%d
                    heightEdges=%d
                    heightNodes=%d
                    diameterEdges=%d
                    balanced=%s
                    full=%s
                    complete=%s
                    perfect=%s
                    """.formatted(
                    profile.nodes(),
                    profile.leaves(),
                    profile.internalNodes(),
                    profile.heightEdges(),
                    profile.heightNodes(),
                    profile.diameterEdges(),
                    profile.balanced(),
                    profile.full(),
                    profile.complete(),
                    profile.perfect()
            );
        }

        static void save(TreeProfile profile) throws IOException {
            Path cwd = Path.of(".").toAbsolutePath().normalize();
            Path target = cwd.resolve("binary_tree_profile.txt").normalize();

            if (!target.getParent().equals(cwd)) {
                throw new IOException(
                        "Output path must remain in current directory"
                );
            }

            Files.writeString(
                    target,
                    toText(profile),
                    StandardCharsets.UTF_8
            );
        }
    }

    static void runTests() {
        TreeService balanced = TreeService.fromLevelOrder(
                List.of(10, 5, 15, 2, 7, 12, 20)
        );

        TreeProfile p = balanced.profile();

        if (p.nodes() != 7 ||
                p.leaves() != 4 ||
                p.internalNodes() != 3 ||
                p.heightEdges() != 2 ||
                p.diameterEdges() != 4 ||
                !p.balanced() ||
                !p.full() ||
                !p.complete() ||
                !p.perfect()) {
            throw new AssertionError("Balanced-tree test failed");
        }

        List<Integer> chainValues = new ArrayList<>();
        Collections.addAll(
                chainValues,
                1, 2, null, 3, null, 4
        );

        TreeProfile chain = TreeService
                .fromLevelOrder(chainValues)
                .profile();

        if (chain.heightEdges() != 3 ||
                chain.diameterEdges() != 3 ||
                chain.balanced() ||
                chain.full()) {
            throw new AssertionError("Chain test failed");
        }

        TreeProfile single = TreeService
                .fromLevelOrder(List.of(42))
                .profile();

        if (single.nodes() != 1 ||
                single.leaves() != 1 ||
                single.heightEdges() != 0 ||
                !single.balanced()) {
            throw new AssertionError("Single-node test failed");
        }

        TreeProfile empty = TreeService
                .fromLevelOrder(List.of())
                .profile();

        if (empty.nodes() != 0 ||
                empty.heightEdges() != -1 ||
                empty.diameterEdges() != 0 ||
                !empty.balanced()) {
            throw new AssertionError("Empty-tree test failed");
        }
    }

    public static void main(String[] args) {
        try {
            runTests();

            TreeService tree = TreeService.fromLevelOrder(
                    List.of(50, 25, 75, 12, 37, 62, 87)
            );

            TreeProfile profile = tree.profile();

            TreePolicy policy = new StructuralPolicy(
                    new Policy(4, true, true)
            );

            PolicyDecision decision = policy.evaluate(profile);

            System.out.println(ReportService.toText(profile));
            System.out.println(
                    "Policy eligible: " + decision.eligible()
            );

            if (!decision.eligible()) {
                System.out.println(
                        decision.violations()
                                .stream()
                                .collect(Collectors.joining(", "))
                );
            }

            ReportService.save(profile);
            System.out.println("Validation: all tests passed.");
            System.out.println(
                    "Profile written to binary_tree_profile.txt"
            );
        } catch (Exception ex) {
            System.err.println(
                    "Execution failed: " + ex.getMessage()
            );
            System.exit(1);
        }
    }
}
