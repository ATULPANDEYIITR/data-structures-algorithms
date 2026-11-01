"""
Binary Tree Traversals
Preorder, Inorder, Postorder, and Level-order traversal.
Recursive and iterative implementations.
Python 3.10+
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Optional


class TraversalOrder(Enum):
    PREORDER = "preorder"
    INORDER = "inorder"
    POSTORDER = "postorder"
    LEVELORDER = "levelorder"


@dataclass
class TreeNode:
    value: int
    left: Optional[TreeNode] = None
    right: Optional[TreeNode] = None


class BinaryTree:
    def __init__(self, root: Optional[TreeNode] = None):
        self.root = root

    def is_empty(self) -> bool:
        return self.root is None

    def preorder_recursive(self) -> list[int]:
        result = []

        def visit(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            result.append(node.value)
            visit(node.left)
            visit(node.right)

        visit(self.root)
        return result

    def inorder_recursive(self) -> list[int]:
        result = []

        def visit(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            visit(node.left)
            result.append(node.value)
            visit(node.right)

        visit(self.root)
        return result

    def postorder_recursive(self) -> list[int]:
        result = []

        def visit(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            visit(node.left)
            visit(node.right)
            result.append(node.value)

        visit(self.root)
        return result

    def levelorder(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        queue = deque([self.root])

        while queue:
            node = queue.popleft()
            result.append(node.value)

            if node.left is not None:
                queue.append(node.left)

            if node.right is not None:
                queue.append(node.right)

        return result

    def preorder_iterative(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        stack = [self.root]

        while stack:
            node = stack.pop()
            result.append(node.value)

            # Push right first so left is processed first.
            if node.right is not None:
                stack.append(node.right)

            if node.left is not None:
                stack.append(node.left)

        return result

    def inorder_iterative(self) -> list[int]:
        result = []
        stack = []
        current = self.root

        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()
            result.append(current.value)
            current = current.right

        return result

    def postorder_iterative(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        stack = [(self.root, False)]

        while stack:
            node, visited = stack.pop()

            if visited:
                result.append(node.value)
                continue

            stack.append((node, True))

            if node.right is not None:
                stack.append((node.right, False))

            if node.left is not None:
                stack.append((node.left, False))

        return result

    def postorder_two_stacks(self) -> list[int]:
        if self.root is None:
            return []

        first = [self.root]
        second = []

        while first:
            node = first.pop()
            second.append(node)

            if node.left is not None:
                first.append(node.left)

            if node.right is not None:
                first.append(node.right)

        return [node.value for node in reversed(second)]

    def levelorder_by_level(self) -> list[list[int]]:
        if self.root is None:
            return []

        queue = deque([self.root])
        levels = []

        while queue:
            level_size = len(queue)
            level = []

            for _ in range(level_size):
                node = queue.popleft()
                level.append(node.value)

                if node.left is not None:
                    queue.append(node.left)

                if node.right is not None:
                    queue.append(node.right)

            levels.append(level)

        return levels

    def traverse(
        self,
        order: TraversalOrder,
        recursive: bool = False
    ) -> list[int]:

        methods = {
            TraversalOrder.PREORDER: (
                self.preorder_recursive if recursive
                else self.preorder_iterative
            ),
            TraversalOrder.INORDER: (
                self.inorder_recursive if recursive
                else self.inorder_iterative
            ),
            TraversalOrder.POSTORDER: (
                self.postorder_recursive if recursive
                else self.postorder_iterative
            ),
            TraversalOrder.LEVELORDER: self.levelorder,
        }

        return methods[order]()

    def height(self) -> int:
        """Calculate tree height measured in nodes."""
        if self.root is None:
            return 0

        queue = deque([(self.root, 1)])
        maximum = 0

        while queue:
            node, depth = queue.popleft()
            maximum = max(maximum, depth)

            if node.left:
                queue.append((node.left, depth + 1))

            if node.right:
                queue.append((node.right, depth + 1))

        return maximum

    def count_nodes(self) -> int:
        if self.root is None:
            return 0

        count = 0
        stack = [self.root]

        while stack:
            node = stack.pop()
            count += 1

            if node.left:
                stack.append(node.left)

            if node.right:
                stack.append(node.right)

        return count

    def find(self, target: int) -> Optional[TreeNode]:
        if self.root is None:
            return None

        queue = deque([self.root])

        while queue:
            node = queue.popleft()

            if node.value == target:
                return node

            if node.left:
                queue.append(node.left)

            if node.right:
                queue.append(node.right)

        return None

    def is_complete(self) -> bool:
        if self.root is None:
            return True

        queue = deque([self.root])
        missing_child_seen = False

        while queue:
            node = queue.popleft()

            for child in (node.left, node.right):
                if child is None:
                    missing_child_seen = True
                else:
                    if missing_child_seen:
                        return False
                    queue.append(child)

        return True

    def print_report(self) -> None:
        print("\nBINARY TREE TRAVERSAL REPORT")
        print("=" * 45)

        for order in TraversalOrder:
            iterative = self.traverse(order)
            print(f"{order.value.title():15}: {iterative}")

        print("\nRECURSIVE RESULTS")
        print("-" * 45)

        print("Preorder       :", self.preorder_recursive())
        print("Inorder        :", self.inorder_recursive())
        print("Postorder      :", self.postorder_recursive())
        print("Level-order    :", self.levelorder())

        print("\nTREE INFORMATION")
        print("-" * 45)
        print("Node count     :", self.count_nodes())
        print("Height         :", self.height())
        print("Complete tree  :", self.is_complete())
        print("Search for 50  :", self.find(50) is not None)


def build_sample_tree() -> BinaryTree:
    """
                    50
                   /  \
                 30    70
                / \   / \
               20 40 60 80
              /       \
             10        65
    """

    root = TreeNode(50)

    root.left = TreeNode(30)
    root.right = TreeNode(70)

    root.left.left = TreeNode(20)
    root.left.right = TreeNode(40)

    root.right.left = TreeNode(60)
    root.right.right = TreeNode(80)

    root.left.left.left = TreeNode(10)
    root.right.left.right = TreeNode(65)

    return BinaryTree(root)


def run_tests() -> None:
    tree = build_sample_tree()

    assert tree.preorder_recursive() == [
        50, 30, 20, 10, 40, 70, 60, 65, 80
    ]

    assert tree.inorder_recursive() == [
        10, 20, 30, 40, 50, 60, 65, 70, 80
    ]

    assert tree.postorder_recursive() == [
        10, 20, 40, 30, 65, 60, 80, 70, 50
    ]

    assert tree.levelorder() == [
        50, 30, 70, 20, 40, 60, 80, 10, 65
    ]

    assert tree.preorder_recursive() == tree.preorder_iterative()
    assert tree.inorder_recursive() == tree.inorder_iterative()
    assert tree.postorder_recursive() == tree.postorder_iterative()

    assert tree.postorder_iterative() == tree.postorder_two_stacks()
    assert tree.count_nodes() == 9
    assert tree.height() == 4
    assert tree.find(65) is not None
    assert tree.find(999) is None

    empty = BinaryTree()
    assert empty.preorder_recursive() == []
    assert empty.inorder_iterative() == []
    assert empty.postorder_iterative() == []
    assert empty.levelorder() == []
    assert empty.height() == 0
    assert empty.count_nodes() == 0

    single = BinaryTree(TreeNode(42))
    assert single.preorder_recursive() == [42]
    assert single.inorder_iterative() == [42]
    assert single.postorder_iterative() == [42]
    assert single.levelorder() == [42]

    print("All binary tree traversal tests passed.")


def main() -> None:
    tree = build_sample_tree()
    tree.print_report()

    print("\nLEVEL-BY-LEVEL TRAVERSAL")
    for depth, values in enumerate(tree.levelorder_by_level()):
        print(f"Level {depth}: {values}")

    print()
    run_tests()


if __name__ == "__main__":
    main()
