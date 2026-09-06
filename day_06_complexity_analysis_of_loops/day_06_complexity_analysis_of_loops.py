"""
Complexity Analysis of Loops
============================

A standalone study and demonstration script covering the complexity analysis of:

1. Single loops
2. Nested loops
3. Consecutive loops
4. Dependent loops
5. Logarithmic loops
6. Linearithmic loops
7. Combinations of loops
8. Triangular and geometric iteration patterns
9. Data-dependent loops
10. Early termination
11. Break and continue
12. Loop-dependent complexity
13. Recurrences caused by loop structure
14. Amortized loop behavior
15. Best, average, and worst cases
16. Exact operation counting
17. Big-O, Big-Theta, and Big-Omega
18. Common analysis mistakes
19. Performance measurement and validation
20. Practical optimization and production considerations

The script uses only the Python standard library.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Optional


# ============================================================================
# SECTION 1: FUNDAMENTAL TERMINOLOGY
# ============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def explain_basic_terminology() -> None:
    """
    Explain the fundamental vocabulary used when analyzing loops.

    Time complexity describes how the number of elementary operations grows
    as the input size n grows.

    Space complexity describes how additional memory grows with n.

    Big-O gives an asymptotic upper bound.
    Big-Omega gives an asymptotic lower bound.
    Big-Theta gives a tight asymptotic bound.

    The important point is that complexity analysis studies growth rather
    than wall-clock time. A Python implementation can be slower than another
    implementation with the same asymptotic complexity because of constants,
    interpreter overhead, memory behavior, and library implementation details.
    """
    section("1. Fundamental Terminology")

    terms = {
        "Input size (n)": (
            "A measure of how large the problem input is. For an array, "
            "n is commonly its number of elements."
        ),
        "Basic operation": (
            "An operation treated as constant-time for the chosen computational "
            "model, such as a simple arithmetic operation or comparison."
        ),
        "Time complexity": (
            "How the amount of computational work grows with input size."
        ),
        "Space complexity": (
            "How additional memory consumption grows with input size."
        ),
        "Big-O": "An asymptotic upper bound on growth.",
        "Big-Omega": "An asymptotic lower bound on growth.",
        "Big-Theta": "A tight asymptotic bound when upper and lower bounds match.",
        "Constant time": "O(1): the number of operations does not grow with n.",
        "Linear time": "O(n): work grows proportionally to n.",
        "Quadratic time": "O(n^2): work grows proportionally to n squared.",
        "Logarithmic time": "O(log n): each iteration reduces the remaining problem geometrically.",
        "Linearithmic time": "O(n log n): commonly produced by n work at each of log n levels.",
    }

    for name, description in terms.items():
        print(f"{name:22} -> {description}")


# ============================================================================
# SECTION 2: OPERATION COUNTERS
# ============================================================================

@dataclass
class OperationCounter:
    """Simple counter used to make loop operation counts observable."""

    comparisons: int = 0
    assignments: int = 0
    additions: int = 0
    multiplications: int = 0
    body_executions: int = 0

    @property
    def total(self) -> int:
        return (
            self.comparisons
            + self.assignments
            + self.additions
            + self.multiplications
        )

    def reset(self) -> None:
        self.comparisons = 0
        self.assignments = 0
        self.additions = 0
        self.multiplications = 0
        self.body_executions = 0


# ============================================================================
# SECTION 3: CONSTANT-TIME LOOPS
# ============================================================================

def constant_time_example(n: int) -> int:
    """
    O(1).

    The loop executes a fixed number of times independent of n.
    """
    total = 0

    for _ in range(5):
        total += 1

    return total


def demonstrate_constant_time() -> None:
    section("2. Constant-Time Loop")

    for n in [1, 10, 100, 1000, 1_000_000]:
        result = constant_time_example(n)
        print(f"n={n:>8}: result={result}, complexity=O(1)")


# ============================================================================
# SECTION 4: SINGLE LINEAR LOOPS
# ============================================================================

def linear_sum(n: int) -> int:
    """
    O(n).

    The loop executes once for every integer from 0 through n - 1.
    """
    total = 0

    for i in range(n):
        total += i

    return total


def linear_search(values: list[int], target: int) -> int:
    """
    O(n) worst case and O(1) best case.

    The search may terminate immediately or may inspect every element.
    """
    for index, value in enumerate(values):
        if value == target:
            return index

    return -1


def demonstrate_single_loops() -> None:
    section("3. Single Linear Loops")

    for n in [0, 1, 5, 10]:
        print(f"linear_sum({n}) = {linear_sum(n)}")

    values = list(range(10))

    print("Best case search:", linear_search(values, 0))
    print("Worst case search:", linear_search(values, 999))

    print(
        "linear_sum: O(n) time, O(1) auxiliary space\n"
        "linear_search: O(1) best-case time, O(n) worst-case time, O(1) space"
    )


# ============================================================================
# SECTION 5: EXACT COUNTING FOR A SINGLE LOOP
# ============================================================================

def counted_linear_loop(n: int, counter: OperationCounter) -> int:
    """
    Count important operations in a linear loop.

    The exact count depends on the selected cost model. The asymptotic result
    remains Theta(n).
    """
    total = 0
    counter.assignments += 1

    for i in range(n):
        counter.body_executions += 1
        counter.additions += 1
        total += i

    return total


def demonstrate_exact_linear_count() -> None:
    section("4. Exact Counting vs Asymptotic Counting")

    for n in [1, 5, 10, 100]:
        counter = OperationCounter()
        counted_linear_loop(n, counter)
        print(
            f"n={n:>3}, body executions={counter.body_executions:>3}, "
            f"additions={counter.additions:>3}, total counted={counter.total:>3}"
        )

    print("Exact operation counts can differ by cost model.")
    print("The asymptotic classification is Theta(n).")


# ============================================================================
# SECTION 6: NESTED LOOPS
# ============================================================================

def nested_product(n: int) -> int:
    """
    O(n^2).

    The inner loop executes n times for each of n outer iterations.
    """
    count = 0

    for _ in range(n):
        for _ in range(n):
            count += 1

    return count


def nested_different_sizes(n: int, m: int) -> int:
    """
    O(n*m).

    Two independent input dimensions should not automatically be combined
    into n^2. If n and m represent different quantities, retain both.
    """
    count = 0

    for _ in range(n):
        for _ in range(m):
            count += 1

    return count


def demonstrate_nested_loops() -> None:
    section("5. Nested Loops")

    for n in [1, 2, 5, 10]:
        executions = nested_product(n)
        print(f"n={n:>2}: inner-body executions={executions:>4}, expected=n^2={n*n}")

    print()
    print("If both dimensions are n: Theta(n^2).")
    print("If dimensions are different: Theta(n*m).")


# ============================================================================
# SECTION 7: NESTED LOOPS WITH NON-UNIFORM INNER WORK
# ============================================================================

def triangular_loop(n: int) -> int:
    """
    O(n^2).

    The inner loop executes:

        0 + 1 + 2 + ... + (n - 1)

    times, which equals n(n - 1)/2.
    """
    count = 0

    for i in range(n):
        for _ in range(i):
            count += 1

    return count


def demonstrate_triangular_loop() -> None:
    section("6. Triangular Nested Loops")

    for n in [0, 1, 2, 5, 10]:
        actual = triangular_loop(n)
        exact = n * (n - 1) // 2
        print(f"n={n:>2}: executions={actual:>3}, formula={exact:>3}")

    print("Although the inner loop is shorter for small i, the total is Theta(n^2).")


# ============================================================================
# SECTION 8: CONSECUTIVE LOOPS
# ============================================================================

def consecutive_loops(n: int) -> int:
    """
    O(n), not O(n^2).

    The first loop costs n and the second costs n, giving:

        n + n = 2n = Theta(n)
    """
    count = 0

    for _ in range(n):
        count += 1

    for _ in range(n):
        count += 1

    return count


def consecutive_different_sizes(n: int, m: int) -> int:
    """
    O(n + m).

    Separate loops over separate inputs add their costs.
    """
    count = 0

    for _ in range(n):
        count += 1

    for _ in range(m):
        count += 1

    return count


def demonstrate_consecutive_loops() -> None:
    section("7. Consecutive Loops")

    for n in [1, 5, 10]:
        print(
            f"n={n:>2}: executions={consecutive_loops(n):>3}, "
            f"formula=2n={2*n:>3}"
        )

    print("Two consecutive O(n) loops produce O(2n), which simplifies to O(n).")
    print("Different inputs produce O(n + m).")


# ============================================================================
# SECTION 9: LOGARITHMIC LOOPS
# ============================================================================

def logarithmic_loop(n: int) -> int:
    """
    O(log n).

    Multiplying the loop variable by 2 means the number of iterations is
    approximately log base 2 of n.
    """
    if n <= 1:
        return 0

    value = 1
    iterations = 0

    while value < n:
        value *= 2
        iterations += 1

    return iterations


def logarithmic_halving_loop(n: int) -> int:
    """
    O(log n).

    Integer division by 2 repeatedly reduces the remaining quantity
    geometrically.
    """
    iterations = 0
    while n > 1:
        n //= 2
        iterations += 1

    return iterations


def demonstrate_logarithmic_loops() -> None:
    section("8. Logarithmic Loops")

    for n in [1, 2, 4, 8, 16, 32, 100, 1000, 1_000_000]:
        print(
            f"n={n:>8}: doubling iterations={logarithmic_loop(n):>3}, "
            f"halving iterations={logarithmic_halving_loop(n):>3}"
        )

    print("Geometric growth or reduction generally produces logarithmic iteration counts.")


# ============================================================================
# SECTION 10: LOGARITHMS WITH DIFFERENT BASES
# ============================================================================

def compare_log_bases(n: int, bases: Iterable[int]) -> None:
    """
    Demonstrate that constant logarithm bases have the same asymptotic class.

    log_a(n) = log_b(n) / log_b(a)

    The conversion factor is constant for fixed a and b.
    """
    print(f"n={n}")
    for base in bases:
        value = math.log(n, base)
        print(f"  log base {base}: {value:.4f}")


def demonstrate_log_bases() -> None:
    section("9. Logarithm Bases")

    compare_log_bases(1_000_000, [2, 3, 10])

    print("O(log_2 n), O(log_3 n), and O(log_10 n) are all O(log n).")
    print("The base matters for exact counts but not for asymptotic classification.")


# ============================================================================
# SECTION 11: LOGARITHMIC INNER LOOPS
# ============================================================================

def linear_outer_log_inner(n: int) -> int:
    """
    O(n log n).

    The outer loop runs n times.
    The inner loop doubles a value, producing O(log n) work per outer iteration.
    """
    count = 0

    for _ in range(n):
        value = 1
        while value < n:
            value *= 2
            count += 1

    return count


def demonstrate_linearithmic_loop() -> None:
    section("10. O(n log n) Combination")

    for n in [2, 4, 8, 16, 32]:
        executions = linear_outer_log_inner(n)
        print(f"n={n:>2}: inner executions={executions:>4}")

    print("n outer iterations multiplied by log(n) inner iterations gives Theta(n log n).")


# ============================================================================
# SECTION 12: DEPENDENT LOOPS
# ============================================================================

def dependent_inner_loop(n: int) -> int:
    """
    O(n^2).

    The inner loop's limit depends on the outer-loop variable.

        i = 0 -> 0 iterations
        i = 1 -> 1 iteration
        ...
        i = n-1 -> n-1 iterations

    Total = n(n-1)/2.
    """
    count = 0

    for i in range(n):
        for _ in range(i):
            count += 1

    return count


def demonstrate_dependent_loops() -> None:
    section("11. Dependent Loops")

    for n in [1, 2, 5, 10, 100]:
        actual = dependent_inner_loop(n)
        formula = n * (n - 1) // 2
        print(f"n={n:>3}: actual={actual:>5}, formula={formula:>5}")

    print("The inner bound depends on i, but the total remains Theta(n^2).")


# ============================================================================
# SECTION 13: INNER LOOP STARTS AT OUTER VARIABLE
# ============================================================================

def upper_triangle_loop(n: int) -> int:
    """
    O(n^2).

    Number of executions:

        n + (n-1) + ... + 1 = n(n+1)/2
    """
    count = 0

    for i in range(n):
        for j in range(i, n):
            count += 1

    return count


def demonstrate_upper_triangle() -> None:
    section("12. Upper-Triangle Iteration")

    for n in [1, 2, 5, 10]:
        actual = upper_triangle_loop(n)
        exact = n * (n + 1) // 2
        print(f"n={n:>2}: executions={actual:>3}, exact={exact:>3}")

    print("A triangular sum is still quadratic: Theta(n^2).")


# ============================================================================
# SECTION 14: THREE NESTED LOOPS
# ============================================================================

def cubic_loop(n: int) -> int:
    """
    O(n^3).

    Three independent loops, each with n iterations.
    """
    count = 0

    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                count += 1

    return count


def demonstrate_cubic_loops() -> None:
    section("13. Three Nested Loops")

    for n in [1, 2, 3, 5]:
        actual = cubic_loop(n)
        print(f"n={n}: executions={actual}, expected={n**3}")

    print("Three independent nested loops with n iterations each give Theta(n^3).")


# ============================================================================
# SECTION 15: MIXED NESTING
# ============================================================================

def mixed_nested_structure(n: int) -> int:
    """
    O(n^3).

    For every outer iteration:
      - one linear loop runs n times
      - another nested pair runs n^2 times

    Their sum is n + n^2 = Theta(n^2) per outer iteration.
    Multiplying by n gives Theta(n^3).
    """
    count = 0

    for _ in range(n):
        for _ in range(n):
            count += 1

        for _ in range(n):
            for _ in range(n):
                count += 1

    return count


def demonstrate_mixed_nesting() -> None:
    section("14. Mixed Nested Structure")

    for n in [1, 2, 3, 5]:
        actual = mixed_nested_structure(n)
        expected = n * (n + n * n)
        print(f"n={n}: executions={actual}, exact expression={expected}")

    print("Per outer iteration: n + n^2. Total: n(n + n^2) = n^2 + n^3.")
    print("Dominant term: Theta(n^3).")


# ============================================================================
# SECTION 16: LOOP WHERE THE VARIABLE INCREASES BY A FIXED AMOUNT
# ============================================================================

def fixed_increment_loop(n: int, step: int = 3) -> int:
    """
    O(n).

    Increasing by a fixed constant changes only the constant factor:

        n / 3 = Theta(n)
    """
    if step <= 0:
        raise ValueError("step must be positive")

    count = 0

    for _ in range(0, n, step):
        count += 1

    return count


def demonstrate_fixed_increment() -> None:
    section("15. Fixed-Step Loops")

    for n in [10, 30, 100]:
        print(f"n={n:>3}: step=3 iterations={fixed_increment_loop(n)}")

    print("A fixed step still produces Theta(n).")


# ============================================================================
# SECTION 17: EXPONENTIAL ITERATION
# ============================================================================

def exponential_growth_loop(n: int) -> int:
    """
    Demonstrate a loop whose state grows exponentially.

    This loop itself is O(log n), because the variable reaches n after
    logarithmically many doublings.
    """
    value = 1
    iterations = 0

    while value <= n:
        value *= 2
        iterations += 1

    return iterations


def demonstrate_exponential_state_growth() -> None:
    section("16. Exponentially Growing Loop Variables")

    for n in [1, 2, 4, 8, 16, 64, 1024]:
        print(
            f"n={n:>4}: iterations={exponential_growth_loop(n):>3}, "
            f"approximately log2(n)+1={math.floor(math.log2(n)) + 1}"
        )


# ============================================================================
# SECTION 18: LOGARITHMIC BASE OTHER THAN 2
# ============================================================================

def base_k_logarithmic_loop(n: int, factor: int) -> int:
    """
    O(log_k n), which is O(log n) for fixed k.

    Example:
        value *= 10
    produces approximately log_10(n) iterations.
    """
    if n <= 1:
        return 0

    if factor <= 1:
        raise ValueError("factor must be greater than 1")

    value = 1
    iterations = 0

    while value < n:
        value *= factor
        iterations += 1

    return iterations


def demonstrate_base_k() -> None:
    section("17. Logarithmic Loops with Arbitrary Bases")

    for factor in [2, 3, 10]:
        print(
            f"factor={factor}: iterations for n=1,000,000 -> "
            f"{base_k_logarithmic_loop(1_000_000, factor)}"
        )


# ============================================================================
# SECTION 19: WHILE LOOP THAT DECREASES BY A CONSTANT
# ============================================================================

def decrement_by_constant(n: int, step: int = 1) -> int:
    """
    O(n).

    Subtracting a fixed constant reduces the value linearly.
    """
    if step <= 0:
        raise ValueError("step must be positive")

    iterations = 0

    while n > 0:
        n -= step
        iterations += 1

    return iterations


def demonstrate_decrement_loop() -> None:
    section("18. Constant Decrement")

    for n in [0, 1, 5, 10]:
        print(f"n={n:>2}: iterations={decrement_by_constant(n)}")

    print("Subtracting a fixed constant produces Theta(n).")


# ============================================================================
# SECTION 20: WHILE LOOP WITH FRACTIONAL REDUCTION
# ============================================================================

def repeatedly_reduce_by_half(n: int) -> int:
    """
    O(log n).

    Replacing n with approximately n/2 each iteration is geometric reduction.
    """
    iterations = 0

    while n > 1:
        n //= 2
        iterations += 1

    return iterations


def demonstrate_fractional_reduction() -> None:
    section("19. Fractional Reduction")

    for n in [2, 4, 8, 16, 32, 64, 1024]:
        print(f"n={n:>4}: iterations={repeatedly_reduce_by_half(n)}")

    print("Reducing the state by a constant fraction gives Theta(log n).")


# ============================================================================
# SECTION 21: LOOP WITH MULTIPLICATIVE REDUCTION
# ============================================================================

def reduce_by_factor(n: int, factor: int) -> int:
    """
    O(log n) for any fixed factor > 1.
    """
    if factor <= 1:
        raise ValueError("factor must be greater than 1")

    iterations = 0

    while n > 1:
        n //= factor
        iterations += 1

    return iterations


def demonstrate_reduction_factor() -> None:
    section("20. General Multiplicative Reduction")

    for factor in [2, 3, 5, 10]:
        print(
            f"factor={factor}: n=1,000,000 -> "
            f"{reduce_by_factor(1_000_000, factor)} iterations"
        )


# ============================================================================
# SECTION 22: BREAK AND BEST/WORST CASE
# ============================================================================

def find_with_break(values: list[int], target: int) -> int:
    """
    Best case: O(1)
    Worst case: O(n)

    The break does not automatically make the algorithm O(1).
    We analyze how much work can occur before the break.
    """
    for value in values:
        if value == target:
            return value

    return -1


def demonstrate_break() -> None:
    section("21. Early Termination and Break")

    values = list(range(100))

    print("Target at beginning:", find_with_break(values, 0))
    print("Target near end:", find_with_break(values, 98))
    print("Target absent:", find_with_break(values, 999))

    print("Best case is O(1); worst case is O(n).")


# ============================================================================
# SECTION 23: BREAK IN NESTED LOOPS
# ============================================================================

def nested_search_with_break(matrix: list[list[int]], target: int) -> tuple[int, int]:
    """
    Worst-case O(rows * columns).

    A break exits only the loop containing it. The outer loop may continue.
    """
    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if value == target:
                return row_index, column_index

    return -1, -1


def demonstrate_nested_break() -> None:
    section("22. Break in Nested Loops")

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    print("Search result:", nested_search_with_break(matrix, 8))
    print("Worst-case complexity for an r x c matrix: O(r*c).")


# ============================================================================
# SECTION 24: CONTINUE DOES NOT REMOVE ITERATIONS
# ============================================================================

def sum_positive(values: list[int]) -> int:
    """
    O(n).

    continue skips part of the body but the loop still examines each element.
    """
    total = 0

    for value in values:
        if value <= 0:
            continue
        total += value

    return total


def demonstrate_continue() -> None:
    section("23. Continue")

    values = [-5, 2, -1, 4, 7, -3]
    print("Positive sum:", sum_positive(values))
    print("Complexity remains O(n), because every input element is inspected.")


# ============================================================================
# SECTION 25: CONDITIONAL INNER LOOP
# ============================================================================

def conditional_inner_loop(n: int) -> int:
    """
    O(n^2) worst case.

    Even though the inner loop executes conditionally, the worst case can
    execute it for every outer iteration.
    """
    count = 0

    for i in range(n):
        if i % 2 == 0:
            for _ in range(n):
                count += 1

    return count


def demonstrate_conditional_inner_loop() -> None:
    section("24. Conditional Nested Loops")

    for n in [2, 5, 10]:
        print(f"n={n}: executions={conditional_inner_loop(n)}")

    print("Only about half of outer iterations invoke the inner loop.")
    print("Half is a constant factor, so worst-case complexity is Theta(n^2).")


# ============================================================================
# SECTION 26: GEOMETRIC NUMBER OF INNER ITERATIONS
# ============================================================================

def geometric_nested_loop(n: int) -> int:
    """
    O(n).

    For each outer iteration, the inner loop runs 1, 2, 4, 8, ...
    until reaching n. That is O(log n) per outer iteration only if the
    geometric loop is independent of the outer iteration.

    Here the geometric sequence is bounded globally and each outer iteration
    repeats it, so the result is O(n log n).
    """
    count = 0

    for _ in range(n):
        value = 1

        while value <= n:
            count += 1
            value *= 2

    return count


def demonstrate_geometric_nested_loop() -> None:
    section("25. Geometric Inner Loop")

    for n in [2, 4, 8, 16, 32]:
        actual = geometric_nested_loop(n)
        expected_scale = n * (math.floor(math.log2(n)) + 1)
        print(
            f"n={n:>2}: executions={actual:>4}, "
            f"n*(floor(log2(n))+1)={expected_scale:>4}"
        )

    print("Outer O(n) multiplied by inner O(log n) gives O(n log n).")


# ============================================================================
# SECTION 27: LOOP WITH INNER BOUND DEPENDING ON OUTER VALUE
# ============================================================================

def dependent_logarithmic_loop(n: int) -> int:
    """
    O(n log n).

    The inner loop runs approximately log(i) times for each i.

        sum_{i=1}^{n} log(i) = log(n!)

    and log(n!) = Theta(n log n).
    """
    count = 0

    for i in range(1, n + 1):
        value = 1

        while value <= i:
            count += 1
            value *= 2

    return count


def demonstrate_dependent_log_loop() -> None:
    section("26. Dependent Logarithmic Loop")

    for n in [2, 4, 8, 16, 32, 64]:
        actual = dependent_logarithmic_loop(n)
        print(f"n={n:>2}: executions={actual:>5}")

    print("The total is Theta(n log n), not Theta(n^2).")


# ============================================================================
# SECTION 28: SUMMATION-BASED ANALYSIS
# ============================================================================

def summation_examples() -> None:
    """
    Display common summations that arise during loop analysis.
    """
    section("27. Common Summations")

    print("1 + 1 + ... + 1 (n terms) = n              -> Theta(n)")
    print("1 + 2 + ... + n = n(n+1)/2                  -> Theta(n^2)")
    print("1 + 2 + ... + n^2                            -> Theta(n^4)")
    print("1 + 2 + 4 + ... + 2^k                       -> Theta(2^k)")
    print("log(1) + log(2) + ... + log(n)              -> Theta(n log n)")
    print("n + n + ... + n (n terms)                    -> Theta(n^2)")
    print("n + n/2 + n/4 + ...                          -> Theta(n)")


# ============================================================================
# SECTION 29: HARMONIC LOOP
# ============================================================================

def harmonic_nested_loop(n: int) -> int:
    """
    O(n log n).

    For each i, the inner loop runs approximately n/i times.

        sum_{i=1}^{n} n/i = n * H_n = Theta(n log n)
    """
    count = 0

    for i in range(1, n + 1):
        j = i

        while j <= n:
            count += 1
            j += i

    return count


def demonstrate_harmonic_loop() -> None:
    section("28. Harmonic Nested Loop")

    for n in [10, 100, 1000]:
        actual = harmonic_nested_loop(n)
        ratio = actual / (n * math.log(n)) if n > 1 else 0
        print(
            f"n={n:>4}: executions={actual:>6}, "
            f"executions/(n log n)={ratio:.4f}"
        )

    print("The sum n/1 + n/2 + ... + n/n is Theta(n log n).")


# ============================================================================
# SECTION 30: DIVISOR ENUMERATION
# ============================================================================

def divisor_count_by_scan(n: int) -> int:
    """
    O(n).

    Checks every integer from 1 through n.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    count = 0

    for candidate in range(1, n + 1):
        if n % candidate == 0:
            count += 1

    return count


