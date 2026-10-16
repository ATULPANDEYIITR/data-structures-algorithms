#!/usr/bin/env python3
"""Recursion fundamentals: executable examples from base cases to memoization."""

from functools import lru_cache
from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


class RecursionErrorDemo(Exception):
    """Raised when an input violates a recursive algorithm's contract."""


def factorial(n: int) -> int:
    """Compute n! using a base case and a smaller recursive subproblem."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("factorial is undefined for negative integers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def factorial_iterative(n: int) -> int:
    """Compute factorial without consuming recursive call-stack frames."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    for factor in range(2, n + 1):
        result *= factor
    return result


def factorial_trace(n: int, depth: int = 0) -> int:
    """Display how calls descend to the base case and return upward."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    print(f"{'  ' * depth}factorial({n})")
    if n <= 1:
        print(f"{'  ' * depth}return 1")
        return 1
    result = n * factorial_trace(n - 1, depth + 1)
    print(f"{'  ' * depth}return {n} * ... = {result}")
    return result


def fibonacci_naive(n: int) -> int:
    """Use two recursive subproblems to expose repeated computation."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


@lru_cache(maxsize=None)
def fibonacci_memoized(n: int) -> int:
    """Cache results so each Fibonacci subproblem is solved once."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)


def fibonacci_bottom_up(n: int) -> int:
    """Compute Fibonacci iteratively with constant auxiliary space."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def binary_search_recursive(
    values: list[int], target: int, left: int = 0, right: int | None = None
) -> int:
    """Return the target index in a sorted list, or -1 if absent."""
    if right is None:
        right = len(values) - 1
    if left > right:
        return -1
    middle = left + (right - left) // 2
    if values[middle] == target:
        return middle
    if target < values[middle]:
        return binary_search_recursive(values, target, left, middle - 1)
    return binary_search_recursive(values, target, middle + 1, right)


def sum_nested(data: list) -> int:
    """Sum arbitrarily nested lists by decomposing each list into elements."""
    total = 0
    for item in data:
        if isinstance(item, bool):
            raise TypeError("Boolean values are not accepted as integers")
        if isinstance(item, list):
            total += sum_nested(item)
        elif isinstance(item, int):
            total += item
        else:
            raise TypeError(f"Unsupported nested value: {type(item).__name__}")
    return total


def recursive_directory_size(tree: dict[str, object]) -> int:
    """Calculate total file bytes from a nested in-memory directory tree.

    Integers represent file sizes. Dictionaries represent subdirectories.
    """
    total = 0
    for name, node in tree.items():
        if not isinstance(name, str) or not name:
            raise ValueError("Every directory entry needs a non-empty name")
        if isinstance(node, bool):
            raise TypeError("Boolean file sizes are invalid")
        if isinstance(node, int):
            if node < 0:
                raise ValueError("File sizes cannot be negative")
            total += node
        elif isinstance(node, dict):
            total += recursive_directory_size(node)
        else:
            raise TypeError(f"Invalid directory entry for {name!r}")
    return total


def merge_sort(values: list[int]) -> list[int]:
    """Sort by recursively splitting, sorting, and merging two halves."""
    if len(values) <= 1:
        return values.copy()

    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def depth_limited_search(
    graph: dict[str, list[str]], start: str, goal: str, max_depth: int
) -> list[str] | None:
    """Find a path without exploring beyond the supplied recursion depth."""
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")

    def visit(
        node: str, remaining: int, path: list[str], active: set[str]
    ) -> list[str] | None:
        if node == goal:
            return path.copy()
        if remaining == 0:
            return None

        # The active set prevents cycles on the current path without
        # incorrectly blocking a node that another path could reach.
        for neighbor in graph.get(node, []):
            if neighbor in active:
                continue
            active.add(neighbor)
            path.append(neighbor)
            result = visit(neighbor, remaining - 1, path, active)
            if result is not None:
                return result
            path.pop()
            active.remove(neighbor)
        return None

    return visit(start, max_depth, [start], {start})


def recursive_power(base: float, exponent: int) -> float:
    """Compute integer powers by exponentiation by squaring."""
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise TypeError("exponent must be an integer")
    if exponent < 0:
        if base == 0:
            raise ZeroDivisionError("zero cannot have a negative exponent")
        return 1.0 / recursive_power(base, -exponent)
    if exponent == 0:
        return 1.0
    half = recursive_power(base, exponent // 2)
    squared = half * half
    return squared if exponent % 2 == 0 else base * squared


def recursive_gcd(a: int, b: int) -> int:
    """Use Euclid's recurrence until the remainder is zero."""
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (a, b)):
        raise TypeError("Both arguments must be integers")
    if b == 0:
        return abs(a)
    return recursive_gcd(b, a % b)


