"""
Recursion Trees: execution tracing, visualization, recurrence analysis,
cost aggregation, memoization, and recursive algorithm case studies.

The program is self-contained and uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable, Optional
import math
import time


# ---------------------------------------------------------------------------
# Recursive execution tree
# ---------------------------------------------------------------------------

@dataclass
class CallNode:
    name: str
    arguments: str
    result: Optional[object] = None
    cost: int = 1
    children: list["CallNode"] = field(default_factory=list)

    def add_child(self, child: "CallNode") -> None:
        self.children.append(child)


def print_tree(
    node: CallNode,
    prefix: str = "",
    is_last: bool = True,
    is_root: bool = True,
) -> None:
    connector = "" if is_root else ("└── " if is_last else "├── ")
    result_text = "" if node.result is None else f" => {node.result}"
    print(
        f"{prefix}{connector}{node.name}({node.arguments})"
        f"{result_text} [cost={node.cost}]"
    )

    child_prefix = prefix if is_root else prefix + ("    " if is_last else "│   ")

    for index, child in enumerate(node.children):
        print_tree(
            child,
            child_prefix,
            index == len(node.children) - 1,
            False,
        )


def tree_height(node: CallNode) -> int:
    if not node.children:
        return 1
    return 1 + max(tree_height(child) for child in node.children)


def count_nodes(node: CallNode) -> int:
    return 1 + sum(count_nodes(child) for child in node.children)


def sum_cost(node: CallNode) -> int:
    return node.cost + sum(sum_cost(child) for child in node.children)


def count_leaves(node: CallNode) -> int:
    if not node.children:
        return 1
    return sum(count_leaves(child) for child in node.children)


# ---------------------------------------------------------------------------
# Fibonacci recursion tree
# ---------------------------------------------------------------------------

def fibonacci_tree(n: int) -> CallNode:
    node = CallNode("fib", str(n))

    if n <= 1:
        node.result = n
        return node

    left = fibonacci_tree(n - 1)
    right = fibonacci_tree(n - 2)

    node.add_child(left)
    node.add_child(right)
    node.result = left.result + right.result
    return node


def fibonacci_with_trace(n: int) -> tuple[int, CallNode]:
    root = fibonacci_tree(n)
    return int(root.result), root


# ---------------------------------------------------------------------------
# Binary recursive divide-and-conquer tree
# ---------------------------------------------------------------------------

def merge_sort_tree(values: list[int]) -> CallNode:
    node = CallNode("merge_sort", str(values))

    if len(values) <= 1:
        node.result = values.copy()
        return node

    midpoint = len(values) // 2
    left = merge_sort_tree(values[:midpoint])
    right = merge_sort_tree(values[midpoint:])

    merged: list[int] = []
    i = j = 0
    left_values = list(left.result)
    right_values = list(right.result)

    while i < len(left_values) and j < len(right_values):
        if left_values[i] <= right_values[j]:
            merged.append(left_values[i])
            i += 1
        else:
            merged.append(right_values[j])
            j += 1

    merged.extend(left_values[i:])
    merged.extend(right_values[j:])

    # A merge touches every element in this subproblem.
    node.cost = len(values)
    node.add_child(left)
    node.add_child(right)
    node.result = merged
    return node


# ---------------------------------------------------------------------------
# Recurrence-oriented operation counters
# ---------------------------------------------------------------------------

def naive_power(base: int, exponent: int, counter: list[int]) -> int:
    """Linear recursive exponentiation: T(n) = T(n-1) + O(1)."""
    counter[0] += 1

    if exponent == 0:
        return 1

    if exponent < 0:
        raise ValueError("This demonstration accepts non-negative exponents.")

    return base * naive_power(base, exponent - 1, counter)


def fast_power(base: int, exponent: int, counter: list[int]) -> int:
    """
    Exponentiation by squaring.

    T(n) = T(floor(n/2)) + O(1), giving O(log n) recursive depth.
    """
    counter[0] += 1

    if exponent == 0:
        return 1

    if exponent < 0:
        raise ValueError("This demonstration accepts non-negative exponents.")

    half = fast_power(base, exponent // 2, counter)

    if exponent % 2 == 0:
        return half * half

    return base * half * half


# ---------------------------------------------------------------------------
# Recursion with overlapping subproblems
# ---------------------------------------------------------------------------

def fib_naive(n: int, counter: list[int]) -> int:
    counter[0] += 1

    if n <= 1:
        return n

    return fib_naive(n - 1, counter) + fib_naive(n - 2, counter)


@lru_cache(maxsize=None)
def fib_memoized(n: int) -> int:
    if n <= 1:
        return n
    return fib_memoized(n - 1) + fib_memoized(n - 2)


def fib_memoized_with_counter(n: int) -> tuple[int, int]:
    calls = 0
    cache: dict[int, int] = {}

    def solve(k: int) -> int:
        nonlocal calls
        calls += 1

        if k in cache:
            return cache[k]

        if k <= 1:
            cache[k] = k
            return k

        cache[k] = solve(k - 1) + solve(k - 2)
        return cache[k]

    return solve(n), calls


# ---------------------------------------------------------------------------
# Recursion depth and skewed trees
# ---------------------------------------------------------------------------

def recursive_sum(values: list[int], index: int = 0) -> int:
    if index == len(values):
        return 0
    return values[index] + recursive_sum(values, index + 1)


def recursion_depth_example(n: int, depth: int = 0) -> int:
    if n == 0:
        return depth
    return recursion_depth_example(n - 1, depth + 1)


# ---------------------------------------------------------------------------
# General-purpose recursion-tree instrumentation
# ---------------------------------------------------------------------------

def instrumented_binary_search(
    values: list[int],
    target: int,
) -> tuple[Optional[int], CallNode]:
    def search(low: int, high: int) -> CallNode:
        node = CallNode("binary_search", f"low={low}, high={high}")

        if low > high:
            node.result = None
            return node

        middle = (low + high) // 2
        node.cost = 1

        if values[middle] == target:
            node.result = middle
            return node

        if target < values[middle]:
            child = search(low, middle - 1)
        else:
            child = search(middle + 1, high)

        node.add_child(child)
        node.result = child.result
        return node

    root = search(0, len(values) - 1)
    return root.result, root


# ---------------------------------------------------------------------------
# Recursion tree rendered as Graphviz DOT
# ---------------------------------------------------------------------------

def tree_to_dot(root: CallNode) -> str:
    lines = [
        "digraph RecursionTree {",
        '    rankdir="TB";',
        '    node [shape=box, fontname="Consolas"];',
    ]

    counter = 0

    def visit(node: CallNode) -> str:
        nonlocal counter
        node_id = f"n{counter}"
        counter += 1

        label = (
            f"{node.name}({node.arguments})"
            f"\\nresult={node.result}"
            f"\\ncost={node.cost}"
        )
        safe_label = label.replace('"', '\\"')
        lines.append(f'    {node_id} [label="{safe_label}"];')

        for child in node.children:
            child_id = visit(child)
            lines.append(f"    {node_id} -> {child_id};")

        return node_id

    visit(root)
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Recurrence comparison
# ---------------------------------------------------------------------------

def recurrence_table(max_n: int) -> list[dict[str, int]]:
    rows = []

    for n in range(max_n + 1):
        fib_calls = [0]
        fib_naive(n, fib_calls)

        linear_calls = [0]
        naive_power(2, n, linear_calls)

        logarithmic_calls = [0]
        fast_power(2, n, logarithmic_calls)

        rows.append(
            {
                "n": n,
                "fib_calls": fib_calls[0],
                "linear_power_calls": linear_calls[0],
                "fast_power_calls": logarithmic_calls[0],
            }
        )

    return rows


# ---------------------------------------------------------------------------
# Recursive tree metrics
# ---------------------------------------------------------------------------

def explain_tree(root: CallNode) -> None:
    print("Tree:")
    print_tree(root)
    print()
    print(f"Height: {tree_height(root)}")
    print(f"Nodes: {count_nodes(root)}")
    print(f"Leaves: {count_leaves(root)}")
    print(f"Accumulated cost: {sum_cost(root)}")


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------

def demonstrate_fibonacci() -> None:
    print("\n=== Fibonacci recursion tree ===")

    value, root = fibonacci_with_trace(6)
    print(f"fib(6) = {value}")
    explain_tree(root)

    print("\nThe repeated fib(4), fib(3), and smaller calls show overlapping")
    print("subproblems. The tree therefore exposes why naive Fibonacci grows")
    print("exponentially instead of behaving like a simple binary tree with")
    print("only one unique subproblem per level.")


def demonstrate_merge_sort() -> None:
    print("\n=== Merge sort recursion tree ===")

    values = [38, 12, 27, 9, 43, 3, 18, 21]
    root = merge_sort_tree(values)

    print(f"Input:  {values}")
    print(f"Sorted: {root.result}")
    explain_tree(root)

    print(
        "\nEach level divides the array into smaller subproblems, while "
        "each merge performs work proportional to the subarray size."
    )


def demonstrate_recurrence_growth() -> None:
    print("\n=== Recurrence growth comparison ===")

    for row in recurrence_table(12):
        print(
            f"n={row['n']:2d} | "
            f"fib calls={row['fib_calls']:4d} | "
            f"linear power calls={row['linear_power_calls']:2d} | "
            f"fast power calls={row['fast_power_calls']:2d}"
        )

    print(
        "\nThe call counts make the recurrence shape observable instead of "
        "treating Big-O notation as an isolated formula."
    )


def demonstrate_binary_search() -> None:
    print("\n=== Single-branch recursive tree ===")

    values = list(range(0, 64, 2))
    target = 42

    result, root = instrumented_binary_search(values, target)

    print(f"Target: {target}")
    print(f"Index: {result}")
    print_tree(root)
    print(
        "\nBinary search has a recursion tree that is effectively a single "
        "path because each call chooses only one half."
    )


def demonstrate_power() -> None:
    print("\n=== Linear recursion versus divide-and-conquer recursion ===")

    exponent = 1024

    linear_counter = [0]
    linear_result = naive_power(2, exponent, linear_counter)

    fast_counter = [0]
    fast_result = fast_power(2, exponent, fast_counter)

    assert linear_result == fast_result

    print(f"2^{exponent} has {len(str(fast_result))} decimal digits.")
    print(f"Linear recursive calls: {linear_counter[0]}")
    print(f"Exponentiation-by-squaring calls: {fast_counter[0]}")

    print(
        "\nThe second algorithm reduces the problem size by roughly half at "
        "each recursive level, producing logarithmic recursion depth."
    )


def demonstrate_memoization() -> None:
    print("\n=== Memoization changes the effective recursion tree ===")

    n = 30

    naive_counter = [0]
    start = time.perf_counter()
    naive_value = fib_naive(n, naive_counter)
    naive_time = time.perf_counter() - start

    start = time.perf_counter()
    memo_value, memo_calls = fib_memoized_with_counter(n)
    memo_time = time.perf_counter() - start

    assert naive_value == memo_value

    print(f"fib({n}) = {naive_value}")
    print(f"Naive calls: {naive_counter[0]}")
    print(f"Memoized calls: {memo_calls}")
    print(f"Naive elapsed time: {naive_time:.6f}s")
    print(f"Memoized elapsed time: {memo_time:.6f}s")

    print(
        "\nMemoization does not merely make individual calls faster. It "
        "collapses repeated branches into shared cached results."
    )


def demonstrate_dot_output() -> None:
    print("\n=== Graphviz DOT representation ===")

    root = fibonacci_tree(4)
    dot = tree_to_dot(root)

    print(dot)
    print(
        "\nThe DOT output can be saved as a .dot file and rendered by a "
        "Graphviz installation. The program itself does not require Graphviz."
    )


def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases and safety boundaries ===")

    empty_values: list[int] = []
    print(f"Recursive sum of empty list: {recursive_sum(empty_values)}")

    try:
        fast_power(2, -1, [0])
    except ValueError as exc:
        print(f"Rejected negative exponent: {exc}")

    try:
        fibonacci_tree(-1)
        print("fib(-1) uses the base-case convention n <= 1.")
    except RecursionError:
        print("Recursion limit reached.")

    print(
        "Recursive depth is a resource. A skewed recursive algorithm can "
        "consume stack space even when its total work is otherwise small."
    )


def main() -> None:
    print("RECURSION TREES")
    print("================")
    print(
        "A recursion tree represents each recursive call as a node. "
        "Children are the recursive calls made by that node."
    )

    demonstrate_fibonacci()
    demonstrate_merge_sort()
    demonstrate_recurrence_growth()
    demonstrate_binary_search()
    demonstrate_power()
    demonstrate_memoization()
    demonstrate_dot_output()
    demonstrate_edge_cases()

    print("\n=== Practical interpretation ===")
    print(
        "For a recurrence T(n), inspect the number of children created by "
        "each call, how quickly the problem size shrinks, the work done at "
        "each node, and whether different branches repeat the same state."
    )
    print(
        "The total algorithmic cost can then be understood by aggregating "
        "node costs across the tree rather than looking only at the root."
    )


if __name__ == "__main__":
    main()
