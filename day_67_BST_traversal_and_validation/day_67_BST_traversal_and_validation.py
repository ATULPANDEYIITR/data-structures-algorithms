#!/usr/bin/env python3
"""
BST Traversal and Validation

Demonstrates:
- Binary Search Tree insertion and deletion
- Inorder, preorder, postorder, and level-order traversal
- BST validation using strict lower and upper bounds
- Minimum and maximum values
- Floor and ceiling queries
- Range queries
- Successor and predecessor
- Balanced-tree construction from sorted values
- Duplicate-key rejection
- Structural integrity checks
- Complexity and performance measurements
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional, Iterable
import random
import time


class BSTError(Exception):
    """Base exception for BST operations."""


class DuplicateKeyError(BSTError):
    """Raised when a duplicate key is inserted."""


class EmptyTreeError(BSTError):
    """Raised when an operation requires a non-empty tree."""


@dataclass
class Node:
    key: int
    left: Optional[Node] = None
    right: Optional[Node] = None
    height: int = 1


class BinarySearchTree:
    """
    Integer BST with unique keys.

    Ordering invariant:
        Every key in the left subtree is smaller.
        Every key in the right subtree is greater.
    """

    def __init__(self):
        self.root: Optional[Node] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: int) -> bool:
        return self.search(key) is not None

    @staticmethod
    def _validate_key(key: int) -> None:
        if isinstance(key, bool) or not isinstance(key, int):
            raise TypeError("BST keys must be integers.")

    def insert(self, key: int) -> None:
        self._validate_key(key)

        if self.root is None:
            self.root = Node(key)
            self._size = 1
            return

        current = self.root

        while True:
            if key == current.key:
                raise DuplicateKeyError(f"Duplicate key: {key}")

            if key < current.key:
                if current.left is None:
                    current.left = Node(key)
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = Node(key)
                    break
                current = current.right

        self._size += 1

    def insert_many(self, values: Iterable[int]) -> None:
        for value in values:
            self.insert(value)

    def search(self, key: int) -> Optional[Node]:
        self._validate_key(key)
        current = self.root

        while current is not None:
            if key == current.key:
                return current
            current = current.left if key < current.key else current.right

        return None

    def inorder(self) -> list[int]:
        """Return keys in ascending order using iterative traversal."""
        result = []
        stack = []
        current = self.root

        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()
            result.append(current.key)
            current = current.right

        return result

    def preorder(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        stack = [self.root]

        while stack:
            node = stack.pop()
            result.append(node.key)

            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)

        return result

    def postorder(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        stack = [(self.root, False)]

        while stack:
            node, visited = stack.pop()

            if visited:
                result.append(node.key)
            else:
                stack.append((node, True))
                if node.right:
                    stack.append((node.right, False))
                if node.left:
                    stack.append((node.left, False))

        return result

    def level_order(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        queue = deque([self.root])

        while queue:
            node = queue.popleft()
            result.append(node.key)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        return result

    def minimum(self) -> int:
        if self.root is None:
            raise EmptyTreeError("Cannot find minimum of an empty tree.")

        current = self.root
        while current.left:
            current = current.left

        return current.key

    def maximum(self) -> int:
        if self.root is None:
            raise EmptyTreeError("Cannot find maximum of an empty tree.")

        current = self.root
        while current.right:
            current = current.right

        return current.key

    def floor(self, key: int) -> Optional[int]:
        """Largest stored key less than or equal to key."""
        self._validate_key(key)

        current = self.root
        candidate = None

        while current:
            if current.key == key:
                return current.key

            if current.key < key:
                candidate = current.key
                current = current.right
            else:
                current = current.left

        return candidate

    def ceiling(self, key: int) -> Optional[int]:
        """Smallest stored key greater than or equal to key."""
        self._validate_key(key)

        current = self.root
        candidate = None

        while current:
            if current.key == key:
                return current.key

            if current.key > key:
                candidate = current.key
                current = current.left
            else:
                current = current.right

        return candidate

    def range_query(self, low: int, high: int) -> list[int]:
        """Return all keys in the inclusive interval [low, high]."""
        self._validate_key(low)
        self._validate_key(high)

        if low > high:
            raise ValueError("Lower bound cannot exceed upper bound.")

        result = []
        stack = []
        current = self.root

        while current is not None or stack:
            while current:
                if current.key >= low:
                    stack.append(current)
                    current = current.left
                else:
                    current = current.right

            if not stack:
                break

            current = stack.pop()

            if current.key > high:
                break

            result.append(current.key)
            current = current.right

        return result

    def successor(self, key: int) -> Optional[int]:
        """Find the smallest stored key strictly greater than key."""
        self._validate_key(key)

        current = self.root
        candidate = None

        while current:
            if current.key > key:
                candidate = current.key
                current = current.left
            else:
                current = current.right

        return candidate

    def predecessor(self, key: int) -> Optional[int]:
        """Find the largest stored key strictly smaller than key."""
        self._validate_key(key)

        current = self.root
        candidate = None

        while current:
            if current.key < key:
                candidate = current.key
                current = current.right
            else:
                current = current.left

        return candidate

    def delete(self, key: int) -> bool:
        """Delete a key using standard BST deletion rules."""
        self._validate_key(key)

        def remove(node: Optional[Node], target: int):
            if node is None:
                return None, False

            if target < node.key:
                node.left, deleted = remove(node.left, target)
                return node, deleted

            if target > node.key:
                node.right, deleted = remove(node.right, target)
                return node, deleted

            if node.left is None:
                return node.right, True

            if node.right is None:
                return node.left, True

            successor_node = node.right
            while successor_node.left:
                successor_node = successor_node.left

            node.key = successor_node.key
            node.right, _ = remove(node.right, successor_node.key)

            return node, True

        self.root, deleted = remove(self.root, key)

        if deleted:
            self._size -= 1

        return deleted

    def validate(self) -> bool:
        """Validate the entire tree, including strict ordering and cycles."""
        visited = set()
        count = 0
        stack = [(self.root, None, None)]

        while stack:
            node, lower, upper = stack.pop()

            if node is None:
                continue

            identity = id(node)

            if identity in visited:
                return False

            visited.add(identity)
            count += 1

            if lower is not None and node.key <= lower:
                return False

            if upper is not None and node.key >= upper:
                return False

            stack.append((node.right, node.key, upper))
            stack.append((node.left, lower, node.key))

        return count == self._size

    @classmethod
    def from_sorted(cls, values: Iterable[int]) -> BinarySearchTree:
        """Construct a height-balanced BST from strictly increasing values."""
        data = list(values)

        for value in data:
            cls._validate_key(value)

        if any(data[i] >= data[i + 1] for i in range(len(data) - 1)):
            raise ValueError("Input must be strictly increasing.")

        tree = cls()

        def build(left: int, right: int) -> Optional[Node]:
            if left > right:
                return None

            middle = (left + right) // 2
            node = Node(data[middle])
            node.left = build(left, middle - 1)
            node.right = build(middle + 1, right)
            return node

        tree.root = build(0, len(data) - 1)
        tree._size = len(data)

        return tree

    def height(self) -> int:
        """Calculate tree height iteratively."""
        if self.root is None:
            return 0

        maximum_depth = 0
        queue = deque([(self.root, 1)])

        while queue:
            node, depth = queue.popleft()
            maximum_depth = max(maximum_depth, depth)

            if node.left:
                queue.append((node.left, depth + 1))
            if node.right:
                queue.append((node.right, depth + 1))

        return maximum_depth

    def clear(self) -> None:
        self.root = None
        self._size = 0

    def display(self) -> None:
        print("Inorder:    ", self.inorder())
        print("Preorder:   ", self.preorder())
        print("Postorder:  ", self.postorder())
        print("Level order:", self.level_order())


def run_tests() -> None:
    tree = BinarySearchTree()
    tree.insert_many([50, 30, 70, 20, 40, 60, 80])

    assert tree.validate()
    assert tree.inorder() == [20, 30, 40, 50, 60, 70, 80]
    assert tree.minimum() == 20
    assert tree.maximum() == 80
    assert tree.floor(45) == 40
    assert tree.floor(15) is None
    assert tree.ceiling(45) == 50
    assert tree.ceiling(85) is None
    assert tree.range_query(30, 70) == [30, 40, 50, 60, 70]
    assert tree.successor(50) == 60
    assert tree.predecessor(50) == 40
    assert tree.search(60).key == 60
    assert tree.search(999) is None

    try:
        tree.insert(50)
        raise AssertionError("Duplicate insertion should fail.")
    except DuplicateKeyError:
        pass

    assert tree.delete(20)
    assert tree.validate()
    assert tree.delete(30)
    assert tree.validate()
    assert tree.delete(50)
    assert tree.validate()
    assert tree.inorder() == [40, 60, 70, 80]
    assert not tree.delete(999)

    balanced = BinarySearchTree.from_sorted(range(1, 16))
    assert balanced.validate()
    assert balanced.inorder() == list(range(1, 16))
    assert balanced.height() == 4

    try:
        BinarySearchTree.from_sorted([1, 3, 2])
        raise AssertionError("Unsorted input should fail.")
    except ValueError:
        pass

    empty = BinarySearchTree()
    assert empty.inorder() == []
    assert empty.validate()

    try:
        empty.minimum()
        raise AssertionError("Empty minimum should fail.")
    except EmptyTreeError:
        pass

    try:
        tree.insert(True)
        raise AssertionError("Boolean keys should fail.")
    except TypeError:
        pass

    print("All BST tests passed.")


def performance_demo() -> None:
    values = list(range(1, 10001))

    random_tree = BinarySearchTree()
    shuffled = values.copy()
    random.Random(42).shuffle(shuffled)

    start = time.perf_counter()
    random_tree.insert_many(shuffled)
    random_insert_time = time.perf_counter() - start

    balanced_tree = BinarySearchTree.from_sorted(values)

    print("\nPerformance comparison")
    print(f"Random insertion height: {random_tree.height()}")
    print(f"Balanced construction height: {balanced_tree.height()}")
    print(f"Random insertion time: {random_insert_time:.6f}s")
    print(f"Random tree valid: {random_tree.validate()}")
    print(f"Balanced tree valid: {balanced_tree.validate()}")


def main() -> None:
    print("BST Traversal and Validation")
    print("=" * 40)

    tree = BinarySearchTree()
    tree.insert_many([50, 30, 70, 20, 40, 60, 80])

    tree.display()

    print("\nMinimum:", tree.minimum())
    print("Maximum:", tree.maximum())
    print("Search 60:", tree.search(60) is not None)
    print("Floor of 45:", tree.floor(45))
    print("Ceiling of 45:", tree.ceiling(45))
    print("Range [30, 70]:", tree.range_query(30, 70))
    print("Successor of 50:", tree.successor(50))
    print("Predecessor of 50:", tree.predecessor(50))
    print("Height:", tree.height())
    print("Valid BST:", tree.validate())

    print("\nDeleting 50")
    tree.delete(50)
    print("Inorder after deletion:", tree.inorder())
    print("Valid after deletion:", tree.validate())

    run_tests()
    performance_demo()


if __name__ == "__main__":
    main()
