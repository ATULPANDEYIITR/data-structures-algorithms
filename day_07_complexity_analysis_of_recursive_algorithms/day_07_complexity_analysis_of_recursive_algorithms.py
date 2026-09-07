"""
Complexity Analysis of Recursive Algorithms
===========================================

A comprehensive, self-contained study script covering:

1. Fundamentals of recursion
2. Time and space complexity
3. Recurrence relations
4. Recursion trees
5. Substitution method
6. Iteration and expansion methods
7. Master Theorem
8. Common recursive algorithm patterns
9. Linear, logarithmic, polynomial, and exponential recursion
10. Divide-and-conquer algorithms
11. Memoization and dynamic programming
12. Tail recursion and stack behavior
13. Edge cases and common mistakes
14. Practical complexity measurement
15. Advanced recurrence analysis
16. Production and debugging considerations

Run this file directly:

    python recursive_complexity_analysis.py
"""

from __future__ import annotations

import math
import time
from functools import lru_cache
from typing import Callable, Dict, List, Optional, Tuple


# =============================================================================
# 1. FUNDAMENTALS: WHAT IS RECURSION?
# =============================================================================

def section(title: str) -> None:
    """Print a visible section heading."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


section("1. FUNDAMENTALS OF RECURSION")

# A recursive function is a function that calls itself.
#
# Every correct recursive algorithm normally requires:
#
# 1. Base case:
#    A condition that stops recursion.
#
# 2. Recursive case:
#    A step that reduces or transforms the problem into a smaller subproblem.
#
# Example:
#
# factorial(n) = n * factorial(n - 1)
# factorial(0) = 1
#
# The recurrence for the running time is:
#
# T(n) = T(n - 1) + O(1)
#
# because each function call performs constant additional work.


def factorial_recursive(n: int) -> int:
    """Calculate n! using recursion."""
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    # Base case.
    if n <= 1:
        return 1

    # Recursive case.
    return n * factorial_recursive(n - 1)


print("factorial_recursive(5) =", factorial_recursive(5))


# =============================================================================
# 2. HOW TO ANALYZE A RECURSIVE ALGORITHM
# =============================================================================

section("2. HOW TO ANALYZE A RECURSIVE ALGORITHM")

# To analyze a recursive algorithm:
#
# Step 1: Define the input size.
# Step 2: Count recursive calls.
# Step 3: Determine how the input changes.
# Step 4: Calculate work performed by each call.
# Step 5: Write a recurrence relation.
# Step 6: Solve the recurrence.
# Step 7: Analyze recursion depth for space complexity.
#
# Example:
#
# def countdown(n):
#     if n == 0:
#         return
#     countdown(n - 1)
#
# Recurrence:
#
# T(n) = T(n - 1) + c
#
# Expanding:
#
# T(n)
# = T(n - 1) + c
# = T(n - 2) + 2c
# = T(n - 3) + 3c
# ...
# = T(0) + nc
#
# Therefore:
#
# T(n) = O(n)
#
# The maximum recursion depth is n, so auxiliary stack space is also O(n).


def countdown(n: int) -> List[int]:
    """Return values visited by a recursive countdown."""
    if n < 0:
        raise ValueError("n must be non-negative.")

    if n == 0:
        return [0]

    return [n] + countdown(n - 1)


print("countdown(5) =", countdown(5))


# =============================================================================
# 3. TIME COMPLEXITY VERSUS SPACE COMPLEXITY
# =============================================================================

section("3. TIME COMPLEXITY VERSUS SPACE COMPLEXITY")

# Time complexity estimates how execution time grows as input size grows.
#
# Space complexity estimates memory growth.
#
# For recursion, it is important to distinguish:
#
# 1. Input space:
#    Memory required to store the input itself.
#
# 2. Auxiliary space:
#    Additional memory used by the algorithm.
#
# 3. Call stack space:
#    Memory used by active recursive calls.
#
# A function can have:
#
# Time:  O(n)
# Space: O(n)
#
# if it makes one recursive call per level and recursion depth is n.
#
# The number of total calls does NOT always equal recursion depth.
#
# Example:
#
# A binary recursion may make O(2^n) total calls but have only O(n)
# simultaneous calls on the stack.


def binary_recursive_example(n: int) -> int:
    """
    Demonstrates exponential total calls but linear recursion depth.

    T(n) = 2T(n - 1) + O(1)

    Time:  O(2^n)
    Space: O(n)
    """
    if n <= 0:
        return 1

    return (
        binary_recursive_example(n - 1)
        + binary_recursive_example(n - 1)
    )


print("binary_recursive_example(4) =", binary_recursive_example(4))


# =============================================================================
# 4. RECURRENCE RELATIONS
# =============================================================================

section("4. RECURRENCE RELATIONS")

# A recurrence relation defines the running time of a problem in terms of
# smaller instances.
#
# Common forms:
#
# T(n) = T(n - 1) + f(n)
#
# T(n) = 2T(n - 1) + f(n)
#
# T(n) = T(n / 2) + f(n)
#
# T(n) = 2T(n / 2) + f(n)
#
# T(n) = aT(n / b) + f(n)
#
# where:
#
# a = number of recursive subproblems
# b = factor by which the input size decreases
# f(n) = non-recursive work performed in each call


def sum_recursive(values: List[int], index: int = 0) -> int:
    """
    Sum a list recursively.

    Recurrence:
        T(n) = T(n - 1) + O(1)

    Time:
        O(n)

    Auxiliary recursion space:
        O(n)
    """
    if index == len(values):
        return 0

    return values[index] + sum_recursive(values, index + 1)


numbers = [10, 20, 30, 40]
print("sum_recursive(numbers) =", sum_recursive(numbers))


# =============================================================================
# 5. THE SUBSTITUTION AND EXPANSION METHOD
# =============================================================================

section("5. SUBSTITUTION AND EXPANSION METHOD")

# Consider:
#
# T(n) = T(n - 1) + 1
#
# Expand:
#
# T(n)
# = T(n - 1) + 1
# = T(n - 2) + 1 + 1
# = T(n - 3) + 1 + 1 + 1
# ...
#
# After k expansions:
#
# T(n) = T(n - k) + k
#
# Stop when:
#
# n - k = 0
#
# Therefore:
#
# k = n
#
# T(n) = T(0) + n
#
# Therefore:
#
# T(n) = O(n)


def linear_recursive_work(n: int) -> int:
    """Example of T(n) = T(n - 1) + O(1)."""
    if n <= 0:
        return 0

    return 1 + linear_recursive_work(n - 1)


print("linear_recursive_work(10) =", linear_recursive_work(10))


# =============================================================================
# 6. LOGARITHMIC RECURSION
# =============================================================================

section("6. LOGARITHMIC RECURSION")

# Consider:
#
# T(n) = T(n / 2) + O(1)
#
# Expansion:
#
# T(n)
# = T(n / 2) + c
# = T(n / 4) + 2c
# = T(n / 8) + 3c
# ...
#
# Stop when:
#
# n / 2^k = 1
#
# Therefore:
#
# 2^k = n
#
# k = log2(n)
#
# Therefore:
#
# T(n) = O(log n)
#
# The recursion depth is also O(log n).


def binary_search_recursive(
    values: List[int],
    target: int,
    left: int = 0,
    right: Optional[int] = None,
) -> int:
    """
    Recursive binary search.

    Time:
        T(n) = T(n / 2) + O(1)
        O(log n)

    Space:
        O(log n) recursion stack.
    """
    if right is None:
        right = len(values) - 1

    if left > right:
        return -1

    middle = left + (right - left) // 2

    if values[middle] == target:
        return middle

    if values[middle] < target:
        return binary_search_recursive(values, target, middle + 1, right)

    return binary_search_recursive(values, target, left, middle - 1)


sorted_values = [2, 4, 7, 9, 15, 21, 30]
print(
    "binary_search_recursive(sorted_values, 15) =",
    binary_search_recursive(sorted_values, 15),
)


# =============================================================================
# 7. RECURRENCE: T(n) = T(n - 1) + O(n)
# =============================================================================

section("7. LINEAR RECURSION WITH LINEAR WORK")

# Consider:
#
# T(n) = T(n - 1) + n
#
# Expand:
#
# T(n)
# = T(n - 1) + n
# = T(n - 2) + (n - 1) + n
# = T(n - 3) + (n - 2) + (n - 1) + n
#
# Therefore:
#
# T(n) = 1 + 2 + 3 + ... + n
#
# Sum of first n integers:
#
# n(n + 1) / 2
#
# Therefore:
#
# T(n) = O(n^2)


def recursive_linear_work(n: int) -> int:
    """
    Demonstrate a recurrence of approximately:

        T(n) = T(n - 1) + O(n)

    The loop contributes O(n) work at every recursive level.
    """
    if n <= 0:
        return 0

    current_level_work = 0

    for value in range(n):
        current_level_work += value

    return current_level_work + recursive_linear_work(n - 1)


print("recursive_linear_work(5) =", recursive_linear_work(5))


# =============================================================================
# 8. BINARY RECURSION
# =============================================================================

section("8. BINARY RECURSION")

# Consider:
#
# T(n) = 2T(n - 1) + O(1)
#
# Expansion:
#
# T(n)
# = 2[T(n - 1)] + c
# = 2[2T(n - 2) + c] + c
# = 4T(n - 2) + 3c
#
# At level k:
#
# Number of nodes = 2^k
#
# Maximum depth = n
#
# Total nodes:
#
# 1 + 2 + 4 + ... + 2^n
#
# This geometric series is O(2^n).
#
# Time:
#     O(2^n)
#
# Stack space:
#     O(n)


def count_binary_calls(n: int) -> int:
    """
    Count leaf calls in a binary recursion tree.

    Recurrence:
        T(n) = 2T(n - 1) + O(1)
    """
    if n == 0:
        return 1

    return count_binary_calls(n - 1) + count_binary_calls(n - 1)


for n in range(6):
    print(f"count_binary_calls({n}) =", count_binary_calls(n))


# =============================================================================
# 9. RECURSION TREES
# =============================================================================

section("9. RECURSION TREES")

# A recursion tree represents recursive calls as nodes.
#
# Each node represents:
#
# - One recursive call
# - The problem size handled by that call
# - The local work performed by that call
#
# Example:
#
# T(n) = 2T(n / 2) + n
#
# Level 0:
#
# Number of nodes: 1
# Work per node: n
# Total level work: n
#
# Level 1:
#
# Number of nodes: 2
# Work per node: n / 2
# Total level work: n
#
# Level 2:
#
# Number of nodes: 4
# Work per node: n / 4
# Total level work: n
#
# Height:
#
# log2(n)
#
# Total:
#
# n * log n
#
# Therefore:
#
# T(n) = O(n log n)


def recursion_tree_level_costs(n: int) -> List[Tuple[int, int, float, float]]:
    """
    Calculate approximate recursion-tree costs for:

        T(n) = 2T(n / 2) + n

    Returns tuples containing:
        (level, nodes, work_per_node, total_level_work)
    """
    if n <= 0:
        raise ValueError("n must be positive.")

    level = 0
    nodes = 1
    problem_size = float(n)
    results = []

    while problem_size >= 1:
        work_per_node = problem_size
        total_level_work = nodes * work_per_node

        results.append(
            (
                level,
                nodes,
                work_per_node,
                total_level_work,
            )
        )

        level += 1
        nodes *= 2
        problem_size /= 2

    return results


for row in recursion_tree_level_costs(16):
    print(
        "level =", row[0],
        "| nodes =", row[1],
        "| work/node =", row[2],
        "| level work =", row[3],
    )


# =============================================================================
# 10. DIVIDE AND CONQUER
# =============================================================================

section("10. DIVIDE AND CONQUER")

# Divide-and-conquer algorithms generally follow:
#
# 1. Divide:
#    Split the original problem into smaller subproblems.
#
# 2. Conquer:
#    Solve subproblems recursively.
#
# 3. Combine:
#    Combine subproblem solutions.
#
# A common recurrence is:
#
# T(n) = aT(n / b) + f(n)
#
# Examples:
#
# Binary search:
#     T(n) = T(n / 2) + O(1)
#
# Merge sort:
#     T(n) = 2T(n / 2) + O(n)
#
# Naive matrix multiplication:
#     T(n) = 8T(n / 2) + O(n^2)


def merge_sort(values: List[int]) -> List[int]:
    """
    Merge sort.

    Recurrence:
        T(n) = 2T(n / 2) + O(n)

    Time:
        O(n log n)

    Extra memory:
        O(n), excluding recursion bookkeeping.

    Recursion depth:
        O(log n)
    """
    if len(values) <= 1:
        return values[:]

    middle = len(values) // 2

    left_half = merge_sort(values[:middle])
    right_half = merge_sort(values[middle:])

    return merge(left_half, right_half)


def merge(left: List[int], right: List[int]) -> List[int]:
    """Merge two sorted lists."""
    merged = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])

    return merged


unsorted_values = [9, 3, 7, 1, 5, 2, 8, 4, 6]
print("merge_sort =", merge_sort(unsorted_values))


# =============================================================================
# 11. MASTER THEOREM
# =============================================================================

section("11. MASTER THEOREM")

# The standard Master Theorem analyzes recurrences of the form:
#
# T(n) = aT(n / b) + f(n)
#
# where:
#
# a >= 1
# b > 1
#
# Calculate:
#
# n^(log_b(a))
#
# Compare f(n) with n^(log_b(a)).
#
#
# CASE 1:
#
# f(n) is polynomially smaller than n^(log_b(a)).
#
# T(n) = Theta(n^(log_b(a)))
#
#
# CASE 2:
#
# f(n) has the same asymptotic growth as n^(log_b(a)).
#
# T(n) = Theta(n^(log_b(a)) log n)
#
#
# CASE 3:
#
# f(n) is polynomially larger than n^(log_b(a)),
# subject to the regularity condition.
#
# T(n) = Theta(f(n))
#
#
# Important limitation:
#
# The basic Master Theorem does NOT directly solve every recurrence.
#
# Examples that may require other methods:
#
# T(n) = T(n - 1) + n
# T(n) = T(n / 2) + T(n / 3) + n
# T(n) = T(n / 2) + n sin(n)
# T(n) = 2T(n / 2) + n log n


def master_exponent(a: float, b: float) -> float:
    """
    Calculate log_b(a), the critical exponent used in the Master Theorem.
    """
    if a <= 0 or b <= 1:
        raise ValueError("Require a > 0 and b > 1.")

    return math.log(a, b)


examples = [
    ("Binary search", 1, 2),
    ("Merge sort", 2, 2),
    ("Three-way divide", 3, 2),
    ("Four subproblems", 4, 2),
]

for name, a_value, b_value in examples:
    print(
        f"{name}: log_{b_value}({a_value}) =",
        round(master_exponent(a_value, b_value), 4),
    )


# =============================================================================
# 12. MASTER THEOREM CASE 1 EXAMPLE
# =============================================================================

section("12. MASTER THEOREM CASE 1")

# Example:
#
# T(n) = 4T(n / 2) + O(n)
#
# a = 4
# b = 2
#
# n^(log_2(4)) = n^2
#
# f(n) = n
#
# n is polynomially smaller than n^2.
#
# Therefore:
#
# T(n) = Theta(n^2)


def four_way_recursive(n: int) -> int:
    """
    Demonstration of:

        T(n) = 4T(n / 2) + O(1)

    For powers of two.

    The recurrence has exponential branching by depth,
    but because the depth is logarithmic, the final
    complexity is polynomial:

        O(n^2)
    """
    if n <= 1:
        return 1

    half = n // 2

    return (
        four_way_recursive(half)
        + four_way_recursive(half)
        + four_way_recursive(half)
        + four_way_recursive(half)
    )


print("four_way_recursive(8) =", four_way_recursive(8))


# =============================================================================
# 13. MASTER THEOREM CASE 2: MERGE SORT
# =============================================================================

section("13. MASTER THEOREM CASE 2")

# Merge sort:
#
# T(n) = 2T(n / 2) + n
#
# a = 2
# b = 2
#
# n^(log_2(2)) = n
#
# f(n) = n
#
# Same asymptotic order.
#
# Therefore:
#
# T(n) = Theta(n log n)


def merge_sort_with_statistics(values: List[int]) -> Tuple[List[int], Dict[str, int]]:
    """
    Merge sort while counting comparisons.

    This demonstrates that practical work depends on data,
    while asymptotic complexity describes growth.
    """
    comparisons = 0

    def sort(items: List[int]) -> List[int]:
        nonlocal comparisons

        if len(items) <= 1:
            return items[:]

        middle = len(items) // 2
        left = sort(items[:middle])
        right = sort(items[middle:])

        merged = []
        left_index = 0
        right_index = 0

        while left_index < len(left) and right_index < len(right):
            comparisons += 1

            if left[left_index] <= right[right_index]:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1

        merged.extend(left[left_index:])
        merged.extend(right[right_index:])

        return merged

    result = sort(values)

    return result, {"comparisons": comparisons}


sorted_result, statistics = merge_sort_with_statistics(unsorted_values)
print("sorted =", sorted_result)
print("statistics =", statistics)


# =============================================================================
# 14. MASTER THEOREM CASE 3
# =============================================================================

section("14. MASTER THEOREM CASE 3")

# Example:
#
# T(n) = 2T(n / 2) + n^2
#
# Critical term:
#
# n^(log_2(2)) = n
#
# f(n) = n^2
#
# n^2 grows polynomially faster than n.
#
# Therefore:
#
# T(n) = Theta(n^2)
#
# Intuition:
#
# Work near the root dominates the total cost.


def recursive_root_heavy_work(n: int) -> int:
    """
    Demonstrates substantial work outside recursive calls.

    Approximate recurrence:

        T(n) = 2T(n / 2) + O(n^2)
    """
    if n <= 1:
        return 1

    local_work = 0

    for _ in range(n):
        for _ in range(n):
            local_work += 1

    half = n // 2

    return (
        local_work
        + recursive_root_heavy_work(half)
        + recursive_root_heavy_work(half)
    )


print("recursive_root_heavy_work(4) =", recursive_root_heavy_work(4))


# =============================================================================
# 15. FIBONACCI: A CLASSIC RECURSIVE COMPLEXITY TRAP
# =============================================================================

section("15. NAIVE RECURSIVE FIBONACCI")

# Naive recursive Fibonacci:
#
# F(n) = F(n - 1) + F(n - 2)
#
# Running time recurrence:
#
# T(n) = T(n - 1) + T(n - 2) + O(1)
#
# This is exponential.
#
# It is often described as O(phi^n), where phi is approximately 1.618.
#
# A looser but simpler upper bound is O(2^n).
#
# The major issue is repeated computation.


def fibonacci_naive(n: int) -> int:
    """
    Naive recursive Fibonacci.

    Time:
        Exponential

    Space:
        O(n) recursion depth
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    if n <= 1:
        return n

    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


