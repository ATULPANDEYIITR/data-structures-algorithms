#!/usr/bin/env python3
"""
Red-Black Trees
---------------
A self-contained implementation of a Red-Black Tree supporting:
- Insertion and deletion
- Left and right rotations
- Search and ordered traversal
- Minimum, maximum, predecessor and successor
- Range queries
- Red-Black property validation
- Tree statistics
- Randomized testing

Python 3.10+
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Generic, Iterator, Optional, TypeVar

K = TypeVar("K")


class Color(Enum):
    RED = "RED"
    BLACK = "BLACK"


@dataclass
class Node(Generic[K]):
    key: Optional[K]
    color: Color
    left: Optional[Node[K]] = None
    right: Optional[Node[K]] = None
    parent: Optional[Node[K]] = None


class RedBlackTree(Generic[K]):

    def __init__(self):
        # A shared black sentinel simplifies boundary and deletion handling.
        self.nil: Node[K] = Node(None, Color.BLACK)
        self.nil.left = self.nil
        self.nil.right = self.nil
        self.nil.parent = self.nil

        self.root: Node[K] = self.nil
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def __contains__(self, key: K) -> bool:
        return self.search(key) is not None

    def _validate_key(self, key: K) -> None:
        if key is None:
            raise ValueError("None is not a valid tree key")

        try:
            _ = key < key
        except TypeError as exc:
            raise TypeError("Keys must support comparison") from exc

    def search(self, key: K) -> Optional[Node[K]]:
        self._validate_key(key)
        current = self.root

        while current != self.nil:
            if key == current.key:
                return current

            current = (
                current.left if key < current.key else current.right
            )

        return None

    def left_rotate(self, x: Node[K]) -> None:
        y = x.right

        if y == self.nil:
            raise ValueError("Left rotation requires a right child")

        x.right = y.left

        if y.left != self.nil:
            y.left.parent = x

        y.parent = x.parent

        if x.parent == self.nil:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x
        x.parent = y

    def right_rotate(self, y: Node[K]) -> None:
        x = y.left

        if x == self.nil:
            raise ValueError("Right rotation requires a left child")

        y.left = x.right

        if x.right != self.nil:
            x.right.parent = y

        x.parent = y.parent

        if y.parent == self.nil:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x

        x.right = y
        y.parent = x

    def insert(self, key: K) -> bool:
        self._validate_key(key)

        parent = self.nil
        current = self.root

        while current != self.nil:
            parent = current

            if key == current.key:
                return False

            current = current.left if key < current.key else current.right

        node = Node(
            key=key,
            color=Color.RED,
            left=self.nil,
            right=self.nil,
            parent=parent
        )

        if parent == self.nil:
            self.root = node
        elif key < parent.key:
            parent.left = node
        else:
            parent.right = node

        self.size += 1
        self._insert_fixup(node)
        return True

    def _insert_fixup(self, z: Node[K]) -> None:
        while z.parent.color == Color.RED:

            if z.parent == z.parent.parent.left:
                uncle = z.parent.parent.right

                if uncle.color == Color.RED:
                    z.parent.color = Color.BLACK
                    uncle.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    z = z.parent
                else:
                    if z == z.parent.right:
                        z = z.parent
                        self.left_rotate(z)

                    z.parent.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    self.right_rotate(z.parent.parent)

            else:
                uncle = z.parent.parent.left

                if uncle.color == Color.RED:
                    z.parent.color = Color.BLACK
                    uncle.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    z = z.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self.right_rotate(z)

                    z.parent.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    self.left_rotate(z.parent.parent)

        self.root.color = Color.BLACK
        self.root.parent = self.nil

    def minimum(self, node: Optional[Node[K]] = None) -> Optional[K]:
        current = self.root if node is None else node

        if current == self.nil:
            return None

        while current.left != self.nil:
            current = current.left

        return current.key

    def maximum(self, node: Optional[Node[K]] = None) -> Optional[K]:
        current = self.root if node is None else node

        if current == self.nil:
            return None

        while current.right != self.nil:
            current = current.right

        return current.key

    def successor(self, key: K) -> Optional[K]:
        node = self.search(key)

        if node is None:
            return None

        if node.right != self.nil:
            return self.minimum(node.right)

        parent = node.parent

        while parent != self.nil and node == parent.right:
            node = parent
            parent = parent.parent

        return parent.key if parent != self.nil else None

    def predecessor(self, key: K) -> Optional[K]:
        node = self.search(key)

        if node is None:
            return None

        if node.left != self.nil:
            return self.maximum(node.left)

        parent = node.parent

        while parent != self.nil and node == parent.left:
            node = parent
            parent = parent.parent

        return parent.key if parent != self.nil else None

    def _transplant(self, u: Node[K], v: Node[K]) -> None:
        if u.parent == self.nil:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v

        # The sentinel parent is temporarily maintained for deletion fixup.
        v.parent = u.parent

    def _delete_fixup(self, x: Node[K]) -> None:
        while x != self.root and x.color == Color.BLACK:

            if x == x.parent.left:
                sibling = x.parent.right

                if sibling.color == Color.RED:
                    sibling.color = Color.BLACK
                    x.parent.color = Color.RED
                    self.left_rotate(x.parent)
                    sibling = x.parent.right

                if (
                    sibling.left.color == Color.BLACK
                    and sibling.right.color == Color.BLACK
                ):
                    sibling.color = Color.RED
                    x = x.parent
                else:
                    if sibling.right.color == Color.BLACK:
                        sibling.left.color = Color.BLACK
                        sibling.color = Color.RED
                        self.right_rotate(sibling)
                        sibling = x.parent.right

                    sibling.color = x.parent.color
                    x.parent.color = Color.BLACK
                    sibling.right.color = Color.BLACK
                    self.left_rotate(x.parent)
                    x = self.root

            else:
                sibling = x.parent.left

                if sibling.color == Color.RED:
                    sibling.color = Color.BLACK
                    x.parent.color = Color.RED
                    self.right_rotate(x.parent)
                    sibling = x.parent.left

                if (
                    sibling.right.color == Color.BLACK
                    and sibling.left.color == Color.BLACK
                ):
                    sibling.color = Color.RED
                    x = x.parent
                else:
                    if sibling.left.color == Color.BLACK:
                        sibling.right.color = Color.BLACK
                        sibling.color = Color.RED
                        self.left_rotate(sibling)
                        sibling = x.parent.left

                    sibling.color = x.parent.color
                    x.parent.color = Color.BLACK
                    sibling.left.color = Color.BLACK
                    self.right_rotate(x.parent)
                    x = self.root

        x.color = Color.BLACK

    def delete(self, key: K) -> bool:
        z = self.search(key)

        if z is None:
            return False

        y = z
        original_color = y.color

        if z.left == self.nil:
            x = z.right
            self._transplant(z, z.right)

        elif z.right == self.nil:
            x = z.left
            self._transplant(z, z.left)

        else:
            y = z.right

            while y.left != self.nil:
                y = y.left

            original_color = y.color
            x = y.right

            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y

            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color

        self.size -= 1

        if original_color == Color.BLACK:
            self._delete_fixup(x)

        self.nil.color = Color.BLACK

        if self.root != self.nil:
            self.root.parent = self.nil

        return True

    def inorder(self) -> list[K]:
        result: list[K] = []

        def traverse(node: Node[K]) -> None:
            if node == self.nil:
                return

            traverse(node.left)
            result.append(node.key)
            traverse(node.right)

        traverse(self.root)
        return result

    def range_query(self, low: K, high: K) -> list[K]:
        self._validate_key(low)
        self._validate_key(high)

        if low > high:
            raise ValueError("Lower bound exceeds upper bound")

        result: list[K] = []

        def traverse(node: Node[K]) -> None:
            if node == self.nil:
                return

            if node.key > low:
                traverse(node.left)

            if low <= node.key <= high:
                result.append(node.key)

            if node.key < high:
                traverse(node.right)

        traverse(self.root)
        return result

    def height(self) -> int:
        def calculate(node: Node[K]) -> int:
            if node == self.nil:
                return 0

            return 1 + max(
                calculate(node.left),
                calculate(node.right)
            )

        return calculate(self.root)

    def validate(self) -> bool:
        if self.nil.color != Color.BLACK:
            raise AssertionError("Sentinel must be black")

        if self.root == self.nil:
            if self.size != 0:
                raise AssertionError("Incorrect size for empty tree")
            return True

        if self.root.parent != self.nil:
            raise AssertionError("Root parent must be sentinel")

        if self.root.color != Color.BLACK:
            raise AssertionError("Root must be black")

        visited = 0

        def inspect(
            node: Node[K],
            lower: Optional[K],
            upper: Optional[K],
            parent: Node[K]
        ) -> int:

            nonlocal visited

            if node == self.nil:
                return 1

            visited += 1

            if node.parent != parent:
                raise AssertionError("Invalid parent pointer")

            if lower is not None and not lower < node.key:
                raise AssertionError("BST lower-bound violation")

            if upper is not None and not node.key < upper:
                raise AssertionError("BST upper-bound violation")

            if node.color == Color.RED:
                if (
                    node.left.color == Color.RED
                    or node.right.color == Color.RED
                ):
                    raise AssertionError("Adjacent red nodes detected")

            left_height = inspect(
                node.left, lower, node.key, node
            )

            right_height = inspect(
                node.right, node.key, upper, node
            )

            if left_height != right_height:
                raise AssertionError("Black-height violation")

            return left_height + (
                1 if node.color == Color.BLACK else 0
            )

        inspect(self.root, None, None, self.nil)

        if visited != self.size:
            raise AssertionError("Tree size does not match node count")

        return True

    def display(self) -> None:
        def print_node(node: Node[K], prefix: str, is_left: bool) -> None:
            if node == self.nil:
                return

            print_node(
                node.right,
                prefix + ("│   " if is_left else "    "),
                False
            )

            branch = "└── " if is_left else "┌── "
            print(
                prefix + branch + f"{node.key} ({node.color.value})"
            )

            print_node(
                node.left,
                prefix + ("    " if is_left else "│   "),
                True
            )

        if self.root == self.nil:
            print("(empty tree)")
        else:
            print_node(self.root, "", True)


def run_tests() -> None:
    tree = RedBlackTree[int]()
    reference: set[int] = set()

    values = [41, 38, 31, 12, 19, 8, 50, 60, 55, 45, 70]

    print("INSERTION")

    for value in values:
        inserted = tree.insert(value)
        assert inserted == (value not in reference)

        reference.add(value)
        assert tree.validate()

        print(f"Inserted {value}: {tree.inorder()}")

    print("\nTREE STRUCTURE")
    tree.display()

    assert tree.inorder() == sorted(reference)
    assert tree.search(19) is not None
    assert tree.search(999) is None

    print("\nMINIMUM:", tree.minimum())
    print("MAXIMUM:", tree.maximum())
    print("SUCCESSOR OF 38:", tree.successor(38))
    print("PREDECESSOR OF 38:", tree.predecessor(38))
    print("RANGE 15-55:", tree.range_query(15, 55))
    print("HEIGHT:", tree.height())

    print("\nDELETION")

    for value in [8, 12, 19, 41, 55, 999]:
        deleted = tree.delete(value)
        assert deleted == (value in reference)

        reference.discard(value)

        assert tree.validate()
        assert tree.inorder() == sorted(reference)

        print(f"Deleted {value}: {tree.inorder()}")

    # Randomized testing against Python's sorted-set behavior.
    print("\nRANDOMIZED TESTING")

    rng = random.Random(42)
    random_tree = RedBlackTree[int]()
    expected: set[int] = set()

    for _ in range(3000):
        value = rng.randint(-500, 500)

        if rng.random() < 0.58:
            result = random_tree.insert(value)
            assert result == (value not in expected)
            expected.add(value)
        else:
            result = random_tree.delete(value)
            assert result == (value in expected)
            expected.discard(value)

        assert random_tree.validate()
        assert random_tree.inorder() == sorted(expected)

    print("Randomized insertion/deletion tests passed.")
    print("Final node count:", len(random_tree))
    print("Final height:", random_tree.height())


if __name__ == "__main__":
    run_tests()
