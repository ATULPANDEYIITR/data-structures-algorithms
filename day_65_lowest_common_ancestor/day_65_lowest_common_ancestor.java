import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.OptionalInt;
import java.util.Set;

public class Main {

    enum NodeState {
        ACTIVE,
        REGISTERED
    }

    record LcaQuery(int first, int second) {
        LcaQuery {
            if (first < 0 || second < 0) {
                throw new IllegalArgumentException(
                    "Node identifiers must be non-negative."
                );
            }
        }
    }

    record QueryResult(
        LcaQuery query,
        int ancestor,
        int distance,
        boolean cached
    ) {}

    static final class TreeNode {
        private final int id;
        private TreeNode left;
        private TreeNode right;
        private TreeNode parent;

        private TreeNode(int id) {
            this.id = id;
        }

        int id() {
            return id;
        }

        TreeNode parent() {
            return parent;
        }
    }

    static final class TreeValidationException
            extends RuntimeException {

        TreeValidationException(String message) {
            super(message);
        }
    }

    static final class BinaryTree {
        private TreeNode root;

        private final Map<Integer, TreeNode> nodes =
            new HashMap<>();

        private NodeState state = NodeState.ACTIVE;

        BinaryTree(int rootId) {
            root = new TreeNode(rootId);
            nodes.put(rootId, root);
        }

        void addChild(int parentId, int childId, boolean leftSide) {
            ensureActive();

            if (nodes.containsKey(childId)) {
                throw new TreeValidationException(
                    "Duplicate node identifier."
                );
            }

            TreeNode parent = getNode(parentId);

            if (leftSide && parent.left != null) {
                throw new TreeValidationException(
                    "Left child already exists."
                );
            }

            if (!leftSide && parent.right != null) {
                throw new TreeValidationException(
                    "Right child already exists."
                );
            }

            TreeNode child = new TreeNode(childId);
            child.parent = parent;

            if (leftSide) {
                parent.left = child;
            } else {
                parent.right = child;
            }

            nodes.put(childId, child);
        }

        TreeNode getNode(int id) {
            TreeNode node = nodes.get(id);

            if (node == null) {
                throw new TreeValidationException(
                    "Unknown node identifier: " + id
                );
            }

            return node;
        }

        TreeNode root() {
            return root;
        }

        int size() {
            return nodes.size();
        }

        void freeze() {
            state = NodeState.REGISTERED;
        }

        void ensureActive() {
            if (state != NodeState.ACTIVE) {
                throw new IllegalStateException(
                    "Tree structure is frozen."
                );
            }
        }

        int recursiveLCA(int firstId, int secondId) {
            TreeNode first = getNode(firstId);
            TreeNode second = getNode(secondId);

            return recursiveSearch(root, first, second).id();
        }

        private TreeNode recursiveSearch(
                TreeNode node,
                TreeNode first,
                TreeNode second) {

            if (node == null || node == first || node == second) {
                return node;
            }

            TreeNode left = recursiveSearch(
                node.left, first, second
            );

            TreeNode right = recursiveSearch(
                node.right, first, second
            );

            if (left != null && right != null) {
                return node;
            }

            return left != null ? left : right;
        }

        int parentLCA(int firstId, int secondId) {
            TreeNode first = getNode(firstId);
            TreeNode second = getNode(secondId);

            Set<Integer> ancestors = new HashSet<>();

            while (first != null) {
                ancestors.add(first.id);
                first = first.parent;
            }

            while (second != null) {
                if (ancestors.contains(second.id)) {
                    return second.id;
                }

                second = second.parent;
            }

            throw new IllegalStateException(
                "No common ancestor exists."
            );
        }

        int depth(int id) {
            TreeNode node = getNode(id);
            int depth = 0;

            while (node.parent != null) {
                depth++;
                node = node.parent;
            }

            return depth;
        }

        int depthLCA(int firstId, int secondId) {
            TreeNode first = getNode(firstId);
            TreeNode second = getNode(secondId);

            int firstDepth = depth(firstId);
            int secondDepth = depth(secondId);

            while (firstDepth > secondDepth) {
                first = first.parent;
                firstDepth--;
            }

            while (secondDepth > firstDepth) {
                second = second.parent;
                secondDepth--;
            }

            while (first != second) {
                first = first.parent;
                second = second.parent;
            }

            return first.id;
        }

        boolean isAncestor(int ancestorId, int descendantId) {
            TreeNode target = getNode(ancestorId);
            TreeNode current = getNode(descendantId);

            while (current != null) {
                if (current == target) {
                    return true;
                }

                current = current.parent;
            }

            return false;
        }