for n in range(10):
    print(f"fibonacci_naive({n}) =", fibonacci_naive(n))


# =============================================================================
# 16. COUNTING REPEATED FIBONACCI CALLS
# =============================================================================

section("16. REPEATED SUBPROBLEMS")

# The recursive call tree for Fibonacci contains repeated subproblems.
#
# For example:
#
# fibonacci(5)
#
# computes fibonacci(3) more than once.
#
# Repeated computation causes exponential growth.


def fibonacci_call_counter(n: int) -> Tuple[int, int]:
    """
    Return:
        (fibonacci_result, number_of_function_calls)
    """
    calls = 0

    def calculate(value: int) -> int:
        nonlocal calls
        calls += 1

        if value <= 1:
            return value

        return calculate(value - 1) + calculate(value - 2)

    result = calculate(n)

    return result, calls


for n in range(1, 11):
    result, calls = fibonacci_call_counter(n)
    print(f"n={n:2d}, result={result:3d}, calls={calls}")


# =============================================================================
# 17. MEMOIZATION
# =============================================================================

section("17. MEMOIZATION")

# Memoization stores previously calculated results.
#
# Instead of recomputing:
#
# fibonacci(30)
#
# multiple times, the value is calculated once and stored.
#
# This changes the complexity substantially.
#
# Naive Fibonacci:
#
# Time: Exponential
#
# Memoized Fibonacci:
#
# Time: O(n)
#
# Space:
#
# O(n) cache
# O(n) recursion depth


