"""
Asymptotic Notations
====================

A self-contained study and demonstration script covering:

1. Why asymptotic analysis is needed
2. Input size and growth rates
3. Big-O notation: O(g(n))
4. Big-Omega notation: Ω(g(n))
5. Big-Theta notation: Θ(g(n))
6. Formal definitions using constants and thresholds
7. Upper, lower, and tight bounds
8. Common growth-rate classes
9. Simplifying mathematical expressions
10. Dominant terms
11. Constant-factor and lower-order-term rules
12. Best, average, and worst-case analysis
13. Loop and nested-loop analysis
14. Sequential and conditional code
15. Logarithmic algorithms
16. Binary search
17. Linear and quadratic algorithms
18. Recursive algorithms
19. Recurrence examples
20. Merge sort
21. Quicksort
22. Space complexity
23. Amortized analysis
24. Comparing algorithms experimentally
25. Common mistakes and edge cases
26. Formal bound verification for selected functions
27. Practical and production considerations

The script uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log2
from random import Random
from time import perf_counter
from typing import Callable, Iterable, Sequence


# ============================================================================
# 1. FUNDAMENTAL IDEAS
# ============================================================================

def print_section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def explain_input_size() -> None:
    """
    Demonstrate the central idea of asymptotic analysis.

    The variable n normally represents input size. The exact interpretation
    depends on the problem:
        - number of elements in a list
        - number of vertices in a graph
        - number of characters in a string
        - number of bits in an integer
        - dimensions of a matrix
    """
    print_section("1. INPUT SIZE AND GROWTH")

    examples = {
        "list-processing problem": "n = number of list elements",
        "string-processing problem": "n = number of characters",
        "graph problem": "n = number of vertices; m = number of edges",
        "matrix problem": "n = matrix dimension",
        "database query": "n = number of rows considered",
    }

    for problem, interpretation in examples.items():
        print(f"{problem:28} -> {interpretation}")

    print(
        "\nAsymptotic analysis studies how resource usage grows as input size "
        "becomes large. The resource can be execution time, memory, network "
        "operations, comparisons, disk accesses, or another measurable cost."
    )


# ============================================================================
# 2. GROWTH-RATE FUNCTIONS
# ============================================================================

def constant_work(n: int) -> int:
    """Perform conceptually constant work."""
    return 42


def logarithmic_work(n: int) -> int:
    """
    Return the number of times n can be repeatedly halved.

    This models the structure of algorithms such as binary search.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    count = 0
    value = n

    while value > 1:
        value //= 2
        count += 1

    return count


def linear_work(n: int) -> int:
    """Perform work proportional to n."""
    total = 0

    for value in range(n):
        total += value

    return total


def linearithmic_work(n: int) -> int:
    """
    Demonstrate n log n work.

    The outer loop executes n times and the inner loop executes approximately
    log2(n) times.
    """
    if n <= 0:
        return 0

    operations = 0

    for _ in range(n):
        value = n
        while value > 1:
            value //= 2
            operations += 1

    return operations


def quadratic_work(n: int) -> int:
    """Perform approximately n^2 operations."""
    operations = 0

    for _ in range(n):
        for _ in range(n):
            operations += 1

    return operations


def cubic_work(n: int) -> int:
    """Perform approximately n^3 operations."""
    operations = 0

    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                operations += 1

    return operations