        int distance(int firstId, int secondId) {
            int ancestorId = parentLCA(firstId, secondId);
            TreeNode ancestor = getNode(ancestorId);

            return distanceTo(getNode(firstId), ancestor)
                + distanceTo(getNode(secondId), ancestor);
        }

        private int distanceTo(TreeNode node, TreeNode ancestor) {
            int result = 0;

            while (node != ancestor) {
                node = node.parent;
                result++;
            }

            return result;
        }

        OptionalInt kthAncestor(int id, int k) {
            if (k < 0) {
                throw new IllegalArgumentException(
                    "k cannot be negative."
                );
            }

            TreeNode current = getNode(id);

            for (int i = 0; i < k; i++) {
                if (current == null) {
                    return OptionalInt.empty();
                }

                current = current.parent;
            }

            return current == null
                ? OptionalInt.empty()
                : OptionalInt.of(current.id);
        }
    }

    static final class AncestorIndex {
        private final BinaryTree tree;
        private final int levels;

        private final Map<Integer, Integer> depth =
            new HashMap<>();

        private final Map<Integer, int[]> up =
            new HashMap<>();

        AncestorIndex(BinaryTree tree) {
            this.tree = Objects.requireNonNull(tree);

            if (tree.size() == 0) {
                throw new IllegalArgumentException(
                    "Cannot index an empty tree."
                );
            }

            levels = Math.max(
                1,
                32 - Integer.numberOfLeadingZeros(tree.size())
            );

            record Entry(TreeNode node, int parent) {}

            ArrayDeque<Entry> queue = new ArrayDeque<>();
            queue.add(new Entry(tree.root(), -1));

            while (!queue.isEmpty()) {
                Entry entry = queue.remove();

                TreeNode node = entry.node();
                int parent = entry.parent();

                int currentDepth =
                    parent == -1 ? 0 : depth.get(parent) + 1;

                depth.put(node.id, currentDepth);

                int[] ancestors = new int[levels];
                ancestors[0] = parent;

                java.util.Arrays.fill(
                    ancestors, 1, levels, -1
                );

                up.put(node.id, ancestors);

                if (node.left != null) {
                    queue.add(
                        new Entry(node.left, node.id)
                    );
                }

                if (node.right != null) {
                    queue.add(
                        new Entry(node.right, node.id)
                    );
                }
            }

            for (int j = 1; j < levels; j++) {
                for (int id : up.keySet()) {
                    int previous = up.get(id)[j - 1];

                    if (previous != -1) {
                        up.get(id)[j] = up.get(previous)[j - 1];
                    }
                }
            }
        }

        int kthAncestor(int id, int k) {
            if (!up.containsKey(id)) {
                throw new TreeValidationException(
                    "Unknown node."
                );
            }

            if (k < 0) {
                throw new IllegalArgumentException(
                    "k cannot be negative."
                );
            }

            if (k > depth.get(id)) {
                return -1;
            }

            int current = id;
            int bit = 0;

            while (k > 0) {
                if ((k & 1) != 0) {
                    current = up.get(current)[bit];

                    if (current == -1) {
                        return -1;
                    }
                }

                k >>>= 1;
                bit++;
            }

            return current;
        }

        int lca(int first, int second) {
            if (!up.containsKey(first)
                    || !up.containsKey(second)) {
                throw new TreeValidationException(
                    "Both nodes must exist."
                );
            }

            if (depth.get(first) < depth.get(second)) {
                int temporary = first;
                first = second;
                second = temporary;
            }

            first = kthAncestor(
                first,
                depth.get(first) - depth.get(second)
            );

            if (first == second) {
                return first;
            }

            for (int j = levels - 1; j >= 0; j--) {
                int a = up.get(first)[j];
                int b = up.get(second)[j];

                if (a != b) {
                    first = a;
                    second = b;
                }
            }

            return up.get(first)[0];
        }

        int distance(int first, int second) {
            int ancestor = lca(first, second);

            return depth.get(first)
                + depth.get(second)
                - 2 * depth.get(ancestor);
        }

        List<Integer> batchLCA(List<LcaQuery> queries) {
            Objects.requireNonNull(queries);

            List<Integer> results = new ArrayList<>();

            for (LcaQuery query : queries) {
                results.add(lca(
                    query.first(),
                    query.second()
                ));
            }

            return Collections.unmodifiableList(results);
        }
    }

    interface QueryPolicy {
        boolean allow(int first, int second);
    }