def fibonacci_memoized(n: int) -> int:
    """Fibonacci using explicit memoization."""
    if n < 0:
        raise ValueError("n must be non-negative.")

    cache: Dict[int, int] = {}

    def calculate(value: int) -> int:
        if value in cache:
            return cache[value]

        if value <= 1:
            result = value
        else:
            result = calculate(value - 1) + calculate(value - 2)

        cache[value] = result
        return result

    return calculate(n)


print("fibonacci_memoized(30) =", fibonacci_memoized(30))


@lru_cache(maxsize=None)
def fibonacci_cached(n: int) -> int:
    """
    Fibonacci using functools.lru_cache.

    The decorator automatically caches function results.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    if n <= 1:
        return n

    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


print("fibonacci_cached(100) =", fibonacci_cached(100))


# =============================================================================
# 18. TAIL RECURSION
# =============================================================================

section("18. TAIL RECURSION")

# A recursive call is in tail position when it is the final operation
# performed by the function.
#
# Example:
#
# factorial(n, accumulator)
#
# Some programming languages optimize tail recursion.
#
# Standard CPython does NOT perform automatic tail-call optimization.
#
# Therefore, tail recursion still consumes stack frames in CPython.


def factorial_tail_recursive(n: int, accumulator: int = 1) -> int:
    """
    Tail-recursive factorial.

    Time:
        O(n)

    Space in CPython:
        O(n)

    Despite being tail-recursive, CPython does not eliminate the stack frames.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    if n <= 1:
        return accumulator

    return factorial_tail_recursive(
        n - 1,
        accumulator * n,
    )