def exponential_work(n: int) -> int:
    """
    Return 2^n.

    This function illustrates exponential growth mathematically rather than
    performing an exponential-size loop.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    return 2 ** n


def factorial_work(n: int) -> int:
    """Return n!, illustrating factorial growth."""
    if n < 0:
        raise ValueError("n must be non-negative")

    result = 1

    for value in range(2, n + 1):
        result *= value

    return result


def demonstrate_growth_rates() -> None:
    print_section("2. COMMON GROWTH RATES")

    growth_functions = [
        ("1", lambda n: 1),
        ("log2(n)", lambda n: log2(n) if n > 0 else 0),
        ("n", lambda n: n),
        ("n log2(n)", lambda n: n * log2(n) if n > 0 else 0),
        ("n^2", lambda n: n**2),
        ("n^3", lambda n: n**3),
        ("2^n", lambda n: 2**n),
        ("n!", factorial_work),
    ]

    print(f"{'Function':<14} {'n=10':>15} {'n=100':>15} {'n=1000':>20}")
    print("-" * 68)

    for name, function in growth_functions:
        values = [function(n) for n in (10, 100, 1000)]
        formatted = []
        for value in values:
            if isinstance(value, float):
                formatted.append(f"{value:.2f}")
            else:
                formatted.append(str(value))

        print(
            f"{name:<14}"
            f"{formatted[0]:>15}"
            f"{formatted[1]:>15}"
            f"{formatted[2]:>20}"
        )

    print(
        "\nFor sufficiently large n, growth rates dominate constant factors and "
        "lower-order terms. This is the basis of asymptotic classification."
    )


# ============================================================================
# 3. FORMAL DEFINITIONS
# ============================================================================

@dataclass(frozen=True)
class BoundExplanation:
    """Represent a formal asymptotic-bound explanation."""

    notation: str
    meaning: str
    inequality: str


def formal_definitions() -> None:
    print_section("3. FORMAL DEFINITIONS OF O, Ω, AND Θ")

    definitions = [
        BoundExplanation(
            "O(g(n))",
            "g(n) is an asymptotic upper bound for f(n).",
            "0 <= f(n) <= c*g(n) for all n >= n0",
        ),
        BoundExplanation(
            "Ω(g(n))",
            "g(n) is an asymptotic lower bound for f(n).",
            "0 <= c*g(n) <= f(n) for all n >= n0",
        ),
        BoundExplanation(
            "Θ(g(n))",
            "g(n) is a tight asymptotic bound for f(n).",
            "0 <= c1*g(n) <= f(n) <= c2*g(n) for all n >= n0",
        ),
    ]

    for definition in definitions:
        print(f"\n{definition.notation}")
        print(f"  Meaning:    {definition.meaning}")
        print(f"  Condition:  {definition.inequality}")

    print(
        "\nHere c, c1, c2 are positive constants and n0 is a positive threshold."
    )
    print(
        "The constants do not depend on n. The threshold allows finite initial "
        "values to be ignored because asymptotic analysis concerns sufficiently "
        "large inputs."
    )


# ============================================================================
# 4. BIG-O: ASYMPTOTIC UPPER BOUNDS
# ============================================================================

def demonstrate_big_o() -> None:
    print_section("4. BIG-O: ASYMPTOTIC UPPER BOUNDS")

    print(
        "Example: f(n) = 3n^2 + 7n + 10.\n"
        "For n >= 1:\n"
        "  3n^2 <= 3n^2\n"
        "  7n <= 7n^2\n"
        "  10 <= 10n^2\n"
        "Therefore:\n"
        "  f(n) <= 20n^2\n"
        "so f(n) is O(n^2)."
    )

    print(
        "\nImportant distinction:\n"
        "O(n^2) means n^2 is an upper bound, not necessarily the tightest one.\n"
        "A function that is Θ(n) is also O(n^2), because n grows no faster "
        "than n^2 for sufficiently large n."
    )


# ============================================================================
# 5. BIG-OMEGA: ASYMPTOTIC LOWER BOUNDS
# ============================================================================

def demonstrate_big_omega() -> None:
    print_section("5. BIG-OMEGA: ASYMPTOTIC LOWER BOUNDS")

    print(
        "Example: f(n) = 3n^2 + 7n + 10.\n"
        "Since every term is non-negative for n >= 0:\n"
        "  f(n) >= 3n^2.\n"
        "Therefore f(n) is Ω(n^2)."
    )

    print(
        "\nA lower bound does not mean that every input requires exactly that "
        "amount of work. It states that the function cannot eventually grow "
        "slower than the specified bound."
    )


# ============================================================================
# 6. BIG-THETA: TIGHT BOUNDS
# ============================================================================

def demonstrate_big_theta() -> None:
    print_section("6. BIG-THETA: TIGHT ASYMPTOTIC BOUNDS")

    print(
        "For f(n) = 3n^2 + 7n + 10, the n^2 term dominates.\n"
        "For n >= 1:\n"
        "  f(n) >= 3n^2\n"
        "and\n"
        "  f(n) <= 20n^2.\n"
        "Therefore:\n"
        "  f(n) = Θ(n^2)."
    )

    print(
        "\nTheta is stronger than Big-O alone because it establishes both an "
        "eventual upper bound and an eventual lower bound."
    )


# ============================================================================
# 7. RELATIONSHIPS BETWEEN NOTATIONS
# ============================================================================

def notation_relationships() -> None:
    print_section("7. RELATIONSHIPS BETWEEN O, Ω, AND Θ")

    print(
        "If f(n) = Θ(g(n)), then both of these are true:\n"
        "  f(n) = O(g(n))\n"
        "  f(n) = Ω(g(n))\n"
        "\n"
        "But f(n) = O(g(n)) alone does not imply Θ(g(n)).\n"
        "Likewise, Ω(g(n)) alone does not imply Θ(g(n))."
    )

    print(
        "\nExample:\n"
        "f(n) = n\n"
        "f(n) is O(n^2), but f(n) is not Θ(n^2).\n"
        "The tight classification is Θ(n)."
    )


# ============================================================================
# 8. LIMIT-BASED COMPARISON
# ============================================================================

def compare_growth_by_limit(
    f: Callable[[int], float],
    g: Callable[[int], float],
    n: int = 1_000_000,
) -> float:
    """
    Approximate f(n)/g(n).

    This is useful for intuition, but it is not itself a formal proof.
    """
    denominator = g(n)

    if denominator == 0:
        raise ZeroDivisionError("g(n) must not be zero at the selected n")

    return f(n) / denominator


def demonstrate_limit_method() -> None:
    print_section("8. LIMIT-BASED GROWTH COMPARISON")

    examples = [
        (
            "n versus n^2",
            lambda n: n,
            lambda n: n**2,
        ),
        (
            "n log n versus n^2",
            lambda n: n * log2(n),
            lambda n: n**2,
        ),
        (
            "3n^2 + 7n versus n^2",
            lambda n: 3 * n**2 + 7 * n,
            lambda n: n**2,
        ),
    ]

    for label, f, g in examples:
        ratio = compare_growth_by_limit(f, g)
        print(f"{label:<32} f(n)/g(n) at n=1,000,000 = {ratio:.8f}")

    print(
        "\nIf lim f(n)/g(n) is a positive finite constant, f(n) and g(n) "
        "have the same asymptotic order, so f(n) = Θ(g(n))."
    )
    print(
        "If the limit is 0, f grows strictly slower than g.\n"
        "If the limit is infinity, f grows strictly faster than g."
    )


# ============================================================================
# 9. SIMPLIFYING EXPRESSIONS
# ============================================================================

def simplify_polynomial(coefficients: Sequence[float]) -> str:
    """
    Display a polynomial in descending degree order.

    coefficients[i] represents the coefficient of n^(degree-i).
    """
    degree = len(coefficients) - 1

    if degree < 0:
        return "0"

    terms = []

    for index, coefficient in enumerate(coefficients):
        power = degree - index

        if coefficient == 0:
            continue

        if power == 0:
            term = f"{coefficient:g}"
        elif power == 1:
            term = f"{coefficient:g}n"
        else:
            term = f"{coefficient:g}n^{power}"

        terms.append(term)

    return " + ".join(terms) if terms else "0"


def demonstrate_simplification_rules() -> None:
    print_section("9. SIMPLIFICATION RULES")

    print(
        "Common rules:\n"
        "  1. Ignore multiplicative constants.\n"
        "  2. Ignore lower-order terms.\n"
        "  3. Keep the fastest-growing term.\n"
        "  4. Logarithm bases differ only by a constant factor.\n"
        "  5. Be careful with products and exponentials."
    )

    examples = [
        ("5n + 100", "Θ(n)"),
        ("12n^2 + 4n + 9", "Θ(n^2)"),
        ("7n^3 + 2n^2 + n", "Θ(n^3)"),
        ("n log2(n) + 100n", "Θ(n log n)"),
        ("4 log2(n) + 20", "Θ(log n)"),
        ("2^n + n^5", "Θ(2^n)"),
    ]

    for expression, classification in examples:
        print(f"{expression:<32} -> {classification}")

    print(
        "\nThe phrase 'ignore constants' applies to asymptotic classification, "
        "not to actual performance. Constants can strongly affect real runtime."
    )


# ============================================================================
# 10. LOGARITHM BASES
# ============================================================================

def demonstrate_logarithm_bases() -> None:
    print_section("10. LOGARITHM BASES")

    n = 1_048_576

    values = {
        "log2(n)": log2(n),
        "log10(n)": log2(n) / log2(10),
        "ln(n)": log2(n) / log2(2.718281828459045),
    }

    for name, value in values.items():
        print(f"{name:<12} = {value:.4f}")

    print(
        "\nBecause log_a(n) = log_b(n) / log_b(a), changing the logarithm base "
        "multiplies the result by a constant. Therefore all fixed logarithm "
        "bases have the same asymptotic classification: Θ(log n)."
    )


# ============================================================================
# 11. CONSTANT AND LINEAR-TIME ALGORITHMS
# ============================================================================

def access_first_element(values: Sequence[int]) -> int:
    """List indexing is conceptually constant time."""
    if not values:
        raise IndexError("cannot access the first element of an empty sequence")

    return values[0]


def find_value_linear(values: Sequence[int], target: int) -> int:
    """
    Linear search.

    Worst case: target is absent or at the final position.
    Best case: target is the first element.
    """
    for index, value in enumerate(values):
        if value == target:
            return index

    return -1


def demonstrate_linear_algorithms() -> None:
    print_section("11. CONSTANT AND LINEAR TIME")

    values = list(range(10))

    print(f"First element: {access_first_element(values)}")
    print(f"Index of 7:     {find_value_linear(values, 7)}")
    print(f"Index of 99:    {find_value_linear(values, 99)}")

    print(
        "\nAccess by index is typically O(1) for Python lists.\n"
        "Linear search is O(n) in the worst case and Ω(1) in the best case."
    )


# ============================================================================
# 12. LOOP ANALYSIS
# ============================================================================

def single_loop_count(n: int) -> int:
    """One loop running n times gives Θ(n)."""
    count = 0

    for _ in range(n):
        count += 1

    return count


def triangular_loop_count(n: int) -> int:
    """
    Count operations in:

        for i in range(n):
            for j in range(i):

    Total work is n(n-1)/2, which is Θ(n^2).
    """
    count = 0

    for i in range(n):
        for _ in range(i):
            count += 1

    return count


def halving_loop_count(n: int) -> int:
    """
    A loop that repeatedly divides its value by 2 runs Θ(log n) times.
    """
    count = 0

    while n > 1:
        n //= 2
        count += 1

    return count


def demonstrate_loop_analysis() -> None:
    print_section("12. ANALYZING LOOPS")

    for n in (1, 2, 10, 100):
        print(
            f"n={n:3}: "
            f"single={single_loop_count(n):5}, "
            f"triangular={triangular_loop_count(n):5}, "
            f"halving={halving_loop_count(n):3}"
        )

    print(
        "\nImportant pattern:\n"
        "  for i in range(n):              -> Θ(n)\n"
        "  for i in range(n):              -> Θ(n^2) when nested with n work\n"
        "  while n > 1: n //= 2             -> Θ(log n)"
    )


# ============================================================================
# 13. SEQUENTIAL LOOPS
# ============================================================================

def two_sequential_loops(values: Sequence[int]) -> int:
    """
    Two consecutive linear loops take Θ(n + n), which simplifies to Θ(n).
    """
    total = 0

    for value in values:
        total += value

    for value in values:
        total += value * 2

    return total


def demonstrate_sequential_loops() -> None:
    print_section("13. SEQUENTIAL VERSUS NESTED LOOPS")

    values = list(range(100))

    print(f"Sequential-loop result: {two_sequential_loops(values)}")

    print(
        "\nSequential loops add their costs:\n"
        "  Θ(n) + Θ(n) = Θ(2n) = Θ(n).\n"
        "\n"
        "Nested loops generally multiply their costs:\n"
        "  Θ(n) * Θ(n) = Θ(n^2)."
    )


# ============================================================================
# 14. CONDITIONAL BRANCHES
# ============================================================================

def conditional_processing(values: Sequence[int], expensive: bool) -> int:
    """
    Demonstrate why the maximum relevant branch matters for worst-case analysis.
    """
    if expensive:
        total = 0

        for value in values:
            for other in values:
                total += value * other

        return total

    return sum(values)


def demonstrate_conditionals() -> None:
    print_section("14. CONDITIONAL BRANCHES")

    values = list(range(10))

    print("Cheap branch result:   ", conditional_processing(values, False))
    print("Expensive branch result:", conditional_processing(values, True))

    print(
        "\nIf one branch is Θ(n) and another is Θ(n^2), worst-case complexity "
        "is Θ(n^2), because the expensive branch dominates."
    )


# ============================================================================
# 15. BINARY SEARCH
# ============================================================================

def binary_search(values: Sequence[int], target: int) -> int:
    """
    Binary search on a sorted sequence.

    Each comparison approximately halves the remaining search space.

    Time:
        Best case: Ω(1)
        Worst case: O(log n)
        Tight worst-case classification: Θ(log n)

    Space:
        The iterative implementation uses Θ(1) auxiliary space.
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            return middle

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def demonstrate_binary_search() -> None:
    print_section("15. BINARY SEARCH: Θ(log n)")

    values = list(range(0, 100, 2))

    for target in (0, 38, 98, 99):
        index = binary_search(values, target)
        print(f"target={target:2} -> index={index}")

    print(
        "\nBinary search requires sorted data. Without the ordering property, "
        "the algorithm cannot safely discard half of the search space."
    )


