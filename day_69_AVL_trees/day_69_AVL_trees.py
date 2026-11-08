#!/usr/bin/env python3
"""
AVL Trees: Self-Balancing Binary Search Trees

Features:
- Node heights and balance factors
- LL, RR, LR, and RL rotations
- Insertion, deletion, and searching
- Minimum and maximum
- In-order, pre-order, and post-order traversal
- Range queries
- Tree validation and structural diagnostics
- JSON serialization and persistence
- Automated test cases

Python 3.10+
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger("avl_tree")


class AVLTreeError(Exception):
    """Base exception for AVL tree operations."""


class InvalidKeyError(AVLTreeError):
    """Raised when a key is invalid."""


@dataclass
class AVLNode:
    key: int
    height: int = 1
    left: Optional["AVLNode"] = None
    right: Optional["AVLNode"] = None


class AVLTree:
    """
    Integer-key AVL tree.

    Balance factor = height(left) - height(right).

    A valid AVL node has a balance factor in {-1, 0, 1}.
    """

    def __init__(self) -> None:
        self.root: Optional[AVLNode] = None
        self.rotation_counts = {
            "LL": 0,
            "RR": 0,
            "LR": 0,
            "RL": 0
        }
        self.operation_counts = {
            "insert": 0,
            "delete": 0,
            "search": 0
        }

    @staticmethod
    def _validate_key(key: int) -> None:
        if isinstance(key, bool) or not isinstance(key, int):
            raise InvalidKeyError("Keys must be integers.")

    @staticmethod
    def _height(node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _balance_factor(self, node: Optional[AVLNode]) -> int:
        if node is None:
            return 0

        return (
            self._height(node.left)
            - self._height(node.right)
        )

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(
            self._height(node.left),
            self._height(node.right)
        )

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """Right rotation used for LL and LR imbalances."""
        x = y.left

        if x is None:
            raise AVLTreeError("Invalid right rotation.")

        transferred_subtree = x.right

        x.right = y
        y.left = transferred_subtree

        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """Left rotation used for RR and RL imbalances."""
        y = x.right

        if y is None:
            raise AVLTreeError("Invalid left rotation.")

        transferred_subtree = y.left

        y.left = x
        x.right = transferred_subtree

        self._update_height(x)
        self._update_height(y)

        return y

    def _rebalance(self, node: AVLNode) -> AVLNode:
        self._update_height(node)

        balance = self._balance_factor(node)

        # Left-heavy subtree.
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                # LR: first rotate left, then right.
                self.rotation_counts["LR"] += 1
                node.left = self._rotate_left(node.left)
            else:
                self.rotation_counts["LL"] += 1

            return self._rotate_right(node)

        # Right-heavy subtree.
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                # RL: first rotate right, then left.
                self.rotation_counts["RL"] += 1
                node.right = self._rotate_right(node.right)
            else:
                self.rotation_counts["RR"] += 1

            return self._rotate_left(node)

        return node

    def _insert(
        self,
        node: Optional[AVLNode],
        key: int
    ) -> AVLNode:

        if node is None:
            return AVLNode(key)

        if key < node.key:
            node.left = self._insert(node.left, key)

        elif key > node.key:
            node.right = self._insert(node.right, key)

        else:
            return node

        return self._rebalance(node)

    def insert(self, key: int) -> bool:
        self._validate_key(key)

        existed = self.search(key)

        if existed:
            return False

        self.root = self._insert(self.root, key)
        self.operation_counts["insert"] += 1

        return True

    def search(self, key: int) -> bool:
        self._validate_key(key)

        self.operation_counts["search"] += 1

        current = self.root

        while current is not None:
            if key == current.key:
                return True

            if key < current.key:
                current = current.left
            else:
                current = current.right

        return False

    @staticmethod
    def _minimum_node(node: AVLNode) -> AVLNode:
        while node.left is not None:
            node = node.left

        return node

    @staticmethod
    def _maximum_node(node: AVLNode) -> AVLNode:
        while node.right is not None:
            node = node.right

        return node

    def minimum(self) -> Optional[int]:
        if self.root is None:
            return None

        return self._minimum_node(self.root).key

    def maximum(self) -> Optional[int]:
        if self.root is None:
            return None

        return self._maximum_node(self.root).key

    def _delete(
        self,
        node: Optional[AVLNode],
        key: int
    ) -> Optional[AVLNode]:

        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)

        elif key > node.key:
            node.right = self._delete(node.right, key)

        else:
            if node.left is None:
                return node.right

            if node.right is None:
                return node.left

            successor = self._minimum_node(node.right)
            node.key = successor.key

            node.right = self._delete(
                node.right,
                successor.key
            )

        return self._rebalance(node)

    def delete(self, key: int) -> bool:
        self._validate_key(key)

        if not self.search(key):
            return False

        self.root = self._delete(self.root, key)
        self.operation_counts["delete"] += 1

        return True

    def inorder(self) -> list[int]:
        result: list[int] = []

        def traverse(node: Optional[AVLNode]) -> None:
            if node is None:
                return

            traverse(node.left)
            result.append(node.key)
            traverse(node.right)

        traverse(self.root)
        return result

    def preorder(self) -> list[int]:
        result: list[int] = []

        def traverse(node: Optional[AVLNode]) -> None:
            if node is None:
                return

            result.append(node.key)
            traverse(node.left)
            traverse(node.right)

        traverse(self.root)
        return result

    def postorder(self) -> list[int]:
        result: list[int] = []

        def traverse(node: Optional[AVLNode]) -> None:
            if node is None:
                return

            traverse(node.left)
            traverse(node.right)
            result.append(node.key)

        traverse(self.root)
        return result

    def level_order(self) -> list[list[int]]:
        if self.root is None:
            return []

        queue = [self.root]
        result = []

        while queue:
            level = []
            next_level = []

            for node in queue:
                level.append(node.key)

                if node.left:
                    next_level.append(node.left)

                if node.right:
                    next_level.append(node.right)

            result.append(level)
            queue = next_level

        return result

    def range_query(self, lower: int, upper: int) -> list[int]:
        self._validate_key(lower)
        self._validate_key(upper)

        if lower > upper:
            raise ValueError("Lower bound cannot exceed upper bound.")

        result = []

        def traverse(node: Optional[AVLNode]) -> None:
            if node is None:
                return

            if node.key > lower:
                traverse(node.left)

            if lower <= node.key <= upper:
                result.append(node.key)

            if node.key < upper:
                traverse(node.right)

        traverse(self.root)
        return result

    def height(self) -> int:
        return self._height(self.root)

    def size(self) -> int:
        return len(self.inorder())

    def clear(self) -> None:
        self.root = None

    def validate(self) -> bool:
        """Check BST ordering, stored heights, and AVL balance."""

        def inspect(
            node: Optional[AVLNode],
            minimum: Optional[int],
            maximum: Optional[int]
        ) -> tuple[bool, int]:

            if node is None:
                return True, 0

            if minimum is not None and node.key <= minimum:
                return False, 0

            if maximum is not None and node.key >= maximum:
                return False, 0

            left_valid, left_height = inspect(
                node.left, minimum, node.key
            )

            right_valid, right_height = inspect(
                node.right, node.key, maximum
            )

            expected_height = 1 + max(
                left_height,
                right_height
            )

            balance = left_height - right_height

            valid = (
                left_valid
                and right_valid
                and node.height == expected_height
                and abs(balance) <= 1
            )

            return valid, expected_height

        valid, _ = inspect(self.root, None, None)
        return valid

    def print_tree(self) -> None:
        """Print keys, heights, and balance factors."""

        def display(
            node: Optional[AVLNode],
            prefix: str = "",
            is_left: bool = True
        ) -> None:

            if node is None:
                return

            display(
                node.right,
                prefix + ("│   " if is_left else "    "),
                False
            )

            connector = "└── " if is_left else "┌── "

            print(
                f"{prefix}{connector}{node.key} "
                f"[H={node.height}, BF={self._balance_factor(node)}]"
            )

            display(
                node.left,
                prefix + ("    " if is_left else "│   "),
                True
            )

        if self.root is None:
            print("(empty tree)")
        else:
            display(self.root)

    def to_dict(self) -> Optional[dict[str, Any]]:
        def serialize(
            node: Optional[AVLNode]
        ) -> Optional[dict[str, Any]]:

            if node is None:
                return None

            return {
                "key": node.key,
                "height": node.height,
                "left": serialize(node.left),
                "right": serialize(node.right)
            }

        return serialize(self.root)

    def save(self, filename: str) -> None:
        path = Path(filename)

        data = {
            "format_version": 1,
            "root": self.to_dict()
        }

        # Avoid partially written files.
        temporary = path.with_suffix(path.suffix + ".tmp")

        try:
            temporary.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8"
            )
            temporary.replace(path)

        except OSError:
            temporary.unlink(missing_ok=True)
            raise

    @classmethod
    def load(cls, filename: str) -> "AVLTree":
        path = Path(filename)

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            if data.get("format_version") != 1:
                raise ValueError("Unsupported file format.")

            tree = cls()

            def restore(
                item: Optional[dict[str, Any]],
                minimum: Optional[int],
                maximum: Optional[int]
            ) -> Optional[AVLNode]:

                if item is None:
                    return None

                if not isinstance(item, dict):
                    raise ValueError("Invalid node structure.")

                key = item.get("key")

                cls._validate_key(key)

                if minimum is not None and key <= minimum:
                    raise ValueError("Invalid BST ordering.")

                if maximum is not None and key >= maximum:
                    raise ValueError("Invalid BST ordering.")

                node = AVLNode(key)

                node.left = restore(
                    item.get("left"), minimum, key
                )

                node.right = restore(
                    item.get("right"), key, maximum
                )

                tree._update_height(node)

                if node.height != item.get("height"):
                    raise ValueError("Invalid stored height.")

                if abs(tree._balance_factor(node)) > 1:
                    raise ValueError("Invalid AVL balance.")

                return node

            tree.root = restore(data.get("root"), None, None)

            if not tree.validate():
                raise ValueError("Invalid AVL tree structure.")

            return tree

        except (OSError, json.JSONDecodeError) as error:
            raise AVLTreeError(
                f"Could not load AVL tree: {error}"
            ) from error


def demonstrate_rotations() -> None:
    print("\nROTATION DEMONSTRATIONS")

    cases = {
        "LL": [30, 20, 10],
        "RR": [10, 20, 30],
        "LR": [30, 10, 20],
        "RL": [10, 30, 20]
    }

    for rotation, values in cases.items():
        tree = AVLTree()

        for value in values:
            tree.insert(value)

        print(f"\n{rotation} case: {values}")
        print("Root:", tree.root.key)
        print("In-order:", tree.inorder())
        print("Rotation counts:", tree.rotation_counts)

        assert tree.root.key == 20
        assert tree.validate()


def run_tests() -> None:
    tree = AVLTree()

    assert tree.inorder() == []
    assert tree.height() == 0
    assert tree.delete(100) is False

    values = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45]

    for value in values:
        assert tree.insert(value)

    assert not tree.insert(50)
    assert tree.validate()

    assert tree.search(40)
    assert not tree.search(999)

    assert tree.minimum() == 10
    assert tree.maximum() == 80

    assert tree.inorder() == sorted(values)
    assert tree.range_query(25, 60) == [
        25, 30, 35, 40, 45, 50, 60
    ]

    assert tree.delete(50)
    assert not tree.search(50)
    assert tree.validate()

    assert not tree.delete(999)

    # Delete a leaf, a one-child node, and a two-child node.
    for key in [10, 20, 40]:
        tree.delete(key)
        assert tree.validate()

    # Empty tree behavior.
    empty = AVLTree()
    assert empty.inorder() == []
    assert empty.minimum() is None
    assert empty.maximum() is None

    # Invalid keys.
    for invalid in ["10", 10.5, True, None]:
        try:
            tree.insert(invalid)
        except InvalidKeyError:
            pass
        else:
            raise AssertionError("Invalid key was accepted.")

    # Persistence.
    filename = "avl_tree_demo.json"
    tree.save(filename)

    restored = AVLTree.load(filename)

    assert restored.inorder() == tree.inorder()
    assert restored.validate()

    Path(filename).unlink(missing_ok=True)

    # Invalid range.
    try:
        tree.range_query(50, 20)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid range was accepted.")

    print("\nAll AVL tree tests passed.")


def main() -> None:
    print("=" * 60)
    print("AVL TREE: SELF-BALANCING BINARY SEARCH TREE")
    print("=" * 60)

    demonstrate_rotations()

    tree = AVLTree()

    inventory_ids = [
        100, 50, 150, 25, 75, 125, 175,
        10, 35, 60, 90, 110, 140, 160, 190
    ]

    print("\nINVENTORY INDEX")

    for item_id in inventory_ids:
        tree.insert(item_id)

    tree.print_tree()

    print("\nIN-ORDER:", tree.inorder())
    print("PRE-ORDER:", tree.preorder())
    print("POST-ORDER:", tree.postorder())
    print("LEVEL-ORDER:", tree.level_order())

    print("\nTree height:", tree.height())
    print("Tree size:", tree.size())
    print("Minimum ID:", tree.minimum())
    print("Maximum ID:", tree.maximum())

    print("\nSearch for 125:", tree.search(125))
    print("Search for 999:", tree.search(999))

    print("IDs between 50 and 150:", tree.range_query(50, 150))

    print("\nDeleting inventory ID 100")

    tree.delete(100)

    print("Updated in-order:", tree.inorder())
    print("AVL valid:", tree.validate())

    print("\nRotation statistics:", tree.rotation_counts)
    print("Operation statistics:", tree.operation_counts)

    run_tests()


if __name__ == "__main__":
    main()