print("factorial_tail_recursive(6) =", factorial_tail_recursive(6))


# =============================================================================
# 19. RECURSION DEPTH VERSUS TOTAL NUMBER OF CALLS
# =============================================================================

section("19. RECURSION DEPTH VERSUS TOTAL CALLS")

# Consider binary recursion:
#
# T(n) = 2T(n - 1) + O(1)
#
# Total calls:
#
# O(2^n)
#
# Maximum simultaneous recursive depth:
#
# O(n)
#
# This distinction is essential.
#
# Space complexity usually depends on maximum simultaneously active calls,
# not on the total number of calls executed during the entire program.


def recursion_depth_example(
    n: int,
    current_depth: int = 0,
) -> Tuple[int, int]:
    """
    Return:
        (total_nodes, maximum_depth)
    """
    if n == 0:
        return 1, current_depth

    left_nodes, left_depth = recursion_depth_example(
        n - 1,
        current_depth + 1,
    )

    right_nodes, right_depth = recursion_depth_example(
        n - 1,
        current_depth + 1,
    )

    return (
        1 + left_nodes + right_nodes,
        max(left_depth, right_depth),
    )


nodes, depth = recursion_depth_example(5)
print("total nodes =", nodes)
print("maximum depth =", depth)


# =============================================================================
# 20. QUICKSORT AND INPUT-DEPENDENT COMPLEXITY
# =============================================================================

section("20. QUICKSORT: INPUT-DEPENDENT RECURRENCE")

# Quicksort demonstrates why recursive complexity may depend on input.
#
# Balanced partition:
#
# T(n) = 2T(n / 2) + O(n)
#
# Time:
#
# O(n log n)
#
# Highly unbalanced partition:
#
# T(n) = T(n - 1) + O(n)
#
# Time:
#
# O(n^2)
#
# Recursion depth:
#
# Balanced:
# O(log n)
#
# Worst case:
# O(n)