def divisor_count_by_square_root(n: int) -> int:
    """
    O(sqrt(n)).

    Divisors occur in pairs. If d divides n, n/d is another divisor.
    Only candidates through sqrt(n) need to be tested.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    count = 0
    candidate = 1

    while candidate * candidate <= n:
        if n % candidate == 0:
            count += 1
            if candidate != n // candidate:
                count += 1

        candidate += 1

    return count


def demonstrate_sqrt_complexity() -> None:
    section("29. O(sqrt(n)) Loop Pattern")

    for n in [1, 10, 36, 100, 9973]:
        scan = divisor_count_by_scan(n)
        optimized = divisor_count_by_square_root(n)
        print(
            f"n={n:>5}: divisors={scan:>3}, "
            f"sqrt-method={optimized:>3}, "
            f"sqrt(n)={math.sqrt(n):.2f}"
        )

    print("Checking up to sqrt(n) is asymptotically faster than checking up to n.")


# ============================================================================
# SECTION 31: PRIME TESTING
# ============================================================================

def is_prime_slow(n: int) -> bool:
    """
    O(n) worst-case loop iterations.
    """
    if n < 2:
        return False

    for candidate in range(2, n):
        if n % candidate == 0:
            return False

    return True


def is_prime_sqrt(n: int) -> bool:
    """
    O(sqrt(n)) worst-case.

    Once candidate exceeds sqrt(n), a smaller factor would already have
    been found if one existed.
    """
    if n < 2:
        return False

    candidate = 2

    while candidate * candidate <= n:
        if n % candidate == 0:
            return False
        candidate += 1

    return True


def demonstrate_prime_testing() -> None:
    section("30. Complexity Optimization: O(n) to O(sqrt(n))")

    for n in [2, 3, 17, 49, 97, 9973]:
        print(
            f"{n:>5}: slow={is_prime_slow(n)}, "
            f"sqrt={is_prime_sqrt(n)}"
        )


# ============================================================================
# SECTION 32: THREE DIFFERENT INPUT SIZES
# ============================================================================

def three_parameter_algorithm(a: int, b: int, c: int) -> int:
    """
    O(a*b + c).

    The nested loops depend on a and b.
    The final loop depends independently on c.
    """
    count = 0

    for _ in range(a):
        for _ in range(b):
            count += 1

    for _ in range(c):
        count += 1

    return count


def demonstrate_multiple_parameters() -> None:
    section("31. Multiple Input Parameters")

    a, b, c = 3, 4, 5
    result = three_parameter_algorithm(a, b, c)

    print(f"a={a}, b={b}, c={c}")
    print(f"work={result}")
    print("Complexity: Theta(a*b + c).")
    print("Do not replace a, b, and c with one n unless the problem explicitly relates them.")


# ============================================================================
# SECTION 33: COMBINATIONS OF LOOPS
# ============================================================================

def combination_one(n: int) -> int:
    """
    O(n^2 + n) = O(n^2).
    """
    count = 0

    for _ in range(n):
        for _ in range(n):
            count += 1

    for _ in range(n):
        count += 1

    return count


def combination_two(n: int) -> int:
    """
    O(n log n + n^2) = O(n^2).
    """
    count = 0

    for _ in range(n):
        value = 1
        while value < n:
            count += 1
            value *= 2

    for _ in range(n):
        for _ in range(n):
            count += 1

    return count


def combination_three(n: int) -> int:
    """
    O(n^3 + n^2 + n log n) = O(n^3).
    """
    count = 0

    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                count += 1

    for _ in range(n):
        for _ in range(n):
            count += 1

    for _ in range(n):
        value = 1
        while value < n:
            count += 1
            value *= 2

    return count


def demonstrate_combinations() -> None:
    section("32. Combining Different Loop Complexities")

    for n in [2, 4, 8]:
        print(
            f"n={n}: "
            f"combination_one={combination_one(n)}, "
            f"combination_two={combination_two(n)}, "
            f"combination_three={combination_three(n)}"
        )

    print("When sequential terms are added, the asymptotically largest term dominates.")


# ============================================================================
# SECTION 34: DOMINANT TERM RULE
# ============================================================================

def demonstrate_dominant_terms() -> None:
    section("33. Dominant-Term Simplification")

    expressions = [
        ("3n + 10", "Theta(n)"),
        ("7n^2 + 3n + 100", "Theta(n^2)"),
        ("n^3 + 100n^2 + n", "Theta(n^3)"),
        ("n log n + n", "Theta(n log n)"),
        ("n^2 + n log n + n", "Theta(n^2)"),
        ("2^n + n^10", "Theta(2^n)"),
    ]

    for expression, classification in expressions:
        print(f"{expression:30} -> {classification}")


# ============================================================================
# SECTION 35: BEST, AVERAGE, AND WORST CASE
# ============================================================================

def first_match_position(values: list[int], target: int) -> Optional[int]:
    """
    Best case O(1), worst case O(n).

    Average complexity depends on the probability distribution of target
    positions and whether the target is guaranteed to exist.
    """
    for index, value in enumerate(values):
        if value == target:
            return index

    return None


def demonstrate_cases() -> None:
    section("34. Best, Average, and Worst Cases")

    values = list(range(10))

    for target in [0, 5, 9, 100]:
        print(f"target={target:>3}: position={first_match_position(values, target)}")

    print("Best case: target at index 0 -> O(1).")
    print("Worst case: target at last index or absent -> O(n).")
    print("Average case requires assumptions about input distribution.")


# ============================================================================
# SECTION 36: EARLY EXIT IN A NESTED LOOP
# ============================================================================

def pair_exists(values: list[int], target_sum: int) -> bool:
    """
    O(n^2) worst case.

    Early return can make practical execution much faster, but does not
    change the worst-case asymptotic bound.
    """
    n = len(values)

    for i in range(n):
        for j in range(i + 1, n):
            if values[i] + values[j] == target_sum:
                return True

    return False


def demonstrate_early_nested_exit() -> None:
    section("35. Early Exit Does Not Necessarily Change Worst-Case Complexity")

    values = [1, 3, 8, 10]

    print("Existing pair:", pair_exists(values, 11))
    print("Missing pair:", pair_exists(values, 100))

    print("Worst-case complexity remains O(n^2).")


# ============================================================================
# SECTION 37: LOOP WITH A DATA-DEPENDENT CONDITION
# ============================================================================

def consume_until_threshold(values: list[int], threshold: int) -> int:
    """
    O(n) worst case.

    Actual iterations depend on the data.
    """
    total = 0
    processed = 0

    for value in values:
        total += value
        processed += 1

        if total >= threshold:
            break

    return processed


def demonstrate_data_dependent_loop() -> None:
    section("36. Data-Dependent Loop Termination")

    values = [10, 20, 30, 40, 50]

    for threshold in [5, 25, 100, 1000]:
        processed = consume_until_threshold(values, threshold)
        print(f"threshold={threshold:>4}: processed={processed}")

    print("The actual count depends on the data, but worst case is O(n).")


# ============================================================================
# SECTION 38: LOOP INVARIANTS
# ============================================================================

def sum_with_invariant(values: list[int]) -> int:
    """
    O(n).

    Loop invariant:
        Before processing values[i], total equals the sum of all elements
        processed before i.

    The invariant helps reason about correctness rather than directly changing
    complexity, but it is an important tool for analyzing loops rigorously.
    """
    total = 0

    for value in values:
        total += value

    return total


def demonstrate_loop_invariant() -> None:
    section("37. Loop Invariants")

    values = [2, 4, 6, 8]
    print("Values:", values)
    print("Sum:", sum_with_invariant(values))
    print(
        "A loop invariant is a statement that remains true at a defined point "
        "of every iteration."
    )


# ============================================================================
# SECTION 39: AMORTIZED LOOP BEHAVIOR
# ============================================================================

class DynamicArraySimulator:
    """
    Simplified dynamic-array model.

    Individual append operations can require O(n) copying when capacity is
    exhausted, but geometric capacity growth makes the amortized cost of
    append O(1).

    This simulator counts element copies rather than implementing Python's
    actual list internals.
    """

    def __init__(self) -> None:
        self.data: list[Optional[int]] = []
        self.size = 0
        self.capacity = 0
        self.copy_operations = 0

    def append(self, value: int) -> None:
        if self.size == self.capacity:
            new_capacity = 1 if self.capacity == 0 else self.capacity * 2
            new_data: list[Optional[int]] = [None] * new_capacity

            for index in range(self.size):
                new_data[index] = self.data[index]
                self.copy_operations += 1

            self.data = new_data
            self.capacity = new_capacity

        self.data[self.size] = value
        self.size += 1


def demonstrate_amortized_complexity() -> None:
    section("38. Amortized Loop Complexity")

    simulator = DynamicArraySimulator()

    for value in range(20):
        before = simulator.copy_operations
        simulator.append(value)
        copies = simulator.copy_operations - before

        print(
            f"append={value:>2}: capacity={simulator.capacity:>2}, "
            f"copies_this_append={copies}"
        )

    print(
        "Some individual appends cost O(n), but geometric resizing makes "
        "the amortized cost per append O(1)."
    )


# ============================================================================
# SECTION 40: TWO POINTERS
# ============================================================================

def two_pointer_sum_exists(values: list[int], target: int) -> bool:
    """
    O(n) for a sorted list.

    Two indices move inward. Although there are two pointers, this is not
    automatically O(n^2). Each pointer moves monotonically and performs at
    most O(n) total movement.
    """
    left = 0
    right = len(values) - 1

    while left < right:
        current = values[left] + values[right]

        if current == target:
            return True

        if current < target:
            left += 1
        else:
            right -= 1

    return False


def demonstrate_two_pointers() -> None:
    section("39. Two Pointers Are Not Automatically Quadratic")

    values = [1, 2, 4, 7, 11, 15]
    print("Target 15:", two_pointer_sum_exists(values, 15))
    print("Target 100:", two_pointer_sum_exists(values, 100))

    print(
        "Because each pointer moves at most n times, total loop movement is "
        "O(n), not O(n^2)."
    )


# ============================================================================
# SECTION 41: MONOTONIC POINTERS IN NESTED-LOOKING STRUCTURES
# ============================================================================

def monotonic_inner_pointer(values: list[int], threshold: int) -> int:
    """
    O(n), despite the apparent nested structure.

    The pointer j never moves backward. Across all outer iterations, j makes
    at most n total increments.

    This is a crucial exception to the simplistic rule:
    "nested loops always mean O(n^2)."
    """
    j = 0
    count = 0
    n = len(values)

    for i in range(n):
        while j < n and values[j] - values[i] < threshold:
            j += 1
            count += 1

    return count


def demonstrate_monotonic_pointer() -> None:
    section("40. Nested Syntax Does Not Always Mean O(n^2)")

    values = list(range(100))
    print("Counted inner-pointer movements:", monotonic_inner_pointer(values, 10))

    print(
        "The while loop is nested syntactically, but j only increases globally "
        "up to n times. This pattern is O(n) for monotonic input-pointer behavior."
    )


# ============================================================================
# SECTION 42: BINARY SEARCH LOOP
# ============================================================================

def binary_search(values: list[int], target: int) -> int:
    """
    O(log n) worst-case time and O(1) auxiliary space.

    Each iteration discards approximately half of the remaining search space.
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
    section("41. Binary Search")

    values = list(range(0, 100, 2))

    for target in [0, 20, 98, 99]:
        print(f"target={target:>2}: index={binary_search(values, target)}")

    print("Binary search repeatedly halves the search interval: O(log n).")


