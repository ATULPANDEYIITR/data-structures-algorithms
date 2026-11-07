import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.OptionalInt;
import java.util.TreeSet;
import java.util.Objects;

public class AdvancedBST {

    enum OperationStatus {
        SUCCESS,
        DUPLICATE,
        NOT_FOUND,
        REJECTED
    }

    static class BSTException extends RuntimeException {
        BSTException(String message) {
            super(message);
        }
    }

    static class InvalidRankException extends BSTException {
        InvalidRankException(String message) {
            super(message);
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

    record TreeStatistics(
        int size,
        int height,
        boolean balanced,
        OptionalInt minimum,
        OptionalInt maximum
    ) {}

    record OperationResult(
        OperationStatus status,
        String message
    ) {}

    record ListEntry(
        int key,
        int position
    ) {}

    static final class DoublyLinkedList {
        static final class Entry {
            final int key;
            Entry previous;
            Entry next;

            Entry(int key) {
                this.key = key;
            }
        }

        private Entry head;
        private Entry tail;
        private int size;

        void append(int key) {
            Entry entry = new Entry(key);

            if (head == null) {
                head = entry;
                tail = entry;
            } else {
                tail.next = entry;
                entry.previous = tail;
                tail = entry;
            }

            size++;
        }

        List<Integer> toList() {
            List<Integer> result = new ArrayList<>();

            for (Entry current = head;
                 current != null;
                 current = current.next) {
                result.add(current.key);
            }

            return Collections.unmodifiableList(result);
        }

        List<Integer> reverseList() {
            List<Integer> result = new ArrayList<>();

            for (Entry current = tail;
                 current != null;
                 current = current.previous) {
                result.add(current.key);
            }

            return Collections.unmodifiableList(result);
        }

        int size() {
            return size;
        }
    }

    static final class BinarySearchTree {
        private Node root;
        private int size;

        int size() {
            return size;
        }

        boolean isEmpty() {
            return root == null;
        }

        boolean insert(int key) {
            if (root == null) {
                root = new Node(key);
                size++;
                return true;
            }

            Node current = root;

            while (true) {
                if (key == current.key) {
                    return false;
                }

                if (key < current.key) {
                    if (current.left == null) {
                        current.left = new Node(key);
                        size++;
                        return true;
                    }

                    current = current.left;
                } else {
                    if (current.right == null) {
                        current.right = new Node(key);
                        size++;
                        return true;
                    }

                    current = current.right;
                }
            }
        }

        boolean search(int key) {
            Node current = root;

            while (current != null) {
                if (key == current.key) {
                    return true;
                }

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            return false;
        }

        boolean delete(int key) {
            boolean[] deleted = {false};

            root = deleteNode(root, key, deleted);

            if (deleted[0]) {
                size--;
            }

            return deleted[0];
        }

        private Node deleteNode(
            Node node,
            int key,
            boolean[] deleted
        ) {
            if (node == null) {
                return null;
            }

            if (key < node.key) {
                node.left = deleteNode(node.left, key, deleted);
                return node;
            }

            if (key > node.key) {
                node.right = deleteNode(node.right, key, deleted);
                return node;
            }

            deleted[0] = true;

            if (node.left == null) {
                return node.right;
            }

            if (node.right == null) {
                return node.left;
            }

            Node successor = minimumNode(node.right);
            node.key = successor.key;
            node.right = deleteNode(
                node.right,
                successor.key,
                new boolean[1]
            );

            return node;
        }

        private Node minimumNode(Node node) {
            if (node == null) {
                throw new BSTException("Empty subtree.");
            }

            while (node.left != null) {
                node = node.left;
            }

            return node;
        }

        private Node maximumNode(Node node) {
            if (node == null) {
                throw new BSTException("Empty subtree.");
            }

            while (node.right != null) {
                node = node.right;
            }

            return node;
        }

        int minimum() {
            return minimumNode(root).key;
        }

        int maximum() {
            return maximumNode(root).key;
        }

        List<Integer> inorder() {
            List<Integer> result = new ArrayList<>();
            inorder(root, result);
            return Collections.unmodifiableList(result);
        }

        private void inorder(Node node, List<Integer> result) {
            if (node == null) return;

            inorder(node.left, result);
            result.add(node.key);
            inorder(node.right, result);
        }

        List<Integer> preorder() {
            List<Integer> result = new ArrayList<>();
            preorder(root, result);
            return Collections.unmodifiableList(result);
        }

        private void preorder(Node node, List<Integer> result) {
            if (node == null) return;

            result.add(node.key);
            preorder(node.left, result);
            preorder(node.right, result);
        }

        List<Integer> postorder() {
            List<Integer> result = new ArrayList<>();
            postorder(root, result);
            return Collections.unmodifiableList(result);
        }

        private void postorder(Node node, List<Integer> result) {
            if (node == null) return;

            postorder(node.left, result);
            postorder(node.right, result);
            result.add(node.key);
        }

        int kthSmallest(int k) {
            if (k < 1 || k > size) {
                throw new InvalidRankException(
                    "k must be between 1 and " + size
                );
            }

            List<Node> stack = new ArrayList<>();
            Node current = root;
            int count = 0;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.add(current);
                    current = current.left;
                }

                current = stack.remove(stack.size() - 1);

                if (++count == k) {
                    return current.key;
                }

                current = current.right;
            }

            throw new BSTException("Unexpected traversal failure.");
        }

        int kthLargest(int k) {
            if (k < 1 || k > size) {
                throw new InvalidRankException("Invalid rank.");
            }

            List<Node> stack = new ArrayList<>();
            Node current = root;
            int count = 0;

            while (current != null || !stack.isEmpty()) {
                while (current != null) {
                    stack.add(current);
                    current = current.right;
                }

                current = stack.remove(stack.size() - 1);

                if (++count == k) {
                    return current.key;
                }

                current = current.left;
            }

            throw new BSTException("Unexpected traversal failure.");
        }

        int lowestCommonAncestor(int first, int second) {
            if (!search(first) || !search(second)) {
                throw new BSTException(
                    "Both keys must exist in the BST."
                );
            }

            Node current = root;

            while (current != null) {
                if (first < current.key && second < current.key) {
                    current = current.left;
                } else if (
                    first > current.key && second > current.key
                ) {
                    current = current.right;
                } else {
                    return current.key;
                }
            }

            throw new BSTException("LCA not found.");
        }

        int height() {
            if (root == null) return 0;

            return height(root);
        }

        private int height(Node node) {
            if (node == null) return 0;

            return 1 + Math.max(
                height(node.left),
                height(node.right)
            );
        }

        boolean isBalanced() {
            return checkBalance(root) != -1;
        }

        private int checkBalance(Node node) {
            if (node == null) return 0;

            int left = checkBalance(node.left);
            if (left == -1) return -1;

            int right = checkBalance(node.right);
            if (right == -1) return -1;

            if (Math.abs(left - right) > 1) return -1;

            return 1 + Math.max(left, right);
        }

        boolean validate() {
            int actual = validateNode(
                root,
                Long.MIN_VALUE,
                Long.MAX_VALUE
            );

            if (actual != size) {
                throw new BSTException("Tree size invariant violated.");
            }

            return true;
        }

        private int validateNode(
            Node node,
            long lower,
            long upper
        ) {
            if (node == null) return 0;

            if (node.key <= lower || node.key >= upper) {
                throw new BSTException(
                    "BST ordering invariant violated."
                );
            }

            return 1
                + validateNode(node.left, lower, node.key)
                + validateNode(node.right, node.key, upper);
        }

        List<Integer> rangeSearch(int low, int high) {
            if (low > high) {
                throw new IllegalArgumentException("Invalid range.");
            }

            List<Integer> result = new ArrayList<>();
            rangeSearch(root, low, high, result);

            return Collections.unmodifiableList(result);
        }

        private void rangeSearch(
            Node node,
            int low,
            int high,
            List<Integer> result
        ) {
            if (node == null) return;

            if (node.key > low) {
                rangeSearch(node.left, low, high, result);
            }

            if (node.key >= low && node.key <= high) {
                result.add(node.key);
            }

            if (node.key < high) {
                rangeSearch(node.right, low, high, result);
            }
        }

        static BinarySearchTree fromSorted(List<Integer> values) {
            Objects.requireNonNull(values, "Values cannot be null.");

            for (int i = 1; i < values.size(); i++) {
                if (values.get(i - 1) >= values.get(i)) {
                    throw new IllegalArgumentException(
                        "Values must be strictly increasing."
                    );
                }
            }

            BinarySearchTree tree = new BinarySearchTree();

            tree.root = buildBalanced(values, 0, values.size() - 1);
            tree.size = values.size();

            return tree;
        }

        private static Node buildBalanced(
            List<Integer> values,
            int start,
            int end
        ) {
            if (start > end) return null;

            int middle = start + (end - start) / 2;
            Node node = new Node(values.get(middle));

            node.left = buildBalanced(values, start, middle - 1);
            node.right = buildBalanced(values, middle + 1, end);

            return node;
        }

        static BinarySearchTree fromPreorder(List<Integer> values) {
            Objects.requireNonNull(values, "Values cannot be null.");

            if (new TreeSet<>(values).size() != values.size()) {
                throw new IllegalArgumentException(
                    "Preorder values must be unique."
                );
            }

            BinarySearchTree tree = new BinarySearchTree();
            int[] index = {0};

            tree.root = buildPreorder(
                values,
                index,
                Long.MIN_VALUE,
                Long.MAX_VALUE
            );

            if (index[0] != values.size()) {
                throw new IllegalArgumentException(
                    "Invalid BST preorder traversal."
                );
            }

            tree.size = values.size();
            return tree;
        }

        private static Node buildPreorder(
            List<Integer> values,
            int[] index,
            long lower,
            long upper
        ) {
            if (index[0] >= values.size()) return null;

            int value = values.get(index[0]);

            if (value <= lower || value >= upper) {
                return null;
            }

            index[0]++;

            Node node = new Node(value);

            node.left = buildPreorder(
                values,
                index,
                lower,
                value
            );

            node.right = buildPreorder(
                values,
                index,
                value,
                upper
            );

            return node;
        }

        void rebalance() {
            List<Integer> sorted = inorder();
            BinarySearchTree rebuilt = fromSorted(sorted);

            root = rebuilt.root;
            size = rebuilt.size;
        }

        DoublyLinkedList toDoublyLinkedList() {
            DoublyLinkedList result = new DoublyLinkedList();
            convert(root, result);
            return result;
        }

        private void convert(
            Node node,
            DoublyLinkedList result
        ) {
            if (node == null) return;

            convert(node.left, result);
            result.append(node.key);
            convert(node.right, result);
        }

        TreeStatistics statistics() {
            return new TreeStatistics(
                size,
                height(),
                isBalanced(),
                root == null
                    ? OptionalInt.empty()
                    : OptionalInt.of(minimum()),
                root == null
                    ? OptionalInt.empty()
                    : OptionalInt.of(maximum())
            );
        }
    }

