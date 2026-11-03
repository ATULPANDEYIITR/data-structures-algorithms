from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(eq=False, slots=True)
class TreeNode:
    """A binary-tree node containing an integer value."""

    value: int
    left: Optional[TreeNode] = None
    right: Optional[TreeNode] = None


@dataclass(frozen=True, slots=True)
class TreeMetrics:
    max_depth: int
    min_depth: int
    has_path_sum: bool
    diameter_edges: int
    balanced: bool
    node_count: int


def _require_integer(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Every node value must be an integer, not a boolean.")
    return value


def validate_tree(root: Optional[TreeNode]) -> int:
    """
    Validate node types, values, and tree ownership.

    A node cannot be visited twice. This rejects both cycles and nodes
    shared by multiple parents.
    """
    if root is None:
        return 0

    stack = [root]
    visited: set[int] = set()

    while stack:
        node = stack.pop()

        if not isinstance(node, TreeNode):
            raise TypeError("Every child must be a TreeNode or None.")

        identity = id(node)
        if identity in visited:
            raise ValueError("The structure contains a cycle or shared node.")

        visited.add(identity)
        _require_integer(node.value)

        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)

    return len(visited)


def from_level_order(values: Iterable[Optional[int]]) -> Optional[TreeNode]:
    """
    Build a tree from level-order values.

    None represents a missing child. Non-None values after all possible
    parents have been consumed are rejected.
    """
    items = list(values)

    if not items:
        return None

    if items[0] is None:
        if any(value is not None for value in items[1:]):
            raise ValueError("A non-empty tree must have a root.")
        return None

    root = TreeNode(_require_integer(items[0]))
    parents = deque([root])
    index = 1

    while parents and index < len(items):
        parent = parents.popleft()

        if index < len(items):
            value = items[index]
            index += 1

            if value is not None:
                parent.left = TreeNode(_require_integer(value))
                parents.append(parent.left)

        if index < len(items):
            value = items[index]
            index += 1

            if value is not None:
                parent.right = TreeNode(_require_integer(value))
                parents.append(parent.right)

    if any(value is not None for value in items[index:]):
        raise ValueError("Level-order input contains unreachable nodes.")

    return root


def max_depth(root: Optional[TreeNode]) -> int:
    """Return the maximum number of nodes on a root-to-leaf path."""
    validate_tree(root)

    if root is None:
        return 0

    queue = deque([(root, 1)])
    maximum = 0

    while queue:
        node, depth = queue.popleft()
        maximum = max(maximum, depth)

        if node.left is not None:
            queue.append((node.left, depth + 1))
        if node.right is not None:
            queue.append((node.right, depth + 1))

    return maximum


def min_depth(root: Optional[TreeNode]) -> int:
    """
    Return the minimum number of nodes on a root-to-leaf path.

    BFS stops at the first actual leaf. A missing child does not
    automatically make a node a leaf.
    """
    validate_tree(root)

    if root is None:
        return 0

    queue = deque([(root, 1)])

    while queue:
        node, depth = queue.popleft()

        if node.left is None and node.right is None:
            return depth

        if node.left is not None:
            queue.append((node.left, depth + 1))
        if node.right is not None:
            queue.append((node.right, depth + 1))

    return 0


def has_path_sum(root: Optional[TreeNode], target_sum: int) -> bool:
    """Check whether a root-to-leaf path has the requested sum."""
    validate_tree(root)
    target_sum = _require_integer(target_sum)

    if root is None:
        return False

    stack = [(root, 0)]

    while stack:
        node, accumulated = stack.pop()
        current_sum = accumulated + node.value

        if node.left is None and node.right is None:
            if current_sum == target_sum:
                return True
            continue

        if node.right is not None:
            stack.append((node.right, current_sum))
        if node.left is not None:
            stack.append((node.left, current_sum))

    return False


