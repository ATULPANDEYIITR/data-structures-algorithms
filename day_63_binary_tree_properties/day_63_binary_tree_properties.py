from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from collections import deque
from pathlib import Path
from typing import Optional
import json


class NodeKind(Enum):
    LEAF = "leaf"
    INTERNAL = "internal"


@dataclass
class TreeNode:
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None

    @property
    def kind(self) -> NodeKind:
        return NodeKind.LEAF if self.left is None and self.right is None else NodeKind.INTERNAL


class BinaryTree:
    def __init__(self, root: Optional[TreeNode] = None):
        self.root = root

    @staticmethod
    def from_level_order(values: list[Optional[int]]) -> "BinaryTree":
        if not values or values[0] is None:
            return BinaryTree()

        root = TreeNode(values[0])
        queue = deque([root])
        index = 1

        while queue and index < len(values):
            node = queue.popleft()

            if index < len(values) and values[index] is not None:
                node.left = TreeNode(values[index])
                queue.append(node.left)
            index += 1

            if index < len(values) and values[index] is not None:
                node.right = TreeNode(values[index])
                queue.append(node.right)
            index += 1

        if index < len(values):
            raise ValueError("Level-order input contains unreachable non-null nodes")

        return BinaryTree(root)

    def validate(self) -> None:
        if self.root is None:
            return

        visited: set[int] = set()
        stack = [self.root]

        while stack:
            node = stack.pop()
            identity = id(node)

            if identity in visited:
                raise ValueError("Cycle or repeated node reference detected")
            visited.add(identity)

            if node.left is node or node.right is node:
                raise ValueError("A node cannot reference itself")

            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)

    def node_count(self) -> int:
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

    def height_edges(self) -> int:
        """Height measured in edges. Empty tree = -1, single node = 0."""
        def height(node: Optional[TreeNode]) -> int:
            if node is None:
                return -1
            return 1 + max(height(node.left), height(node.right))

        return height(self.root)

    def height_nodes(self) -> int:
        """Height measured in nodes. Empty tree = 0, single node = 1."""
        return self.height_edges() + 1 if self.root else 0

    def leaf_count(self) -> int:
        if self.root is None:
            return 0

        count = 0
        stack = [self.root]

        while stack:
            node = stack.pop()
            if node.left is None and node.right is None:
                count += 1
            else:
                if node.left:
                    stack.append(node.left)
                if node.right:
                    stack.append(node.right)

        return count

    def internal_count(self) -> int:
        return self.node_count() - self.leaf_count()

    def diameter_edges(self) -> int:
        """
        Diameter is the maximum number of edges on a path between two nodes.
        The algorithm is O(n) and computes subtree height and diameter together.
        """
        def visit(node: Optional[TreeNode]) -> tuple[int, int]:
            if node is None:
                return -1, 0

            left_height, left_diameter = visit(node.left)
            right_height, right_diameter = visit(node.right)

            height = 1 + max(left_height, right_height)
            through_node = left_height + right_height + 2
            diameter = max(left_diameter, right_diameter, through_node)

            return height, diameter

        return visit(self.root)[1] if self.root else 0

    def is_balanced(self) -> bool:
        """Balanced means every node has left/right subtree heights differing by <= 1."""

        def check(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0

            left_height = check(node.left)
            if left_height == -2:
                return -2

            right_height = check(node.right)
            if right_height == -2:
                return -2

            if abs(left_height - right_height) > 1:
                return -2

            return 1 + max(left_height, right_height)

        return check(self.root) != -2

    def full_tree(self) -> bool:
        """Every node has either zero children or exactly two children."""
        if self.root is None:
            return True

        stack = [self.root]
        while stack:
            node = stack.pop()
            children = int(node.left is not None) + int(node.right is not None)

            if children == 1:
                return False

            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)

        return True

    def perfect_tree(self) -> bool:
        """
        A perfect tree has all internal nodes with two children and all leaves
        at the same depth.
        """
        if self.root is None:
            return True

        expected_leaf_depth: Optional[int] = None
        stack = [(self.root, 0)]

        while stack:
            node, depth = stack.pop()
            has_left = node.left is not None
            has_right = node.right is not None

            if not has_left and not has_right:
                if expected_leaf_depth is None:
                    expected_leaf_depth = depth
                elif expected_leaf_depth != depth:
                    return False
                continue

            if not has_left or not has_right:
                return False

            stack.append((node.left, depth + 1))
            stack.append((node.right, depth + 1))

        return True

    def complete_tree(self) -> bool:
        """
        A complete tree has every level full except possibly the last,
        and the final level is filled from left to right.
        """
        if self.root is None:
            return True

        queue = deque([self.root])
        encountered_missing_child = False

        while queue:
            node = queue.popleft()

            if node.left:
                if encountered_missing_child:
                    return False
                queue.append(node.left)
            else:
                encountered_missing_child = True

            if node.right:
                if encountered_missing_child:
                    return False
                queue.append(node.right)
            else:
                encountered_missing_child = True

        return True

    def traversals(self) -> dict[str, list[int]]:
        preorder: list[int] = []
        inorder: list[int] = []
        postorder: list[int] = []
        level_order: list[int] = []

        def walk(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            preorder.append(node.value)
            walk(node.left)
            inorder.append(node.value)
            walk(node.right)
            postorder.append(node.value)

        walk(self.root)

        if self.root:
            queue = deque([self.root])
            while queue:
                node = queue.popleft()
                level_order.append(node.value)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

        return {
            "preorder": preorder,
            "inorder": inorder,
            "postorder": postorder,
            "level_order": level_order,
        }

    def structural_profile(self) -> dict:
        self.validate()

        nodes = self.node_count()
        leaves = self.leaf_count()
        internal = self.internal_count()
        height = self.height_edges()

        return {
            "nodes": nodes,
            "leaves": leaves,
            "internal_nodes": internal,
            "height_edges": height,
            "height_nodes": height + 1 if nodes else 0,
            "diameter_edges": self.diameter_edges(),
            "balanced": self.is_balanced(),
            "full": self.full_tree(),
            "complete": self.complete_tree(),
            "perfect": self.perfect_tree(),
            "leaf_internal_identity_holds": leaves == internal + 1
            if nodes > 0 and self.full_tree()
            else None,
        }


def build_examples() -> dict[str, BinaryTree]:
    return {
        "balanced_complete": BinaryTree.from_level_order(
            [10, 5, 15, 2, 7, 12, 20]
        ),
        "unbalanced_chain": BinaryTree.from_level_order(
            [1, 2, None, 3, None, 4, None, 5]
        ),
        "perfect": BinaryTree.from_level_order(
            [8, 4, 12, 2, 6, 10, 14]
        ),
        "full_not_perfect": BinaryTree.from_level_order(
            [10, 5, 15, 2, 7, None, None]
        ),
        "single_node": BinaryTree.from_level_order([42]),
        "empty": BinaryTree.from_level_order([]),
    }


def run_assertions() -> None:
    balanced = BinaryTree.from_level_order([10, 5, 15, 2, 7, 12, 20])
    assert balanced.node_count() == 7
    assert balanced.leaf_count() == 4
    assert balanced.internal_count() == 3
    assert balanced.height_edges() == 2
    assert balanced.diameter_edges() == 4
    assert balanced.is_balanced()
    assert balanced.full_tree()
    assert balanced.complete_tree()
    assert balanced.perfect_tree()

    chain = BinaryTree.from_level_order([1, 2, None, 3, None, 4])
    assert chain.height_edges() == 3
    assert chain.diameter_edges() == 3
    assert not chain.is_balanced()
    assert not chain.full_tree()

    single = BinaryTree.from_level_order([99])
    assert single.height_edges() == 0
    assert single.diameter_edges() == 0
    assert single.leaf_count() == 1
    assert single.internal_count() == 0
    assert single.is_balanced()

    empty = BinaryTree()
    assert empty.node_count() == 0
    assert empty.height_edges() == -1
    assert empty.diameter_edges() == 0
    assert empty.is_balanced()
    assert empty.perfect_tree()

    try:
        BinaryTree.from_level_order([1, None, None, 2])
    except ValueError:
        pass
    else:
        raise AssertionError("Unreachable node should be rejected")


def export_profile(profile: dict, filename: str = "binary_tree_profile.json") -> None:
    """
    Restrict the output path to the current working directory to avoid
    accidentally writing analysis data to an arbitrary filesystem location.
    """
    path = Path(filename).resolve()
    cwd = Path.cwd().resolve()

    if path.parent != cwd:
        raise ValueError("Output file must remain in the current working directory")

    path.write_text(json.dumps(profile, indent=2), encoding="utf-8")


def main() -> None:
    run_assertions()

    print("Binary Tree Structural Analysis")
    print("=" * 34)

    for name, tree in build_examples().items():
        profile = tree.structural_profile()
        print(f"\n{name}")
        print(json.dumps(profile, indent=2))

        if tree.root:
            print("traversals:", json.dumps(tree.traversals()))

    export_profile(
        build_examples()["balanced_complete"].structural_profile()
    )

    print("\nValidation: all assertions passed.")
    print("Profile written to binary_tree_profile.json")


if __name__ == "__main__":
    main()