    enum AssetStatus {
        ACTIVE,
        ARCHIVED,
        PENDING
    }

    record Asset(
        int id,
        String name,
        AssetStatus status
    ) {
        Asset {
            if (id <= 0) {
                throw new IllegalArgumentException(
                    "Asset ID must be positive."
                );
            }

            Objects.requireNonNull(name);
            Objects.requireNonNull(status);

            if (name.isBlank()) {
                throw new IllegalArgumentException(
                    "Asset name cannot be blank."
                );
            }
        }
    }

    static final class AssetRegistry {
        private final BinarySearchTree index =
            new BinarySearchTree();

        private final java.util.Map<Integer, Asset> assets =
            new java.util.HashMap<>();

        OperationResult register(Asset asset) {
            Objects.requireNonNull(asset);

            if (assets.containsKey(asset.id())) {
                return new OperationResult(
                    OperationStatus.DUPLICATE,
                    "Asset already registered."
                );
            }

            if (!index.insert(asset.id())) {
                return new OperationResult(
                    OperationStatus.REJECTED,
                    "Index integrity conflict."
                );
            }

            assets.put(asset.id(), asset);

            return new OperationResult(
                OperationStatus.SUCCESS,
                "Asset registered."
            );
        }

        OperationResult remove(int id) {
            Asset existing = assets.get(id);

            if (existing == null) {
                return new OperationResult(
                    OperationStatus.NOT_FOUND,
                    "Asset not found."
                );
            }

            if (!index.delete(id)) {
                throw new BSTException(
                    "Asset index and registry are inconsistent."
                );
            }

            assets.remove(id);

            return new OperationResult(
                OperationStatus.SUCCESS,
                "Asset removed."
            );
        }

