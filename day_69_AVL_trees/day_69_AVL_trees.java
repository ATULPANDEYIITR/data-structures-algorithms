import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.OptionalInt;
import java.util.Set;

/**
 * AVL Trees: Enterprise Product Catalog Index.
 *
 * Java 17 implementation featuring:
 * - Generic AVL tree
 * - LL, RR, LR, RL rotations
 * - Insertion and deletion
 * - Search and range retrieval
 * - Structural validation
 * - Immutable search results
 * - Rotation and operation monitoring
 * - Enterprise service and validation layer
 *
 * Compile:
 * javac AVLTreeDemo.java
 *
 * Run:
 * java AVLTreeDemo
 */
public class AVLTreeDemo {

    enum RotationType {
        LL, RR, LR, RL
    }

    enum OperationType {
        INSERT, DELETE, SEARCH
    }

    record Product(
        int productId,
        String name,
        String category,
        int quantity
    ) {
        Product {
            if (productId <= 0) {
                throw new IllegalArgumentException(
                    "Product ID must be positive."
                );
            }

            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Product name is required."
                );
            }

            if (category == null || category.isBlank()) {
                throw new IllegalArgumentException(
                    "Product category is required."
                );
            }

            if (quantity < 0) {
                throw new IllegalArgumentException(
                    "Quantity cannot be negative."
                );
            }