# ============================================================================
# SECTION 43: LINEAR SEARCH VS BINARY SEARCH
# ============================================================================

def demonstrate_search_comparison() -> None:
    section("42. Linear Search vs Binary Search")

    print("Linear search:")
    print("  Best: O(1)")
    print("  Worst: O(n)")
    print("  Requires sorted data? No")

    print()
    print("Binary search:")
    print("  Best: O(1)")
    print("  Worst: O(log n)")
    print("  Requires sorted/random-access-compatible structure? Yes")


# ============================================================================
# SECTION 44: NESTED LOOP WITH SQUARE ROOT BOUND
# ============================================================================

def sqrt_bounded_nested_loop(n: int) -> int:
    """
    O(n * sqrt(n)).

    Outer loop: n.
    Inner loop: sqrt(n).
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    inner_limit = math.isqrt(n)
    count = 0

    for _ in range(n):
        for _ in range(inner_limit):
            count += 1

    return count


def demonstrate_sqrt_nested_loop() -> None:
    section("43. O(n sqrt(n))")

    for n in [4, 16, 100, 400]:
        print(
            f"n={n:>3}: executions={sqrt_bounded_nested_loop(n):>6}, "
            f"n*sqrt(n)={n * math.isqrt(n):>6}"
        )


# ============================================================================
# SECTION 45: POLYNOMIAL COMBINATIONS
# ============================================================================

def polynomial_loop_combination(n: int) -> int:
    """
    O(n^4 + n^2 + n).

    The quartic term dominates.
    """
    count = 0

    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                for _ in range(n):
                    count += 1

    for _ in range(n):
        for _ in range(n):
            count += 1

    for _ in range(n):
        count += 1

    return count


def demonstrate_polynomial_combination() -> None:
    section("44. Polynomial Combination")

    for n in [1, 2, 3]:
        result = polynomial_loop_combination(n)
        expected = n**4 + n**2 + n
        print(f"n={n}: actual={result}, exact={expected}")

    print("Theta(n^4 + n^2 + n) simplifies to Theta(n^4).")


# ============================================================================
# SECTION 46: LOOP COMPLEXITY TABLE
# ============================================================================

def print_complexity_reference() -> None:
    section("45. Loop Complexity Reference")

    patterns = [
        ("Fixed number of iterations", "O(1)", "for _ in range(10)"),
        ("Single loop", "O(n)", "for i in range(n)"),
        ("Two consecutive loops", "O(n)", "n + n"),
        ("Two independent nested loops", "O(n^2)", "n * n"),
        ("Three independent nested loops", "O(n^3)", "n * n * n"),
        ("Halving/doubling loop", "O(log n)", "x //= 2 or x *= 2"),
        ("n outer + log n inner", "O(n log n)", "n * log n"),
        ("Inner bound i", "O(n^2)", "sum(i)"),
        ("Inner bound n/i", "O(n log n)", "sum(n/i)"),
        ("Inner bound sqrt(n)", "O(n sqrt(n))", "n * sqrt(n)"),
        ("Monotonic shared pointer", "O(n)", "total pointer movement <= n"),
    ]

    for pattern, complexity, example in patterns:
        print(f"{pattern:32} | {complexity:12} | {example}")


# ============================================================================
# SECTION 47: SPACE COMPLEXITY OF LOOP VARIABLES
# ============================================================================

def loop_space_example(values: list[int]) -> int:
    """
    O(1) auxiliary space.

    The loop uses only a fixed number of scalar variables.
    The input itself is not counted as newly allocated auxiliary space.
    """
    total = 0

    for value in values:
        total += value

    return total


def loop_space_with_output(values: list[int]) -> list[int]:
    """
    O(n) auxiliary/output space because a new list grows with input size.
    """
    result = []

    for value in values:
        result.append(value * 2)

    return result


def demonstrate_space_complexity() -> None:
    section("46. Space Complexity of Loops")

    values = [1, 2, 3, 4]

    print("Scalar accumulator result:", loop_space_example(values))
    print("New list result:", loop_space_with_output(values))

    print("A loop can be O(n) time and O(1) auxiliary space.")
    print("Creating an output collection of n elements introduces O(n) space.")


# ============================================================================
# SECTION 48: INPUT SPACE VS AUXILIARY SPACE
# ============================================================================

def demonstrate_space_distinction() -> None:
    section("47. Input Space vs Auxiliary Space")

    print(
        "Input space refers to memory occupied by supplied input.\n"
        "Auxiliary space refers to additional memory used by the algorithm.\n"
        "An in-place loop can process O(n) input using O(1) auxiliary space."
    )


# ============================================================================
# SECTION 49: PERFORMANCE MEASUREMENT
# ============================================================================

def measure_runtime(
    function: Callable[[int], int],
    inputs: list[int],
    repetitions: int = 3,
) -> list[tuple[int, float]]:
    """
    Measure elapsed wall-clock time.

    Timing is empirical evidence, not a substitute for asymptotic analysis.
    """
    if repetitions <= 0:
        raise ValueError("repetitions must be positive")

    results = []

    for n in inputs:
        start = time.perf_counter()

        for _ in range(repetitions):
            function(n)

        elapsed = time.perf_counter() - start
        average = elapsed / repetitions
        results.append((n, average))

    return results


def demonstrate_runtime_measurement() -> None:
    section("48. Empirical Timing")

    inputs = [1_000, 2_000, 4_000]

    measurements = measure_runtime(linear_sum, inputs, repetitions=2)

    for n, seconds in measurements:
        print(f"linear_sum({n:>5}) average time={seconds:.8f} seconds")

    print(
        "Runtime depends on hardware, Python implementation, operating-system "
        "load, caching, and interpreter overhead. Complexity explains growth."
    )


# ============================================================================
# SECTION 50: RANDOMIZED INPUT AND AVERAGE BEHAVIOR
# ============================================================================

def random_search_average_experiment(
    n: int,
    trials: int = 100,
    seed: int = 42,
) -> float:
    """
    Estimate average inspected elements when the target position is uniformly
    random.

    For a successful uniformly distributed target, the expected position is
    approximately (n + 1) / 2.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if trials <= 0:
        raise ValueError("trials must be positive")

    rng = random.Random(seed)
    total_inspected = 0

    values = list(range(n))

    for _ in range(trials):
        target = rng.randrange(n)

        for index, value in enumerate(values, start=1):
            if value == target:
                total_inspected += index
                break

    return total_inspected / trials


