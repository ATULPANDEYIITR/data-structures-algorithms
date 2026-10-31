import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.HashMap;
import java.util.HashSet;

public class BinaryTreeEnterpriseModel {

    enum NodeRole {
        ROOT,
        INTERNAL,
        LEAF
    }

    record NodeInfo(
            int value,
            Integer parent,
            List<Integer> children,
            int degree,
            int depth,
            int level,
            NodeRole role
    ) {
        public NodeInfo {
            children = List.copyOf(children);
        }
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

        void setLeft(TreeNode node) {
            left = node;
        }

        void setRight(TreeNode node) {
            right = node;
        }
    }

    static final class InvalidTreeException extends RuntimeException {
        InvalidTreeException(String message) {
            super(message);
        }
    }

    interface TreePolicy {
        boolean accepts(NodeInfo node);
    }

    static final class LeafPolicy implements TreePolicy {
        @Override
        public boolean accepts(NodeInfo node) {
            return node.role() == NodeRole.LEAF && node.degree() == 0;
        }
    }

    static final class BinaryTreeService {
        private final TreeNode root;

        BinaryTreeService(TreeNode root) {
            this.root = root;
            validateStructure();
        }

        private void validateStructure() {
            if (root == null) {
                return;
            }

            Set<TreeNode> visited =
                    Collections.newSetFromMap(new java.util.IdentityHashMap<>());

            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.add(root);

            while (!queue.isEmpty()) {
                TreeNode node = queue.remove();

                if (!visited.add(node)) {
                    throw new InvalidTreeException(
                            "Tree contains a cycle or shared node."
                    );
                }

                if (node.left() != null) {
                    queue.add(node.left());
                }

                if (node.right() != null) {
                    queue.add(node.right());
                }
            }
        }

        int height() {
            if (root == null) {
                return -1;
            }

            record DepthNode(TreeNode node, int depth) {}

            Deque<DepthNode> queue = new ArrayDeque<>();
            queue.add(new DepthNode(root, 0));

            int height = 0;

            while (!queue.isEmpty()) {
                DepthNode current = queue.remove();
                height = Math.max(height, current.depth());

                if (current.node().left() != null) {
                    queue.add(
                            new DepthNode(
                                    current.node().left(),
                                    current.depth() + 1
                            )
                    );
                }

                if (current.node().right() != null) {
                    queue.add(
                            new DepthNode(
                                    current.node().right(),
                                    current.depth() + 1
                            )
                    );
                }
            }

            return height;
        }

        Optional<NodeInfo> inspect(int target) {
            if (root == null) {
                return Optional.empty();
            }

            record SearchNode(
                    TreeNode node,
                    TreeNode parent,
                    int depth
            ) {}

            Deque<SearchNode> queue = new ArrayDeque<>();
            queue.add(new SearchNode(root, null, 0));

            while (!queue.isEmpty()) {
                SearchNode current = queue.remove();
                TreeNode node = current.node();

                if (node.value() == target) {
                    List<Integer> children = new ArrayList<>();

                    if (node.left() != null) {
                        children.add(node.left().value());
                    }

                    if (node.right() != null) {
                        children.add(node.right().value());
                    }

                    int degree = children.size();

                    NodeRole role;
                    if (current.parent() == null) {
                        role = NodeRole.ROOT;
                    } else if (degree == 0) {
                        role = NodeRole.LEAF;
                    } else {
                        role = NodeRole.INTERNAL;
                    }

                    return Optional.of(
                            new NodeInfo(
                                    node.value(),
                                    current.parent() == null
                                            ? null
                                            : current.parent().value(),
                                    children,
                                    degree,
                                    current.depth(),
                                    current.depth() + 1,
                                    role
                            )
                    );
                }

                if (node.left() != null) {
                    queue.add(
                            new SearchNode(
                                    node.left(),
                                    node,
                                    current.depth() + 1
                            )
                    );
                }

                if (node.right() != null) {
                    queue.add(
                            new SearchNode(
                                    node.right(),
                                    node,
                                    current.depth() + 1
                            )
                    );
                }
            }

            return Optional.empty();
        }

        List<Integer> levelOrder() {
            if (root == null) {
                return List.of();
            }

            List<Integer> result = new ArrayList<>();
            Deque<TreeNode> queue = new ArrayDeque<>();
            queue.add(root);

            while (!queue.isEmpty()) {
                TreeNode node = queue.remove();
                result.add(node.value());

                if (node.left() != null) {
                    queue.add(node.left());
                }

                if (node.right() != null) {
                    queue.add(node.right());
                }
            }

            return List.copyOf(result);
        }

        List<NodeInfo> leaves() {
            List<NodeInfo> result = new ArrayList<>();
            TreePolicy policy = new LeafPolicy();

            for (int value : levelOrder()) {
                Optional<NodeInfo> info = inspect(value);

                if (info.isPresent() && policy.accepts(info.get())) {
                    result.add(info.get());
                }
            }

            return List.copyOf(result);
        }
    }

    private static TreeNode buildTree() {
        TreeNode root = new TreeNode(80);

        TreeNode left = new TreeNode(40);
        TreeNode right = new TreeNode(120);

        left.setLeft(new TreeNode(20));
        left.setRight(new TreeNode(60));

        right.setLeft(new TreeNode(100));
        right.setRight(new TreeNode(140));

        right.right().setLeft(new TreeNode(130));

        root.setLeft(left);
        root.setRight(right);

        return root;
    }

    private static void printNode(NodeInfo info) {
        System.out.println("Node " + info.value());
        System.out.println("  Parent: " + info.parent());
        System.out.println("  Children: " + info.children());
        System.out.println("  Degree: " + info.degree());
        System.out.println("  Depth: " + info.depth());
        System.out.println("  Level: " + info.level());
        System.out.println("  Role: " + info.role());
    }

    public static void main(String[] args) {
        BinaryTreeService service =
                new BinaryTreeService(buildTree());

        System.out.println("Enterprise Binary Tree Model");
        System.out.println("============================");
        System.out.println("Height: " + service.height());
        System.out.println("Level-order: " + service.levelOrder());

        Optional<NodeInfo> selected = service.inspect(130);

        if (selected.isEmpty()) {
            throw new IllegalStateException("Expected node 130.");
        }

        printNode(selected.get());

        if (selected.get().depth() != 3) {
            throw new IllegalStateException("Incorrect depth.");
        }

        if (!selected.get().role().equals(NodeRole.LEAF)) {
            throw new IllegalStateException("Node 130 must be a leaf.");
        }

        List<NodeInfo> leaves = service.leaves();

        System.out.println("\nLeaf nodes:");
        leaves.stream()
                .map(NodeInfo::value)
                .sorted()
                .forEach(value -> System.out.println("  " + value));

        if (service.inspect(999).isPresent()) {
            throw new IllegalStateException("Unknown node was found.");
        }

        BinaryTreeService empty = new BinaryTreeService(null);

        if (empty.height() != -1 || !empty.levelOrder().isEmpty()) {
            throw new IllegalStateException("Empty tree handling failed.");
        }

        System.out.println("\nValidation completed successfully.");
        System.out.println("Tree operations use O(n) traversal in the worst case.");
    }
}