def diameter(root: Optional[TreeNode]) -> int:
    """
    Return the tree diameter measured in edges.

    The diameter is the longest path between any two nodes. It does
    not have to pass through the root.
    """
    validate_tree(root)

    if root is None:
        return 0

    heights: dict[int, int] = {}
    stack = [(root, False)]

    while stack:
        node, expanded = stack.pop()

        if not expanded:
            stack.append((node, True))

            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
        else:
            left_height = heights.get(id(node.left), 0)
            right_height = heights.get(id(node.right), 0)
            heights[id(node)] = 1 + max(left_height, right_height)

    longest = 0
    for node_id, height in heights.items():
        # The maximum is computed in the separate postorder implementation
        # below so no references to nodes need to be retained in this map.
        pass

    node_metrics: dict[int, tuple[int, int]] = {}
    stack = [(root, False)]

    while stack:
        node, expanded = stack.pop()

        if not expanded:
            stack.append((node, True))

            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
        else:
            left_height, left_diameter = node_metrics.get(id(node.left), (0, 0))
            right_height, right_diameter = node_metrics.get(id(node.right), (0, 0))

            height = 1 + max(left_height, right_height)
            longest = max(
                left_height + right_height,
                left_diameter,
                right_diameter,
                longest,
            )
            node_metrics[id(node)] = (
                height,
                max(left_height + right_height, left_diameter, right_diameter),
            )

    return longest


def is_balanced(root: Optional[TreeNode]) -> bool:
    """
    Determine whether every node has left and right subtree heights
    differing by no more than one.
    """
    validate_tree(root)

    if root is None:
        return True

    results: dict[int, tuple[int, bool]] = {}
    stack = [(root, False)]

    while stack:
        node, expanded = stack.pop()

        if not expanded:
            stack.append((node, True))

            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
        else:
            left_height, left_balanced = results.get(id(node.left), (0, True))
            right_height, right_balanced = results.get(id(node.right), (0, True))

            balanced = (
                left_balanced
                and right_balanced
                and abs(left_height - right_height) <= 1
            )
            results[id(node)] = (1 + max(left_height, right_height), balanced)

    return results[id(root)][1]


def count_nodes(root: Optional[TreeNode]) -> int:
    """Count nodes in any valid binary tree."""
    return validate_tree(root)


def is_complete_tree(root: Optional[TreeNode]) -> bool:
    """
    Check completeness using level-order traversal.

    In a complete tree, no non-null child may occur after a missing
    child in level order.
    """
    validate_tree(root)

    if root is None:
        return True

    queue = deque([root])
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


def _leftmost_height(root: Optional[TreeNode]) -> int:
    height = 0

    while root is not None:
        height += 1
        root = root.left

    return height


def count_complete_nodes(
    root: Optional[TreeNode],
    verify: bool = True,
) -> int:
    """
    Count nodes in a complete binary tree.

    When verify=True, completeness is checked first. Set verify=False
    only when the caller already guarantees the complete-tree property.

    Counting after validation takes O(log^2 n) time. Validation itself
    takes O(n) time.
    """
    validate_tree(root)

    if root is None:
        return 0

    if verify and not is_complete_tree(root):
        raise ValueError("The optimized counting method requires a complete tree.")

    total = 0
    current = root

    while current is not None:
        left_height = _leftmost_height(current.left)
        right_height = _leftmost_height(current.right)

        if left_height == right_height:
            # The left subtree is perfect. Count it and the current node.
            total += 1 << left_height
            current = current.right
        else:
            # The right subtree is perfect. Count it and the current node.
            total += 1 << right_height
            current = current.left

    return total