def demonstrate_average_case() -> None:
    section("49. Average-Case Experiment")

    for n in [10, 100, 1000]:
        average = random_search_average_experiment(n)
        theoretical = (n + 1) / 2
        print(
            f"n={n:>4}: measured average={average:>8.2f}, "
            f"theoretical={theoretical:>8.2f}"
        )

    print("Average-case analysis requires a specified probability model.")


# ============================================================================
# SECTION 51: EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    section("50. Edge Cases")

    print("linear_sum(0):", linear_sum(0))
    print("logarithmic_loop(0):", logarithmic_loop(0))
    print("logarithmic_loop(1):", logarithmic_loop(1))
    print("triangular_loop(0):", triangular_loop(0))
    print("cubic_loop(0):", cubic_loop(0))

    print()
    print(
        "Important edge cases include n=0, n=1, empty collections, "
        "negative parameters where applicable, and invalid loop steps."
    )


# ============================================================================
# SECTION 52: INVALID PARAMETERS
# ============================================================================

def demonstrate_validation() -> None:
    section("51. Validation and Infinite-Loop Prevention")

    invalid_calls = [
        ("fixed_increment_loop", lambda: fixed_increment_loop(10, 0)),
        ("base_k_logarithmic_loop", lambda: base_k_logarithmic_loop(100, 1)),
        ("reduce_by_factor", lambda: reduce_by_factor(100, 1)),
        ("divisor_count_by_scan", lambda: divisor_count_by_scan(0)),
    ]

    for name, operation in invalid_calls:
        try:
            operation()
        except ValueError as error:
            print(f"{name}: correctly rejected invalid input -> {error}")


