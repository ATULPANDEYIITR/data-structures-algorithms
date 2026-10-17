"""
Basic Recursion Problems
========================

A self-contained practical study of recursion through:
- Factorial
- Fibonacci numbers
- Integer exponentiation
- Sum of digits
- Reversing numbers
- Recursive array traversal

The implementations progress from direct recursive definitions to
memoization, divide-and-conquer exponentiation, explicit validation,
recursion-depth considerations, and iterative alternatives.

Run with:
    python recursion_problems.py

Only the Python standard library is required.
"""

from functools import lru_cache
from time import perf_counter
from typing import Callable, Sequence


def display(title: str) -> None:
    """Print a readable heading for a demonstration."""
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")


def factorial_recursive(n: int) -> int:
    """
    Calculate n! using the recurrence:
        factorial(0) = 1
        factorial(n) = n * factorial(n - 1)

    Time complexity: O(n)
    Auxiliary recursion space: O(n)

    Python integers support arbitrary precision, although very large
    results still consume substantial memory and computation time.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("Factorial requires an integer.")
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    if n == 0 or n == 1:
        return 1

    return n * factorial_recursive(n - 1)


def factorial_iterative(n: int) -> int:
    """Calculate factorial without consuming recursive call-stack space."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("Factorial requires an integer.")
    if n < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    result = 1
    for factor in range(2, n + 1):
        result *= factor
    return result


def fibonacci_recursive(n: int) -> int:
    """
    Calculate the nth Fibonacci number using the direct recurrence.

    F(0) = 0, F(1) = 1
    F(n) = F(n - 1) + F(n - 2)

    This version intentionally demonstrates overlapping subproblems.
    Its time complexity is exponential, approximately O(2**n).
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("The Fibonacci index must be an integer.")
    if n < 0:
        raise ValueError("The Fibonacci index cannot be negative.")

    if n < 2:
        return n

    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


@lru_cache(maxsize=None)
def fibonacci_memoized(n: int) -> int:
    """
    Calculate Fibonacci with cached recursive results.

    Each index is computed once. Time and cache space are O(n),
    excluding the increasing bit lengths of the integer results.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("The Fibonacci index must be an integer.")
    if n < 0:
        raise ValueError("The Fibonacci index cannot be negative.")

    if n < 2:
        return n

    return fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)


