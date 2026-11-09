import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Random;
import java.util.TreeSet;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/*
 * Red-Black Tree: Enterprise Asset Registry
 *
 * Java 17 implementation featuring:
 * - Generic ordered tree
 * - Explicit domain records
 * - Insertion and deletion balancing
 * - Read/write locking
 * - Immutable operation results
 * - Registry service layer
 * - Validation and audit events
 * - Randomized verification
 */

public class RedBlackTreeEnterprise {

    enum Color {
        RED,
        BLACK
    }

    enum Operation {
        INSERT,
        DELETE
    }

    record AuditEvent(
        Operation operation,
        int assetId,
        boolean changed,
        long timestamp
    ) {}

    record TreeStatistics(
        int size,
        int height,
        int redNodes,
        int blackNodes
    ) {}

    static class TreeValidationException extends RuntimeException {
        TreeValidationException(String message) {
            super(message);
        }
    }

    static class Node<K> {
        K key;
        Color color;
        Node<K> left;
        Node<K> right;
        Node<K> parent;

        Node(K key, Color color) {
            this.key = key;
            this.color = color;
        }
    }

    static class RedBlackTree<K extends Comparable<? super K>> {

        private final Node<K> nil;
        private Node<K> root;
        private int size;

        RedBlackTree() {
            nil = new Node<>(null, Color.BLACK);
            nil.left = nil;
            nil.right = nil;
            nil.parent = nil;
            root = nil;
        }

        int size() {
            return size;
        }

        private void validateKey(K key) {
            if (key == null) {
                throw new IllegalArgumentException(
                    "Null keys are not supported"
                );
            }
        }

        Optional<K> search(K key) {
            validateKey(key);

            Node<K> current = root;

            while (current != nil) {
                int comparison = key.compareTo(current.key);

                if (comparison == 0) {
                    return Optional.of(current.key);
                }

                current = comparison < 0
                    ? current.left
                    : current.right;
            }

            return Optional.empty();
        }

        private void leftRotate(Node<K> x) {
            Node<K> y = x.right;

            if (y == nil) {
                throw new IllegalStateException(
                    "Invalid left rotation"
                );
            }

            x.right = y.left;

            if (y.left != nil) {
                y.left.parent = x;
            }

            y.parent = x.parent;

            if (x.parent == nil) {
                root = y;
            } else if (x == x.parent.left) {
                x.parent.left = y;
            } else {
                x.parent.right = y;
            }

            y.left = x;
            x.parent = y;
        }

        private void rightRotate(Node<K> y) {
            Node<K> x = y.left;

            if (x == nil) {
                throw new IllegalStateException(
                    "Invalid right rotation"
                );
            }

            y.left = x.right;

            if (x.right != nil) {
                x.right.parent = y;
            }

            x.parent = y.parent;

            if (y.parent == nil) {
                root = x;
            } else if (y == y.parent.right) {
                y.parent.right = x;
            } else {
                y.parent.left = x;
            }

            x.right = y;
            y.parent = x;
        }

        boolean insert(K key) {
            validateKey(key);

            Node<K> parent = nil;
            Node<K> current = root;

            while (current != nil) {
                parent = current;

                int comparison = key.compareTo(current.key);

                if (comparison == 0) {
                    return false;
                }

                current = comparison < 0
                    ? current.left
                    : current.right;
            }

            Node<K> node = new Node<>(key, Color.RED);
            node.left = nil;
            node.right = nil;
            node.parent = parent;

            if (parent == nil) {
                root = node;
            } else if (key.compareTo(parent.key) < 0) {
                parent.left = node;
            } else {
                parent.right = node;
            }

            size++;
            insertFixup(node);

            return true;
        }