def tree_height(tree: dict | None) -> int:
    """Return the height of a binary tree represented by nested dictionaries.

    A missing node has height zero; each existing node contributes one level.
    """
    if tree is None:
        return 0
    if not isinstance(tree, dict):
        raise TypeError("A tree node must be a dictionary or None")
    left_height = tree_height(tree.get("left"))
    right_height = tree_height(tree.get("right"))
    return 1 + max(left_height, right_height)


def timed_call(function: Callable[[int], int], n: int) -> tuple[int, float]:
    """Measure a function without confusing the result with its runtime."""
    start = perf_counter()
    result = function(n)
    return result, perf_counter() - start


def expect_exception(
    exception_type: type[BaseException], function: Callable[[], object]
) -> None:
    """Verify that an invalid operation fails with the expected exception."""
    try:
        function()
    except exception_type as error:
        print(f"Expected {exception_type.__name__}: {error}")
    else:
        raise AssertionError(f"Expected {exception_type.__name__}")


def run_tests() -> None:
    """Check ordinary inputs, boundaries, and invalid contracts."""
    assert factorial(0) == 1
    assert factorial(5) == 120
    assert factorial_iterative(10) == factorial(10)
    assert fibonacci_memoized(0) == 0
    assert fibonacci_memoized(10) == 55
    assert fibonacci_bottom_up(100) == fibonacci_memoized(100)
    assert binary_search_recursive([1, 3, 5, 7], 5) == 2
    assert binary_search_recursive([], 5) == -1
    assert sum_nested([1, [2, [3, 4]], -2]) == 8
    assert recursive_directory_size({"a.txt": 10, "docs": {"b.txt": 20}}) == 30
    assert merge_sort([5, 1, 4, 1, 3]) == [1, 1, 3, 4, 5]
    assert recursive_power(2, 10) == 1024
    assert recursive_power(2, -3) == 0.125
    assert recursive_gcd(-54, 24) == 6
    assert tree_height({"left": {"left": None}, "right": None}) == 3

    graph = {
        "repository": ["api", "web"],
        "api": ["database"],
        "web": ["database"],
        "database": [],
    }
    assert depth_limited_search(graph, "repository", "database", 2) == [
        "repository", "api", "database"
    ]
    assert depth_limited_search(graph, "repository", "database", 1) is None

    expect_exception(ValueError, lambda: factorial(-1))
    expect_exception(TypeError, lambda: factorial(True))
    expect_exception(ZeroDivisionError, lambda: recursive_power(0, -1))
    expect_exception(TypeError, lambda: sum_nested([1, "invalid"]))

    print("All recursion tests passed.")


def main() -> None:
    print("Factorial call-stack trace")
    factorial_trace(4)

    print("\nRecursive problem decomposition")
    print("Nested total:", sum_nested([120, [55, [8, 13]], 4]))

    print("\nRepository dependency search")
    dependencies = {
        "web-app": ["authentication", "api"],
        "authentication": ["identity-store"],
        "api": ["database", "cache"],
        "identity-store": [],
        "database": [],
        "cache": [],
    }
    print(
        "Path to database:",
        depth_limited_search(dependencies, "web-app", "database", 3),
    )

    print("\nSorting and binary search")
    values = [42, 7, 19, 7, 31, 2]
    ordered = merge_sort(values)
    print("Sorted:", ordered)
    print("Index of 19:", binary_search_recursive(ordered, 19))

    print("\nRecursive versus cached Fibonacci")
    for n in (10, 25):
        result, elapsed = timed_call(fibonacci_naive, n)
        print(f"Naive F({n}) = {result}; elapsed={elapsed:.6f}s")

    result, elapsed = timed_call(fibonacci_memoized, 100)
    print(f"Cached F(100) = {result}; elapsed={elapsed:.6f}s")
    print("Cache statistics:", fibonacci_memoized.cache_info())

    print("\nFast exponentiation and Euclid's algorithm")
    print("3^13 =", recursive_power(3, 13))
    print("gcd(252, 105) =", recursive_gcd(252, 105))

    print("\nNested directory storage")
    directory = {
        "app.py": 4096,
        "tests": {"test_app.py": 2048, "fixtures": {"sample.json": 512}},
        "static": {"site.css": 1024, "site.js": 3072},
    }
    print("Total bytes:", recursive_directory_size(directory))

    print("\nAutomated verification")
    run_tests()


if __name__ == "__main__":
    main()