def fibonacci_iterative(n: int) -> int:
    """
    Compute Fibonacci using constant-count working variables.

    The number of arithmetic operations is O(n), and auxiliary space
    is O(1), excluding storage for the resulting integer.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("The Fibonacci index must be an integer.")
    if n < 0:
        raise ValueError("The Fibonacci index cannot be negative.")

    previous, current = 0, 1

    for _ in range(n):
        previous, current = current, previous + current

    return previous


def power_recursive(base: int | float, exponent: int) -> int | float:
    """
    Calculate base raised to an integer exponent by exponentiation
    by squaring.

    T(n) = T(floor(n / 2)) + O(1), giving O(log |n|) multiplications.

    Negative exponents return reciprocals. A zero base with a negative
    exponent is rejected. Floating-point bases retain floating-point
    rounding behavior.
    """
    if isinstance(base, bool) or not isinstance(base, (int, float)):
        raise TypeError("The base must be an integer or float.")
    if isinstance(base, float) and not __import__("math").isfinite(base):
        raise ValueError("The base must be finite.")
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise TypeError("The exponent must be an integer.")
    if base == 0 and exponent < 0:
        raise ZeroDivisionError("Zero cannot be raised to a negative power.")

    def positive_power(value: int | float, exp: int) -> int | float:
        if exp == 0:
            return 1

        half = positive_power(value, exp // 2)
        squared = half * half

        if exp % 2 == 0:
            return squared

        return squared * value

    if exponent < 0:
        return 1 / positive_power(base, -exponent)

    return positive_power(base, exponent)


def sum_of_digits_recursive(n: int) -> int:
    """
    Return the sum of the decimal digits of an integer.

    The sign is ignored, so -472 produces 13.
    Each recursive call removes the final digit using // 10.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("The input must be an integer.")

    n = abs(n)

    if n < 10:
        return n

    return n % 10 + sum_of_digits_recursive(n // 10)


def reverse_number_recursive(n: int) -> int:
    """
    Reverse an integer's decimal digits recursively.

    The result is an integer, so leading zeros in the reversed
    representation disappear. The original sign is preserved.

    Example: -1200 becomes -21.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("The input must be an integer.")

    sign = -1 if n < 0 else 1
    magnitude = abs(n)

    def reverse_positive(value: int, accumulated: int = 0) -> int:
        if value == 0:
            return accumulated

        return reverse_positive(
            value // 10,
            accumulated * 10 + value % 10,
        )

    return sign * reverse_positive(magnitude)


def recursive_sum(values: Sequence[int], index: int = 0) -> int:
    """Sum a sequence by recursively advancing an index."""
    if index < 0 or index > len(values):
        raise IndexError("The starting index is outside the sequence.")

    if index == len(values):
        return 0

    return values[index] + recursive_sum(values, index + 1)


def recursive_find(
    values: Sequence[int],
    target: int,
    index: int = 0,
) -> int:
    """
    Return the first matching index or -1.

    Each recursive call examines one element. Worst-case time and
    recursion space are O(n).
    """
    if index < 0 or index > len(values):
        raise IndexError("The starting index is outside the sequence.")

    if index == len(values):
        return -1

    if values[index] == target:
        return index

    return recursive_find(values, target, index + 1)


def recursive_maximum(values: Sequence[int], index: int = 0) -> int:
    """Find the maximum element through recursive traversal."""
    if not values:
        raise ValueError("Cannot find the maximum of an empty sequence.")
    if index < 0 or index >= len(values):
        raise IndexError("The starting index must identify an element.")

    if index == len(values) - 1:
        return values[index]

    return max(values[index], recursive_maximum(values, index + 1))


def recursive_map(
    values: Sequence[int],
    transform: Callable[[int], int],
    index: int = 0,
) -> list[int]:
    """
    Build a transformed list recursively.

    The slicing-free index approach avoids allocating a new list at
    every recursive call. The output itself requires O(n) space.
    """
    if index < 0 or index > len(values):
        raise IndexError("The starting index is outside the sequence.")

    if index == len(values):
        return []

    return [transform(values[index])] + recursive_map(
        values, transform, index + 1
    )


def recursive_binary_search(
    sorted_values: Sequence[int],
    target: int,
    low: int = 0,
    high: int | None = None,
) -> int:
    """
    Search a sorted sequence using divide and conquer.

    The caller must supply an ascending sequence.
    Time complexity is O(log n); recursive space is O(log n).
    """
    if high is None:
        high = len(sorted_values) - 1

    if low < 0 or high >= len(sorted_values):
        if not (low == 0 and high == -1 and len(sorted_values) == 0):
            raise IndexError("Search bounds are outside the sequence.")

    if low > high:
        return -1

    middle = low + (high - low) // 2

    if sorted_values[middle] == target:
        return middle

    if target < sorted_values[middle]:
        return recursive_binary_search(
            sorted_values, target, low, middle - 1
        )

    return recursive_binary_search(
        sorted_values, target, middle + 1, high
    )


def recursive_palindrome(text: str) -> bool:
    """Test whether a string reads identically in both directions."""
    def check(left: int, right: int) -> bool:
        if left >= right:
            return True
        if text[left] != text[right]:
            return False
        return check(left + 1, right - 1)

    return check(0, len(text) - 1)


def demonstrate_validation() -> None:
    """Show expected exceptions without terminating the demonstration."""
    cases: list[tuple[str, Callable[[], object]]] = [
        ("Negative factorial", lambda: factorial_recursive(-3)),
        ("Fractional factorial", lambda: factorial_recursive(3.5)),
        ("Negative Fibonacci index", lambda: fibonacci_memoized(-1)),
        ("Zero to negative power", lambda: power_recursive(0, -2)),
        ("Empty maximum", lambda: recursive_maximum([])),
        ("Invalid traversal index", lambda: recursive_sum([4, 8], 3)),
    ]

    for label, operation in cases:
        try:
            operation()
        except (TypeError, ValueError, IndexError, ZeroDivisionError) as exc:
            print(f"{label}: {type(exc).__name__}: {exc}")
        else:
            raise AssertionError(f"{label} should have failed.")


def run_assertions() -> None:
    """Check core definitions, boundaries, and recursive behavior."""
    assert factorial_recursive(0) == 1
    assert factorial_recursive(6) == 720
    assert factorial_iterative(12) == factorial_recursive(12)

    assert [fibonacci_recursive(i) for i in range(10)] == [
        0, 1, 1, 2, 3, 5, 8, 13, 21, 34
    ]
    assert fibonacci_memoized(100) == 354224848179261915075
    assert fibonacci_iterative(100) == fibonacci_memoized(100)

    assert power_recursive(2, 10) == 1024
    assert power_recursive(3, 0) == 1
    assert power_recursive(2, -3) == 0.125
    assert power_recursive(-2, 3) == -8

    assert sum_of_digits_recursive(4729) == 22
    assert sum_of_digits_recursive(-4729) == 22
    assert sum_of_digits_recursive(0) == 0

    assert reverse_number_recursive(12340) == 4321
    assert reverse_number_recursive(-1200) == -21
    assert reverse_number_recursive(0) == 0

    numbers = [12, 5, 30, 5, -4]
    assert recursive_sum(numbers) == 48
    assert recursive_find(numbers, 5) == 1
    assert recursive_find(numbers, 99) == -1
    assert recursive_maximum(numbers) == 30
    assert recursive_map(numbers, lambda value: value * 2) == [
        24, 10, 60, 10, -8
    ]

    assert recursive_binary_search([2, 4, 6, 8, 10], 8) == 3
    assert recursive_binary_search([2, 4, 6, 8, 10], 7) == -1
    assert recursive_binary_search([], 7) == -1

    assert recursive_palindrome("racecar")
    assert recursive_palindrome("")
    assert not recursive_palindrome("recursion")


def main() -> None:
    run_assertions()
    print("All recursion assertions passed.")

    display("Factorial: Base Cases and Recursive Reduction")
    for number in range(7):
        print(
            f"{number}! = {factorial_recursive(number):>3} "
            f"(iterative: {factorial_iterative(number)})"
        )

    display("Fibonacci: Overlapping Subproblems")
    print("Direct recursion:")
    print([fibonacci_recursive(i) for i in range(11)])
    print("Memoized recursion:")
    print([fibonacci_memoized(i) for i in range(21)])
    print("F(100):", fibonacci_memoized(100))
    print("Memoization cache:", fibonacci_memoized.cache_info())

    display("Fibonacci Performance Comparison")
    index = 30
    start = perf_counter()
    direct = fibonacci_recursive(index)
    direct_time = perf_counter() - start

    start = perf_counter()
    memoized = fibonacci_memoized(index)
    memoized_time = perf_counter() - start

    print(f"F({index}) = {direct}")
    print(f"Direct recursion: {direct_time:.6f} seconds")
    print(f"Memoized lookup: {memoized_time:.6f} seconds")
    print("The memoized call may be a cache hit after earlier demonstrations.")

    display("Exponentiation by Squaring")
    for base, exponent in [(2, 10), (5, 0), (3, -2), (-2, 7)]:
        print(f"{base}^{exponent} = {power_recursive(base, exponent)}")

    display("Recursive Sum of Digits")
    for number in [0, 7, 4729, -5821, 10000]:
        print(f"digit_sum({number}) = {sum_of_digits_recursive(number)}")

    display("Recursive Number Reversal")
    for number in [12345, 1200, -987, 0]:
        print(f"reverse({number}) = {reverse_number_recursive(number)}")

    display("Recursive Array Traversal")
    measurements = [12, 5, 30, 5, -4, 18]
    print("Measurements:", measurements)
    print("Sum:", recursive_sum(measurements))
    print("Maximum:", recursive_maximum(measurements))
    print("First occurrence of 5:", recursive_find(measurements, 5))
    print("Search for 100:", recursive_find(measurements, 100))
    print(
        "Calibration doubles:",
        recursive_map(measurements, lambda value: value * 2),
    )

    display("Divide-and-Conquer Array Search")
    ordered_measurements = sorted(measurements)
    print("Sorted measurements:", ordered_measurements)
    for target in [18, -4, 100]:
        print(
            f"Search for {target}: "
            f"{recursive_binary_search(ordered_measurements, target)}"
        )

    display("Recursive Palindrome Checking")
    for value in ["racecar", "level", "recursion", ""]:
        print(f"{value!r}: {recursive_palindrome(value)}")

    display("Validation and Failure Conditions")
    demonstrate_validation()

    display("Practical Limitations")
    print("Python does not optimize tail-recursive calls.")
    print("Deep linear recursion can raise RecursionError.")
    print("Direct Fibonacci repeats work; memoization avoids repeated states.")
    print("For large arrays, iterative traversal is generally safer.")
    print("Binary search requires ascending input.")
    print("Factorial and Fibonacci results can become extremely large.")


if __name__ == "__main__":
    main()
