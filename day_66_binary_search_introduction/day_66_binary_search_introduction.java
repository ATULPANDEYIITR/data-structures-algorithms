import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Optional;
import java.util.Objects;
import java.util.function.Consumer;

public class Main {

    enum OperationType {
        INSERT,
        DELETE,
        SEARCH,
        DUPLICATE_REJECTED
    }

    enum NodePosition {
        ROOT,
        LEFT,
        RIGHT
    }

    record AuditEvent(
        OperationType operation,
        int key,
        int currentSize
    ) {}

    record SearchResult(
        boolean found,
        Integer value,
        int comparisons
    ) {}

    record TreeStatistics(
        int nodeCount,
        int height,
        Optional<Integer> minimum,
        Optional<Integer> maximum
    ) {}

    static final class BSTException extends RuntimeException {
        BSTException(String message) {
            super(message);
        }
    }

    static final class Node {
        private int key;
        private Node left;
        private Node right;

        Node(int key) {
            this.key = key;
        }
    }

    interface TreePolicy {
        boolean allowInsertion(int currentSize);

        void validateKey(int key);
    }

    static final class EnterpriseTreePolicy implements TreePolicy {
        private final int maximumNodes;

        EnterpriseTreePolicy(int maximumNodes) {
            if (maximumNodes < 0) {
                throw new IllegalArgumentException(
                    "Maximum node count cannot be negative."
                );
            }

            this.maximumNodes = maximumNodes;
        }

        @Override
        public boolean allowInsertion(int currentSize) {
            return currentSize < maximumNodes;
        }

        @Override
        public void validateKey(int key) {
            // Java int provides a fixed, bounded integer key domain.
        }
    }

    static final class BinarySearchTree {
        private Node root;
        private int size;

        private final TreePolicy policy;
        private final List<Consumer<AuditEvent>> listeners =
            new ArrayList<>();

