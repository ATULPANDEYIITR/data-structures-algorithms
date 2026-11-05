from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable


@dataclass
class Node:
    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None


class BinarySearchTree:
    """
    Binary Search Tree with unique integer keys.

    Ordering invariant:
        Every key in the left subtree is smaller than the node key.
        Every key in the right subtree is greater than the node key.

    Duplicate keys are rejected.
    """

    def __init__(self):
        self.root: Optional[Node] = None
        self.size = 0

    @staticmethod
    def _validate_key(key: int) -> None:
        if isinstance(key, bool) or not isinstance(key, int):
            raise TypeError("BST keys must be integers.")

    def insert(self, key: int) -> bool:
        self._validate_key(key)

        new_node = Node(key)

        if self.root is None:
            self.root = new_node
            self.size += 1
            return True

        current = self.root

        while True:
            if key == current.key:
                return False

            if key < current.key:
                if current.left is None:
                    current.left = new_node
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    break
                current = current.right

        self.size += 1
        return True

    def search(self, key: int) -> Optional[Node]:
        self._validate_key(key)

        current = self.root

        while current is not None:
            if key == current.key:
                return current

            if key < current.key:
                current = current.left
            else:
                current = current.right

        return None

    def contains(self, key: int) -> bool:
        return self.search(key) is not None

    def find_minimum(self, node: Optional[Node] = None) -> Optional[Node]:
        current = self.root if node is None else node

        if current is None:
            return None

        while current.left is not None:
            current = current.left

        return current

    def find_maximum(self, node: Optional[Node] = None) -> Optional[Node]:
        current = self.root if node is None else node

        if current is None:
            return None

        while current.right is not None:
            current = current.right

        return current

    def predecessor(self, key: int) -> Optional[int]:
        """
        Return the greatest key smaller than the supplied key.

        The key does not need to exist in the tree.
        """
        self._validate_key(key)

        current = self.root
        candidate = None

        while current is not None:
            if current.key < key:
                candidate = current.key
                current = current.right
            else:
                current = current.left

        return candidate

    def successor(self, key: int) -> Optional[int]:
        """
        Return the smallest key greater than the supplied key.

        The key does not need to exist in the tree.
        """
        self._validate_key(key)

        current = self.root
        candidate = None

        while current is not None:
            if current.key > key:
                candidate = current.key
                current = current.left
            else:
                current = current.right

        return candidate

    def delete(self, key: int) -> bool:
        self._validate_key(key)

        parent = None
        current = self.root

        while current is not None and current.key != key:
            parent = current

            if key < current.key:
                current = current.left
            else:
                current = current.right

        if current is None:
            return False

        # A node with two children is replaced by its inorder successor.
        if current.left is not None and current.right is not None:
            successor_parent = current
            successor_node = current.right

            while successor_node.left is not None:
                successor_parent = successor_node
                successor_node = successor_node.left

            current.key = successor_node.key
            parent = successor_parent
            current = successor_node

        # The node now has at most one child.
        child = current.left if current.left is not None else current.right

        if parent is None:
            self.root = child
        elif parent.left is current:
            parent.left = child
        else:
            parent.right = child

        self.size -= 1
        return True

    def inorder(self) -> list[int]:
        result = []
        stack = []
        current = self.root

        while stack or current is not None:
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

            if node.right is not None:
                stack.append(node.right)

            if node.left is not None:
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

                if node.right is not None:
                    stack.append((node.right, False))

                if node.left is not None:
                    stack.append((node.left, False))

        return result

    def level_order(self) -> list[int]:
        if self.root is None:
            return []

        result = []
        queue = [self.root]
        index = 0

        while index < len(queue):
            node = queue[index]
            index += 1

            result.append(node.key)

            if node.left is not None:
                queue.append(node.left)

            if node.right is not None:
                queue.append(node.right)

        return result

    def height(self) -> int:
        if self.root is None:
            return 0

        stack = [(self.root, 1)]
        maximum = 0

        while stack:
            node, depth = stack.pop()
            maximum = max(maximum, depth)

            if node.left is not None:
                stack.append((node.left, depth + 1))

            if node.right is not None:
                stack.append((node.right, depth + 1))

        return maximum

    def validate(self) -> bool:
        """Verify the complete BST ordering invariant."""
        if self.root is None:
            return self.size == 0

        stack = [(self.root, None, None)]
        count = 0

        while stack:
            node, lower, upper = stack.pop()
            count += 1

            if lower is not None and node.key <= lower:
                return False

            if upper is not None and node.key >= upper:
                return False

            if node.left is not None:
                stack.append((node.left, lower, node.key))

            if node.right is not None:
                stack.append((node.right, node.key, upper))

        return count == self.size

    def range_search(self, low: int, high: int) -> list[int]:
        self._validate_key(low)
        self._validate_key(high)

        if low > high:
            raise ValueError("Lower bound cannot exceed upper bound.")

        result = []
        stack = []
        current = self.root

        while stack or current is not None:
            while current is not None:
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

    def clear(self) -> None:
        self.root = None
        self.size = 0


def run_tests() -> None:
    tree = BinarySearchTree()

    values = [50, 30, 70, 20, 40, 60, 80, 35, 45, 65]

    for value in values:
        assert tree.insert(value)

    assert not tree.insert(50)
    assert tree.size == 10
    assert tree.validate()

    assert tree.contains(40)
    assert not tree.contains(99)

    assert tree.inorder() == [20, 30, 35, 40, 45, 50, 60, 65, 70, 80]

    assert tree.predecessor(50) == 45
    assert tree.successor(50) == 60
    assert tree.predecessor(35) == 30
    assert tree.successor(65) == 70
    assert tree.predecessor(10) is None
    assert tree.successor(100) is None

    assert tree.range_search(35, 65) == [35, 40, 45, 50, 60, 65]

    # Delete a leaf.
    assert tree.delete(20)
    assert not tree.contains(20)
    assert tree.validate()

    # Delete a node with one child.
    assert tree.delete(30)
    assert tree.validate()

    # Delete a node with two children.
    assert tree.delete(70)
    assert tree.validate()

    # Delete the root.
    assert tree.delete(50)
    assert tree.validate()

    # Missing-key deletion.
    assert not tree.delete(999)

    # Empty tree.
    empty = BinarySearchTree()
    assert empty.inorder() == []
    assert empty.height() == 0
    assert not empty.delete(10)

    # Invalid keys.
    for invalid in ("50", 3.5, True):
        try:
            tree.insert(invalid)
            raise AssertionError("Invalid key was accepted.")
        except TypeError:
            pass

    print("All BST tests passed.")


def demonstrate() -> None:
    tree = BinarySearchTree()

    for key in [50, 30, 70, 20, 40, 60, 80]:
        tree.insert(key)

    print("\nBINARY SEARCH TREE DEMONSTRATION")
    print("Inorder:     ", tree.inorder())
    print("Preorder:    ", tree.preorder())
    print("Postorder:   ", tree.postorder())
    print("Level order: ", tree.level_order())
    print("Minimum:     ", tree.find_minimum().key)
    print("Maximum:     ", tree.find_maximum().key)
    print("Search 40:   ", tree.contains(40))
    print("Predecessor: ", tree.predecessor(50))
    print("Successor:   ", tree.successor(50))
    print("Range 30-70: ", tree.range_search(30, 70))
    print("Height:      ", tree.height())

    print("\nDeleting 50...")
    tree.delete(50)

    print("Inorder after deletion:", tree.inorder())
    print("BST invariant valid:", tree.validate())


if __name__ == "__main__":
    run_tests()
    demonstrate()