        private void insertFixup(Node<K> z) {
            while (z.parent.color == Color.RED) {
                if (z.parent == z.parent.parent.left) {
                    Node<K> uncle = z.parent.parent.right;

                    if (uncle.color == Color.RED) {
                        z.parent.color = Color.BLACK;
                        uncle.color = Color.BLACK;
                        z.parent.parent.color = Color.RED;
                        z = z.parent.parent;
                    } else {
                        if (z == z.parent.right) {
                            z = z.parent;
                            leftRotate(z);
                        }

                        z.parent.color = Color.BLACK;
                        z.parent.parent.color = Color.RED;
                        rightRotate(z.parent.parent);
                    }
                } else {
                    Node<K> uncle = z.parent.parent.left;

                    if (uncle.color == Color.RED) {
                        z.parent.color = Color.BLACK;
                        uncle.color = Color.BLACK;
                        z.parent.parent.color = Color.RED;
                        z = z.parent.parent;
                    } else {
                        if (z == z.parent.left) {
                            z = z.parent;
                            rightRotate(z);
                        }

                        z.parent.color = Color.BLACK;
                        z.parent.parent.color = Color.RED;
                        leftRotate(z.parent.parent);
                    }
                }
            }

            root.color = Color.BLACK;
            root.parent = nil;
        }

        private Node<K> minimumNode(Node<K> node) {
            while (node.left != nil) {
                node = node.left;
            }
            return node;
        }

        private void transplant(Node<K> u, Node<K> v) {
            if (u.parent == nil) {
                root = v;
            } else if (u == u.parent.left) {
                u.parent.left = v;
            } else {
                u.parent.right = v;
            }

            v.parent = u.parent;
        }

        boolean delete(K key) {
            validateKey(key);

            Node<K> z = root;

            while (z != nil) {
                int comparison = key.compareTo(z.key);

                if (comparison == 0) {
                    break;
                }

                z = comparison < 0 ? z.left : z.right;
            }

            if (z == nil) {
                return false;
            }

            Node<K> y = z;
            Node<K> x;
            Color originalColor = y.color;

            if (z.left == nil) {
                x = z.right;
                transplant(z, z.right);
            } else if (z.right == nil) {
                x = z.left;
                transplant(z, z.left);
            } else {
                y = minimumNode(z.right);
                originalColor = y.color;
                x = y.right;

                if (y.parent == z) {
                    x.parent = y;
                } else {
                    transplant(y, y.right);
                    y.right = z.right;
                    y.right.parent = y;
                }

                transplant(z, y);
                y.left = z.left;
                y.left.parent = y;
                y.color = z.color;
            }

            size--;

            if (originalColor == Color.BLACK) {
                deleteFixup(x);
            }

            nil.color = Color.BLACK;

            if (root != nil) {
                root.parent = nil;
            }

            return true;
        }

        private void deleteFixup(Node<K> x) {
            while (x != root && x.color == Color.BLACK) {
                if (x == x.parent.left) {
                    Node<K> sibling = x.parent.right;

                    if (sibling.color == Color.RED) {
                        sibling.color = Color.BLACK;
                        x.parent.color = Color.RED;
                        leftRotate(x.parent);
                        sibling = x.parent.right;
                    }

                    if (
                        sibling.left.color == Color.BLACK &&
                        sibling.right.color == Color.BLACK
                    ) {
                        sibling.color = Color.RED;
                        x = x.parent;
                    } else {
                        if (sibling.right.color == Color.BLACK) {
                            sibling.left.color = Color.BLACK;
                            sibling.color = Color.RED;
                            rightRotate(sibling);
                            sibling = x.parent.right;
                        }

                        sibling.color = x.parent.color;
                        x.parent.color = Color.BLACK;
                        sibling.right.color = Color.BLACK;
                        leftRotate(x.parent);
                        x = root;
                    }
                } else {
                    Node<K> sibling = x.parent.left;

                    if (sibling.color == Color.RED) {
                        sibling.color = Color.BLACK;
                        x.parent.color = Color.RED;
                        rightRotate(x.parent);
                        sibling = x.parent.left;
                    }

                    if (
                        sibling.right.color == Color.BLACK &&
                        sibling.left.color == Color.BLACK
                    ) {
                        sibling.color = Color.RED;
                        x = x.parent;
                    } else {
                        if (sibling.left.color == Color.BLACK) {
                            sibling.right.color = Color.BLACK;
                            sibling.color = Color.RED;
                            leftRotate(sibling);
                            sibling = x.parent.left;
                        }

                        sibling.color = x.parent.color;
                        x.parent.color = Color.BLACK;
                        sibling.left.color = Color.BLACK;
                        rightRotate(x.parent);
                        x = root;
                    }
                }
            }

            x.color = Color.BLACK;
        }