# ============================================================================
# SECTION 53: COMMON MISTAKE 1
# ============================================================================

def mistake_nested_loops_are_always_n_squared() -> None:
    """
    Demonstrate why syntax alone is insufficient.

    Example:
        for i in range(n):
            while j < n:
                j += 1

    If j is not reset, the total number of j increments is only O(n).
    """
    section("52. Common Mistake: Every Nested Loop Is O(n^2)")

    values = list(range(20))
    movements = monotonic_inner_pointer(values, 5)

    print("Monotonic-pointer movements:", movements)
    print(
        "The inner pointer is shared across iterations and never moves backward."
    )
    print("Correct complexity: O(n) for this structure.")


# ============================================================================
# SECTION 54: COMMON MISTAKE 2
# ============================================================================

def mistake_consecutive_loops_are_multiplied() -> None:
    section("53. Common Mistake: Multiplying Consecutive Loops")

    print("Incorrect reasoning: n * n = n^2")
    print("Correct reasoning for two consecutive loops: n + n = 2n = O(n).")


# ============================================================================
# SECTION 55: COMMON MISTAKE 3
# ============================================================================

def mistake_constants_change_complexity() -> None:
    section("54. Common Mistake: Treating Constants as New Complexity Classes")

    print("n iterations:       O(n)")
    print("n/2 iterations:     O(n)")
    print("3n iterations:      O(n)")
    print("1000n iterations:   O(n)")
    print("The constant changes runtime but not asymptotic class.")


