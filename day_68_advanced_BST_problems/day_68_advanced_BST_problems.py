from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable
import random


class BSTError(Exception):
    """Base exception for BST operations."""


class InvalidBSTError(BSTError):
    pass


class InvalidKError(BSTError):
    pass


@dataclass
class Node:
    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None


@dataclass
class DoublyLinkedNode:
    key: int
    prev: Optional["DoublyLinkedNode"] = None
    next: Optional["DoublyLinkedNode"] = None


@dataclass
class ConversionResult:
    head: Optional[DoublyLinkedNode]
    tail: Optional[DoublyLinkedNode]
    size: int


class BinarySearchTree:
    """
    Integer BST with unique keys.

    Invariant:
        Every key in the left subtree is smaller.
        Every key in the right subtree is larger.
    """

    def __init__(self, values: Iterable[int] = ()):
        self.root: Optional[Node] = None
        self._size = 0
        for value in values:
            self.insert(value)

    @staticmethod
    def _validate_key(key: int) -> None:
        if isinstance(key, bool) or not isinstance(key, int):
            raise TypeError("BST keys must be integers.")

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    def insert(self, key: int) -> bool:
        self._validate_key(key)

        if self.root is None:
            self.root = Node(key)
            self._size = 1
            return True

        current = self.root

        while True:
            if key == current.key:
                return False

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
        return True

    def search(self, key: int) -> bool:
        self._validate_key(key)
        current = self.root

        while current is not None:
            if key == current.key:
                return True
            current = current.left if key < current.key else current.right

        return False

    def minimum(self, node: Optional[Node] = None) -> int:
        current = self.root if node is None else node

        if current is None:
            raise BSTError("Cannot find minimum in an empty tree.")

        while current.left is not None:
            current = current.left

        return current.key

    def maximum(self, node: Optional[Node] = None) -> int:
        current = self.root if node is None else node

        if current is None:
            raise BSTError("Cannot find maximum in an empty tree.")

        while current.right is not None:
            current = current.right

        return current.key

    def delete(self, key: int) -> bool:
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

            # Replace a two-child node with its inorder successor.
            successor = node.right
            while successor.left is not None:
                successor = successor.left

            node.key = successor.key
            node.right, _ = remove(node.right, successor.key)
            return node, True

        self.root, deleted = remove(self.root, key)

        if deleted:
            self._size -= 1

        return deleted

    def inorder(self) -> list[int]:
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
        result = []

        def visit(node):
            if node is None:
                return
            visit(node.left)
            visit(node.right)
            result.append(node.key)

        visit(self.root)
        return result

    def kth_smallest(self, k: int) -> int:
        if isinstance(k, bool) or not isinstance(k, int):
            raise InvalidKError("k must be an integer.")

        if not 1 <= k <= self._size:
            raise InvalidKError(
                f"k must be between 1 and {self._size}."
            )

        # Inorder traversal visits BST keys in ascending order.
        stack = []
        current = self.root
        count = 0

        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()
            count += 1

            if count == k:
                return current.key

            current = current.right

        raise BSTError("Unexpected traversal failure.")

    def kth_largest(self, k: int) -> int:
        if isinstance(k, bool) or not isinstance(k, int):
            raise InvalidKError("k must be an integer.")

        if not 1 <= k <= self._size:
            raise InvalidKError("k is outside the valid range.")

        stack = []
        current = self.root
        count = 0

        # Reverse inorder traversal visits keys in descending order.
        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.right

            current = stack.pop()
            count += 1

            if count == k:
                return current.key

            current = current.left

        raise BSTError("Unexpected traversal failure.")

    def lowest_common_ancestor(self, first: int, second: int) -> int:
        self._validate_key(first)
        self._validate_key(second)

        if not self.search(first) or not self.search(second):
            raise BSTError("Both keys must exist in the BST.")

        current = self.root

        while current is not None:
            if first < current.key and second < current.key:
                current = current.left
            elif first > current.key and second > current.key:
                current = current.right
            else:
                return current.key

        raise BSTError("LCA could not be determined.")

    def height(self) -> int:
        if self.root is None:
            return 0

        stack = [(self.root, 1)]
        maximum_height = 0

        while stack:
            node, depth = stack.pop()
            maximum_height = max(maximum_height, depth)

            if node.left:
                stack.append((node.left, depth + 1))
            if node.right:
                stack.append((node.right, depth + 1))

        return maximum_height

    def is_balanced(self) -> bool:
        def check(node):
            if node is None:
                return 0

            left_height = check(node.left)
            if left_height == -1:
                return -1

            right_height = check(node.right)
            if right_height == -1:
                return -1

            if abs(left_height - right_height) > 1:
                return -1

            return 1 + max(left_height, right_height)

        return check(self.root) != -1

    def validate(self) -> bool:
        """Check ordering, uniqueness, and node count."""

        def check(node, lower, upper):
            if node is None:
                return 0

            if lower is not None and node.key <= lower:
                raise InvalidBSTError("BST lower-bound violation.")

            if upper is not None and node.key >= upper:
                raise InvalidBSTError("BST upper-bound violation.")

            return (
                1
                + check(node.left, lower, node.key)
                + check(node.right, node.key, upper)
            )

        actual_count = check(self.root, None, None)

        if actual_count != self._size:
            raise InvalidBSTError("Stored size does not match node count.")

        return True

    @classmethod
    def from_sorted(cls, values: Iterable[int]) -> "BinarySearchTree":
        """Construct a height-balanced BST from strictly increasing keys."""

        data = list(values)

        for value in data:
            cls._validate_key(value)

        if any(data[i] >= data[i + 1] for i in range(len(data) - 1)):
            raise ValueError("Input must be strictly increasing.")

        tree = cls()

        def build(start, end):
            if start > end:
                return None

            middle = (start + end) // 2
            node = Node(data[middle])

            node.left = build(start, middle - 1)
            node.right = build(middle + 1, end)

            return node

        tree.root = build(0, len(data) - 1)
        tree._size = len(data)
        return tree

    def rebalance(self) -> None:
        """Rebuild the tree while preserving all keys."""
        sorted_keys = self.inorder()
        rebuilt = self.from_sorted(sorted_keys)
        self.root = rebuilt.root
        self._size = rebuilt._size

    def to_doubly_linked_list(self) -> ConversionResult:
        """
        Convert the BST into an inorder doubly linked list.

        This creates new list nodes and does not modify the BST.
        """
        head = None
        tail = None
        count = 0

        def convert(node):
            nonlocal head, tail, count

            if node is None:
                return

            convert(node.left)

            linked = DoublyLinkedNode(node.key)

            if tail is None:
                head = linked
            else:
                tail.next = linked
                linked.prev = tail

            tail = linked
            count += 1

            convert(node.right)

        convert(self.root)
        return ConversionResult(head, tail, count)

    @staticmethod
    def list_values(result: ConversionResult) -> list[int]:
        values = []
        current = result.head

        while current is not None:
            values.append(current.key)
            current = current.next

        return values

    @staticmethod
    def from_preorder(values: Iterable[int]) -> "BinarySearchTree":
        """Construct a BST from a valid preorder traversal in O(n)."""
        data = list(values)

        for value in data:
            BinarySearchTree._validate_key(value)

        if len(set(data)) != len(data):
            raise ValueError("Preorder keys must be unique.")

        index = 0

        def build(lower, upper):
            nonlocal index

            if index >= len(data):
                return None

            value = data[index]

            if value <= lower or value >= upper:
                return None

            index += 1
            node = Node(value)
            node.left = build(lower, value)
            node.right = build(value, upper)

            return node

        tree = BinarySearchTree()
        tree.root = build(float("-inf"), float("inf"))

        if index != len(data):
            raise ValueError("Invalid BST preorder traversal.")

        tree._size = len(data)
        return tree

    def range_search(self, low: int, high: int) -> list[int]:
        self._validate_key(low)
        self._validate_key(high)

        if low > high:
            raise ValueError("Lower bound cannot exceed upper bound.")

        result = []

        def visit(node):
            if node is None:
                return

            if node.key > low:
                visit(node.left)

            if low <= node.key <= high:
                result.append(node.key)

            if node.key < high:
                visit(node.right)

        visit(self.root)
        return result

    def statistics(self) -> dict:
        return {
            "size": self._size,
            "height": self.height(),
            "balanced": self.is_balanced(),
            "minimum": self.minimum() if self.root else None,
            "maximum": self.maximum() if self.root else None,
            "valid": self.validate(),
        }


