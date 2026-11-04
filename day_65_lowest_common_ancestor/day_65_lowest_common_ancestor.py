from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TreeNode:
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None
    parent: Optional["TreeNode"] = field(default=None, repr=False)


class BinaryTree:
    """Binary tree with validated node ownership and multiple LCA algorithms."""

    def __init__(self) -> None:
        self.root: Optional[TreeNode] = None
        self.nodes: dict[int, TreeNode] = {}

    def add_root(self, value: int) -> TreeNode:
        if self.root is not None:
            raise ValueError("Root already exists.")
        if value in self.nodes:
            raise ValueError("Duplicate node value.")

        self.root = TreeNode(value)
        self.nodes[value] = self.root
        return self.root

    def add_child(self, parent_value: int, child_value: int,
                  side: str) -> TreeNode:
        if parent_value not in self.nodes:
            raise ValueError("Parent does not exist.")
        if child_value in self.nodes:
            raise ValueError("Duplicate node value.")
        if side not in ("left", "right"):
            raise ValueError("Side must be 'left' or 'right'.")

        parent = self.nodes[parent_value]

        if getattr(parent, side) is not None:
            raise ValueError(f"{side} child already exists.")

        child = TreeNode(child_value, parent=parent)
        setattr(parent, side, child)
        self.nodes[child_value] = child
        return child

    def get_node(self, value: int) -> TreeNode:
        if value not in self.nodes:
            raise ValueError(f"Node {value} does not exist.")
        return self.nodes[value]

    def recursive_lca(self, p: int, q: int) -> Optional[int]:
        """Recursive LCA using subtree presence information."""
        first = self.get_node(p)
        second = self.get_node(q)

        def solve(node: Optional[TreeNode]) -> Optional[TreeNode]:
            if node is None or node is first or node is second:
                return node

            left = solve(node.left)
            right = solve(node.right)

            if left is not None and right is not None:
                return node

            return left if left is not None else right

        candidate = solve(self.root)

        # Standard recursive LCA must verify that both nodes exist.
        if candidate is None:
            return None

        found: set[int] = set()

        def collect(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            if node is first or node is second:
                found.add(node.value)
            collect(node.left)
            collect(node.right)

        collect(self.root)

        if len(found) != 2:
            return None

        return candidate.value

    def parent_pointer_lca(self, p: int, q: int) -> int:
        """Find LCA using parent pointers and a visited set."""
        first = self.get_node(p)
        second = self.get_node(q)

        ancestors: set[int] = set()
        current: Optional[TreeNode] = first

        while current is not None:
            ancestors.add(current.value)
            current = current.parent

        current = second

        while current is not None:
            if current.value in ancestors:
                return current.value
            current = current.parent

        raise RuntimeError("Nodes do not belong to the same tree.")

    def depth(self, value: int) -> int:
        node = self.get_node(value)
        result = 0

        while node.parent is not None:
            result += 1
            node = node.parent

        return result

    def depth_lca(self, p: int, q: int) -> int:
        """Align depths before moving both nodes upward."""
        first = self.get_node(p)
        second = self.get_node(q)

        depth_first = self.depth(p)
        depth_second = self.depth(q)

        while depth_first > depth_second:
            first = first.parent
            depth_first -= 1

        while depth_second > depth_first:
            second = second.parent
            depth_second -= 1

        while first is not second:
            first = first.parent
            second = second.parent

        if first is None:
            raise RuntimeError("No common ancestor exists.")

        return first.value

    def ancestors(self, value: int) -> list[int]:
        current: Optional[TreeNode] = self.get_node(value)
        result = []

        while current is not None:
            result.append(current.value)
            current = current.parent

        return result

    def distance(self, p: int, q: int) -> int:
        ancestor = self.get_node(self.parent_pointer_lca(p, q))
        first = self.get_node(p)
        second = self.get_node(q)

        def distance_to(node: TreeNode) -> int:
            distance = 0
            while node is not ancestor:
                node = node.parent
                distance += 1
            return distance

        return distance_to(first) + distance_to(second)

    def is_ancestor(self, ancestor: int, descendant: int) -> bool:
        current: Optional[TreeNode] = self.get_node(descendant)
        target = self.get_node(ancestor)

        while current is not None:
            if current is target:
                return True
            current = current.parent

        return False

    def kth_ancestor(self, value: int, k: int) -> Optional[int]:
        if k < 0:
            raise ValueError("k cannot be negative.")

        current: Optional[TreeNode] = self.get_node(value)

        for _ in range(k):
            if current is None:
                return None
            current = current.parent

        return current.value if current else None

    def build_binary_lifting(self) -> "BinaryLifting":
        return BinaryLifting(self)


class BinaryLifting:
    """
    O(N log N) preprocessing.
    O(log N) kth ancestor and LCA queries.
    """

    def __init__(self, tree: BinaryTree) -> None:
        if tree.root is None:
            raise ValueError("Cannot preprocess an empty tree.")

        self.tree = tree
        self.n = len(tree.nodes)
        self.levels = max(1, self.n.bit_length())

        self.depths: dict[int, int] = {}
        self.up: dict[int, list[Optional[int]]] = {}

        queue = deque([(tree.root, 0, None)])

        while queue:
            node, depth, parent = queue.popleft()

            self.depths[node.value] = depth
            self.up[node.value] = [parent] + [None] * (self.levels - 1)

            if node.left:
                queue.append((node.left, depth + 1, node.value))

            if node.right:
                queue.append((node.right, depth + 1, node.value))

        for j in range(1, self.levels):
            for value in self.tree.nodes:
                previous = self.up[value][j - 1]

                if previous is not None:
                    self.up[value][j] = self.up[previous][j - 1]

    def kth_ancestor(self, value: int, k: int) -> Optional[int]:
        if value not in self.up:
            raise ValueError("Unknown node.")
        if k < 0:
            raise ValueError("k cannot be negative.")

        if k > self.depths[value]:
            return None

        bit = 0

        while k:
            if k & 1:
                value = self.up[value][bit]
                if value is None:
                    return None

            k >>= 1
            bit += 1

        return value

    def lca(self, p: int, q: int) -> int:
        if p not in self.up or q not in self.up:
            raise ValueError("Both nodes must exist in the tree.")

        if self.depths[p] < self.depths[q]:
            p, q = q, p

        p = self.kth_ancestor(p, self.depths[p] - self.depths[q])

        if p == q:
            return p

        for j in range(self.levels - 1, -1, -1):
            first = self.up[p][j]
            second = self.up[q][j]

            if first != second:
                p = first
                q = second

        ancestor = self.up[p][0]

        if ancestor is None:
            raise RuntimeError("No common ancestor exists.")

        return ancestor

    def distance(self, p: int, q: int) -> int:
        ancestor = self.lca(p, q)

        return (
            self.depths[p]
            + self.depths[q]
            - 2 * self.depths[ancestor]
        )


def build_sample_tree() -> BinaryTree:
    tree = BinaryTree()

    tree.add_root(1)

    tree.add_child(1, 2, "left")
    tree.add_child(1, 3, "right")

    tree.add_child(2, 4, "left")
    tree.add_child(2, 5, "right")

    tree.add_child(3, 6, "left")
    tree.add_child(3, 7, "right")

    tree.add_child(4, 8, "left")
    tree.add_child(4, 9, "right")

    tree.add_child(5, 10, "left")

    return tree


def run_tests() -> None:
    tree = build_sample_tree()
    lifting = tree.build_binary_lifting()

    assert tree.recursive_lca(8, 9) == 4
    assert tree.recursive_lca(8, 10) == 2
    assert tree.recursive_lca(8, 6) == 1
    assert tree.recursive_lca(2, 8) == 2
    assert tree.recursive_lca(7, 7) == 7

    assert tree.parent_pointer_lca(8, 10) == 2
    assert tree.depth_lca(8, 6) == 1

    assert lifting.lca(8, 10) == 2
    assert lifting.lca(8, 6) == 1
    assert lifting.lca(5, 10) == 5

    assert tree.distance(8, 10) == 4
    assert lifting.distance(8, 6) == 5

    assert tree.is_ancestor(2, 8)
    assert not tree.is_ancestor(3, 8)

    assert tree.kth_ancestor(8, 2) == 2
    assert lifting.kth_ancestor(8, 3) == 1
    assert lifting.kth_ancestor(8, 4) is None

    assert tree.recursive_lca(8, 999) is None

    try:
        tree.get_node(999)
    except ValueError:
        pass
    else:
        raise AssertionError("Missing-node validation failed.")

    try:
        tree.add_child(1, 11, "middle")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid-side validation failed.")

    print("All Lowest Common Ancestor tests passed.")


def main() -> None:
    tree = build_sample_tree()
    lifting = tree.build_binary_lifting()

    print("LOWEST COMMON ANCESTOR")

    queries = [(8, 9), (8, 10), (8, 6), (5, 10), (2, 8)]

    for p, q in queries:
        print(
            f"Nodes: {p}, {q} | "
            f"Recursive LCA: {tree.recursive_lca(p, q)} | "
            f"Parent LCA: {tree.parent_pointer_lca(p, q)} | "
            f"Binary Lifting LCA: {lifting.lca(p, q)}"
        )

    print("\nAncestor chain of node 8:", tree.ancestors(8))
    print("Distance between 8 and 10:", lifting.distance(8, 10))
    print("3rd ancestor of 8:", lifting.kth_ancestor(8, 3))
    print("Is 2 an ancestor of 8:", tree.is_ancestor(2, 8))

    run_tests()


if __name__ == "__main__":
    main()
