import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * Enterprise Binary Tree Traversal System.
 *
 * Implements recursive and iterative depth-first traversals,
 * breadth-first traversal, level grouping, and tree analytics.
 */
public class BinaryTreeTraversal {

    enum TraversalOrder {
        PREORDER,
        INORDER,
        POSTORDER,
        LEVELORDER
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

        TreeNode left() {
            return left;
        }

        TreeNode right() {
            return right;
        }

        void setLeft(TreeNode child) {
            if (left != null) {
                throw new IllegalStateException(
                    "Left child already exists."
                );
            }

            validateChild(child);
            left = child;
        }

        void setRight(TreeNode child) {
            if (right != null) {
                throw new IllegalStateException(
                    "Right child already exists."
                );
            }

            validateChild(child);
            right = child;
        }

        private void validateChild(TreeNode child) {
            if (child == null) {
                throw new IllegalArgumentException(
                    "Child cannot be null."
                );
            }

            if (child == this) {
                throw new IllegalArgumentException(
                    "A node cannot reference itself."
                );
            }

            if (contains(child, this)) {
                throw new IllegalArgumentException(
                    "Attaching this child would create a cycle."
                );
            }
        }

        private static boolean contains(
            TreeNode start,
            TreeNode target
        ) {
            Deque<TreeNode> stack = new ArrayDeque<>();
            stack.push(start);

            while (!stack.isEmpty()) {
                TreeNode current = stack.pop();

                if (current == target) {
                    return true;
                }

                if (current.left != null) {
                    stack.push(current.left);
                }

                if (current.right != null) {
                    stack.push(current.right);
                }
            }

            return false;
        }
    }

    record TraversalResult(
        TraversalOrder order,
        List<Integer> values,
        long elapsedNanos
    ) {
        TraversalResult {
            Objects.requireNonNull(order);
            values = List.copyOf(values);

            if (elapsedNanos < 0) {
                throw new IllegalArgumentException(
                    "Elapsed time cannot be negative."
                );
            }
        }
    }

    interface TraversalStrategy {
        List<Integer> execute(TreeNode root);
    }

    static final class TraversalException
            extends RuntimeException {

        TraversalException(String message) {
            super(message);
        }
    }

    static final class TraversalService {

        private final TreeNode root;

        private final Map<TraversalOrder, TraversalStrategy>
            strategies = new EnumMap<>(TraversalOrder.class);

        TraversalService(TreeNode root) {
            this.root = root;

            strategies.put(
                TraversalOrder.PREORDER,
                this::preorderIterative
            );

            strategies.put(
                TraversalOrder.INORDER,
                this::inorderIterative
            );

            strategies.put(
                TraversalOrder.POSTORDER,
                this::postorderIterative
            );

            strategies.put(
                TraversalOrder.LEVELORDER,
                this::levelOrder
            );
        }

        private void preorderRecursive(
            TreeNode node,
            List<Integer> result
        ) {
            if (node == null) return;

            result.add(node.value());

            preorderRecursive(node.left(), result);
            preorderRecursive(node.right(), result);
        }

        private void inorderRecursive(
            TreeNode node,
            List<Integer> result
        ) {
            if (node == null) return;

            inorderRecursive(node.left(), result);
            result.add(node.value());
            inorderRecursive(node.right(), result);
        }

        private void postorderRecursive(
            TreeNode node,
            List<Integer> result
        ) {
            if (node == null) return;

            postorderRecursive(node.left(), result);
            postorderRecursive(node.right(), result);
            result.add(node.value());
        }

        public List<Integer> preorderRecursive() {
            List<Integer> result = new ArrayList<>();
            preorderRecursive(root, result);
            return List.copyOf(result);
        }

        public List<Integer> inorderRecursive() {
            List<Integer> result = new ArrayList<>();
            inorderRecursive(root, result);
            return List.copyOf(result);
        }

        public List<Integer> postorderRecursive() {
            List<Integer> result = new ArrayList<>();
            postorderRecursive(root, result);
            return List.copyOf(result);
        }

        public List<Integer> preorderIterative() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Deque<TreeNode> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                TreeNode current = stack.pop();
                result.add(current.value());

                if (current.right() != null) {
                    stack.push(current.right());
                }