        Asset find(int id) {
            Asset asset = assets.get(id);

            if (asset == null) {
                throw new BSTException("Asset not found.");
            }

            return asset;
        }

        Asset findByRank(int rank) {
            return find(index.kthSmallest(rank));
        }

        int commonAssetGroup(int first, int second) {
            return index.lowestCommonAncestor(first, second);
        }

        void optimize() {
            index.rebalance();
            index.validate();
        }

        void printReport() {
            System.out.println("Registered asset IDs: " + index.inorder());
            System.out.println("Tree statistics: " + index.statistics());
        }
    }

    private static void runTests() {
        BinarySearchTree tree = new BinarySearchTree();

        for (int key : new int[]{50, 30, 70, 20, 40, 60, 80}) {
            tree.insert(key);
        }

        assert tree.validate();
        assert tree.size() == 7;
        assert tree.inorder().equals(
            List.of(20, 30, 40, 50, 60, 70, 80)
        );

        assert tree.kthSmallest(3) == 40;
        assert tree.kthLargest(2) == 70;
        assert tree.lowestCommonAncestor(20, 40) == 30;
        assert tree.lowestCommonAncestor(20, 80) == 50;

        assert tree.insert(90);
        assert !tree.insert(50);
        assert tree.delete(70);
        assert !tree.search(70);
        assert tree.validate();

        DoublyLinkedList linked = tree.toDoublyLinkedList();

        assert linked.toList().equals(tree.inorder());
        assert linked.reverseList().equals(
            new ArrayList<>(tree.inorder().reversed())
        );

        BinarySearchTree balanced = BinarySearchTree.fromSorted(
            List.of(10, 20, 30, 40, 50, 60, 70)
        );

        assert balanced.isBalanced();

        BinarySearchTree reconstructed =
            BinarySearchTree.fromPreorder(
                List.of(50, 30, 20, 40, 70, 60, 80)
            );

        assert reconstructed.inorder().equals(
            List.of(20, 30, 40, 50, 60, 70, 80)
        );

        BinarySearchTree skewed = new BinarySearchTree();

        for (int i = 1; i <= 100; i++) {
            skewed.insert(i);
        }

        assert !skewed.isBalanced();
        assert skewed.height() == 100;

        skewed.rebalance();

        assert skewed.isBalanced();
        assert skewed.height() <= 7;
        assert skewed.validate();

        BinarySearchTree empty = new BinarySearchTree();

        assert empty.isEmpty();
        assert empty.height() == 0;
        assert empty.isBalanced();

        try {
            tree.kthSmallest(0);
            throw new AssertionError("Invalid rank accepted.");
        } catch (InvalidRankException expected) {
            // Expected validation failure.
        }

        try {
            BinarySearchTree.fromSorted(List.of(1, 2, 2, 3));
            throw new AssertionError("Duplicate keys accepted.");
        } catch (IllegalArgumentException expected) {
            // Expected validation failure.
        }

        try {
            BinarySearchTree.fromPreorder(
                List.of(10, 5, 12, 4)
            );
            throw new AssertionError("Invalid preorder accepted.");
        } catch (IllegalArgumentException expected) {
            // Expected validation failure.
        }

        AssetRegistry registry = new AssetRegistry();

        assert registry.register(
            new Asset(1001, "Server", AssetStatus.ACTIVE)
        ).status() == OperationStatus.SUCCESS;

        assert registry.register(
            new Asset(1002, "Router", AssetStatus.ACTIVE)
        ).status() == OperationStatus.SUCCESS;

        assert registry.findByRank(1).id() == 1001;
        assert registry.remove(1001).status() ==
            OperationStatus.SUCCESS;

        System.out.println("All Java 17 BST tests passed.");
    }