def quicksort(values: List[int]) -> List[int]:
    """
    Functional quicksort using a middle element as pivot.

    Average complexity:
        O(n log n)

    Worst case:
        O(n^2)

    This implementation creates additional lists, so memory behavior differs
    from an in-place partitioning implementation.
    """
    if len(values) <= 1:
        return values[:]

    pivot = values[len(values) // 2]

    smaller = [value for value in values if value < pivot]
    equal = [value for value in values if value == pivot]
    larger = [value for value in values if value > pivot]

    return quicksort(smaller) + equal + quicksort(larger)


print("quicksort =", quicksort(unsorted_values))


# =============================================================================
# 21. BINARY SEARCH: SUBTLE COMPLEXITY DETAILS
# =============================================================================

section("21. BINARY SEARCH: SUBTLE COMPLEXITY DETAILS")

# A common mistake is writing recursive binary search with slicing:
#
# values[:middle]
#
# In Python, slicing a list creates a new list.
#
# That copying requires O(n) time for a slice of size n.
#
# Therefore, the implementation details can change practical and asymptotic
# complexity.
#
# The earlier implementation used indices instead of slicing, preserving
# O(log n) time.
#
# This inefficient implementation demonstrates the difference.


def binary_search_with_slicing(
    values: List[int],
    target: int,
) -> bool:
    """
    Recursive binary search with slicing.

    The recursive search depth remains O(log n), but slicing copies data.

    Depending on the implementation and accounting model, repeated copying
    introduces additional work that should not be ignored.
    """
    if not values:
        return False

    middle = len(values) // 2

    if values[middle] == target:
        return True

    if target < values[middle]:
        return binary_search_with_slicing(
            values[:middle],
            target,
        )

    return binary_search_with_slicing(
        values[middle + 1:],
        target,
    )


print(
    "binary_search_with_slicing(sorted_values, 21) =",
    binary_search_with_slicing(sorted_values, 21),
)


# =============================================================================
# 22. RECURSIVE TREE TRAVERSAL
# =============================================================================

section("22. TREE TRAVERSAL")

# Recursive algorithms often operate naturally on recursive data structures.
#
# A binary tree consists of nodes whose children are themselves binary trees.
#
# Tree traversal usually has:
#
# Time:
# O(n), because each node is visited once.
#
# Space:
# O(h), where h is tree height.
#
# Balanced tree:
# h = O(log n)
#
# Skewed tree:
# h = O(n)


class TreeNode:
    """A simple binary tree node."""

    def __init__(
        self,
        value: int,
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
    ) -> None:
        self.value = value
        self.left = left
        self.right = right


def inorder_traversal(
    node: Optional[TreeNode],
) -> List[int]:
    """Perform recursive inorder traversal."""
    if node is None:
        return []

    return (
        inorder_traversal(node.left)
        + [node.value]
        + inorder_traversal(node.right)
    )


tree = TreeNode(
    4,
    TreeNode(
        2,
        TreeNode(1),
        TreeNode(3),
    ),
    TreeNode(
        6,
        TreeNode(5),
        TreeNode(7),
    ),
)

print("inorder traversal =", inorder_traversal(tree))


# =============================================================================
# 23. AVOIDING HIDDEN EXTRA WORK
# =============================================================================

section("23. HIDDEN EXTRA WORK IN RECURSIVE CODE")

# Complexity analysis must include all operations.
#
# A recursive call may appear simple while performing hidden work.
#
# Common sources:
#
# - List slicing
# - String concatenation
# - Creating new containers
# - Sorting inside every recursive call
# - Copying dictionaries
# - Repeated linear searches
#
# Example:
#
# Building a string with:
#
# result = result + character
#
# may repeatedly copy strings because strings are immutable.
#
# The recursive structure alone is not sufficient for complexity analysis.


def reverse_string_recursive(text: str) -> str:
    """
    Reverse a string recursively.

    This implementation uses slicing and concatenation.

    Although recursion depth is O(n), the repeated copying can produce
    O(n^2) total work.
    """
    if len(text) <= 1:
        return text

    return (
        text[-1]
        + reverse_string_recursive(text[:-1])
    )


print(
    "reverse_string_recursive('recursion') =",
    reverse_string_recursive("recursion"),
)


def reverse_string_efficient(text: str) -> str:
    """
    Reverse a string using an accumulator.

    Python's slicing still has costs, but the implementation avoids repeatedly
    constructing increasingly long strings through recursive concatenation.
    """
    characters: List[str] = []

    def collect(index: int) -> None:
        if index < 0:
            return

        characters.append(text[index])
        collect(index - 1)

    collect(len(text) - 1)

    return "".join(characters)


print(
    "reverse_string_efficient('recursion') =",
    reverse_string_efficient("recursion"),
)


# =============================================================================
# 24. BACKTRACKING
# =============================================================================

section("24. BACKTRACKING")

# Backtracking recursively explores possible choices.
#
# Complexity is often exponential because the algorithm explores a search tree.
#
# Example:
#
# Generate all subsets of n elements.
#
# Every element has two choices:
#
# - Include
# - Exclude
#
# Number of subsets:
#
# 2^n
#
# Therefore:
#
# Time is at least O(2^n) because the algorithm must output 2^n results.
#
# This is an important output-size lower bound.


def generate_subsets(values: List[int]) -> List[List[int]]:
    """
    Generate all subsets using backtracking.

    Number of outputs:
        2^n

    Time:
        At least O(2^n)

    If copying/output construction is fully counted:
        O(n * 2^n) can be a more appropriate bound.

    Stack space:
        O(n)
    """
    results: List[List[int]] = []
    current_subset: List[int] = []

    def backtrack(index: int) -> None:
        if index == len(values):
            results.append(current_subset.copy())
            return

        # Exclude current element.
        backtrack(index + 1)

        # Include current element.
        current_subset.append(values[index])
        backtrack(index + 1)
        current_subset.pop()

    backtrack(0)

    return results


subsets = generate_subsets([1, 2, 3])
print("subsets =", subsets)
print("number of subsets =", len(subsets))


# =============================================================================
# 25. PERMUTATION COMPLEXITY
# =============================================================================

section("25. PERMUTATIONS")

# Number of permutations of n distinct elements:
#
# n!
#
# Therefore, generating all permutations necessarily requires at least:
#
# Omega(n!)
#
# time because the output itself contains n! permutations.
#
# If each permutation of length n is copied or processed:
#
# O(n * n!)
#
# can describe total output construction.


def generate_permutations(values: List[int]) -> List[List[int]]:
    """Generate permutations using recursive backtracking."""
    results: List[List[int]] = []

    def backtrack(start: int) -> None:
        if start == len(values):
            results.append(values.copy())
            return

        for index in range(start, len(values)):
            values[start], values[index] = values[index], values[start]
            backtrack(start + 1)
            values[start], values[index] = values[index], values[start]

    working_values = values[:]
    backtrack(0)

    return results


permutations = generate_permutations([1, 2, 3])
print("permutations =", permutations)
print("number of permutations =", len(permutations))


# =============================================================================
# 26. RECURRENCE WITH UNEQUAL SUBPROBLEMS
# =============================================================================

section("26. UNEQUAL SUBPROBLEMS")

# Not every recurrence has equally sized subproblems.
#
# Example:
#
# T(n) = T(n / 2) + T(n / 3) + n
#
# The standard Master Theorem does not directly apply.
#
# Possible approaches:
#
# - Recursion trees
# - Substitution
# - Akra-Bazzi theorem for appropriate forms
# - Bounding techniques
#
# Unequal subproblem sizes require more careful analysis.


def uneven_recursive_sum(values: List[int]) -> int:
    """
    Demonstrate recursion with unequal partitions.

    This is a structural example rather than an optimized algorithm.
    """
    size = len(values)

    if size == 0:
        return 0

    if size == 1:
        return values[0]

    first_size = max(1, size // 2)
    second_size = max(1, size // 3)

    # Ensure progress and avoid excessive overlap for demonstration.
    first_part = values[:first_size]
    second_start = first_size
    second_end = min(size, second_start + second_size)

    second_part = values[second_start:second_end]

    local_work = sum(values)

    if not second_part:
        return local_work

    return (
        local_work
        + uneven_recursive_sum(first_part)
        + uneven_recursive_sum(second_part)
    )


print(
    "uneven_recursive_sum([1, 2, 3, 4, 5, 6]) =",
    uneven_recursive_sum([1, 2, 3, 4, 5, 6]),
)


# =============================================================================
# 27. RECURRENCE TREE LEVEL COST COMPARISON
# =============================================================================

section("27. LEVEL COST PATTERNS")

# A useful recursion-tree question:
#
# Does the work:
#
# - Increase toward leaves?
# - Stay approximately equal per level?
# - Decrease toward leaves?
#
# Examples:
#
# T(n) = 2T(n / 2) + 1
#
# Level work:
#
# 1, 2, 4, 8, ...
#
# Leaves dominate.
#
#
# T(n) = 2T(n / 2) + n
#
# Level work:
#
# n, n, n, ...
#
# All levels contribute equally.
#
#
# T(n) = 2T(n / 2) + n^2
#
# Level work:
#
# n^2, n^2/2, n^2/4, ...
#
# Root dominates.


def level_cost(
    n: int,
    branching_factor: int,
    local_power: float,
) -> List[Tuple[int, float]]:
    """
    Estimate level costs for a recurrence:

        T(n) = aT(n / 2) + n^p

    Returns:
        [(level, total_level_cost), ...]
    """
    if n < 1:
        raise ValueError("n must be at least 1.")

    if branching_factor < 1:
        raise ValueError("branching_factor must be at least 1.")

    level = 0
    nodes = 1
    problem_size = float(n)
    results = []

    while problem_size >= 1:
        work_per_node = problem_size ** local_power
        total_work = nodes * work_per_node

        results.append((level, total_work))

        level += 1
        nodes *= branching_factor
        problem_size /= 2

    return results


for power in [0, 1, 2]:
    print(f"\nFor T(n) = 2T(n/2) + n^{power}:")
    for level, cost in level_cost(16, 2, power):
        print(f"level={level}, cost={cost:.2f}")


# =============================================================================
# 28. BASE CASE COMPLEXITY
# =============================================================================

section("28. BASE CASE COMPLEXITY")

# Base cases are usually assumed to have O(1) cost.
#
# That assumption is not automatically valid.
#
# Example:
#
# if n == 1:
#     sort(large_global_structure)
#
# The base case itself may be expensive.
#
# Complexity analysis must include actual work.


def expensive_base_case(n: int, data: List[int]) -> int:
    """
    Demonstrates a non-constant base case.

    For educational purposes only.
    """
    if n <= 1:
        # Sorting is O(m log m), where m is len(data).
        return sum(sorted(data))

    return expensive_base_case(n - 1, data)


print(
    "expensive_base_case(3, [3, 1, 2]) =",
    expensive_base_case(3, [3, 1, 2]),
)


# =============================================================================
# 29. MULTIPLE PARAMETERS
# =============================================================================

section("29. MULTIPLE INPUT PARAMETERS")

# Not every recursive algorithm depends on one variable.
#
# Example:
#
# T(m, n) = T(m - 1, n) + O(n)
#
# Complexity depends on both m and n.
#
# Collapsing all input dimensions into a single "n" can hide important costs.


def recursive_matrix_sum(
    matrix: List[List[int]],
    row: int = 0,
) -> int:
    """
    Sum a matrix recursively by rows.

    If:
        rows = r
        columns = c

    Each recursive level processes one row in O(c).

    Time:
        O(r * c)

    Stack space:
        O(r)
    """
    if row == len(matrix):
        return 0

    return sum(matrix[row]) + recursive_matrix_sum(
        matrix,
        row + 1,
    )


matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

print("recursive_matrix_sum =", recursive_matrix_sum(matrix))


# =============================================================================
# 30. RECURSIVE SPACE COMPLEXITY
# =============================================================================

section("30. CALCULATING RECURSIVE SPACE COMPLEXITY")

# To estimate recursion stack space:
#
# 1. Find maximum recursion depth.
# 2. Determine memory required per stack frame.
#
# Simplified asymptotic analysis often assumes each frame uses O(1)
# auxiliary space unless it allocates input-sized objects.
#
# Examples:
#
# T(n) = T(n - 1)
# Depth: O(n)
# Stack: O(n)
#
# T(n) = T(n / 2)
# Depth: O(log n)
# Stack: O(log n)
#
# T(n) = 2T(n / 2)
# Depth: O(log n)
# Stack: O(log n)
#
# T(n) = T(n - 1) + T(n - 1)
# Total calls: O(2^n)
# Stack: O(n)


def halving_recursion_depth(n: int) -> int:
    """Return recursion depth for repeated halving."""
    if n <= 1:
        return 0

    return 1 + halving_recursion_depth(n // 2)


print("halving_recursion_depth(1024) =", halving_recursion_depth(1024))


# =============================================================================
# 31. RECURSION LIMITS IN PYTHON
# =============================================================================

section("31. PYTHON RECURSION LIMITS")

# Python implementations have practical recursion-depth limits.
#
# Therefore:
#
# An algorithm may have mathematically correct complexity but still fail
# for sufficiently large inputs with RecursionError.
#
# Increasing recursion limits blindly can risk exhausting the process stack.
#
# Iterative implementations are often preferable for deeply recursive
# linear algorithms.


def demonstrate_recursion_error_safely(n: int) -> int:
    """
    A simple recursive function.

    Do not call with an extremely large n unless recursion limits and
    platform constraints are understood.
    """
    if n == 0:
        return 0

    return 1 + demonstrate_recursion_error_safely(n - 1)


print(
    "demonstrate_recursion_error_safely(10) =",
    demonstrate_recursion_error_safely(10),
)


# =============================================================================
# 32. ITERATIVE VERSUS RECURSIVE IMPLEMENTATION
# =============================================================================

section("32. ITERATIVE VERSUS RECURSIVE IMPLEMENTATION")

# Recursive factorial:
#
# Time: O(n)
# Space: O(n) stack
#
# Iterative factorial:
#
# Time: O(n)
# Auxiliary space: O(1)
#
# Same time complexity does not imply identical space complexity.


def factorial_iterative(n: int) -> int:
    """Calculate factorial iteratively."""
    if n < 0:
        raise ValueError("n must be non-negative.")

    result = 1

    for value in range(2, n + 1):
        result *= value

    return result


print("factorial_iterative(6) =", factorial_iterative(6))


# =============================================================================
# 33. PERFORMANCE MEASUREMENT
# =============================================================================

section("33. EMPIRICAL PERFORMANCE MEASUREMENT")

# Asymptotic complexity predicts growth trends.
#
# Real execution time also depends on:
#
# - Hardware
# - Interpreter overhead
# - Constant factors
# - Memory allocation
# - Input distribution
# - Caching
# - Operating system behavior
#
# Timing small functions is noisy.
#
# The following utility demonstrates basic measurement.


def measure_execution_time(
    function: Callable[..., object],
    *args: object,
    **kwargs: object,
) -> Tuple[object, float]:
    """Return a function result and elapsed execution time."""
    start = time.perf_counter()
    result = function(*args, **kwargs)
    elapsed = time.perf_counter() - start

    return result, elapsed


result, elapsed = measure_execution_time(
    fibonacci_memoized,
    30,
)

print("result =", result)
print(f"elapsed seconds = {elapsed:.8f}")


# =============================================================================
# 34. COMMON MISTAKE: COUNTING ONLY RECURSIVE CALLS
# =============================================================================

section("34. COMMON MISTAKE: IGNORING LOCAL WORK")

# Incorrect reasoning:
#
# "The function calls itself once, so it must be O(n)."
#
# Counterexample:
#
# T(n) = T(n - 1) + O(n^2)
#
# Expanding:
#
# T(n) = n^2 + (n - 1)^2 + ... + 1
#
# The sum of squares is:
#
# O(n^3)


def recursive_quadratic_work(n: int) -> int:
    """
    Approximate recurrence:

        T(n) = T(n - 1) + O(n^2)

    Total:
        O(n^3)
    """
    if n <= 0:
        return 0

    work = 0

    for _ in range(n):
        for _ in range(n):
            work += 1

    return work + recursive_quadratic_work(n - 1)


print(
    "recursive_quadratic_work(4) =",
    recursive_quadratic_work(4),
)


# =============================================================================
# 35. COMMON MISTAKE: ASSUMING TWO RECURSIVE CALLS MEAN O(2^n)
# =============================================================================

section("35. TWO RECURSIVE CALLS DO NOT ALWAYS MEAN O(2^n)")

# Consider:
#
# T(n) = 2T(n / 2) + O(1)
#
# The number of branches is 2, but recursion depth is log n.
#
# Number of leaves:
#
# 2^(log2(n)) = n
#
# Therefore:
#
# T(n) = O(n)
#
# Branching factor alone is insufficient.
#
# Both branching factor and recursion depth matter.


def split_into_halves_count(n: int) -> int:
    """
    Count leaves produced by repeatedly splitting n.

    Approximate recurrence:

        T(n) = 2T(n / 2) + O(1)

    Time:
        O(n)
    """
    if n <= 1:
        return 1

    half = n // 2

    return (
        split_into_halves_count(half)
        + split_into_halves_count(n - half)
    )


print("split_into_halves_count(16) =", split_into_halves_count(16))


# =============================================================================
# 36. COMMON MISTAKE: CONFUSING O(n log n) WITH O(log n)
# =============================================================================

section("36. DEPTH IS NOT TOTAL WORK")

# Merge sort has recursion depth O(log n).
#
# That does NOT mean merge sort has O(log n) time.
#
# Each level processes O(n) total data.
#
# Therefore:
#
# Time:
#
# O(n log n)
#
# Stack depth:
#
# O(log n)
#
# Recursive complexity requires analyzing:
#
# - Number of levels
# - Work performed at each level


# =============================================================================
# 37. SUBSTITUTION METHOD FOR PROOF
# =============================================================================

section("37. SUBSTITUTION METHOD")

# The substitution method can prove a guessed bound.
#
# Suppose:
#
# T(n) = 2T(n / 2) + n
#
# Guess:
#
# T(n) <= c n log2(n)
#
# Substitute:
#
# T(n)
# <= 2[c(n/2) log2(n/2)] + n
#
# = c n (log2(n) - 1) + n
#
# = c n log2(n) - c n + n
#
# For sufficiently large c:
#
# -c n + n <= 0
#
# Therefore:
#
# T(n) <= c n log2(n)
#
# Base cases must also be verified.
#
# A proof requires:
#
# 1. A hypothesis
# 2. Substitution into the recurrence
# 3. Algebraic simplification
# 4. Verification of constants and base cases


# =============================================================================
# 38. RECURRENCE SOLVING WITH MEMOIZED CALL COUNTING
# =============================================================================

section("38. MEASURING UNIQUE SUBPROBLEMS")

# Memoization reduces repeated computation by ensuring that each distinct
# subproblem is solved once.
#
# The number of unique states is often a strong indicator of dynamic
# programming complexity.


def fibonacci_unique_state_count(n: int) -> Tuple[int, int]:
    """
    Return:
        (result, number_of_unique_states_computed)
    """
    computed_states = 0

    @lru_cache(maxsize=None)
    def calculate(value: int) -> int:
        nonlocal computed_states
        computed_states += 1

        if value <= 1:
            return value

        return calculate(value - 1) + calculate(value - 2)

    return calculate(n), computed_states


result, states = fibonacci_unique_state_count(20)
print("fibonacci result =", result)
print("unique states =", states)


# =============================================================================
# 39. ADVANCED IDEA: OVERLAPPING SUBPROBLEMS
# =============================================================================

section("39. OVERLAPPING SUBPROBLEMS")

# Divide-and-conquer:
#
# Subproblems are often independent.
#
# Example:
#
# Merge sort left half and right half do not overlap.
#
# Dynamic programming:
#
# Recursive calls often revisit the same logical states.
#
# Example:
#
# Fibonacci repeatedly computes the same smaller Fibonacci values.
#
# The distinction affects whether memoization can substantially reduce time.


# =============================================================================
# 40. ADVANCED IDEA: RECURSION TREE VERSUS CALL GRAPH
# =============================================================================

section("40. RECURSION TREE VERSUS CALL GRAPH")

# Without memoization:
#
# A recursion tree may contain many duplicate nodes representing identical
# subproblems.
#
# With memoization:
#
# The computation can be represented more accurately as a directed acyclic
# graph of unique states.
#
# This explains why memoization can transform exponential recursion into
# polynomial or linear-time computation.


# =============================================================================
# 41. PRACTICAL RECURRENCE ANALYSIS HELPER
# =============================================================================

section("41. PRACTICAL RECURRENCE ANALYSIS HELPER")

# The following helper does not solve arbitrary recurrences.
#
# It estimates recursion-tree characteristics for recurrences of the form:
#
# T(n) = aT(n / b) + O(n^p)
#
# This helps visualize:
#
# - recursion depth
# - nodes per level
# - local work
# - total work per level


def analyze_standard_recurrence(
    n: int,
    a: int,
    b: int,
    local_power: float,
) -> List[Dict[str, float]]:
    """
    Analyze a recurrence approximately:

        T(n) = aT(n / b) + O(n^local_power)

    Assumes positive integer-like input behavior.
    """
    if n < 1:
        raise ValueError("n must be at least 1.")

    if a < 1:
        raise ValueError("a must be at least 1.")

    if b <= 1:
        raise ValueError("b must be greater than 1.")

    rows: List[Dict[str, float]] = []

    level = 0
    nodes = 1.0
    problem_size = float(n)

    while problem_size >= 1:
        work_per_node = problem_size ** local_power
        level_work = nodes * work_per_node

        rows.append(
            {
                "level": float(level),
                "nodes": nodes,
                "problem_size": problem_size,
                "work_per_node": work_per_node,
                "level_work": level_work,
            }
        )

        level += 1
        nodes *= a
        problem_size /= b

    return rows


analysis = analyze_standard_recurrence(
    n=16,
    a=2,
    b=2,
    local_power=1,
)

for row in analysis:
    print(
        f"level={int(row['level'])}, "
        f"nodes={row['nodes']:.0f}, "
        f"problem_size={row['problem_size']:.2f}, "
        f"level_work={row['level_work']:.2f}"
    )


# =============================================================================
# 42. EDGE CASES IN RECURSIVE PROGRAMS
# =============================================================================

section("42. EDGE CASES")

# Important recursive edge cases include:
#
# 1. Empty input
# 2. Single-element input
# 3. Negative input where unsupported
# 4. Missing base cases
# 5. Base cases that are unreachable
# 6. Recursive calls that do not reduce the problem
# 7. Integer division that prevents progress
# 8. Unexpected cyclic data structures
# 9. Extremely deep recursion
# 10. Repeated overlapping subproblems


def safe_gcd(a: int, b: int) -> int:
    """
    Recursive Euclidean algorithm.

    Recurrence:
        T(n) = T(smaller problem) + O(1)

    Worst-case complexity:
        O(log(min(a, b))) for positive inputs.

    Recursion terminates because the remainder decreases.
    """
    a = abs(a)
    b = abs(b)

    if a == 0 and b == 0:
        raise ValueError("gcd(0, 0) is undefined.")

    if b == 0:
        return a

    return safe_gcd(b, a % b)


print("safe_gcd(48, 18) =", safe_gcd(48, 18))


# =============================================================================
# 43. TERMINATION AS A CORRECTNESS REQUIREMENT
# =============================================================================

section("43. TERMINATION")

# Complexity is meaningful only for terminating algorithms.
#
# A recursive function requires a well-founded progression toward a base case.
#
# Example of dangerous recursion:
#
# def bad(n):
#     return bad(n)
#
# Another subtle problem:
#
# def bad(n):
#     if n == 0:
#         return 0
#     return bad(n + 1)
#
# The base case exists but may be unreachable from positive input.
#
# A useful design technique is to identify a measure that strictly decreases:
#
# - Remaining list length
# - Search interval size
# - Tree height
# - Remaining choices
# - Numeric value


# =============================================================================
# 44. SECURITY AND RESOURCE CONSIDERATIONS
# =============================================================================

section("44. RESOURCE AND SECURITY CONSIDERATIONS")

# Recursive algorithms can become a resource concern when input is controlled
# by external users.
#
# Potential issues:
#
# - Stack exhaustion
# - Exponential computation
# - Excessive memory allocation
# - Algorithmic denial of service
#
# Example:
#
# A service that accepts arbitrary n for naive Fibonacci can be forced to
# perform extremely expensive exponential computation.
#
# Defensive strategies include:
#
# - Validate input ranges
# - Use memoization where appropriate
# - Prefer iterative algorithms for deep linear recursion
# - Enforce resource limits
# - Avoid exponential algorithms for untrusted large inputs


def fibonacci_safe(n: int, maximum_input: int = 100_000) -> int:
    """
    Iterative Fibonacci with input validation.

    This avoids recursion-depth problems.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer.")

    if n < 0:
        raise ValueError("n must be non-negative.")

    if n > maximum_input:
        raise ValueError(
            f"n must not exceed {maximum_input}."
        )

    previous = 0
    current = 1

    for _ in range(n):
        previous, current = current, previous + current

    return previous


print("fibonacci_safe(20) =", fibonacci_safe(20))


# =============================================================================
# 45. DEBUGGING RECURSIVE ALGORITHMS
# =============================================================================

section("45. DEBUGGING RECURSIVE ALGORITHMS")

# Common debugging questions:
#
# 1. Is the base case correct?
# 2. Is the base case reachable?
# 3. Does each recursive call reduce the problem?
# 4. Are recursive results combined correctly?
# 5. Are mutable structures restored during backtracking?
# 6. Is repeated computation causing unexpected slowness?
#
# A depth parameter can make recursive execution visible.


def traced_factorial(
    n: int,
    depth: int = 0,
) -> int:
    """Factorial with explicit recursion tracing."""
    indentation = "  " * depth

    print(f"{indentation}Entering factorial({n})")

    if n <= 1:
        print(f"{indentation}Base case returns 1")
        return 1

    result = n * traced_factorial(
        n - 1,
        depth + 1,
    )

    print(f"{indentation}Returning {result}")

    return result


print("traced_factorial(4) =", traced_factorial(4))


# =============================================================================
# 46. TESTING RECURSIVE FUNCTIONS
# =============================================================================

section("46. TESTING RECURSIVE FUNCTIONS")

# Recursive functions should be tested with:
#
# - Base cases
# - Small recursive cases
# - Boundary values
# - Invalid input
# - Large practical inputs
# - Repeated structures
#
# Python assertions provide lightweight testing.


def run_basic_tests() -> None:
    """Run assertions for examples in this script."""
    assert factorial_recursive(0) == 1
    assert factorial_recursive(5) == 120
    assert factorial_iterative(6) == 720

    assert fibonacci_naive(10) == 55
    assert fibonacci_memoized(20) == 6765
    assert fibonacci_cached(20) == 6765
    assert fibonacci_safe(20) == 6765

    assert binary_search_recursive(
        [1, 3, 5, 7],
        5,
    ) == 2

    assert binary_search_recursive(
        [1, 3, 5, 7],
        2,
    ) == -1

    assert merge_sort([3, 1, 2]) == [1, 2, 3]

    assert safe_gcd(48, 18) == 6
    assert safe_gcd(0, 5) == 5

    assert len(generate_subsets([1, 2, 3])) == 8
    assert len(generate_permutations([1, 2, 3])) == 6

    print("All basic tests passed.")


run_basic_tests()


# =============================================================================
# 47. COMPLEXITY COMPARISON TABLE
# =============================================================================

section("47. COMMON RECURSIVE COMPLEXITY PATTERNS")

patterns = [
    (
        "Linear recursion",
        "T(n) = T(n - 1) + O(1)",
        "O(n)",
        "O(n)",
    ),
    (
        "Linear recursion with linear local work",
        "T(n) = T(n - 1) + O(n)",
        "O(n^2)",
        "O(n)",
    ),
    (
        "Halving recursion",
        "T(n) = T(n / 2) + O(1)",
        "O(log n)",
        "O(log n)",
    ),
    (
        "Merge-sort pattern",
        "T(n) = 2T(n / 2) + O(n)",
        "O(n log n)",
        "O(log n) stack",
    ),
    (
        "Linear divide-and-conquer",
        "T(n) = 2T(n / 2) + O(1)",
        "O(n)",
        "O(log n)",
    ),
    (
        "Root-dominated recursion",
        "T(n) = 2T(n / 2) + O(n^2)",
        "O(n^2)",
        "O(log n) stack",
    ),
    (
        "Naive Fibonacci",
        "T(n) = T(n - 1) + T(n - 2) + O(1)",
        "Exponential",
        "O(n)",
    ),
    (
        "Subset generation",
        "Binary choice tree",
        "O(2^n) or output-dependent",
        "O(n) stack",
    ),
    (
        "Permutation generation",
        "Branching decreases by level",
        "O(n * n!) output construction",
        "O(n)",
    ),
]

for name, recurrence, time_complexity, space_complexity in patterns:
    print("\nPattern:", name)
    print("Recurrence:", recurrence)
    print("Time:", time_complexity)
    print("Space:", space_complexity)


# =============================================================================
# 48. PRACTICAL ANALYSIS CHECKLIST
# =============================================================================

section("48. PRACTICAL ANALYSIS CHECKLIST")

checklist = [
    "Identify the input size parameter or parameters.",
    "Identify every base case.",
    "Verify that recursive calls progress toward termination.",
    "Count the number of recursive calls created by one call.",
    "Determine the size of every recursive subproblem.",
    "Measure local work outside recursive calls.",
    "Write the recurrence relation.",
    "Select an appropriate solving technique.",
    "Calculate maximum recursion depth for stack space.",
    "Account for copied lists, strings, and temporary structures.",
    "Check for overlapping subproblems.",
    "Consider memoization when identical states are recomputed.",
    "Analyze best, average, and worst cases when input affects branching.",
    "Consider output size for generation algorithms.",
    "Validate practical recursion-depth limits.",
    "Test base cases and boundary conditions.",
]

for number, item in enumerate(checklist, start=1):
    print(f"{number}. {item}")


# =============================================================================
# 49. FINAL INTEGRATED EXAMPLE: ANALYZING A RECURSIVE ALGORITHM
# =============================================================================

section("49. INTEGRATED EXAMPLE: COMPLETE ANALYSIS")

# Algorithm:
#
# def process(n):
#     if n <= 1:
#         return
#
#     process(n // 2)
#     process(n // 2)
#
#     for i in range(n):
#         perform_constant_work()
#
#
# Analysis:
#
# Number of subproblems:
#
# a = 2
#
# Size reduction:
#
# b = 2
#
# Local work:
#
# f(n) = O(n)
#
# Recurrence:
#
# T(n) = 2T(n / 2) + O(n)
#
# Master Theorem:
#
# n^(log_2(2)) = n
#
# f(n) = n
#
# Same asymptotic order:
#
# Time:
#
# O(n log n)
#
# Recursion depth:
#
# O(log n)
#
# If each frame uses constant auxiliary memory:
#
# Stack space:
#
# O(log n)


def integrated_recursive_process(n: int) -> int:
    """
    Executable form of the integrated example.

    Returns the amount of local work performed.
    """
    if n <= 1:
        return 1

    left_work = integrated_recursive_process(n // 2)
    right_work = integrated_recursive_process(n // 2)

    local_work = 0

    for _ in range(n):
        local_work += 1

    return left_work + right_work + local_work


print(
    "integrated_recursive_process(16) =",
    integrated_recursive_process(16),
)


# =============================================================================
# 50. END OF STUDY SCRIPT
# =============================================================================

section("END OF RECURSIVE COMPLEXITY ANALYSIS")

print(
    "This script demonstrated how recursive complexity depends on "
    "subproblem count, subproblem size, local work, recursion depth, "
    "overlapping states, implementation details, and input structure."
)