# ============================================================================
# SECTION 56: COMMON MISTAKE 4
# ============================================================================

def mistake_log_loop() -> None:
    section("55. Common Mistake: Misclassifying Doubling")

    print("x += 1 until x reaches n -> O(n)")
    print("x *= 2 until x reaches n -> O(log n)")
    print("x //= 2 until x reaches 1 -> O(log n)")


# ============================================================================
# SECTION 57: COMMON MISTAKE 5
# ============================================================================

def mistake_break_is_constant() -> None:
    section("56. Common Mistake: Assuming break Makes a Loop O(1)")

    print(
        "break only limits execution on paths where the condition is reached.\n"
        "If the condition can be false for all n elements, worst-case work remains O(n)."
    )


# ============================================================================
# SECTION 58: COMMON MISTAKE 6
# ============================================================================

def mistake_hidden_costs() -> None:
    section("57. Common Mistake: Ignoring Operations Inside Loops")

    print(
        "A loop's complexity is not determined only by its iteration count.\n"
        "If the loop body itself costs O(n), then n iterations can produce O(n^2).\n"
        "Likewise, an apparently constant-looking operation must be examined "
        "according to the data structure and implementation."
    )


def body_cost_example(n: int) -> int:
    """
    O(n^2).

    The outer loop executes n times and the body scans n elements.
    """
    values = list(range(n))
    count = 0

    for _ in range(n):
        for _ in values:
            count += 1

    return count


def demonstrate_hidden_body_cost() -> None:
    section("58. Hidden Body Cost")

    for n in [1, 2, 5]:
        print(f"n={n}: operations={body_cost_example(n)}")

    print("Outer n * inner n = Theta(n^2).")


# ============================================================================
# SECTION 59: COMPARING ALGORITHMS
# ============================================================================