def run_tests():
    tree = BinarySearchTree([50, 30, 70, 20, 40, 60, 80])

    assert tree.validate()
    assert tree.inorder() == [20, 30, 40, 50, 60, 70, 80]
    assert tree.preorder() == [50, 30, 20, 40, 70, 60, 80]
    assert tree.kth_smallest(1) == 20
    assert tree.kth_smallest(4) == 50
    assert tree.kth_largest(1) == 80
    assert tree.lowest_common_ancestor(20, 40) == 30
    assert tree.lowest_common_ancestor(20, 80) == 50
    assert tree.range_search(30, 70) == [30, 40, 50, 60, 70]

    assert tree.insert(90)
    assert not tree.insert(50)
    assert tree.search(90)
    assert tree.delete(70)
    assert not tree.search(70)
    assert tree.validate()

    linked = tree.to_doubly_linked_list()
    assert BinarySearchTree.list_values(linked) == tree.inorder()
    assert linked.head.prev is None
    assert linked.tail.next is None

    sorted_tree = BinarySearchTree.from_sorted(range(1, 16))
    assert sorted_tree.inorder() == list(range(1, 16))
    assert sorted_tree.is_balanced()

    preorder_tree = BinarySearchTree.from_preorder(
        [50, 30, 20, 40, 70, 60, 80]
    )
    assert preorder_tree.inorder() == tree.inorder()[:]
    # The previous tree has 70 deleted, so compare its original counterpart.
    assert preorder_tree.inorder() == [20, 30, 40, 50, 60, 70, 80]

    skewed = BinarySearchTree(range(1, 101))
    assert not skewed.is_balanced()
    assert skewed.height() == 100

    skewed.rebalance()
    assert skewed.is_balanced()
    assert skewed.height() <= 7
    assert skewed.inorder() == list(range(1, 101))

    empty = BinarySearchTree()
    assert empty.inorder() == []
    assert empty.height() == 0
    assert empty.is_balanced()
    assert empty.delete(10) is False

    for invalid_k in (0, 101, 1.5, True):
        try:
            sorted_tree.kth_smallest(invalid_k)
            raise AssertionError("Invalid k was accepted.")
        except InvalidKError:
            pass

    for invalid_input in ([1, 2, 2, 3], [3, 1, 2]):
        try:
            BinarySearchTree.from_sorted(invalid_input)
            raise AssertionError("Invalid sorted input was accepted.")
        except ValueError:
            pass

    try:
        BinarySearchTree.from_preorder([10, 5, 12, 4])
        raise AssertionError("Invalid preorder was accepted.")
    except ValueError:
        pass

    print("All BST tests passed.")


def demonstration():
    print("\nADVANCED BINARY SEARCH TREE")

    tree = BinarySearchTree([50, 30, 70, 20, 40, 60, 80])

    print("Inorder:", tree.inorder())
    print("Preorder:", tree.preorder())
    print("Postorder:", tree.postorder())

    print("3rd smallest:", tree.kth_smallest(3))
    print("2nd largest:", tree.kth_largest(2))
    print("LCA of 20 and 40:", tree.lowest_common_ancestor(20, 40))

    print("Tree statistics:", tree.statistics())

    linked = tree.to_doubly_linked_list()
    print("Doubly linked list:", BinarySearchTree.list_values(linked))

    print("\nCreating an unbalanced tree...")
    unbalanced = BinarySearchTree(range(1, 16))
    print("Before:", unbalanced.statistics())

    unbalanced.rebalance()
    print("After:", unbalanced.statistics())

    print("\nBuilding a BST from sorted data...")
    balanced = BinarySearchTree.from_sorted([10, 20, 30, 40, 50, 60, 70])
    print("Balanced preorder:", balanced.preorder())


if __name__ == "__main__":
    run_tests()
    demonstration()