    public static void main(String[] args) {
        try {
            runTests();

            BinarySearchTree tree = new BinarySearchTree();

            for (int value : new int[]{
                50, 30, 70, 20, 40, 60, 80
            }) {
                tree.insert(value);
            }

            System.out.println("\nADVANCED BST DEMONSTRATION");

            System.out.println("Inorder: " + tree.inorder());
            System.out.println("Preorder: " + tree.preorder());
            System.out.println("Postorder: " + tree.postorder());

            System.out.println("3rd smallest: " +
                tree.kthSmallest(3));

            System.out.println("2nd largest: " +
                tree.kthLargest(2));

            System.out.println("LCA of 20 and 40: " +
                tree.lowestCommonAncestor(20, 40));

            System.out.println("Statistics: " +
                tree.statistics());

            DoublyLinkedList linked = tree.toDoublyLinkedList();

            System.out.println("Doubly linked list: " +
                linked.toList());

            System.out.println("Reverse list: " +
                linked.reverseList());

            AssetRegistry registry = new AssetRegistry();

            registry.register(
                new Asset(1040, "Database Server", AssetStatus.ACTIVE)
            );

            registry.register(
                new Asset(1020, "Network Router", AssetStatus.ACTIVE)
            );

            registry.register(
                new Asset(1060, "Security Gateway", AssetStatus.PENDING)
            );

            registry.register(
                new Asset(1010, "Storage Unit", AssetStatus.ACTIVE)
            );

            registry.register(
                new Asset(1030, "Application Server", AssetStatus.ACTIVE)
            );

            System.out.println("\nEnterprise Asset Registry");

            registry.printReport();

            System.out.println("Third asset by ID: " +
                registry.findByRank(3));

            registry.optimize();

            System.out.println("After index optimization:");
            registry.printReport();

        } catch (Exception exception) {
            System.err.println(
                "Execution failed: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