def analyze_tree(
    root: Optional[TreeNode],
    target_sum: int,
) -> TreeMetrics:
    """
    Calculate the main tree metrics.

    A postorder traversal combines subtree heights, minimum depths,
    diameters, balance states, and node counts. Path sums are checked
    in a separate traversal.
    """
    validate_tree(root)
    target_sum = _require_integer(target_sum)

    if root is None:
        return TreeMetrics(
            max_depth=0,
            min_depth=0,
            has_path_sum=False,
            diameter_edges=0,
            balanced=True,
            node_count=0,
        )

    # Values: height, minimum leaf depth, diameter, balanced, node count.
    stats: dict[int, tuple[int, int, int, bool, int]] = {}
    stack = [(root, False)]

    while stack:
        node, expanded = stack.pop()

        if not expanded:
            stack.append((node, True))

            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
        else:
            left = stats.get(id(node.left), (0, 0, 0, True, 0))
            right = stats.get(id(node.right), (0, 0, 0, True, 0))

            height = 1 + max(left[0], right[0])

            if node.left is None and node.right is None:
                minimum = 1
            elif node.left is None:
                minimum = 1 + right[1]
            elif node.right is None:
                minimum = 1 + left[1]
            else:
                minimum = 1 + min(left[1], right[1])

            tree_diameter = max(
                left[0] + right[0],
                left[2],
                right[2],
            )
            balanced = (
                left[3]
                and right[3]
                and abs(left[0] - right[0]) <= 1
            )
            nodes = 1 + left[4] + right[4]

            stats[id(node)] = (
                height,
                minimum,
                tree_diameter,
                balanced,
                nodes,
            )

    has_target = has_path_sum(root, target_sum)
    result = stats[id(root)]

    return TreeMetrics(
        max_depth=result[0],
        min_depth=result[1],
        has_path_sum=has_target,
        diameter_edges=result[2],
        balanced=result[3],
        node_count=result[4],
    )


def run_tests() -> None:
    balanced_tree = from_level_order([10, 5, 15, 3, 7, 12, 18])

    assert max_depth(balanced_tree) == 3
    assert min_depth(balanced_tree) == 3
    assert has_path_sum(balanced_tree, 22)
    assert not has_path_sum(balanced_tree, 100)
    assert diameter(balanced_tree) == 4
    assert is_balanced(balanced_tree)
    assert count_nodes(balanced_tree) == 7
    assert is_complete_tree(balanced_tree)
    assert count_complete_nodes(balanced_tree) == 7

    metrics = analyze_tree(balanced_tree, 22)
    assert metrics == TreeMetrics(3, 3, True, 4, True, 7)

    skewed_tree = from_level_order([5, 4, None, 3, None, 2])
    assert max_depth(skewed_tree) == 4
    assert min_depth(skewed_tree) == 4
    assert diameter(skewed_tree) == 3
    assert not is_balanced(skewed_tree)
    assert count_nodes(skewed_tree) == 4
    assert not is_complete_tree(skewed_tree)

    # A node with only one child is not itself a leaf.
    single_branch = TreeNode(1, left=TreeNode(2))
    assert min_depth(single_branch) == 2
    assert diameter(single_branch) == 1

    # Negative values are valid in path-sum problems.
    negative_tree = from_level_order([-2, -3, -4])
    assert has_path_sum(negative_tree, -5)

    assert max_depth(None) == 0
    assert min_depth(None) == 0
    assert diameter(None) == 0
    assert is_balanced(None)
    assert count_nodes(None) == 0
    assert count_complete_nodes(None) == 0
    assert not has_path_sum(None, 0)

    try:
        count_complete_nodes(skewed_tree)
    except ValueError:
        pass
    else:
        raise AssertionError("Incomplete tree was accepted.")

    try:
        from_level_order([None, 1])
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid level-order input was accepted.")

    shared = TreeNode(9)
    invalid_tree = TreeNode(1, TreeNode(2, shared), TreeNode(3, shared))

    try:
        validate_tree(invalid_tree)
    except ValueError:
        pass
    else:
        raise AssertionError("Shared child was accepted.")

    print("All binary tree tests passed.")


def main() -> None:
    run_tests()

    root = from_level_order([10, 5, 15, 3, 7, 12, 18])
    metrics = analyze_tree(root, 22)

    print("\nBinary Tree Analysis")
    print(f"Maximum depth: {metrics.max_depth}")
    print(f"Minimum depth: {metrics.min_depth}")
    print(f"Path sum 22 exists: {metrics.has_path_sum}")
    print(f"Diameter in edges: {metrics.diameter_edges}")
    print(f"Balanced: {metrics.balanced}")
    print(f"Node count: {metrics.node_count}")
    print(f"Complete tree: {is_complete_tree(root)}")
    print(f"Optimized complete-tree count: {count_complete_nodes(root)}")


if __name__ == "__main__":
    main()