            name = name.strip();
            category = category.strip();
        }
    }

    record SearchResult<T>(
        T value,
        boolean found
    ) {}

    record TreeMetrics(
        int size,
        int height,
        boolean balanced
    ) {}

    static class AVLNode<T> {
        int key;
        int height;

        T value;

        AVLNode<T> left;
        AVLNode<T> right;

        AVLNode(int key, T value) {
            this.key = key;
            this.value = value;
            this.height = 1;
        }
    }

    static class AVLTree<T> {

        private AVLNode<T> root;

        private int size;

        private final Map<RotationType, Integer> rotations =
            new EnumMap<>(RotationType.class);

        private final Map<OperationType, Long> operations =
            new EnumMap<>(OperationType.class);

        AVLTree() {
            for (RotationType type : RotationType.values()) {
                rotations.put(type, 0);
            }

            for (OperationType type : OperationType.values()) {
                operations.put(type, 0L);
            }
        }

        private static int height(AVLNode<?> node) {
            return node == null ? 0 : node.height;
        }

        private int balanceFactor(AVLNode<T> node) {
            if (node == null) return 0;

            return height(node.left) - height(node.right);
        }

        private void updateHeight(AVLNode<T> node) {
            node.height = 1 + Math.max(
                height(node.left),
                height(node.right)
            );
        }

        private void recordRotation(RotationType type) {
            rotations.merge(type, 1, Integer::sum);
        }

        private AVLNode<T> rotateRight(AVLNode<T> y) {
            if (y == null || y.left == null) {
                throw new IllegalStateException(
                    "Invalid right rotation."
                );
            }

            AVLNode<T> x = y.left;
            AVLNode<T> transferred = x.right;

            x.right = y;
            y.left = transferred;

            updateHeight(y);
            updateHeight(x);

            return x;
        }

        private AVLNode<T> rotateLeft(AVLNode<T> x) {
            if (x == null || x.right == null) {
                throw new IllegalStateException(
                    "Invalid left rotation."
                );
            }

            AVLNode<T> y = x.right;
            AVLNode<T> transferred = y.left;

            y.left = x;
            x.right = transferred;

            updateHeight(x);
            updateHeight(y);

            return y;
        }

        private AVLNode<T> rebalance(AVLNode<T> node) {
            if (node == null) return null;

            updateHeight(node);

            int balance = balanceFactor(node);

            if (balance > 1) {
                if (balanceFactor(node.left) < 0) {
                    recordRotation(RotationType.LR);

                    node.left = rotateLeft(node.left);
                } else {
                    recordRotation(RotationType.LL);
                }

                return rotateRight(node);
            }

            if (balance < -1) {
                if (balanceFactor(node.right) > 0) {
                    recordRotation(RotationType.RL);

                    node.right = rotateRight(node.right);
                } else {
                    recordRotation(RotationType.RR);
                }

                return rotateLeft(node);
            }

            return node;
        }

        private AVLNode<T> insertNode(
            AVLNode<T> node,
            int key,
            T value
        ) {
            if (node == null) {
                return new AVLNode<>(key, value);
            }

            if (key < node.key) {
                node.left = insertNode(node.left, key, value);
            } else if (key > node.key) {
                node.right = insertNode(node.right, key, value);
            } else {
                throw new IllegalArgumentException(
                    "Duplicate key: " + key
                );
            }

            return rebalance(node);
        }

        public void insert(int key, T value) {
            if (key <= 0) {
                throw new IllegalArgumentException(
                    "Key must be positive."
                );
            }

            if (value == null) {
                throw new IllegalArgumentException(
                    "Null values are not supported."
                );
            }

            if (findNode(key) != null) {
                throw new IllegalArgumentException(
                    "Duplicate key: " + key
                );
            }

            root = insertNode(root, key, value);

            size++;

            operations.merge(
                OperationType.INSERT,
                1L,
                Long::sum
            );
        }

        private AVLNode<T> findNode(int key) {
            AVLNode<T> current = root;

            while (current != null) {
                if (key == current.key) {
                    return current;
                }

                current = key < current.key
                    ? current.left
                    : current.right;
            }

            return null;
        }

        public SearchResult<T> search(int key) {
            operations.merge(
                OperationType.SEARCH,
                1L,
                Long::sum
            );

            AVLNode<T> node = findNode(key);

            return new SearchResult<>(
                node == null ? null : node.value,
                node != null
            );
        }

        private AVLNode<T> minimumNode(AVLNode<T> node) {
            while (node.left != null) {
                node = node.left;
            }

            return node;
        }

        private AVLNode<T> deleteNode(
            AVLNode<T> node,
            int key
        ) {
            if (node == null) return null;

            if (key < node.key) {
                node.left = deleteNode(node.left, key);
            } else if (key > node.key) {
                node.right = deleteNode(node.right, key);
            } else {
                if (node.left == null) return node.right;
                if (node.right == null) return node.left;

                AVLNode<T> successor = minimumNode(node.right);

                node.key = successor.key;
                node.value = successor.value;

                node.right = deleteNode(
                    node.right,
                    successor.key
                );
            }

            return rebalance(node);
        }

        public boolean delete(int key) {
            if (findNode(key) == null) {
                return false;
            }

            root = deleteNode(root, key);

            size--;

            operations.merge(
                OperationType.DELETE,
                1L,
                Long::sum
            );

            return true;
        }

        private void inorder(
            AVLNode<T> node,
            List<T> result
        ) {
            if (node == null) return;

            inorder(node.left, result);
            result.add(node.value);
            inorder(node.right, result);
        }

        public List<T> inorder() {
            List<T> result = new ArrayList<>(size);

            inorder(root, result);

            return List.copyOf(result);
        }

        private void preorder(
            AVLNode<T> node,
            List<T> result
        ) {
            if (node == null) return;

            result.add(node.value);

            preorder(node.left, result);
            preorder(node.right, result);
        }

        public List<T> preorder() {
            List<T> result = new ArrayList<>(size);

            preorder(root, result);

            return List.copyOf(result);
        }

        public List<List<Integer>> levelOrder() {
            if (root == null) return List.of();

            Deque<AVLNode<T>> queue = new ArrayDeque<>();

            queue.add(root);

            List<List<Integer>> result = new ArrayList<>();

            while (!queue.isEmpty()) {
                int count = queue.size();

                List<Integer> level = new ArrayList<>();

                for (int i = 0; i < count; i++) {
                    AVLNode<T> node = queue.remove();

                    level.add(node.key);

                    if (node.left != null) {
                        queue.add(node.left);
                    }

                    if (node.right != null) {
                        queue.add(node.right);
                    }
                }

                result.add(List.copyOf(level));
            }

            return List.copyOf(result);
        }

        public List<T> rangeQuery(int lower, int upper) {
            if (lower > upper) {
                throw new IllegalArgumentException(
                    "Invalid range."
                );
            }

            List<T> result = new ArrayList<>();

            collectRange(root, lower, upper, result);

            return List.copyOf(result);
        }

        private void collectRange(
            AVLNode<T> node,
            int lower,
            int upper,
            List<T> result
        ) {
            if (node == null) return;

            if (node.key > lower) {
                collectRange(
                    node.left, lower, upper, result
                );
            }

            if (node.key >= lower && node.key <= upper) {
                result.add(node.value);
            }

            if (node.key < upper) {
                collectRange(
                    node.right, lower, upper, result
                );
            }
        }

        private record Validation(
            boolean valid,
            int height
        ) {}

        private Validation validateNode(
            AVLNode<T> node,
            Integer lower,
            Integer upper,
            Set<AVLNode<T>> visited
        ) {
            if (node == null) {
                return new Validation(true, 0);
            }

            if (!visited.add(node)) {
                return new Validation(false, 0);
            }

            if (
                (lower != null && node.key <= lower) ||
                (upper != null && node.key >= upper)
            ) {
                return new Validation(false, 0);
            }

            Validation left = validateNode(
                node.left,
                lower,
                node.key,
                visited
            );

            Validation right = validateNode(
                node.right,
                node.key,
                upper,
                visited
            );

            int expectedHeight = 1 + Math.max(
                left.height(),
                right.height()
            );

            boolean valid = (
                left.valid() &&
                right.valid() &&
                node.height == expectedHeight &&
                Math.abs(
                    left.height() - right.height()
                ) <= 1
            );

            return new Validation(valid, expectedHeight);
        }

        public boolean validate() {
            Set<AVLNode<T>> visited = new HashSet<>();

            Validation result = validateNode(
                root,
                null,
                null,
                visited
            );

            return result.valid() && visited.size() == size;
        }

        public int height() {
            return height(root);
        }

        public int size() {
            return size;
        }

        public OptionalInt minimum() {
            if (root == null) return OptionalInt.empty();

            return OptionalInt.of(
                minimumNode(root).key
            );
        }

        public OptionalInt maximum() {
            if (root == null) return OptionalInt.empty();

            AVLNode<T> current = root;

            while (current.right != null) {
                current = current.right;
            }

            return OptionalInt.of(current.key);
        }

        public TreeMetrics metrics() {
            return new TreeMetrics(
                size,
                height(),
                validate()
            );
        }

        public Map<RotationType, Integer> rotationStatistics() {
            return Collections.unmodifiableMap(
                new EnumMap<>(rotations)
            );
        }

        public Map<OperationType, Long> operationStatistics() {
            return Collections.unmodifiableMap(
                new EnumMap<>(operations)
            );
        }

        public void clear() {
            root = null;
            size = 0;
        }
    }

    /**
     * Enterprise service layer.
     *
     * The AVL structure indexes products by their unique IDs.
     * Business validation remains separate from tree mechanics.
     */
    static class ProductCatalogService {

        private final AVLTree<Product> index = new AVLTree();

        public void register(Product product) {
            if (product == null) {
                throw new IllegalArgumentException(
                    "Product is required."
                );
            }

            index.insert(
                product.productId(),
                product
            );
        }

        public SearchResult<Product> findProduct(int id) {
            return index.search(id);
        }

        public boolean discontinueProduct(int id) {
            return index.delete(id);
        }

        public List<Product> findProducts(
            int minimumId,
            int maximumId
        ) {
            return index.rangeQuery(
                minimumId,
                maximumId
            );
        }

        public List<Product> listAll() {
            return index.inorder();
        }

        public TreeMetrics metrics() {
            return index.metrics();
        }

        public Map<RotationType, Integer> rotations() {
            return index.rotationStatistics();
        }

        public Map<OperationType, Long> operations() {
            return index.operationStatistics();
        }

        public boolean validateIndex() {
            return index.validate();
        }
    }

    private static void demonstrateRotations() {
        System.out.println("\nROTATION TESTS");

        Map<RotationType, List<Integer>> cases =
            new EnumMap<>(RotationType.class);

        cases.put(RotationType.LL, List.of(30, 20, 10));
        cases.put(RotationType.RR, List.of(10, 20, 30));
        cases.put(RotationType.LR, List.of(30, 10, 20));
        cases.put(RotationType.RL, List.of(10, 30, 20));

        for (var entry : cases.entrySet()) {
            AVLTree<String> tree = new AVLTree<>();

            for (int key : entry.getValue()) {
                tree.insert(key, "Product-" + key);
            }

            List<String> ordered = tree.inorder();

            System.out.println(
                entry.getKey() +
                " => " + ordered +
                ", valid=" + tree.validate()
            );

            if (
                !tree.validate() ||
                !tree.preorder().get(0).equals("Product-20")
            ) {
                throw new IllegalStateException(
                    "Rotation test failed: " + entry.getKey()
                );
            }
        }
    }

    private static void runTests() {
        AVLTree<String> tree = new AVLTree<>();

        tree.insert(50, "A");
        tree.insert(30, "B");
        tree.insert(70, "C");
        tree.insert(20, "D");
        tree.insert(40, "E");
        tree.insert(60, "F");
        tree.insert(80, "G");

        if (!tree.validate()) {
            throw new AssertionError("Invalid AVL structure.");
        }

        if (tree.size() != 7) {
            throw new AssertionError("Incorrect size.");
        }

        if (!tree.search(40).found()) {
            throw new AssertionError("Search failed.");
        }

        if (tree.search(999).found()) {
            throw new AssertionError("Unexpected search result.");
        }

        if (!tree.delete(50)) {
            throw new AssertionError("Deletion failed.");
        }

        if (tree.search(50).found()) {
            throw new AssertionError("Deleted key still exists.");
        }

        if (!tree.validate()) {
            throw new AssertionError("Invalid tree after deletion.");
        }

        if (tree.delete(999)) {
            throw new AssertionError("Unexpected deletion.");
        }

        try {
            tree.rangeQuery(100, 10);
            throw new AssertionError("Invalid range accepted.");
        } catch (IllegalArgumentException expected) {
            // Expected.
        }

        AVLTree<String> empty = new AVLTree<>();

        if (
            empty.height() != 0 ||
            empty.size() != 0 ||
            empty.minimum().isPresent()
        ) {
            throw new AssertionError("Empty-tree test failed.");
        }

        System.out.println("\nAll Java 17 AVL tests passed.");
    }

    public static void main(String[] args) {
        try {
            System.out.println(
                "AVL TREE: ENTERPRISE PRODUCT CATALOG"
            );

            demonstrateRotations();

            ProductCatalogService catalog =
                new ProductCatalogService();

            List<Product> products = List.of(
                new Product(1001, "Laptop", "Electronics", 25),
                new Product(501, "Keyboard", "Accessories", 100),
                new Product(1501, "Monitor", "Electronics", 40),
                new Product(251, "Mouse", "Accessories", 150),
                new Product(751, "Router", "Networking", 30),
                new Product(1251, "Printer", "Office", 20),
                new Product(1751, "Scanner", "Office", 15),
                new Product(101, "USB Cable", "Accessories", 500),
                new Product(351, "Webcam", "Electronics", 45),
                new Product(651, "SSD", "Storage", 60)
            );

            System.out.println("\nREGISTERING PRODUCTS");

            for (Product product : products) {
                catalog.register(product);
            }

            System.out.println("\nORDERED CATALOG");

            catalog.listAll().forEach(System.out::println);

            System.out.println("\nSEARCH");

            SearchResult<Product> result =
                catalog.findProduct(751);

            if (result.found()) {
                System.out.println(result.value());
            }

            System.out.println("\nRANGE QUERY");

            catalog.findProducts(350, 1251)
                .forEach(System.out::println);

            System.out.println("\nTREE METRICS");

            System.out.println(catalog.metrics());

            System.out.println("\nROTATION STATISTICS");

            System.out.println(catalog.rotations());

            System.out.println("\nOPERATION STATISTICS");

            System.out.println(catalog.operations());

            System.out.println("\nDISCONTINUING PRODUCT 751");

            catalog.discontinueProduct(751);

            System.out.println(
                "Product found: " +
                catalog.findProduct(751).found()
            );

            System.out.println(
                "Index valid: " +
                catalog.validateIndex()
            );

            runTests();

        } catch (RuntimeException error) {
            System.err.println(
                "Catalog operation failed: " +
                error.getMessage()
            );

            System.exitCode = 1;
        }
    }
}