                if (current.left() != null) {
                    stack.push(current.left());
                }
            }

            return List.copyOf(result);
        }

        public List<Integer> inorderIterative() {
            List<Integer> result = new ArrayList<>();
            Deque<TreeNode> stack = new ArrayDeque<>();

            TreeNode current = root;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.push(current);
                    current = current.left();
                }

                current = stack.pop();
                result.add(current.value());
                current = current.right();
            }

            return List.copyOf(result);
        }

        private record VisitState(
            TreeNode node,
            boolean visited
        ) {}

        public List<Integer> postorderIterative() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Deque<VisitState> stack = new ArrayDeque<>();

            stack.push(new VisitState(root, false));

            while (!stack.isEmpty()) {
                VisitState state = stack.pop();
                TreeNode current = state.node();

                if (state.visited()) {
                    result.add(current.value());
                    continue;
                }

                stack.push(new VisitState(current, true));

                if (current.right() != null) {
                    stack.push(
                        new VisitState(current.right(), false)
                    );
                }

                if (current.left() != null) {
                    stack.push(
                        new VisitState(current.left(), false)
                    );
                }
            }

            return List.copyOf(result);
        }

        public List<Integer> levelOrder() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.addLast(root);

            while (!queue.isEmpty()) {
                TreeNode current = queue.removeFirst();
                result.add(current.value());

                if (current.left() != null) {
                    queue.addLast(current.left());
                }

                if (current.right() != null) {
                    queue.addLast(current.right());
                }
            }

            return List.copyOf(result);
        }

        public List<List<Integer>> levelOrderByLevel() {
            if (root == null) return List.of();

            List<List<Integer>> levels = new ArrayList<>();
            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.addLast(root);

            while (!queue.isEmpty()) {
                int levelSize = queue.size();
                List<Integer> level = new ArrayList<>();

                for (int i = 0; i < levelSize; i++) {
                    TreeNode current = queue.removeFirst();
                    level.add(current.value());

                    if (current.left() != null) {
                        queue.addLast(current.left());
                    }

                    if (current.right() != null) {
                        queue.addLast(current.right());
                    }
                }

                levels.add(List.copyOf(level));
            }

            return List.copyOf(levels);
        }

        public TraversalResult execute(
            TraversalOrder order
        ) {
            Objects.requireNonNull(order, "Traversal order is required.");

            TraversalStrategy strategy = strategies.get(order);

            if (strategy == null) {
                throw new TraversalException(
                    "Unsupported traversal order."
                );
            }

            long start = System.nanoTime();
            List<Integer> result = strategy.execute(root);
            long elapsed = System.nanoTime() - start;

            return new TraversalResult(
                order,
                result,
                elapsed
            );
        }

        public Optional<TreeNode> find(int target) {
            if (root == null) return Optional.empty();

            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.addLast(root);

            while (!queue.isEmpty()) {
                TreeNode current = queue.removeFirst();

                if (current.value() == target) {
                    return Optional.of(current);
                }

                if (current.left() != null) {
                    queue.addLast(current.left());
                }

                if (current.right() != null) {
                    queue.addLast(current.right());
                }
            }

            return Optional.empty();
        }

        public int countNodes() {
            if (root == null) return 0;

            int count = 0;
            Deque<TreeNode> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                TreeNode current = stack.pop();
                count++;

                if (current.left() != null) {
                    stack.push(current.left());
                }

                if (current.right() != null) {
                    stack.push(current.right());
                }
            }

            return count;
        }

        public int height() {
            if (root == null) return 0;

            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.addLast(root);

            int height = 0;

            while (!queue.isEmpty()) {
                int levelSize = queue.size();

                for (int i = 0; i < levelSize; i++) {
                    TreeNode current = queue.removeFirst();

                    if (current.left() != null) {
                        queue.addLast(current.left());
                    }

                    if (current.right() != null) {
                        queue.addLast(current.right());
                    }
                }

                height++;
            }

            return height;
        }

        public boolean isComplete() {
            if (root == null) return true;

            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.addLast(root);

            boolean missingChild = false;

            while (!queue.isEmpty()) {
                TreeNode current = queue.removeFirst();

                TreeNode[] children = {
                    current.left(),
                    current.right()
                };

                for (TreeNode child : children) {
                    if (child == null) {
                        missingChild = true;
                    } else {
                        if (missingChild) return false;
                        queue.addLast(child);
                    }
                }
            }

            return true;
        }
    }

    private static TreeNode buildSampleTree() {
        TreeNode root = new TreeNode(50);

        TreeNode node30 = new TreeNode(30);
        TreeNode node70 = new TreeNode(70);

        root.setLeft(node30);
        root.setRight(node70);

        node30.setLeft(new TreeNode(20));
        node30.setRight(new TreeNode(40));

        TreeNode node60 = new TreeNode(60);
        node70.setLeft(node60);
        node70.setRight(new TreeNode(80));

        node30.left().setLeft(new TreeNode(10));
        node60.setRight(new TreeNode(65));

        return root;
    }

    private static void runTests(TraversalService service) {
        if (!service.preorderRecursive().equals(
            List.of(50, 30, 20, 10, 40, 70, 60, 65, 80)
        )) {
            throw new AssertionError("Preorder test failed.");
        }

        if (!service.inorderRecursive().equals(
            List.of(10, 20, 30, 40, 50, 60, 65, 70, 80)
        )) {
            throw new AssertionError("Inorder test failed.");
        }

        if (!service.postorderRecursive().equals(
            List.of(10, 20, 40, 30, 65, 60, 80, 70, 50)
        )) {
            throw new AssertionError("Postorder test failed.");
        }

        if (!service.levelOrder().equals(
            List.of(50, 30, 70, 20, 40, 60, 80, 10, 65)
        )) {
            throw new AssertionError("Level-order test failed.");
        }

        if (!service.preorderRecursive().equals(
            service.preorderIterative()
        )) {
            throw new AssertionError("Preorder mismatch.");
        }

        if (!service.inorderRecursive().equals(
            service.inorderIterative()
        )) {
            throw new AssertionError("Inorder mismatch.");
        }

        if (!service.postorderRecursive().equals(
            service.postorderIterative()
        )) {
            throw new AssertionError("Postorder mismatch.");
        }

        if (service.countNodes() != 9 || service.height() != 4) {
            throw new AssertionError("Tree metrics mismatch.");
        }

        if (service.find(65).isEmpty()) {
            throw new AssertionError("Search test failed.");
        }

        TraversalService empty = new TraversalService(null);

        if (!empty.levelOrder().isEmpty() || empty.height() != 0) {
            throw new AssertionError("Empty tree test failed.");
        }

        TreeNode singleRoot = new TreeNode(42);
        TraversalService single = new TraversalService(singleRoot);

        if (!single.inorderIterative().equals(List.of(42))) {
            throw new AssertionError("Single-node test failed.");
        }

        boolean rejected = false;

        try {
            singleRoot.setLeft(singleRoot);
        } catch (IllegalArgumentException exception) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError("Cycle validation failed.");
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            TreeNode root = buildSampleTree();
            TraversalService service = new TraversalService(root);

            System.out.println("BINARY TREE TRAVERSAL SYSTEM");
            System.out.println("============================");

            for (TraversalOrder order : TraversalOrder.values()) {
                TraversalResult result = service.execute(order);

                System.out.printf(
                    "%-12s %s | %d ns%n",
                    order,
                    result.values(),
                    result.elapsedNanos()
                );
            }

            System.out.println("\nRECURSIVE TRAVERSALS");
            System.out.println("Preorder : " + service.preorderRecursive());
            System.out.println("Inorder  : " + service.inorderRecursive());
            System.out.println("Postorder: " + service.postorderRecursive());

            System.out.println("\nLEVEL-WISE TRAVERSAL");

            List<List<Integer>> levels =
                service.levelOrderByLevel();

            for (int i = 0; i < levels.size(); i++) {
                System.out.println(
                    "Level " + i + ": " + levels.get(i)
                );
            }

            System.out.println("\nTREE ANALYTICS");
            System.out.println("Node count: " + service.countNodes());
            System.out.println("Height: " + service.height());
            System.out.println("Complete: " + service.isComplete());
            System.out.println(
                "Search 65: " + service.find(65).isPresent()
            );

            runTests(service);

        } catch (RuntimeException exception) {
            System.err.println(
                "Traversal system failure: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