        List<K> inorder() {
            List<K> result = new ArrayList<>();
            inorder(root, result);
            return Collections.unmodifiableList(result);
        }

        private void inorder(Node<K> node, List<K> result) {
            if (node == nil) {
                return;
            }

            inorder(node.left, result);
            result.add(node.key);
            inorder(node.right, result);
        }

        List<K> rangeQuery(K low, K high) {
            validateKey(low);
            validateKey(high);

            if (low.compareTo(high) > 0) {
                throw new IllegalArgumentException(
                    "Invalid range boundaries"
                );
            }

            List<K> result = new ArrayList<>();
            collectRange(root, low, high, result);

            return Collections.unmodifiableList(result);
        }

        private void collectRange(
            Node<K> node,
            K low,
            K high,
            List<K> result
        ) {
            if (node == nil) {
                return;
            }

            if (node.key.compareTo(low) > 0) {
                collectRange(node.left, low, high, result);
            }

            if (
                node.key.compareTo(low) >= 0 &&
                node.key.compareTo(high) <= 0
            ) {
                result.add(node.key);
            }

            if (node.key.compareTo(high) < 0) {
                collectRange(node.right, low, high, result);
            }
        }

        int height() {
            return height(root);
        }

        private int height(Node<K> node) {
            if (node == nil) {
                return 0;
            }

            return 1 + Math.max(
                height(node.left),
                height(node.right)
            );
        }

        TreeStatistics statistics() {
            int[] counts = new int[2];
            int height = countColors(root, counts);

            return new TreeStatistics(
                size,
                height,
                counts[0],
                counts[1]
            );
        }

        private int countColors(Node<K> node, int[] counts) {
            if (node == nil) {
                return 0;
            }

            if (node.color == Color.RED) {
                counts[0]++;
            } else {
                counts[1]++;
            }

            return 1 + Math.max(
                countColors(node.left, counts),
                countColors(node.right, counts)
            );
        }

        void validate() {
            if (nil.color != Color.BLACK) {
                throw new TreeValidationException(
                    "Sentinel must be black"
                );
            }

            if (root == nil) {
                if (size != 0) {
                    throw new TreeValidationException(
                        "Invalid empty-tree size"
                    );
                }
                return;
            }

            if (root.color != Color.BLACK) {
                throw new TreeValidationException(
                    "Root must be black"
                );
            }

            if (root.parent != nil) {
                throw new TreeValidationException(
                    "Invalid root parent"
                );
            }

            int[] count = {0};

            inspect(root, null, null, nil, count);

            if (count[0] != size) {
                throw new TreeValidationException(
                    "Node count mismatch"
                );
            }
        }

        private int inspect(
            Node<K> node,
            K lower,
            K upper,
            Node<K> parent,
            int[] count
        ) {
            if (node == nil) {
                return 1;
            }

            count[0]++;

            if (node.parent != parent) {
                throw new TreeValidationException(
                    "Parent pointer violation"
                );
            }

            if (
                lower != null &&
                node.key.compareTo(lower) <= 0
            ) {
                throw new TreeValidationException(
                    "BST lower-bound violation"
                );
            }

            if (
                upper != null &&
                node.key.compareTo(upper) >= 0
            ) {
                throw new TreeValidationException(
                    "BST upper-bound violation"
                );
            }

            if (node.color == Color.RED) {
                if (
                    node.left.color == Color.RED ||
                    node.right.color == Color.RED
                ) {
                    throw new TreeValidationException(
                        "Adjacent red nodes"
                    );
                }
            }

            int leftHeight = inspect(
                node.left, lower, node.key, node, count
            );

            int rightHeight = inspect(
                node.right, node.key, upper, node, count
            );

            if (leftHeight != rightHeight) {
                throw new TreeValidationException(
                    "Black-height violation"
                );
            }

            return leftHeight +
                (node.color == Color.BLACK ? 1 : 0);
        }
    }

    /*
     * Service layer:
     * The read/write lock protects tree mutations and queries.
     * Audit events are recorded only after successful state changes.
     */
    static class AssetRegistry {

        private final RedBlackTree<Integer> tree =
            new RedBlackTree<>();