    static final class SameTreePolicy implements QueryPolicy {
        @Override
        public boolean allow(int first, int second) {
            return first >= 0 && second >= 0;
        }
    }

    static final class LcaQueryService {
        private final AncestorIndex index;
        private final QueryPolicy policy;

        private final Map<LcaQuery, Integer> cache =
            new HashMap<>();

        LcaQueryService(
                AncestorIndex index,
                QueryPolicy policy) {
            this.index = Objects.requireNonNull(index);
            this.policy = Objects.requireNonNull(policy);
        }

        QueryResult execute(LcaQuery query) {
            if (!policy.allow(
                    query.first(), query.second())) {
                throw new SecurityException(
                    "Query rejected by policy."
                );
            }

            LcaQuery key = query.first() <= query.second()
                ? query
                : new LcaQuery(
                    query.second(), query.first()
                );

            boolean cached = cache.containsKey(key);

            int ancestor;

            if (cached) {
                ancestor = cache.get(key);
            } else {
                ancestor = index.lca(
                    query.first(), query.second()
                );
                cache.put(key, ancestor);
            }

            return new QueryResult(
                query,
                ancestor,
                index.distance(
                    query.first(), query.second()
                ),
                cached
            );
        }
    }

    static BinaryTree createSampleTree() {
        BinaryTree tree = new BinaryTree(1);

        tree.addChild(1, 2, true);
        tree.addChild(1, 3, false);

        tree.addChild(2, 4, true);
        tree.addChild(2, 5, false);

        tree.addChild(3, 6, true);
        tree.addChild(3, 7, false);

        tree.addChild(4, 8, true);
        tree.addChild(4, 9, false);

        tree.addChild(5, 10, true);

        tree.freeze();

        return tree;
    }

    static void runTests() {
        BinaryTree tree = createSampleTree();
        AncestorIndex index = new AncestorIndex(tree);

        assert tree.recursiveLCA(8, 9) == 4;
        assert tree.recursiveLCA(8, 10) == 2;
        assert tree.recursiveLCA(8, 6) == 1;
        assert tree.recursiveLCA(5, 10) == 5;

        assert tree.parentLCA(8, 10) == 2;
        assert tree.depthLCA(8, 6) == 1;

        assert index.lca(8, 10) == 2;
        assert index.lca(8, 6) == 1;

        assert index.kthAncestor(8, 3) == 1;
        assert index.kthAncestor(8, 4) == -1;

        assert index.distance(8, 10) == 4;
        assert tree.distance(8, 6) == 5;

        assert tree.isAncestor(2, 8);
        assert !tree.isAncestor(3, 8);

        LcaQueryService service = new LcaQueryService(
            index, new SameTreePolicy()
        );

        assert !service.execute(
            new LcaQuery(8, 10)
        ).cached();

        assert service.execute(
            new LcaQuery(10, 8)
        ).cached();

        boolean rejected = false;

        try {
            index.lca(8, 999);
        } catch (TreeValidationException exception) {
            rejected = true;
        }

        assert rejected;

        System.out.println("All Java 17 LCA tests passed.");
    }

    public static void main(String[] args) {
        try {
            BinaryTree tree = createSampleTree();
            AncestorIndex index = new AncestorIndex(tree);

            LcaQueryService service = new LcaQueryService(
                index,
                new SameTreePolicy()
            );

            List<LcaQuery> queries = List.of(
                new LcaQuery(8, 9),
                new LcaQuery(8, 10),
                new LcaQuery(8, 6),
                new LcaQuery(5, 10),
                new LcaQuery(2, 8)
            );

            System.out.println("LOWEST COMMON ANCESTOR\n");

            for (LcaQuery query : queries) {
                QueryResult result = service.execute(query);

                System.out.printf(
                    "Nodes %d, %d | LCA: %d | Distance: %d | Cached: %b%n",
                    query.first(),
                    query.second(),
                    result.ancestor(),
                    result.distance(),
                    result.cached()
                );
            }

            System.out.println(
                "\nRecursive LCA of 8 and 10: "
                    + tree.recursiveLCA(8, 10)
            );

            System.out.println(
                "Parent-pointer LCA of 8 and 10: "
                    + tree.parentLCA(8, 10)
            );

            System.out.println(
                "3rd ancestor of 8: "
                    + index.kthAncestor(8, 3)
            );

            System.out.println(
                "Batch LCA results: "
                    + index.batchLCA(queries)
            );

            runTests();

        } catch (RuntimeException exception) {
            System.err.println(
                "Execution failed: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
