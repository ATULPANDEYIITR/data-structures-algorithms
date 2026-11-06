import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;

/**
 * BST Traversal and Validation
 *
 * Enterprise scenario:
 * An asset registry maintains unique integer asset identifiers.
 * The BST supports ordered retrieval, boundary searches, and
 * integrity validation.
 *
 * Java 17 implementation with explicit domain types,
 * immutable audit events, and service-level validation.
 */
public class Main {

    enum Operation {
        INSERT,
        DELETE
    }

    enum RegistryStatus {
        ACTIVE,
        EMPTY
    }

    record AuditEvent(
        long sequence,
        Operation operation,
        int key
    ) {}

    record QueryResult<T>(
        boolean found,
        T value
    ) {
        static <T> QueryResult<T> of(Optional<T> value) {
            return new QueryResult<>(
                value.isPresent(),
                value.orElse(null)
            );
        }
    }

    static class RegistryException extends RuntimeException {
        RegistryException(String message) {
            super(message);
        }
    }

    static class DuplicateAssetException extends RegistryException {
        DuplicateAssetException(int key) {
            super("Asset identifier already exists: " + key);
        }
    }

    static class InvalidRangeException extends RegistryException {
        InvalidRangeException() {
            super("The lower range boundary exceeds the upper boundary.");
        }
    }

    static final class Node {
        int key;
        Node left;
        Node right;

        Node(int key) {
            this.key = key;
        }
    }

    static final class BinarySearchTree {

        private Node root;
        private int size;

        private final List<AuditEvent> auditEvents =
            new ArrayList<>();

        private final AtomicLong sequence =
            new AtomicLong();

        int size() {
            return size;
        }

        RegistryStatus status() {
            return root == null
                ? RegistryStatus.EMPTY
                : RegistryStatus.ACTIVE;
        }

        private void record(Operation operation, int key) {
            auditEvents.add(
                new AuditEvent(
                    sequence.incrementAndGet(),
                    operation,
                    key
                )
            );
        }

        List<AuditEvent> auditEvents() {
            return Collections.unmodifiableList(
                new ArrayList<>(auditEvents)
            );
        }

        void insert(int key) {
            if (root == null) {
                root = new Node(key);
                size++;
                record(Operation.INSERT, key);
                return;
            }

            Node current = root;

            while (true) {
                if (key == current.key) {
                    throw new DuplicateAssetException(key);
                }

                if (key < current.key) {
                    if (current.left == null) {
                        current.left = new Node(key);
                        break;
                    }

                    current = current.left;
                } else {
                    if (current.right == null) {
                        current.right = new Node(key);
                        break;
                    }

                    current = current.right;
                }
            }

            size++;
            record(Operation.INSERT, key);
        }

        /**
         * Batch insertion validates all keys before changing the tree.
         */
        void insertBatch(List<Integer> keys) {
            Set<Integer> batch = new HashSet<>();

            for (Integer key : keys) {
                if (key == null) {
                    throw new IllegalArgumentException(
                        "Asset identifiers cannot be null."
                    );
                }

                if (!batch.add(key) || search(key)) {
                    throw new DuplicateAssetException(key);
                }
            }

            for (int key : keys) {
                insert(key);
            }
        }

        boolean search(int key) {
            Node current = root;

            while (current != null) {
                if (key == current.key) return true;

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            return false;
        }

        List<Integer> inorder() {
            List<Integer> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();

            Node current = root;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.push(current);
                    current = current.left;
                }

                current = stack.pop();
                result.add(current.key);
                current = current.right;
            }

            return List.copyOf(result);
        }

        List<Integer> preorder() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                result.add(node.key);

                if (node.right != null) {
                    stack.push(node.right);
                }

