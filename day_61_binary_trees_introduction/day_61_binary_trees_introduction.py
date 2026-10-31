from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from typing import Optional, Iterable


@dataclass
class TreeNode:
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


class BinaryTree:
    def __init__(self, root: Optional[TreeNode] = None) -> None:
        self.root = root

    def is_empty(self) -> bool:
        return self.root is None

    def height(self) -> int:
        """Height measured in edges. Empty tree has height -1."""
        def visit(node: Optional[TreeNode]) -> int:
            if node is None:
                return -1
            return 1 + max(visit(node.left), visit(node.right))

        return visit(self.root)

    def node_depth(self, target: int) -> int:
        """Return the depth of the first matching value, or -1 if absent."""
        if self.root is None:
            return -1

        queue = deque([(self.root, 0)])
        while queue:
            node, depth = queue.popleft()
            if node.value == target:
                return depth

            if node.left is not None:
                queue.append((node.left, depth + 1))
            if node.right is not None:
                queue.append((node.right, depth + 1))

        return -1

    def level(self, target: int) -> int:
        """Level is depth + 1, with the root at level 1."""
        depth = self.node_depth(target)
        return -1 if depth == -1 else depth + 1

    def parent_of(self, target: int) -> Optional[int]:
        if self.root is None or self.root.value == target:
            return None

        queue = deque([self.root])
        while queue:
            node = queue.popleft()

            for child in (node.left, node.right):
                if child is not None:
                    if child.value == target:
                        return node.value
                    queue.append(child)

        return None

    def children_of(self, target: int) -> Optional[list[int]]:
        node = self.find(target)
        if node is None:
            return None

        return [
            child.value
            for child in (node.left, node.right)
            if child is not None
        ]

    def degree(self, target: int) -> int:
        node = self.find(target)
        if node is None:
            return -1

        return int(node.left is not None) + int(node.right is not None)

    def find(self, target: int) -> Optional[TreeNode]:
        if self.root is None:
            return None

        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node.value == target:
                return node

            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)

        return None

    def subtree_values(self, target: int) -> Optional[list[int]]:
        node = self.find(target)
        if node is None:
            return None

        result: list[int] = []
        queue = deque([node])

        while queue:
            current = queue.popleft()
            result.append(current.value)

            if current.left is not None:
                queue.append(current.left)
            if current.right is not None:
                queue.append(current.right)

        return result

    def preorder(self) -> list[int]:
        result: list[int] = []

        def visit(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            result.append(node.value)
            visit(node.left)
            visit(node.right)

        visit(self.root)
        return result

    def inorder(self) -> list[int]:
        result: list[int] = []

        def visit(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            visit(node.left)
            result.append(node.value)
            visit(node.right)

        visit(self.root)
        return result

    def postorder(self) -> list[int]:
        result: list[int] = []

        def visit(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            visit(node.left)
            visit(node.right)
            result.append(node.value)

        visit(self.root)
        return result

    def level_order(self) -> list[int]:
        if self.root is None:
            return []

        result: list[int] = []
        queue = deque([self.root])

        while queue:
            node = queue.popleft()
            result.append(node.value)

            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)

        return result

    def validate_unique_values(self) -> None:
        values = self.level_order()
        if len(values) != len(set(values)):
            raise ValueError("Tree contains duplicate node values.")


def build_sample_tree() -> BinaryTree:
    #             10
    #           /    \
    #          5      15
    #         / \    /  \
    #        2   7  12   20
    #           /
    #          6
    root = TreeNode(
        10,
        left=TreeNode(
            5,
            left=TreeNode(2),
            right=TreeNode(7, left=TreeNode(6)),
        ),
        right=TreeNode(
            15,
            left=TreeNode(12),
            right=TreeNode(20),
        ),
    )
    return BinaryTree(root)


def print_tree_report(tree: BinaryTree) -> None:
    tree.validate_unique_values()

    print("Binary Tree Terminology Report")
    print("=" * 32)
    print(f"Root: {tree.root.value if tree.root else None}")
    print(f"Height in edges: {tree.height()}")
    print(f"Preorder: {tree.preorder()}")
    print(f"Inorder: {tree.inorder()}")
    print(f"Postorder: {tree.postorder()}")
    print(f"Level-order: {tree.level_order()}")
    print()

    for value in tree.level_order():
        print(
            f"Node {value}: "
            f"parent={tree.parent_of(value)}, "
            f"children={tree.children_of(value)}, "
            f"degree={tree.degree(value)}, "
            f"depth={tree.node_depth(value)}, "
            f"level={tree.level(value)}, "
            f"subtree={tree.subtree_values(value)}"
        )


def run_edge_case_tests() -> None:
    empty = BinaryTree()
    assert empty.height() == -1
    assert empty.level_order() == []
    assert empty.node_depth(1) == -1
    assert empty.parent_of(1) is None
    assert empty.children_of(1) is None
    assert empty.degree(1) == -1

    single = BinaryTree(TreeNode(42))
    assert single.height() == 0
    assert single.node_depth(42) == 0
    assert single.level(42) == 1
    assert single.parent_of(42) is None
    assert single.children_of(42) == []
    assert single.degree(42) == 0

    skewed = BinaryTree(TreeNode(1, right=TreeNode(2, right=TreeNode(3))))
    assert skewed.height() == 2
    assert skewed.node_depth(3) == 2
    assert skewed.level(3) == 3
    assert skewed.parent_of(3) == 2

    duplicate = BinaryTree(TreeNode(1, left=TreeNode(1)))
    try:
        duplicate.validate_unique_values()
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate-value validation failed.")

    print("\nAll edge-case tests passed.")


def main() -> None:
    tree = build_sample_tree()
    print_tree_report(tree)
    run_edge_case_tests()


if __name__ == "__main__":
    main()