# ============================================================================
# 16. MERGE SORT
# ============================================================================

def merge(left: Sequence[int], right: Sequence[int]) -> list[int]:
    """Merge two already sorted sequences in linear time."""
    merged: list[int] = []
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


def merge_sort(values: Sequence[int]) -> list[int]:
    """
    Merge sort.

    Recurrence:
        T(n) = 2T(n/2) + Θ(n)

    By the Master Theorem:
        T(n) = Θ(n log n)

    Auxiliary space:
        Θ(n) for the merged result.
    """
    if len(values) <= 1:
        return list(values)

    middle = len(values) // 2

    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    return merge(left, right)


def demonstrate_merge_sort() -> None:
    print_section("16. MERGE SORT: Θ(n log n)")

    values = [38, 27, 43, 3, 9, 82, 10]
    print("Input: ", values)
    print("Sorted:", merge_sort(values))

    print(
        "\nMerge sort repeatedly divides the input and then performs linear "
        "work while merging each level. There are Θ(log n) levels and Θ(n) "
        "work per level, producing Θ(n log n)."
    )


# ============================================================================
# 17. QUICKSORT
# ============================================================================

def quicksort(values: list[int]) -> list[int]:
    """
    Functional quicksort using the first element as pivot.

    Average-case time: Θ(n log n)
    Worst-case time: Θ(n^2)
    Auxiliary recursion/partition storage in this implementation varies.

    Choosing the first element as pivot is intentionally simple for teaching.
    Production implementations often use better pivot strategies or use a
    well-tested library sorting implementation.
    """
    if len(values) <= 1:
        return values.copy()

    pivot = values[0]

    less = [value for value in values[1:] if value < pivot]
    equal = [value for value in values[1:] if value == pivot]
    greater = [value for value in values[1:] if value > pivot]

    return quicksort(less) + [pivot] + equal + quicksort(greater)