        private final ReentrantReadWriteLock lock =
            new ReentrantReadWriteLock();

        private final List<AuditEvent> audit =
            new ArrayList<>();

        boolean registerAsset(int assetId) {
            lock.writeLock().lock();

            try {
                boolean changed = tree.insert(assetId);

                if (changed) {
                    audit.add(new AuditEvent(
                        Operation.INSERT,
                        assetId,
                        true,
                        System.currentTimeMillis()
                    ));
                }

                return changed;
            } finally {
                lock.writeLock().unlock();
            }
        }

        boolean retireAsset(int assetId) {
            lock.writeLock().lock();

            try {
                boolean changed = tree.delete(assetId);

                if (changed) {
                    audit.add(new AuditEvent(
                        Operation.DELETE,
                        assetId,
                        true,
                        System.currentTimeMillis()
                    ));
                }

                return changed;
            } finally {
                lock.writeLock().unlock();
            }
        }

        Optional<Integer> findAsset(int assetId) {
            lock.readLock().lock();

            try {
                return tree.search(assetId);
            } finally {
                lock.readLock().unlock();
            }
        }

        List<Integer> listAssets() {
            lock.readLock().lock();

            try {
                return tree.inorder();
            } finally {
                lock.readLock().unlock();
            }
        }

        List<Integer> findAssetsInRange(int low, int high) {
            lock.readLock().lock();

            try {
                return tree.rangeQuery(low, high);
            } finally {
                lock.readLock().unlock();
            }
        }

        TreeStatistics statistics() {
            lock.readLock().lock();

            try {
                return tree.statistics();
            } finally {
                lock.readLock().unlock();
            }
        }

        List<AuditEvent> auditTrail() {
            lock.readLock().lock();

            try {
                return List.copyOf(audit);
            } finally {
                lock.readLock().unlock();
            }
        }

        void validate() {
            lock.readLock().lock();

            try {
                tree.validate();
            } finally {
                lock.readLock().unlock();
            }
        }
    }

    public static void main(String[] args) {

        AssetRegistry registry = new AssetRegistry();

        int[] assetIds = {
            100, 50, 150, 25, 75, 125, 175,
            10, 35, 60, 90, 110, 140, 160, 190
        };

        System.out.println("ENTERPRISE ASSET REGISTRY");

        for (int id : assetIds) {
            registry.registerAsset(id);
        }

        registry.validate();

        System.out.println(
            "Registered assets: " + registry.listAssets()
        );

        System.out.println(
            "Asset 75: " + registry.findAsset(75)
        );

        System.out.println(
            "Asset 999: " + registry.findAsset(999)
        );

        System.out.println(
            "Range 50-140: " +
            registry.findAssetsInRange(50, 140)
        );

        System.out.println(
            "Statistics: " + registry.statistics()
        );

        System.out.println("\nRETIREMENT");

        for (int id : new int[]{25, 100, 150, 999}) {
            System.out.println(
                "Retire " + id + ": " +
                registry.retireAsset(id)
            );

            registry.validate();
        }

        System.out.println(
            "Remaining assets: " + registry.listAssets()
        );

        System.out.println(
            "Audit events: " + registry.auditTrail().size()
        );

        // Cross-check against the standard ordered-set implementation.
        System.out.println("\nRANDOMIZED VERIFICATION");

        RedBlackTree<Integer> tested = new RedBlackTree<>();
        TreeSet<Integer> reference = new TreeSet<>();
        Random random = new Random(42);

        for (int i = 0; i < 3000; i++) {
            int value = random.nextInt(1001) - 500;

            if (random.nextBoolean()) {
                boolean expected = reference.add(value);
                boolean actual = tested.insert(value);

                if (expected != actual) {
                    throw new AssertionError("Insertion mismatch");
                }
            } else {
                boolean expected = reference.remove(value);
                boolean actual = tested.delete(value);

                if (expected != actual) {
                    throw new AssertionError("Deletion mismatch");
                }
            }

            tested.validate();

            if (!tested.inorder().equals(
                new ArrayList<>(reference)
            )) {
                throw new AssertionError("Ordering mismatch");
            }
        }

        System.out.println("All randomized tests passed.");
        System.out.println(tested.statistics());
    }
}