        BinarySearchTree(TreePolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        public void addListener(Consumer<AuditEvent> listener) {
            listeners.add(Objects.requireNonNull(listener));
        }

        private void publish(OperationType operation, int key) {
            AuditEvent event = new AuditEvent(operation, key, size);

            // Isolate the tree from failures in external audit consumers.
            for (Consumer<AuditEvent> listener :
                    List.copyOf(listeners)) {
                try {
                    listener.accept(event);
                } catch (RuntimeException exception) {
                    System.err.println(
                        "Audit listener failed: " + exception.getMessage()
                    );
                }
            }
        }

        public boolean insert(int key) {
            policy.validateKey(key);

            if (!policy.allowInsertion(size)) {
                throw new BSTException("Tree capacity exceeded.");
            }

            if (root == null) {
                root = new Node(key);
                size++;
                publish(OperationType.INSERT, key);
                return true;
            }

            Node current = root;

            while (true) {
                if (key == current.key) {
                    publish(OperationType.DUPLICATE_REJECTED, key);
                    return false;
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
            publish(OperationType.INSERT, key);
            return true;
        }

        public SearchResult search(int key) {
            policy.validateKey(key);

            Node current = root;
            int comparisons = 0;

            while (current != null) {
                comparisons++;

                if (key == current.key) {
                    publish(OperationType.SEARCH, key);

                    return new SearchResult(
                        true,
                        current.key,
                        comparisons
                    );
                }

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            publish(OperationType.SEARCH, key);

            return new SearchResult(false, null, comparisons);
        }

        public Optional<Integer> minimum() {
            Node node = root;

            if (node == null) return Optional.empty();

            while (node.left != null) {
                node = node.left;
            }

            return Optional.of(node.key);
        }

        public Optional<Integer> maximum() {
            Node node = root;

            if (node == null) return Optional.empty();

            while (node.right != null) {
                node = node.right;
            }

            return Optional.of(node.key);
        }

        public Optional<Integer> predecessor(int key) {
            policy.validateKey(key);

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

        public Optional<Integer> successor(int key) {
            policy.validateKey(key);

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

        public boolean delete(int key) {
            policy.validateKey(key);

            Node parent = null;
            Node current = root;

            while (current != null && current.key != key) {
                parent = current;

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            if (current == null) return false;

            // Two-child deletion: replace with the inorder successor.
            if (current.left != null && current.right != null) {
                Node successorParent = current;
                Node successor = current.right;

                while (successor.left != null) {
                    successorParent = successor;
                    successor = successor.left;
                }

                current.key = successor.key;
                parent = successorParent;
                current = successor;
            }

            Node child = current.left != null
                ? current.left
                : current.right;

            if (parent == null) {
                root = child;
            } else if (parent.left == current) {
                parent.left = child;
            } else {
                parent.right = child;
            }

            size--;
            publish(OperationType.DELETE, key);
            return true;
        }

        public List<Integer> inorder() {
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

        public List<Integer> preorder() {
            List<Integer> result = new ArrayList<>();

            if (root == null) return List.of();

            Deque<Node> stack = new ArrayDeque<>();
            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                result.add(node.key);

                if (node.right != null) stack.push(node.right);
                if (node.left != null) stack.push(node.left);
            }

            return List.copyOf(result);
        }

        public List<Integer> postorder() {
            List<Integer> result = new ArrayList<>();

            if (root == null) return List.of();

            Deque<Node> stack = new ArrayDeque<>();
            Deque<Node> output = new ArrayDeque<>();

            stack.push(root);

            while (!stack.isEmpty()) {
                Node node = stack.pop();
                output.push(node);

                if (node.left != null) stack.push(node.left);
                if (node.right != null) stack.push(node.right);
            }

            while (!output.isEmpty()) {
                result.add(output.pop().key);
            }

            return List.copyOf(result);
        }

        public List<Integer> levelOrder() {
            List<Integer> result = new ArrayList<>();

            if (root == null) return List.of();

            Deque<Node> queue = new ArrayDeque<>();
            queue.add(root);

            while (!queue.isEmpty()) {
                Node node = queue.removeFirst();
                result.add(node.key);

                if (node.left != null) queue.addLast(node.left);
                if (node.right != null) queue.addLast(node.right);
            }

            return List.copyOf(result);
        }

        public List<Integer> rangeSearch(int low, int high) {
            if (low > high) {
                throw new IllegalArgumentException(
                    "Lower bound exceeds upper bound."
                );
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

        public int height() {
            if (root == null) return 0;

            record LevelNode(Node node, int depth) {}

            Deque<LevelNode> stack = new ArrayDeque<>();
            stack.push(new LevelNode(root, 1));

            int maximum = 0;

            while (!stack.isEmpty()) {
                LevelNode entry = stack.pop();
                Node node = entry.node();

                maximum = Math.max(maximum, entry.depth());

                if (node.left != null) {
                    stack.push(
                        new LevelNode(node.left, entry.depth() + 1)
                    );
                }

                if (node.right != null) {
                    stack.push(
                        new LevelNode(node.right, entry.depth() + 1)
                    );
                }
            }

            return maximum;
        }

        public boolean validate() {
            record Bounds(Node node, Long lower, Long upper) {}

            if (root == null) return size == 0;

            Deque<Bounds> stack = new ArrayDeque<>();
            stack.push(new Bounds(root, null, null));

            int count = 0;

            while (!stack.isEmpty()) {
                Bounds entry = stack.pop();
                Node node = entry.node();
                count++;

                if (entry.lower() != null &&
                        node.key <= entry.lower()) {
                    return false;
                }

                if (entry.upper() != null &&
                        node.key >= entry.upper()) {
                    return false;
                }

                if (node.left != null) {
                    stack.push(
                        new Bounds(node.left, entry.lower(), (long) node.key)
                    );
                }

                if (node.right != null) {
                    stack.push(
                        new Bounds(node.right, (long) node.key, entry.upper())
                    );
                }
            }

            return count == size;
        }

        public TreeStatistics statistics() {
            return new TreeStatistics(
                size,
                height(),
                minimum(),
                maximum()
            );
        }

        public int size() {
            return size;
        }
    }

    private static void runTests() {
        BinarySearchTree tree =
            new BinarySearchTree(new EnterpriseTreePolicy(100));

        for (int key : new int[]{50, 30, 70, 20, 40, 60, 80}) {
            assert tree.insert(key);
        }

        assert !tree.insert(50);

        assert tree.search(40).found();
        assert !tree.search(999).found();

        assert tree.minimum().orElseThrow() == 20;
        assert tree.maximum().orElseThrow() == 80;

        assert tree.predecessor(50).orElseThrow() == 40;
        assert tree.successor(50).orElseThrow() == 60;

        assert tree.predecessor(10).isEmpty();
        assert tree.successor(100).isEmpty();

        assert tree.inorder().equals(
            List.of(20, 30, 40, 50, 60, 70, 80)
        );

        assert tree.delete(20);
        assert tree.delete(30);
        assert tree.delete(70);
        assert tree.delete(50);
        assert !tree.delete(999);

        assert tree.validate();
        assert tree.size() == 3;

        assert tree.rangeSearch(40, 80).equals(
            List.of(40, 60, 80)
        );

        boolean failed = false;

        try {
            tree.rangeSearch(80, 20);
        } catch (IllegalArgumentException exception) {
            failed = true;
        }

        assert failed;

        BinarySearchTree limited =
            new BinarySearchTree(new EnterpriseTreePolicy(1));

        limited.insert(10);

        failed = false;

        try {
            limited.insert(20);
        } catch (BSTException exception) {
            failed = true;
        }

        assert failed;

        System.out.println("All Java 17 BST tests passed.");
    }

    private static void demonstrate() {
        BinarySearchTree employeeIndex =
            new BinarySearchTree(new EnterpriseTreePolicy(1000));

        employeeIndex.addListener(event ->
            System.out.printf(
                "AUDIT operation=%s key=%d size=%d%n",
                event.operation(),
                event.key(),
                event.currentSize()
            )
        );

        // Unique employee identifiers.
        for (int id : new int[]{
            5000, 3000, 7000, 2000, 4000, 6000, 8000
        }) {
            employeeIndex.insert(id);
        }

        System.out.println("\nEMPLOYEE DIRECTORY INDEX");
        System.out.println("Inorder: " + employeeIndex.inorder());
        System.out.println("Preorder: " + employeeIndex.preorder());
        System.out.println("Postorder: " + employeeIndex.postorder());
        System.out.println("Level order: " + employeeIndex.levelOrder());

        System.out.println(
            "Search employee 4000: " + employeeIndex.search(4000)
        );

        System.out.println(
            "Predecessor: " +
            employeeIndex.predecessor(5000).orElseThrow()
        );

        System.out.println(
            "Successor: " +
            employeeIndex.successor(5000).orElseThrow()
        );

        System.out.println("Statistics: " + employeeIndex.statistics());

        employeeIndex.delete(5000);

        System.out.println(
            "After deletion: " + employeeIndex.inorder()
        );

        System.out.println(
            "Ordering valid: " + employeeIndex.validate()
        );
    }

    public static void main(String[] args) {
        runTests();
        demonstrate();
    }
}