                if (node.left != null) {
                    stack.push(node.left);
                }
            }

            return List.copyOf(result);
        }

        List<Integer> postorder() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();

            Deque<Node> stack = new ArrayDeque<>();
            Deque<Node> output = new ArrayDeque<>();

            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                output.push(node);

                if (node.left != null) {
                    stack.push(node.left);
                }

                if (node.right != null) {
                    stack.push(node.right);
                }
            }

            while (!output.isEmpty()) {
                result.add(output.pop().key);
            }

            return List.copyOf(result);
        }

        List<Integer> levelOrder() {
            if (root == null) return List.of();

            List<Integer> result = new ArrayList<>();
            Deque<Node> queue = new ArrayDeque<>();

            queue.add(root);

            while (!queue.isEmpty()) {
                Node node = queue.remove();

                result.add(node.key);

                if (node.left != null) queue.add(node.left);
                if (node.right != null) queue.add(node.right);
            }

            return List.copyOf(result);
        }

        int minimum() {
            if (root == null) {
                throw new RegistryException(
                    "Minimum is undefined for an empty registry."
                );
            }

            Node current = root;

            while (current.left != null) {
                current = current.left;
            }

            return current.key;
        }

        int maximum() {
            if (root == null) {
                throw new RegistryException(
                    "Maximum is undefined for an empty registry."
                );
            }

            Node current = root;

            while (current.right != null) {
                current = current.right;
            }

            return current.key;
        }

        Optional<Integer> floor(int key) {
            Node current = root;
            Integer candidate = null;

            while (current != null) {
                if (current.key == key) {
                    return Optional.of(key);
                }

                if (current.key < key) {
                    candidate = current.key;
                    current = current.right;
                } else {
                    current = current.left;
                }
            }

            return Optional.ofNullable(candidate);
        }

        Optional<Integer> ceiling(int key) {
            Node current = root;
            Integer candidate = null;

            while (current != null) {
                if (current.key == key) {
                    return Optional.of(key);
                }

                if (current.key > key) {
                    candidate = current.key;
                    current = current.left;
                } else {
                    current = current.right;
                }
            }

            return Optional.ofNullable(candidate);
        }

        List<Integer> rangeQuery(int low, int high) {
            if (low > high) {
                throw new InvalidRangeException();
            }

            List<Integer> result = new ArrayList<>();
            Deque<Node> stack = new ArrayDeque<>();

            Node current = root;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    if (current.key >= low) {
                        stack.push(current);
                        current = current.left;
                    } else {
                        current = current.right;
                    }
                }

                if (stack.isEmpty()) break;

                current = stack.pop();

                if (current.key > high) break;

                result.add(current.key);
                current = current.right;
            }

            return List.copyOf(result);
        }

        Optional<Integer> successor(int key) {
            Node current = root;
            Integer candidate = null;

            while (current != null) {
                if (current.key > key) {
                    candidate = current.key;
                    current = current.left;
                } else {
                    current = current.right;
                }
            }

            return Optional.ofNullable(candidate);
        }

        Optional<Integer> predecessor(int key) {
            Node current = root;
            Integer candidate = null;

            while (current != null) {
                if (current.key < key) {
                    candidate = current.key;
                    current = current.right;
                } else {
                    current = current.left;
                }
            }

            return Optional.ofNullable(candidate);
        }

        boolean delete(int key) {
            boolean[] deleted = {false};

            root = deleteNode(root, key, deleted);

            if (deleted[0]) {
                size--;
                record(Operation.DELETE, key);
            }

            return deleted[0];
        }

        private Node deleteNode(
            Node node,
            int key,
            boolean[] deleted
        ) {
            if (node == null) return null;

            if (key < node.key) {
                node.left = deleteNode(node.left, key, deleted);
            } else if (key > node.key) {
                node.right = deleteNode(node.right, key, deleted);
            } else {
                deleted[0] = true;

                if (node.left == null) return node.right;
                if (node.right == null) return node.left;

                Node successor = node.right;

                while (successor.left != null) {
                    successor = successor.left;
                }

                node.key = successor.key;
                node.right = deleteNode(
                    node.right,
                    successor.key,
                    new boolean[1]
                );
            }

            return node;
        }

        boolean validate() {
            record ValidationState(
                Node node,
                Long lower,
                Long upper
            ) {}

            Set<Node> visited = new HashSet<>();

            Deque<ValidationState> stack = new ArrayDeque<>();

            if (root != null) {
                stack.push(new ValidationState(root, null, null));
            }

            int count = 0;

            while (!stack.isEmpty()) {
                ValidationState state = stack.pop();
                Node node = state.node();

                if (!visited.add(node)) return false;

                count++;

                if (state.lower() != null &&
                    node.key <= state.lower()) {
                    return false;
                }

                if (state.upper() != null &&
                    node.key >= state.upper()) {
                    return false;
                }

                if (node.right != null) {
                    stack.push(
                        new ValidationState(
                            node.right,
                            (long) node.key,
                            state.upper()
                        )
                    );
                }

                if (node.left != null) {
                    stack.push(
                        new ValidationState(
                            node.left,
                            state.lower(),
                            (long) node.key
                        )
                    );
                }
            }

            return count == size;
        }

        int height() {
            if (root == null) return 0;

            record DepthNode(Node node, int depth) {}

            Deque<DepthNode> queue = new ArrayDeque<>();
            queue.add(new DepthNode(root, 1));

            int maximumDepth = 0;

            while (!queue.isEmpty()) {
                DepthNode current = queue.remove();

                maximumDepth = Math.max(
                    maximumDepth,
                    current.depth()
                );

                if (current.node().left != null) {
                    queue.add(
                        new DepthNode(
                            current.node().left,
                            current.depth() + 1
                        )
                    );
                }

                if (current.node().right != null) {
                    queue.add(
                        new DepthNode(
                            current.node().right,
                            current.depth() + 1
                        )
                    );
                }
            }

            return maximumDepth;
        }

        static BinarySearchTree fromSorted(List<Integer> values) {
            for (int i = 1; i < values.size(); i++) {
                if (values.get(i - 1) >= values.get(i)) {
                    throw new IllegalArgumentException(
                        "Input must be strictly increasing."
                    );
                }
            }

            BinarySearchTree tree = new BinarySearchTree();

            tree.root = buildBalanced(
                values,
                0,
                values.size() - 1
            );

            tree.size = values.size();

            return tree;
        }

        private static Node buildBalanced(
            List<Integer> values,
            int left,
            int right
        ) {
            if (left > right) return null;

            int middle = left + (right - left) / 2;

            Node node = new Node(values.get(middle));

            node.left = buildBalanced(
                values,
                left,
                middle - 1
            );

            node.right = buildBalanced(
                values,
                middle + 1,
                right
            );

            return node;
        }
    }

    static final class RegistryService {

        private final BinarySearchTree tree;

        RegistryService(BinarySearchTree tree) {
            this.tree = tree;
        }

        QueryResult<Integer> findFloor(int key) {
            return QueryResult.of(tree.floor(key));
        }

        QueryResult<Integer> findCeiling(int key) {
            return QueryResult.of(tree.ceiling(key));
        }

        List<Integer> getAssetsInRange(int minimum, int maximum) {
            return tree.rangeQuery(minimum, maximum);
        }

        boolean isRegistryHealthy() {
            return tree.validate();
        }
    }

    private static void runTests() {
        BinarySearchTree tree = new BinarySearchTree();

        tree.insertBatch(
            List.of(50, 30, 70, 20, 40, 60, 80)
        );

        assert tree.validate();
        assert tree.inorder().equals(
            List.of(20, 30, 40, 50, 60, 70, 80)
        );

        assert tree.minimum() == 20;
        assert tree.maximum() == 80;

        assert tree.floor(45).orElseThrow() == 40;
        assert tree.ceiling(45).orElseThrow() == 50;

        assert tree.successor(50).orElseThrow() == 60;
        assert tree.predecessor(50).orElseThrow() == 40;

        assert tree.rangeQuery(30, 70).equals(
            List.of(30, 40, 50, 60, 70)
        );

        try {
            tree.insert(50);
            throw new AssertionError("Duplicate should fail.");
        } catch (DuplicateAssetException expected) {
        }

        assert tree.delete(20);
        assert tree.delete(30);
        assert tree.delete(50);
        assert tree.validate();

        BinarySearchTree balanced = BinarySearchTree.fromSorted(
            java.util.stream.IntStream.rangeClosed(1, 15)
                .boxed()
                .toList()
        );

        assert balanced.height() == 4;
        assert balanced.validate();

        BinarySearchTree empty = new BinarySearchTree();
        assert empty.validate();
        assert empty.inorder().isEmpty();

        try {
            tree.rangeQuery(100, 50);
            throw new AssertionError("Invalid range should fail.");
        } catch (InvalidRangeException expected) {
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        BinarySearchTree assetRegistry = new BinarySearchTree();

        assetRegistry.insertBatch(
            List.of(
                5000, 3000, 7000, 2000,
                4000, 6000, 8000
            )
        );

        RegistryService service =
            new RegistryService(assetRegistry);

        System.out.println("Enterprise Asset Registry");
        System.out.println("==========================");

        System.out.println("Inorder: " + assetRegistry.inorder());
        System.out.println("Preorder: " + assetRegistry.preorder());
        System.out.println("Postorder: " + assetRegistry.postorder());
        System.out.println("Level order: " + assetRegistry.levelOrder());

        System.out.println("\nRegistry queries");

        System.out.println("Minimum: " + assetRegistry.minimum());
        System.out.println("Maximum: " + assetRegistry.maximum());

        System.out.println(
            "Floor of 4500: " + service.findFloor(4500)
        );

        System.out.println(
            "Ceiling of 4500: " + service.findCeiling(4500)
        );

        System.out.println(
            "Range 3000-7000: " +
            service.getAssetsInRange(3000, 7000)
        );

        System.out.println(
            "Successor of 5000: " +
            assetRegistry.successor(5000)
        );

        System.out.println(
            "Predecessor of 5000: " +
            assetRegistry.predecessor(5000)
        );

        System.out.println(
            "\nRegistry healthy: " +
            service.isRegistryHealthy()
        );

        System.out.println(
            "Registry height: " + assetRegistry.height()
        );

        assetRegistry.delete(5000);

        System.out.println(
            "After deletion: " + assetRegistry.inorder()
        );

        System.out.println(
            "Audit event count: " +
            assetRegistry.auditEvents().size()
        );

        System.out.println(
            "Registry healthy after deletion: " +
            service.isRegistryHealthy()
        );

        runTests();
    }
}