def complexity_comparison_values(n: int) -> dict[str, float]:
    """
    Return representative growth values for common complexity classes.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    return {
        "1": 1,
        "log2(n)": math.log2(n),
        "sqrt(n)": math.sqrt(n),
        "n": n,
        "n log2(n)": n * math.log2(n),
        "n^2": n**2,
        "n^3": n**3,
        "2^n": 2**n,
    }


def demonstrate_growth_rates() -> None:
    section("59. Growth-Rate Comparison")

    for n in [10, 100, 1000]:
        print(f"\nn={n}")
        values = complexity_comparison_values(n)

        for name, value in values.items():
            if value < 1e12:
                print(f"  {name:12}: {value:.2f}")
            else:
                print(f"  {name:12}: {value:.3e}")


# ============================================================================
# SECTION 60: ASYMPTOTIC RANKING
# ============================================================================

def demonstrate_asymptotic_ranking() -> None:
    section("60. Common Asymptotic Ranking")

    ranking = [
        "O(1)",
        "O(log n)",
        "O(sqrt(n))",
        "O(n)",
        "O(n log n)",
        "O(n^2)",
        "O(n^3)",
        "O(2^n)",
        "O(n!)",
    ]

    for rank, complexity in enumerate(ranking, start=1):
        print(f"{rank:>2}. {complexity}")


# ============================================================================
# SECTION 61: LOOP TRANSFORMATION EXAMPLE
# ============================================================================

def quadratic_duplicate_detection(values: list[int]) -> bool:
    """
    O(n^2).

    Checks every pair using nested loops.
    """
    n = len(values)

    for i in range(n):
        for j in range(i + 1, n):
            if values[i] == values[j]:
                return True

    return False


def demonstrate_algorithmic_improvement() -> None:
    section("61. Loop-Based Algorithmic Improvement")

    values = list(range(100))

    print("Pairwise duplicate check:", quadratic_duplicate_detection(values))
    print(
        "The pairwise implementation uses O(n^2) comparisons in the worst case."
    )
    print(
        "A hash-set-based solution can reduce expected duplicate detection "
        "to O(n) time using O(n) additional space."
    )


def linear_duplicate_detection(values: list[int]) -> bool:
    """
    Expected O(n) time and O(n) auxiliary space.
    """
    seen: set[int] = set()

    for value in values:
        if value in seen:
            return True
        seen.add(value)

    return False


def demonstrate_duplicate_implementations() -> None:
    section("62. Quadratic vs Expected Linear Duplicate Detection")

    values = [1, 3, 5, 7, 9, 3]

    print("Quadratic method:", quadratic_duplicate_detection(values))
    print("Hash-set method:", linear_duplicate_detection(values))


# ============================================================================
# SECTION 62: SORTING AND LOOP COMPLEXITY
# ============================================================================

def insertion_sort(values: list[int]) -> list[int]:
    """
    Worst-case O(n^2), best-case O(n), O(1) auxiliary space.

    The nested-looking behavior is dependent on how far each element must move.
    """
    result = values.copy()

    for i in range(1, len(result)):
        current = result[i]
        j = i - 1

        while j >= 0 and result[j] > current:
            result[j + 1] = result[j]
            j -= 1

        result[j + 1] = current

    return result


def demonstrate_insertion_sort() -> None:
    section("63. Real Algorithm: Insertion Sort")

    inputs = [
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [4, 1, 3, 2],
    ]

    for values in inputs:
        print(f"{values} -> {insertion_sort(values)}")

    print("Best case: Theta(n) when already sorted.")
    print("Worst case: Theta(n^2) when reverse sorted.")
    print("Auxiliary space: Theta(1), excluding the copied demonstration input.")


# ============================================================================
# SECTION 63: GRAPH-LIKE LOOP PATTERN
# ============================================================================

def adjacency_matrix_scan(matrix: list[list[int]]) -> int:
    """
    O(V^2) for a V x V adjacency matrix.
    """
    count = 0

    for row in matrix:
        for value in row:
            count += value

    return count


def demonstrate_graph_matrix() -> None:
    section("64. Real Application: Adjacency Matrix")

    matrix = [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ]

    print("Matrix edge-value sum:", adjacency_matrix_scan(matrix))
    print("Scanning all cells of a V x V matrix requires Theta(V^2) work.")


# ============================================================================
# SECTION 64: LOOP NESTING WITH DIFFERENT DIMENSIONS
# ============================================================================

def matrix_multiplication_work(rows_a: int, cols_a: int, cols_b: int) -> int:
    """
    Standard matrix multiplication has O(rows_a * cols_a * cols_b)
    arithmetic operations.
    """
    operations = 0

    for _ in range(rows_a):
        for _ in range(cols_a):
            for _ in range(cols_b):
                operations += 1

    return operations


def demonstrate_matrix_multiplication() -> None:
    section("65. Real Application: Matrix Multiplication")

    dimensions = (2, 3, 4)
    operations = matrix_multiplication_work(*dimensions)

    print(
        f"rows_a={dimensions[0]}, cols_a={dimensions[1]}, "
        f"cols_b={dimensions[2]}"
    )
    print("Multiplication/addition loop count:", operations)
    print("Complexity: Theta(rows_a * cols_a * cols_b).")


# ============================================================================
# SECTION 65: LOOP DEPENDENCY GRAPH CONCEPT
# ============================================================================

def explain_loop_dependency() -> None:
    section("66. Loop Dependency Analysis")

    print(
        "For each loop, ask:\n"
        "1. What determines its number of iterations?\n"
        "2. Is that number independent of another loop?\n"
        "3. Does the loop variable depend on an outer variable?\n"
        "4. Does an inner pointer continue moving across outer iterations?\n"
        "5. Does each iteration shrink or expand the state geometrically?\n"
        "6. Can the loop terminate early?\n"
        "7. What is the cost of the loop body?"
    )


# ============================================================================
# SECTION 66: A SYSTEMATIC ANALYSIS FUNCTION
# ============================================================================

def analyze_loop_pattern(
    outer_iterations: str,
    inner_iterations: Optional[str],
    relationship: str,
    body_cost: str = "O(1)",
) -> str:
    """
    Produce a human-readable complexity statement for common patterns.

    This is educational rather than a symbolic algebra system.
    """
    relationship = relationship.lower().strip()

    if inner_iterations is None:
        return f"Outer work {outer_iterations} with body {body_cost}."

    if relationship == "nested-independent":
        return (
            f"Nested independent loops: {outer_iterations} * "
            f"{inner_iterations}, with body {body_cost}."
        )

    if relationship == "consecutive":
        return (
            f"Consecutive loops: {outer_iterations} + "
            f"{inner_iterations}, with body {body_cost}."
        )

    if relationship == "dependent":
        return (
            f"Dependent loops require summation of the inner bound over "
            f"outer iterations: sum({inner_iterations}) with body {body_cost}."
        )

    if relationship == "geometric":
        return (
            f"Geometric loop behavior usually contributes logarithmic "
            f"iteration count: {inner_iterations}."
        )

    return "Inspect the loop bounds and derive the corresponding summation or product."


def demonstrate_systematic_analysis() -> None:
    section("67. Systematic Loop Analysis")

    examples = [
        ("n", None, "single"),
        ("n", "n", "nested-independent"),
        ("n", "n", "consecutive"),
        ("n", "i", "dependent"),
        ("n", "log(n)", "nested-independent"),
        ("n", "n/i", "dependent"),
    ]

    for outer, inner, relationship in examples:
        print(
            analyze_loop_pattern(
                outer,
                inner,
                relationship,
            )
        )


# ============================================================================
# SECTION 67: TESTS
# ============================================================================

def run_correctness_tests() -> None:
    """
    Basic assertions validate the demonstrations.

    Complexity analysis should not be separated from correctness. An incorrect
    loop can have a precisely analyzed complexity and still solve the wrong
    problem.
    """
    section("68. Correctness Tests")

    assert linear_sum(0) == 0
    assert linear_sum(5) == 10

    assert nested_product(5) == 25
    assert triangular_loop(5) == 10
    assert upper_triangle_loop(5) == 15

    assert logarithmic_loop(1) == 0
    assert logarithmic_loop(8) == 3

    assert divisor_count_by_scan(36) == 9
    assert divisor_count_by_square_root(36) == 9

    assert is_prime_sqrt(2)
    assert is_prime_sqrt(17)
    assert not is_prime_sqrt(49)

    assert binary_search([1, 3, 5, 7], 5) == 2
    assert binary_search([1, 3, 5, 7], 6) == -1

    assert insertion_sort([4, 1, 3, 2]) == [1, 2, 3, 4]

    assert quadratic_duplicate_detection([1, 2, 3])
    assert not quadratic_duplicate_detection([1, 2, 3])

    assert linear_duplicate_detection([1, 2, 1])
    assert not linear_duplicate_detection([1, 2, 3])

    print("All correctness tests passed.")


# ============================================================================
# SECTION 68: SECURITY AND PRODUCTION CONSIDERATIONS
# ============================================================================

def production_considerations() -> None:
    section("69. Production Considerations")

    print(
        "1. Validate input sizes and loop bounds to prevent accidental "
        "resource exhaustion."
    )
    print(
        "2. Avoid unbounded while loops. Ensure loop state progresses toward "
        "a termination condition."
    )
    print(
        "3. Be cautious with user-controlled values that determine nested "
        "loop sizes. An O(n^2) operation can become a denial-of-service risk "
        "when n is uncontrolled."
    )
    print(
        "4. Measure real workloads when performance matters. Asymptotic analysis "
        "and profiling answer different questions."
    )
    print(
        "5. Use data structures that match the required operations. Replacing "
        "repeated linear searches with hashing or indexing can change complexity."
    )
    print(
        "6. Avoid premature micro-optimization. A better asymptotic algorithm "
        "usually matters more for sufficiently large inputs."
    )
    print(
        "7. Document assumptions such as sorted input, bounded dimensions, "
        "expected hash-table behavior, or fixed loop factors."
    )


# ============================================================================
# SECTION 69: DESIGN TRADE-OFFS
# ============================================================================

def design_tradeoffs() -> None:
    section("70. Complexity Trade-Offs")

    tradeoffs = [
        (
            "Time vs space",
            "Hashing can reduce expected time from O(n^2) to O(n) "
            "while using O(n) additional space."
        ),
        (
            "Worst case vs average case",
            "An algorithm can have excellent average behavior but a poor "
            "worst-case guarantee."
        ),
        (
            "Exact count vs asymptotic class",
            "Constants and lower-order terms matter for small inputs but "
            "are suppressed asymptotically."
        ),
        (
            "Algorithm vs implementation",
            "Two O(n) implementations can differ substantially in actual runtime."
        ),
        (
            "Input assumptions",
            "Sorted data or bounded values can enable faster loop structures."
        ),
    ]

    for name, description in tradeoffs:
        print(f"{name:24}: {description}")


# ============================================================================
# SECTION 70: FINAL STUDY CHECKLIST
# ============================================================================

def study_checklist() -> None:
    section("71. Loop Complexity Analysis Checklist")

    checklist = [
        "Identify the input size or dimensions.",
        "Determine how many times each loop executes.",
        "Determine whether loop bounds are independent or dependent.",
        "Multiply costs for truly nested independent loops.",
        "Add costs for consecutive loops.",
        "Use summations for dependent bounds.",
        "Recognize geometric growth or reduction as logarithmic.",
        "Inspect whether inner pointers reset or remain monotonic.",
        "Include the cost of the loop body.",
        "Account for early termination separately from worst-case behavior.",
        "Distinguish best, average, and worst cases.",
        "Retain multiple input dimensions such as O(n*m) when appropriate.",
        "Simplify using dominant asymptotic terms.",
        "Analyze auxiliary space separately.",
        "Check edge cases and termination conditions.",
        "Validate correctness before trusting the complexity analysis.",
        "Use profiling for real-world performance validation.",
        "Consider resource-exhaustion risks when loop bounds are externally controlled.",
    ]

    for index, item in enumerate(checklist, start=1):
        print(f"{index:>2}. {item}")


# ============================================================================
# SECTION 71: INTEGRATED EXAMPLE
# ============================================================================

def integrated_example(n: int) -> int:
    """
    Integrated analysis example.

    Complexity derivation:

        Loop A:
            n iterations
            -> O(n)

        Loop B:
            n outer iterations
            log(n) inner iterations
            -> O(n log n)

        Loop C:
            i-dependent inner bound
            -> sum(i), i=1..n
            -> O(n^2)

        Total:
            O(n) + O(n log n) + O(n^2)
            = O(n^2)

    The implementation deliberately combines several common patterns.
    """
    count = 0

    # Loop A: linear.
    for _ in range(n):
        count += 1

    # Loop B: linearithmic.
    for _ in range(n):
        value = 1
        while value < n:
            count += 1
            value *= 2

    # Loop C: triangular.
    for i in range(n):
        for _ in range(i):
            count += 1

    return count


def demonstrate_integrated_example() -> None:
    section("72. Integrated Complexity Analysis")

    for n in [1, 2, 4, 8, 16]:
        print(f"n={n:>2}: operations={integrated_example(n)}")

    print()
    print("Loop A: O(n)")
    print("Loop B: O(n log n)")
    print("Loop C: O(n^2)")
    print("Combined: O(n + n log n + n^2) = O(n^2).")


# ============================================================================
# SECTION 72: MAIN PROGRAM
# ============================================================================

def main() -> None:
    """
    Execute all educational demonstrations in a logical order.
    """
    explain_basic_terminology()
    demonstrate_constant_time()
    demonstrate_single_loops()
    demonstrate_exact_linear_count()
    demonstrate_nested_loops()
    demonstrate_triangular_loop()
    demonstrate_consecutive_loops()
    demonstrate_logarithmic_loops()
    demonstrate_log_bases()
    demonstrate_linearithmic_loop()
    demonstrate_dependent_loops()
    demonstrate_upper_triangle()
    demonstrate_cubic_loops()
    demonstrate_mixed_nesting()
    demonstrate_fixed_increment()
    demonstrate_exponential_state_growth()
    demonstrate_base_k()
    demonstrate_decrement_loop()
    demonstrate_fractional_reduction()
    demonstrate_reduction_factor()
    demonstrate_break()
    demonstrate_nested_break()
    demonstrate_continue()
    demonstrate_conditional_inner_loop()
    demonstrate_geometric_nested_loop()
    demonstrate_dependent_log_loop()
    summation_examples()
    demonstrate_harmonic_loop()
    demonstrate_sqrt_complexity()
    demonstrate_prime_testing()
    demonstrate_multiple_parameters()
    demonstrate_combinations()
    demonstrate_dominant_terms()
    demonstrate_cases()
    demonstrate_early_nested_exit()
    demonstrate_data_dependent_loop()
    demonstrate_loop_invariant()
    demonstrate_amortized_complexity()
    demonstrate_two_pointers()
    demonstrate_monotonic_pointer()
    demonstrate_binary_search()
    demonstrate_search_comparison()
    demonstrate_sqrt_nested_loop()
    demonstrate_polynomial_combination()
    print_complexity_reference()
    demonstrate_space_complexity()
    demonstrate_space_distinction()
    demonstrate_runtime_measurement()
    demonstrate_average_case()
    demonstrate_edge_cases()
    demonstrate_validation()
    mistake_nested_loops_are_always_n_squared()
    mistake_consecutive_loops_are_multiplied()
    mistake_constants_change_complexity()
    mistake_log_loop()
    mistake_break_is_constant()
    mistake_hidden_costs()
    demonstrate_hidden_body_cost()
    demonstrate_growth_rates()
    demonstrate_asymptotic_ranking()
    demonstrate_algorithmic_improvement()
    demonstrate_duplicate_implementations()
    demonstrate_insertion_sort()
    demonstrate_graph_matrix()
    demonstrate_matrix_multiplication()
    explain_loop_dependency()
    demonstrate_systematic_analysis()
    run_correctness_tests()
    production_considerations()
    design_tradeoffs()
    study_checklist()
    demonstrate_integrated_example()

    section("73. End of Demonstration")
    print(
        "The script has demonstrated how loop bounds, nesting, dependency, "
        "geometric progress, early termination, body cost, and data structure "
        "choices determine algorithmic complexity."
    )


if __name__ == "__main__":
    main()