def demonstrate_quicksort() -> None:
    print_section("17. QUICKSORT")

    values = [8, 3, 7, 4, 9, 2, 6, 5]
    print("Input: ", values)
    print("Sorted:", quicksort(values))

    print(
        "\nQuicksort demonstrates why average and worst-case analysis can differ.\n"
        "Balanced partitions give approximately log n recursion levels.\n"
        "Repeatedly choosing extremely unbalanced partitions can produce n "
        "levels and Θ(n^2) work."
    )


# ============================================================================
# 18. RECURSIVE FACTORIAL AND FIBONACCI
# ============================================================================

def factorial_recursive(n: int) -> int:
    """Recursive factorial: Θ(n) time and Θ(n) recursion-stack space."""
    if n < 0:
        raise ValueError("n must be non-negative")

    if n <= 1:
        return 1

    return n * factorial_recursive(n - 1)


def fibonacci_naive(n: int) -> int:
    """
    Naive recursive Fibonacci.

    This is exponential because the recursion tree repeatedly solves the
    same subproblems.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if n <= 1:
        return n

    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


def fibonacci_dynamic(n: int) -> int:
    """
    Dynamic-programming Fibonacci.

    Time: Θ(n)
    Space: Θ(n)
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if n <= 1:
        return n

    previous = 0
    current = 1

    for _ in range(2, n + 1):
        previous, current = current, previous + current

    return current


def fibonacci_constant_space(n: int) -> int:
    """
    Fibonacci with Θ(1) auxiliary space.

    Time: Θ(n)
    Auxiliary space: Θ(1)
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    previous = 0
    current = 1

    for _ in range(n):
        previous, current = current, previous + current

    return previous


def demonstrate_recursive_complexity() -> None:
    print_section("18. RECURSION AND COMPLEXITY")

    print("factorial_recursive(6):", factorial_recursive(6))
    print("fibonacci_naive(10):   ", fibonacci_naive(10))
    print("fibonacci_dynamic(30): ", fibonacci_dynamic(30))
    print("fibonacci_constant_space(30):", fibonacci_constant_space(30))

    print(
        "\nThe naive Fibonacci implementation illustrates a major principle: "
        "recursive code is not automatically logarithmic or efficient. Its "
        "recurrence must be analyzed."
    )


# ============================================================================
# 19. RECURRENCE ANALYSIS
# ============================================================================

def recurrence_examples() -> None:
    print_section("19. COMMON RECURRENCES")

    examples = [
        ("T(n) = T(n/2) + Θ(1)", "Θ(log n)", "Binary search"),
        ("T(n) = T(n-1) + Θ(1)", "Θ(n)", "Linear recursive process"),
        (
            "T(n) = 2T(n/2) + Θ(n)",
            "Θ(n log n)",
            "Merge sort",
        ),
        (
            "T(n) = 2T(n-1) + Θ(1)",
            "Θ(2^n)",
            "Naive Fibonacci-like recursion",
        ),
        (
            "T(n) = T(n/2) + Θ(n)",
            "Θ(n)",
            "Decreasing geometric work",
        ),
    ]

    for recurrence, complexity, example in examples:
        print(f"\n{recurrence}")
        print(f"  Complexity: {complexity}")
        print(f"  Example:    {example}")

    print(
        "\nRecurrences can be solved with substitution, recursion trees, the "
        "Master Theorem for applicable divide-and-conquer recurrences, or "
        "other mathematical techniques."
    )


# ============================================================================
# 20. MASTER THEOREM
# ============================================================================

def master_theorem_examples() -> None:
    print_section("20. MASTER THEOREM")

    print(
        "For recurrences of the form:\n"
        "  T(n) = aT(n/b) + f(n)\n"
        "\n"
        "compare f(n) with n^(log_b(a))."
    )

    cases = [
        (
            "T(n)=2T(n/2)+n",
            "n^(log2(2)) = n",
            "Θ(n log n)",
        ),
        (
            "T(n)=2T(n/2)+1",
            "n^(log2(2)) = n dominates 1",
            "Θ(n)",
        ),
        (
            "T(n)=4T(n/2)+n",
            "n^(log2(4)) = n^2",
            "Θ(n^2)",
        ),
    ]

    for recurrence, comparison, answer in cases:
        print(f"\n{recurrence}")
        print(f"  Comparison: {comparison}")
        print(f"  Result:     {answer}")


# ============================================================================
# 21. BEST, AVERAGE, AND WORST CASE
# ============================================================================

def classify_search_cases() -> None:
    print_section("21. BEST, AVERAGE, AND WORST CASE")

    print(
        "Linear search illustrates different input-dependent costs:\n\n"
        "Best case:\n"
        "  target is first -> Θ(1)\n\n"
        "Worst case:\n"
        "  target is absent or last -> Θ(n)\n\n"
        "Average case:\n"
        "  under a suitable random-position model -> Θ(n)\n"
    )

    print(
        "Big-O is frequently used informally for worst-case upper bounds, "
        "but mathematically O(g(n)) describes an upper bound on a function. "
        "It does not inherently mean 'worst case'."
    )


# ============================================================================
# 22. SPACE COMPLEXITY
# ============================================================================

def iterative_sum(values: Sequence[int]) -> int:
    """
    Sum a sequence.

    Time: Θ(n)
    Auxiliary space: Θ(1), excluding the input itself.
    """
    total = 0

    for value in values:
        total += value

    return total


def copied_sum(values: Sequence[int]) -> int:
    """
    Create an explicit copy before processing.

    Time: Θ(n)
    Auxiliary space: Θ(n)
    """
    copied_values = list(values)
    return sum(copied_values)


def demonstrate_space_complexity() -> None:
    print_section("22. SPACE COMPLEXITY")

    values = list(range(100))

    print("Iterative sum:", iterative_sum(values))
    print("Copied sum:   ", copied_sum(values))

    print(
        "\nTime and space complexity are separate dimensions.\n"
        "An algorithm can be fast but memory-intensive, or memory-efficient "
        "but slower. Recursive calls also consume call-stack space."
    )


# ============================================================================
# 23. AMORTIZED ANALYSIS
# ============================================================================

class SimpleDynamicArray:
    """
    A simplified dynamic-array implementation.

    When capacity is exhausted, the array doubles its capacity.

    Individual append operations can require Θ(n) copying during resizing,
    but across many appends the amortized cost per append is Θ(1).
    """

    def __init__(self) -> None:
        self._data: list[object | None] = [None]
        self._size = 0

    def append(self, value: object) -> None:
        if self._size == len(self._data):
            old_data = self._data
            self._data = [None] * (2 * len(old_data))

            for index, old_value in enumerate(old_data):
                self._data[index] = old_value

        self._data[self._size] = value
        self._size += 1

    @property
    def size(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._data)


def demonstrate_amortized_analysis() -> None:
    print_section("23. AMORTIZED ANALYSIS")

    dynamic_array = SimpleDynamicArray()

    for value in range(10):
        dynamic_array.append(value)
        print(
            f"append({value}) -> size={dynamic_array.size}, "
            f"capacity={dynamic_array.capacity}"
        )

    print(
        "\nA resize can cost Θ(n), so one append is not always Θ(1).\n"
        "With geometric capacity growth, the total copying across many "
        "appends is linear in the number of inserted elements. Therefore "
        "the amortized cost per append is Θ(1)."
    )


# ============================================================================
# 24. ALGORITHM COMPARISON
# ============================================================================

@dataclass(frozen=True)
class AlgorithmProfile:
    name: str
    best_case: str
    average_case: str
    worst_case: str
    auxiliary_space: str


def algorithm_profiles() -> list[AlgorithmProfile]:
    return [
        AlgorithmProfile(
            "Linear Search",
            "Θ(1)",
            "Θ(n)",
            "Θ(n)",
            "Θ(1)",
        ),
        AlgorithmProfile(
            "Binary Search",
            "Θ(1)",
            "Θ(log n)",
            "Θ(log n)",
            "Θ(1)",
        ),
        AlgorithmProfile(
            "Merge Sort",
            "Θ(n log n)",
            "Θ(n log n)",
            "Θ(n log n)",
            "Θ(n)",
        ),
        AlgorithmProfile(
            "Quicksort",
            "Θ(n log n)",
            "Θ(n log n)",
            "Θ(n^2)",
            "Implementation-dependent",
        ),
    ]


def print_algorithm_comparison() -> None:
    print_section("24. ALGORITHM COMPARISON")

    print(
        f"{'Algorithm':<18}"
        f"{'Best':<14}"
        f"{'Average':<14}"
        f"{'Worst':<14}"
        f"{'Aux. Space':<20}"
    )
    print("-" * 80)

    for profile in algorithm_profiles():
        print(
            f"{profile.name:<18}"
            f"{profile.best_case:<14}"
            f"{profile.average_case:<14}"
            f"{profile.worst_case:<14}"
            f"{profile.auxiliary_space:<20}"
        )


# ============================================================================
# 25. EXPERIMENTAL COMPARISON
# ============================================================================

def measure_runtime(
    function: Callable[[int], object],
    input_size: int,
    repetitions: int = 3,
) -> float:
    """Measure approximate execution time in seconds."""
    if repetitions <= 0:
        raise ValueError("repetitions must be positive")

    start = perf_counter()

    for _ in range(repetitions):
        function(input_size)

    elapsed = perf_counter() - start
    return elapsed / repetitions


def demonstrate_empirical_growth() -> None:
    print_section("25. EMPIRICAL GROWTH VERSUS ASYMPTOTIC ANALYSIS")

    print(
        "Small benchmark. Runtime varies by hardware, interpreter, operating "
        "system, system load, and implementation details. It is evidence, not "
        "a mathematical proof of complexity."
    )

    benchmark_functions = [
        ("linear", linear_work),
        ("quadratic", quadratic_work),
    ]

    for n in (100, 500, 1000):
        print(f"\nInput size n={n}")

        for name, function in benchmark_functions:
            elapsed = measure_runtime(function, n)
            print(f"  {name:<10}: {elapsed:.8f} seconds")

    print(
        "\nAsymptotic analysis and benchmarking answer different questions.\n"
        "Asymptotic analysis studies scaling behavior.\n"
        "Benchmarking measures actual performance under specific conditions."
    )


# ============================================================================
# 26. FORMAL BOUND CHECKING
# ============================================================================

def verify_upper_bound(
    f: Callable[[int], float],
    g: Callable[[int], float],
    constant: float,
    threshold: int,
    maximum_n: int = 100_000,
) -> bool:
    """
    Empirically verify f(n) <= constant*g(n) over a finite range.

    This cannot prove an asymptotic statement for all sufficiently large n.
    It only checks a finite interval.
    """
    if constant <= 0:
        raise ValueError("constant must be positive")

    if threshold < 1:
        raise ValueError("threshold must be positive")

    for n in range(threshold, maximum_n + 1):
        if f(n) > constant * g(n):
            return False

    return True


def verify_lower_bound(
    f: Callable[[int], float],
    g: Callable[[int], float],
    constant: float,
    threshold: int,
    maximum_n: int = 100_000,
) -> bool:
    """Empirically check c*g(n) <= f(n) over a finite range."""
    if constant <= 0:
        raise ValueError("constant must be positive")

    if threshold < 1:
        raise ValueError("threshold must be positive")

    for n in range(threshold, maximum_n + 1):
        if constant * g(n) > f(n):
            return False

    return True


def demonstrate_formal_bounds() -> None:
    print_section("26. FINITE CHECKS OF FORMAL BOUNDS")

    f = lambda n: 3 * n**2 + 7 * n + 10
    g = lambda n: n**2

    upper_holds = verify_upper_bound(f, g, constant=20, threshold=1)
    lower_holds = verify_lower_bound(f, g, constant=3, threshold=1)

    print("Upper bound f(n) <= 20n^2 for tested n:", upper_holds)
    print("Lower bound 3n^2 <= f(n) for tested n:", lower_holds)

    print(
        "\nTogether these inequalities support the classification Θ(n^2).\n"
        "A finite computational check is not a formal proof for all n; "
        "mathematical reasoning is required for a general proof."
    )


# ============================================================================
# 27. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    print_section("27. EDGE CASES")

    print("Empty linear search:", find_value_linear([], 5))
    print("Single-element search:", find_value_linear([5], 5))
    print("Single-element miss:", find_value_linear([5], 4))
    print("Empty merge sort:", merge_sort([]))
    print("Single merge sort:", merge_sort([7]))
    print("Duplicate quicksort:", quicksort([3, 3, 3, 1, 2, 2]))

    for invalid_n in (0, -1):
        try:
            logarithmic_work(invalid_n)
        except ValueError as error:
            print(f"logarithmic_work({invalid_n}) -> ValueError: {error}")

    print(
        "\nEdge cases matter because mathematical assumptions such as n > 0 "
        "may not hold for actual programs. Complexity analysis does not "
        "eliminate the need for input validation."
    )


# ============================================================================
# 28. COMMON MISTAKES
# ============================================================================

def demonstrate_common_mistakes() -> None:
    print_section("28. COMMON MISTAKES")

    mistakes = [
        (
            "Treating O(n^2) as an exact runtime",
            "Big-O describes an asymptotic upper bound, not exact execution time.",
        ),
        (
            "Assuming O(g(n)) means worst case",
            "O is mathematical notation; worst-case complexity requires a defined worst-case input measure.",
        ),
        (
            "Keeping every term in the final classification",
            "Asymptotic simplification removes constant factors and lower-order terms.",
        ),
        (
            "Assuming nested loops always mean Θ(n^2)",
            "Loop bounds may depend on each other or shrink geometrically.",
        ),
        (
            "Ignoring data ordering",
            "Binary search requires sorted data.",
        ),
        (
            "Ignoring recursion stack",
            "Recursive algorithms can use substantial auxiliary space.",
        ),
        (
            "Using benchmarks as proofs",
            "Measurements are environment-dependent and finite.",
        ),
        (
            "Confusing input value with input size",
            "For some problems, the number of bits needed to represent a value matters.",
        ),
    ]

    for mistake, correction in mistakes:
        print(f"\nMistake:    {mistake}")
        print(f"Correction: {correction}")


# ============================================================================
# 29. INPUT REPRESENTATION AND BIT COMPLEXITY
# ============================================================================

def bit_length_of_integer(value: int) -> int:
    """
    Return the number of bits needed to represent the magnitude of an integer.

    This highlights the distinction between treating an integer as a unit-size
    machine value and analyzing algorithms under a bit-complexity model.
    """
    if value == 0:
        return 1

    return abs(value).bit_length() + (1 if value < 0 else 0)


def demonstrate_bit_complexity() -> None:
    print_section("29. INPUT SIZE VERSUS NUMERICAL VALUE")

    for value in (7, 255, 256, 1_000_000, 10**100):
        print(
            f"value={value} -> approximate representation length="
            f"{bit_length_of_integer(value)} bits"
        )

    print(
        "\nIn a RAM-style model, fixed-width integers are often treated as "
        "constant-size objects. In a bit-complexity model, arithmetic cost can "
        "depend on the number of bits. This distinction becomes important for "
        "very large integers and exact computational complexity."
    )


# ============================================================================
# 30. GRAPH COMPLEXITY EXAMPLE
# ============================================================================

def graph_edge_scan(vertex_count: int, edges: Sequence[tuple[int, int]]) -> int:
    """
    Scan every edge once.

    Complexity:
        Θ(m), where m is the number of edges.
    """
    if vertex_count < 0:
        raise ValueError("vertex_count must be non-negative")

    processed = 0

    for source, destination in edges:
        if not (0 <= source < vertex_count):
            raise ValueError("invalid source vertex")

        if not (0 <= destination < vertex_count):
            raise ValueError("invalid destination vertex")

        processed += 1

    return processed


def demonstrate_multiple_input_parameters() -> None:
    print_section("30. MULTIPLE INPUT PARAMETERS")

    edges = [(0, 1), (1, 2), (2, 3), (3, 4)]

    print("Edges processed:", graph_edge_scan(5, edges))

    print(
        "\nFor graph algorithms, writing O(n) alone can be misleading.\n"
        "If n is the number of vertices and m is the number of edges, an "
        "algorithm might be O(n + m), O(nm), or O(m log n).\n"
        "The correct complexity should preserve independent input parameters "
        "when they can vary independently."
    )


# ============================================================================
# 31. LOWER-ORDER TERMS
# ============================================================================

def lower_order_demo(n: int) -> tuple[float, float]:
    """
    Compare a quadratic dominant term with its lower-order additions.
    """
    full_function = 3 * n**2 + 1000 * n + 1_000_000
    dominant_term = 3 * n**2

    return full_function, dominant_term


def demonstrate_dominant_term() -> None:
    print_section("31. DOMINANT TERMS")

    for n in (10, 100, 10_000, 1_000_000):
        full, dominant = lower_order_demo(n)
        ratio = full / dominant

        print(
            f"n={n:>8}: f(n)={full:.3e}, "
            f"dominant={dominant:.3e}, ratio={ratio:.6f}"
        )

    print(
        "\nThe lower-order terms can matter substantially for small n. "
        "They disappear from the asymptotic classification because their "
        "relative contribution tends toward zero as n grows."
    )


# ============================================================================
# 32. SPACE-TIME TRADE-OFF
# ============================================================================

def count_frequencies_without_extra_structure(values: Sequence[int]) -> dict[int, int]:
    """
    Count frequencies with a dictionary.

    Expected time: Θ(n)
    Auxiliary space: O(k), where k is the number of distinct values.
    """
    frequencies: dict[int, int] = {}

    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1

    return frequencies


def count_frequencies_quadratically(values: Sequence[int]) -> dict[int, int]:
    """
    Illustrative quadratic approach without a dictionary.

    This demonstrates a time-space trade-off.
    """
    frequencies: dict[int, int] = {}

    for index, value in enumerate(values):
        if value in frequencies:
            continue

        count = 0

        for other in values[index:]:
            if other == value:
                count += 1

        frequencies[value] = count

    return frequencies


def demonstrate_space_time_tradeoff() -> None:
    print_section("32. TIME-SPACE TRADE-OFF")

    values = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]

    print(
        "Dictionary approach:",
        count_frequencies_without_extra_structure(values),
    )
    print(
        "Quadratic approach: ",
        count_frequencies_quadratically(values),
    )

    print(
        "\nThe dictionary consumes additional memory but reduces repeated "
        "searching. Complexity analysis helps make this trade-off explicit."
    )


# ============================================================================
# 33. SECURITY AND RESOURCE CONSIDERATIONS
# ============================================================================

def demonstrate_resource_safety() -> None:
    print_section("33. SECURITY AND RESOURCE CONSIDERATIONS")

    print(
        "Asymptotic complexity has direct security implications when inputs "
        "can be controlled by untrusted users."
    )

    print(
        "\nExamples:\n"
        "  * An O(n^2) parser may become expensive when n is attacker-controlled.\n"
        "  * Exponential algorithms can become unusable with surprisingly small inputs.\n"
        "  * Excessive memory growth can produce denial-of-service conditions.\n"
        "  * Deep recursion can exhaust the call stack.\n"
        "  * Poor hash-table behavior can degrade expected performance under adversarial conditions.\n"
        "  * Unbounded input sizes should be validated and constrained."
    )

    print(
        "\nComplexity is not a complete security analysis. Constant factors, "
        "implementation behavior, memory allocation, concurrency, network "
        "latency, and adversarial input distributions also matter."
    )


# ============================================================================
# 34. PRODUCTION CONSIDERATIONS
# ============================================================================

def production_considerations() -> None:
    print_section("34. PRODUCTION CONSIDERATIONS")

    points = [
        "Choose an appropriate asymptotic class before optimizing constants.",
        "Measure real workloads after selecting a sound algorithm.",
        "Account for memory limits as well as CPU time.",
        "Consider input distributions rather than only theoretical worst cases.",
        "Use stable, well-tested library implementations when appropriate.",
        "Preserve independent parameters such as n and m in graph problems.",
        "Document assumptions such as sorted input or bounded key ranges.",
        "Set practical limits on externally supplied input.",
        "Consider latency, throughput, concurrency, and I/O separately.",
        "Do not sacrifice correctness merely to obtain a better asymptotic class.",
    ]

    for index, point in enumerate(points, start=1):
        print(f"{index:2}. {point}")


# ============================================================================
# 35. COMPLEXITY CLASSIFICATION EXERCISES
# ============================================================================

def exercise_one(n: int) -> int:
    """Θ(n)."""
    total = 0

    for _ in range(n):
        total += 1

    return total


def exercise_two(n: int) -> int:
    """Θ(n log n)."""
    total = 0

    for _ in range(n):
        value = n

        while value > 1:
            value //= 2
            total += 1

    return total


def exercise_three(n: int) -> int:
    """Θ(n^2)."""
    total = 0

    for i in range(n):
        for j in range(i, n):
            total += 1

    return total


def exercise_four(n: int) -> int:
    """Θ(log n)."""
    total = 0

    while n > 1:
        n //= 3
        total += 1

    return total


def exercise_five(n: int) -> int:
    """
    Θ(n) despite the nested appearance.

    The inner loop executes a constant number of times because its bound is 10.
    """
    total = 0

    for _ in range(n):
        for _ in range(10):
            total += 1

    return total


def demonstrate_classification_exercises() -> None:
    print_section("35. COMPLEXITY CLASSIFICATION EXERCISES")

    functions = [
        ("exercise_one", exercise_one, "Θ(n)"),
        ("exercise_two", exercise_two, "Θ(n log n)"),
        ("exercise_three", exercise_three, "Θ(n^2)"),
        ("exercise_four", exercise_four, "Θ(log n)"),
        ("exercise_five", exercise_five, "Θ(n)"),
    ]

    for name, function, expected in functions:
        result = function(100)
        print(f"{name:<18} result={result:<10} expected complexity={expected}")


# ============================================================================
# 36. SPECIAL CASE: SUMMATIONS
# ============================================================================

def demonstrate_summations() -> None:
    print_section("36. SUMMATION PATTERNS")

    print(
        "Important summations:\n"
        "\n"
        "1 + 1 + ... + 1, n terms\n"
        "    = n\n"
        "    = Θ(n)\n"
        "\n"
        "1 + 2 + ... + n\n"
        "    = n(n+1)/2\n"
        "    = Θ(n^2)\n"
        "\n"
        "1 + 2 + 4 + ... + 2^k\n"
        "    = Θ(2^k)\n"
        "\n"
        "1 + 1/2 + 1/4 + ...\n"
        "    = O(1) when the number of terms grows without exceeding the geometric-series limit."
    )

    for n in (10, 100, 1000):
        triangular = n * (n + 1) // 2
        print(f"n={n:4}: 1+...+n = {triangular}")


# ============================================================================
# 37. ASYMPTOTIC DOMINATION ORDER
# ============================================================================

def demonstrate_domination_order() -> None:
    print_section("37. TYPICAL GROWTH ORDER")

    print(
        "A common ordering from slower to faster growth is:\n\n"
        "Θ(1)\n"
        "  < Θ(log n)\n"
        "  < Θ(n)\n"
        "  < Θ(n log n)\n"
        "  < Θ(n^2)\n"
        "  < Θ(n^3)\n"
        "  < Θ(2^n)\n"
        "  < Θ(n!)\n"
        "\n"
        "This ordering is useful for comparison, but actual algorithm selection "
        "must consider constants, memory, data structure behavior, input size, "
        "and implementation details."
    )


# ============================================================================
# 38. COMMON NOTATION DISTINCTIONS
# ============================================================================

def notation_distinctions() -> None:
    print_section("38. IMPORTANT NOTATION DISTINCTIONS")

    distinctions = {
        "O(g(n))": "An asymptotic upper bound.",
        "Ω(g(n))": "An asymptotic lower bound.",
        "Θ(g(n))": "An asymptotically tight bound.",
        "o(g(n))": "A strict asymptotic upper relationship; f grows strictly slower than g.",
        "ω(g(n))": "A strict asymptotic lower relationship; f grows strictly faster than g.",
    }

    for notation, meaning in distinctions.items():
        print(f"{notation:<12} -> {meaning}")

    print(
        "\nLittle-o and little-omega are stronger relationships than Big-O and "
        "Big-Omega. For example, n is o(n^2), while n is O(n^2)."
    )


# ============================================================================
# 39. SMALL NUMBERS AND CONSTANT FACTORS
# ============================================================================

def demonstrate_small_input_behavior() -> None:
    print_section("39. ASYMPTOTICS DO NOT TELL THE WHOLE PERFORMANCE STORY")

    algorithms = {
        "A: 1000n": lambda n: 1000 * n,
        "B: n^2": lambda n: n**2,
    }

    for n in (10, 100, 1000, 10000):
        print(f"\nn={n}")

        for name, function in algorithms.items():
            print(f"  {name:<10}: {function(n):>15}")

    print(
        "\nFor sufficiently large n, Θ(n) eventually beats Θ(n^2), but the "
        "constant factor can make the quadratic algorithm faster for some "
        "small inputs. Asymptotic analysis describes eventual scaling, not "
        "every finite-input performance comparison."
    )


# ============================================================================
# 40. FINAL STUDY CHECK
# ============================================================================

def study_check() -> None:
    print_section("40. ASYMPTOTIC ANALYSIS CHECKLIST")

    checklist = [
        "Identify what constitutes input size n.",
        "Identify the resource being analyzed.",
        "Count the dominant operations.",
        "Determine whether loops are sequential, nested, or logarithmically shrinking.",
        "For recursion, write the recurrence.",
        "Remove constant factors for asymptotic classification.",
        "Remove lower-order terms.",
        "Distinguish upper, lower, and tight bounds.",
        "State whether the result describes best, average, or worst case.",
        "Analyze auxiliary space separately.",
        "Preserve multiple independent input parameters.",
        "Check edge cases and assumptions.",
        "Consider empirical performance for production decisions.",
        "Consider resource exhaustion when inputs are untrusted.",
    ]

    for index, item in enumerate(checklist, start=1):
        print(f"{index:2}. {item}")


# ============================================================================
# 41. MAIN DEMONSTRATION
# ============================================================================

def main() -> None:
    """Run the complete asymptotic-notation learning program."""
    explain_input_size()
    demonstrate_growth_rates()

    formal_definitions()
    demonstrate_big_o()
    demonstrate_big_omega()
    demonstrate_big_theta()
    notation_relationships()

    demonstrate_limit_method()
    demonstrate_simplification_rules()
    demonstrate_logarithm_bases()

    demonstrate_linear_algorithms()
    demonstrate_loop_analysis()
    demonstrate_sequential_loops()
    demonstrate_conditionals()

    demonstrate_binary_search()
    demonstrate_merge_sort()
    demonstrate_quicksort()

    demonstrate_recursive_complexity()
    recurrence_examples()
    master_theorem_examples()

    classify_search_cases()
    demonstrate_space_complexity()
    demonstrate_amortized_analysis()

    print_algorithm_comparison()
    demonstrate_empirical_growth()
    demonstrate_formal_bounds()

    demonstrate_edge_cases()
    demonstrate_common_mistakes()
    demonstrate_bit_complexity()
    demonstrate_multiple_input_parameters()
    demonstrate_dominant_term()
    demonstrate_space_time_tradeoff()

    demonstrate_resource_safety()
    production_considerations()

    demonstrate_classification_exercises()
    demonstrate_summations()
    demonstrate_domination_order()
    notation_distinctions()
    demonstrate_small_input_behavior()

    study_check()


if __name__ == "__main__":
    main()
