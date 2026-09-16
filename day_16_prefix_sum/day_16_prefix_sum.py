"""
Prefix Sum: From Fundamentals to Advanced Range-Query Techniques

This standalone study script teaches prefix sums from first principles and
progresses through one-dimensional, two-dimensional, weighted, difference-
array, immutable, dynamic, and advanced range-query techniques.

The examples are executable and intentionally use the standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from bisect import bisect_left
from random import Random
from time import perf_counter
from typing import Iterable, Sequence


# ---------------------------------------------------------------------------
# 1. The basic problem: repeated range sums
# ---------------------------------------------------------------------------

def naive_range_sum(values: Sequence[int], left: int, right: int) -> int:
    """Return sum(values[left:right + 1]) by scanning every element."""
    if left < 0 or right >= len(values) or left > right:
        raise ValueError("Invalid inclusive range")
    return sum(values[left:right + 1])


def build_prefix_sum(values: Sequence[int]) -> list[int]:
    """
    Build a prefix array with one extra element.

    prefix[i] is the sum of values[0:i].
    Therefore:
        sum(values[left:right + 1]) = prefix[right + 1] - prefix[left]

    The extra zero at prefix[0] removes special cases for ranges starting
    at index zero.
    """
    prefix = [0] * (len(values) + 1)

    for index, value in enumerate(values):
        prefix[index + 1] = prefix[index] + value

    return prefix


def prefix_range_sum(
    prefix: Sequence[int],
    left: int,
    right: int,
) -> int:
    """Answer an inclusive range-sum query in O(1)."""
    if left < 0 or right < left or right + 1 >= len(prefix):
        raise ValueError("Invalid inclusive range")
    return prefix[right + 1] - prefix[left]


# ---------------------------------------------------------------------------
# 2. Basic demonstration
# ---------------------------------------------------------------------------

def demonstrate_basic_prefix_sum() -> None:
    values = [4, 2, 7, 1, 5, 3]

    prefix = build_prefix_sum(values)

    print("Original array :", values)
    print("Prefix array   :", prefix)
    print("Sum [1, 4]     :", prefix_range_sum(prefix, 1, 4))
    print("Sum [0, 5]     :", prefix_range_sum(prefix, 0, 5))
    print("Sum [3, 3]     :", prefix_range_sum(prefix, 3, 3))

    # Prefix:
    # [0, 4, 6, 13, 14, 19, 22]
    #
    # Sum [1, 4] = prefix[5] - prefix[1] = 19 - 4 = 15


# ---------------------------------------------------------------------------
# 3. Why prefix sums improve repeated calculations
# ---------------------------------------------------------------------------

def answer_many_queries_naively(
    values: Sequence[int],
    queries: Iterable[tuple[int, int]],
) -> list[int]:
    return [naive_range_sum(values, left, right) for left, right in queries]


def answer_many_queries_with_prefix(
    values: Sequence[int],
    queries: Iterable[tuple[int, int]],
) -> list[int]:
    prefix = build_prefix_sum(values)
    return [
        prefix_range_sum(prefix, left, right)
        for left, right in queries
    ]


def demonstrate_performance_difference() -> None:
    random = Random(42)
    values = [random.randint(-100, 100) for _ in range(20_000)]
    queries = [
        (
            random.randint(0, len(values) - 2),
            random.randint(1, len(values) - 1),
        )
        for _ in range(5_000)
    ]

    # Normalize each query so left <= right.
    queries = [
        (min(left, right), max(left, right))
        for left, right in queries
    ]

    start = perf_counter()
    naive_results = answer_many_queries_naively(values, queries)
    naive_time = perf_counter() - start

    start = perf_counter()
    prefix_results = answer_many_queries_with_prefix(values, queries)
    prefix_time = perf_counter() - start

    assert naive_results == prefix_results

    print("\nPerformance demonstration")
    print(f"Naive query processing : {naive_time:.6f} seconds")
    print(f"Prefix-sum processing  : {prefix_time:.6f} seconds")


# ---------------------------------------------------------------------------
# 4. Prefix sums with negative numbers
# ---------------------------------------------------------------------------

def demonstrate_negative_values() -> None:
    values = [5, -3, 8, -10, 6]
    prefix = build_prefix_sum(values)

    print("\nNegative values")
    print("Values :", values)
    print("Prefix :", prefix)
    print("Sum [1, 3] :", prefix_range_sum(prefix, 1, 3))


# ---------------------------------------------------------------------------
# 5. Prefix sums for counting
# ---------------------------------------------------------------------------

def build_binary_prefix(values: Sequence[int]) -> list[int]:
    """
    Prefix sums work for any additive quantity.

    For a binary sequence, the prefix sum represents the number of ones
    encountered so far.
    """
    if any(value not in (0, 1) for value in values):
        raise ValueError("Binary prefix requires only 0 and 1")

    return build_prefix_sum(values)


def count_ones(
    binary_prefix: Sequence[int],
    left: int,
    right: int,
) -> int:
    return prefix_range_sum(binary_prefix, left, right)


def demonstrate_counting() -> None:
    values = [1, 0, 1, 1, 0, 0, 1, 1]
    prefix = build_binary_prefix(values)

    print("\nCounting with prefix sums")
    print("Binary array :", values)
    print("Ones in [2, 6] :", count_ones(prefix, 2, 6))


# ---------------------------------------------------------------------------
# 6. Prefix sums for conditional counting
# ---------------------------------------------------------------------------

def build_predicate_prefix(
    values: Sequence[int],
    predicate,
) -> list[int]:
    """
    Store 1 when a condition is true and 0 otherwise.

    This converts a range-condition query into an ordinary range sum.
    """
    flags = [1 if predicate(value) else 0 for value in values]
    return build_prefix_sum(flags)


def demonstrate_conditional_counting() -> None:
    values = [3, 12, 7, 19, 4, 22, 9]
    even_prefix = build_predicate_prefix(values, lambda value: value % 2 == 0)

    print("\nConditional counting")
    print("Values :", values)
    print(
        "Even values in [1, 5] :",
        prefix_range_sum(even_prefix, 1, 5),
    )


# ---------------------------------------------------------------------------
# 7. Multiple prefix arrays
# ---------------------------------------------------------------------------

@dataclass
class StatisticsPrefix:
    count: list[int]
    sum_values: list[int]
    sum_squares: list[int]

    @classmethod
    def build(cls, values: Sequence[int]) -> "StatisticsPrefix":
        count = [0]
        sums = [0]
        squares = [0]

        for value in values:
            count.append(count[-1] + 1)
            sums.append(sums[-1] + value)
            squares.append(squares[-1] + value * value)

        return cls(count, sums, squares)

    def range_sum(self, left: int, right: int) -> int:
        return self.sum_values[right + 1] - self.sum_values[left]

    def range_count(self, left: int, right: int) -> int:
        return self.count[right + 1] - self.count[left]

    def range_mean(self, left: int, right: int) -> float:
        return self.range_sum(left, right) / self.range_count(left, right)

    def range_variance(self, left: int, right: int) -> float:
        count = self.range_count(left, right)
        total = self.range_sum(left, right)
        square_total = (
            self.squares[right + 1] - self.squares[left]
        )
        mean = total / count
        return square_total / count - mean * mean


def demonstrate_statistics() -> None:
    values = [2, 4, 6, 8, 10]
    statistics = StatisticsPrefix.build(values)

    print("\nRange statistics")
    print("Sum [1, 3] :", statistics.range_sum(1, 3))
    print("Mean [1, 3] :", statistics.range_mean(1, 3))
    print("Variance [1, 3] :", statistics.range_variance(1, 3))


# ---------------------------------------------------------------------------
# 8. Prefix sums and weighted values
# ---------------------------------------------------------------------------

def weighted_prefix(values: Sequence[int], weights: Sequence[int]) -> list[int]:
    """
    Prefix sums can store the accumulated contribution value[i] * weight[i].
    """
    if len(values) != len(weights):
        raise ValueError("Values and weights must have equal length")

    return build_prefix_sum(
        value * weight for value, weight in zip(values, weights)
    )


def demonstrate_weighted_queries() -> None:
    prices = [10, 20, 30, 40]
    quantities = [2, 1, 3, 2]

    revenue_prefix = weighted_prefix(prices, quantities)

    print("\nWeighted prefix sum")
    print("Revenue [1, 3] :",
          prefix_range_sum(revenue_prefix, 1, 3))


# ---------------------------------------------------------------------------
# 9. Difference between prefix sum and prefix XOR
# ---------------------------------------------------------------------------

def build_prefix_xor(values: Sequence[int]) -> list[int]:
    result = [0]

    for value in values:
        result.append(result[-1] ^ value)

    return result


def xor_range_query(
    prefix_xor: Sequence[int],
    left: int,
    right: int,
) -> int:
    # XOR has an inverse because x ^ x = 0.
    return prefix_xor[right + 1] ^ prefix_xor[left]


def demonstrate_prefix_xor() -> None:
    values = [5, 2, 7, 3, 9]
    prefix = build_prefix_xor(values)

    print("\nPrefix XOR")
    print("XOR [1, 3] :", xor_range_query(prefix, 1, 3))


# ---------------------------------------------------------------------------
# 10. Two-dimensional prefix sums
# ---------------------------------------------------------------------------

def build_2d_prefix(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    """
    Build a summed-area table.

    prefix[row][column] represents the sum of the rectangle from (0, 0)
    to (row - 1, column - 1).

    Formula:
        P[r][c] =
            A[r-1][c-1]
            + P[r-1][c]
            + P[r][c-1]
            - P[r-1][c-1]

    The subtraction removes the upper-left region that was counted twice.
    """
    if not matrix:
        return [[0]]

    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("Matrix rows must have equal length")

    rows = len(matrix)
    prefix = [[0] * (columns + 1) for _ in range(rows + 1)]

    for row in range(rows):
        for column in range(columns):
            prefix[row + 1][column + 1] = (
                matrix[row][column]
                + prefix[row][column + 1]
                + prefix[row + 1][column]
                - prefix[row][column]
            )

    return prefix


def rectangle_sum(
    prefix: Sequence[Sequence[int]],
    top: int,
    left: int,
    bottom: int,
    right: int,
) -> int:
    """Return the inclusive rectangle sum in O(1)."""
    if top > bottom or left > right:
        raise ValueError("Invalid rectangle")

    return (
        prefix[bottom + 1][right + 1]
        - prefix[top][right + 1]
        - prefix[bottom + 1][left]
        + prefix[top][left]
    )


def demonstrate_2d_prefix() -> None:
    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
    ]

    prefix = build_2d_prefix(matrix)

    print("\nTwo-dimensional prefix sum")
    print("Rectangle rows 0..1, columns 1..3 :",
          rectangle_sum(prefix, 0, 1, 1, 3))


# ---------------------------------------------------------------------------
# 11. Three-dimensional prefix sums
# ---------------------------------------------------------------------------

def build_3d_prefix(cube: list[list[list[int]]]) -> list[list[list[int]]]:
    """
    Build a 3D summed-volume table.

    Inclusion-exclusion is the three-dimensional extension of the 2D rule.
    """
    if not cube:
        return [[[0]]]

    depth = len(cube)
    rows = len(cube[0])
    columns = len(cube[0][0])

    prefix = [
        [[0] * (columns + 1) for _ in range(rows + 1)]
        for _ in range(depth + 1)
    ]

    for z in range(depth):
        for y in range(rows):
            for x in range(columns):
                prefix[z + 1][y + 1][x + 1] = (
                    cube[z][y][x]
                    + prefix[z][y + 1][x + 1]
                    + prefix[z + 1][y][x + 1]
                    + prefix[z + 1][y + 1][x]
                    - prefix[z][y][x + 1]
                    - prefix[z][y + 1][x]
                    - prefix[z + 1][y][x]
                    + prefix[z][y][x]
                )

    return prefix


def demonstrate_3d_prefix() -> None:
    cube = [
        [[1, 2], [3, 4]],
        [[5, 6], [7, 8]],
    ]

    prefix = build_3d_prefix(cube)
    total = prefix[2][2][2]

    print("\nThree-dimensional prefix sum")
    print("Total cube sum :", total)


# ---------------------------------------------------------------------------
# 12. Prefix sums and subarray problems
# ---------------------------------------------------------------------------

def count_subarrays_with_sum(
    values: Sequence[int],
    target: int,
) -> int:
    """
    Count subarrays whose sum equals target.

    If prefix[j] - prefix[i] == target,
    then prefix[i] == prefix[j] - target.

    A frequency dictionary lets us count previous matching prefix sums.
    This handles negative numbers correctly.
    """
    frequencies = {0: 1}
    current_sum = 0
    answer = 0

    for value in values:
        current_sum += value
        answer += frequencies.get(current_sum - target, 0)
        frequencies[current_sum] = frequencies.get(current_sum, 0) + 1

    return answer


def demonstrate_subarray_sum_count() -> None:
    values = [1, 2, 1, 2, 1]
    target = 3

    print("\nSubarray sum counting")
    print("Number of subarrays with sum 3 :",
          count_subarrays_with_sum(values, target))


# ---------------------------------------------------------------------------
# 13. Longest subarray with a target sum
# ---------------------------------------------------------------------------

def longest_subarray_with_sum(
    values: Sequence[int],
    target: int,
) -> tuple[int, int] | None:
    """
    Return (left, right) for the longest target-sum subarray.

    Store the earliest position at which each prefix sum occurs.
    """
    first_seen = {0: -1}
    current_sum = 0
    best: tuple[int, int] | None = None

    for index, value in enumerate(values):
        current_sum += value
        needed = current_sum - target

        if needed in first_seen:
            candidate = (first_seen[needed] + 1, index)

            if (
                best is None
                or candidate[1] - candidate[0]
                > best[1] - best[0]
            ):
                best = candidate

        if current_sum not in first_seen:
            first_seen[current_sum] = index

    return best


# ---------------------------------------------------------------------------
# 14. Prefix sum modulo arithmetic
# ---------------------------------------------------------------------------

def count_subarrays_divisible_by(
    values: Sequence[int],
    divisor: int,
) -> int:
    """
    Count subarrays whose sum is divisible by divisor.

    Two prefix sums produce a divisible range when their remainders match.
    """
    if divisor == 0:
        raise ValueError("Divisor cannot be zero")

    frequencies = {0: 1}
    remainder = 0
    answer = 0

    for value in values:
        remainder = (remainder + value) % divisor
        answer += frequencies.get(remainder, 0)
        frequencies[remainder] = frequencies.get(remainder, 0) + 1

    return answer


# ---------------------------------------------------------------------------
# 15. Difference arrays: the inverse operation
# ---------------------------------------------------------------------------

def apply_range_additions(
    size: int,
    operations: Sequence[tuple[int, int, int]],
) -> list[int]:
    """
    Efficiently apply many inclusive range additions.

    Instead of changing every element in [left, right], record:
        difference[left] += amount
        difference[right + 1] -= amount

    A final prefix sum reconstructs the resulting array.

    This is the reverse relationship:
        difference -> prefix sum -> actual values
    """
    difference = [0] * (size + 1)

    for left, right, amount in operations:
        if not (0 <= left <= right < size):
            raise ValueError("Invalid update range")

        difference[left] += amount
        difference[right + 1] -= amount

    result = [0] * size
    running = 0

    for index in range(size):
        running += difference[index]
        result[index] = running

    return result


def demonstrate_difference_array() -> None:
    operations = [
        (1, 3, 5),
        (2, 5, 2),
        (0, 1, 4),
    ]

    print("\nDifference-array range updates")
    print("Final values :", apply_range_additions(6, operations))


# ---------------------------------------------------------------------------
# 16. Coordinate compression with range accumulation
# ---------------------------------------------------------------------------

def aggregate_intervals(
    intervals: Sequence[tuple[int, int, int]],
) -> list[tuple[int, int, int]]:
    """
    Aggregate weighted intervals using coordinate compression.

    Each interval is [start, end) with a weight.
    This is useful when coordinates are large but the number of distinct
    endpoints is relatively small.
    """
    if not intervals:
        return []

    coordinates = sorted({
        coordinate
        for start, end, _ in intervals
        for coordinate in (start, end)
    })

    index = {coordinate: i for i, coordinate in enumerate(coordinates)}
    difference = [0] * (len(coordinates) + 1)

    for start, end, weight in intervals:
        if start >= end:
            raise ValueError("Intervals must satisfy start < end")

        difference[index[start]] += weight
        difference[index[end]] -= weight

    result = []
    active = 0

    for i in range(len(coordinates) - 1):
        active += difference[i]

        if active != 0:
            result.append(
                (coordinates[i], coordinates[i + 1], active)
            )

    return result


# ---------------------------------------------------------------------------
# 17. Prefix sums for frequency tables
# ---------------------------------------------------------------------------

def frequency_prefix(values: Sequence[int], maximum_value: int) -> list[int]:
    """
    Build cumulative frequencies for values in [0, maximum_value].

    This is useful when values belong to a compact integer domain.
    """
    if maximum_value < 0:
        raise ValueError("Maximum value must be non-negative")

    frequency = [0] * (maximum_value + 1)

    for value in values:
        if not 0 <= value <= maximum_value:
            raise ValueError("Value outside supported domain")
        frequency[value] += 1

    return build_prefix_sum(frequency)


def count_values_in_domain(
    frequency_prefix_array: Sequence[int],
    low: int,
    high: int,
) -> int:
    return prefix_range_sum(frequency_prefix_array, low, high)


# ---------------------------------------------------------------------------
# 18. Immutable range-query data structure
# ---------------------------------------------------------------------------

class PrefixRangeQuery:
    """Immutable array supporting O(1) range-sum queries."""

    def __init__(self, values: Sequence[int]):
        self._values = tuple(values)
        self._prefix = build_prefix_sum(self._values)

    def query(self, left: int, right: int) -> int:
        return prefix_range_sum(self._prefix, left, right)

    def __len__(self) -> int:
        return len(self._values)


# ---------------------------------------------------------------------------
# 19. Dynamic data: Fenwick tree
# ---------------------------------------------------------------------------

class FenwickTree:
    """
    Binary Indexed Tree.

    Prefix sums solve static range sums efficiently.
    If values must change, rebuilding the prefix array after every update
    can be expensive.

    A Fenwick tree supports:
        point update: O(log n)
        prefix sum:   O(log n)
        range sum:    O(log n)
    """

    def __init__(self, values: Sequence[int]):
        self.size = len(values)
        self.tree = [0] * (self.size + 1)

        for index, value in enumerate(values, start=1):
            self.add(index, value)

    def add(self, index: int, delta: int) -> None:
        """Add delta to the one-based position index."""
        if not 1 <= index <= self.size:
            raise IndexError("Fenwick index out of range")

        while index <= self.size:
            self.tree[index] += delta
            index += index & -index

    def prefix_sum(self, index: int) -> int:
        """Sum the first index one-based elements."""
        if not 0 <= index <= self.size:
            raise IndexError("Fenwick prefix index out of range")

        total = 0

        while index > 0:
            total += self.tree[index]
            index -= index & -index

        return total

    def range_sum(self, left: int, right: int) -> int:
        """Inclusive zero-based range sum."""
        if left < 0 or right < left or right >= self.size:
            raise ValueError("Invalid range")

        return self.prefix_sum(right + 1) - self.prefix_sum(left)


def demonstrate_fenwick_tree() -> None:
    values = [2, 4, 6, 8, 10]
    tree = FenwickTree(values)

    print("\nFenwick tree")
    print("Initial sum [1, 3] :", tree.range_sum(1, 3))

    # Add 5 to zero-based index 2.
    tree.add(3, 5)

    print("After update [1, 3] :", tree.range_sum(1, 3))


# ---------------------------------------------------------------------------
# 20. Segment tree for dynamic range sums
# ---------------------------------------------------------------------------

class SegmentTree:
    """
    Segment tree for point updates and range sums.

    Both update and query take O(log n).
    Segment trees use more memory and implementation complexity than prefix
    sums, but they generalize to many other associative operations.
    """

    def __init__(self, values: Sequence[int]):
        self.size = 1

        while self.size < len(values):
            self.size *= 2

        self.tree = [0] * (2 * self.size)

        for index, value in enumerate(values):
            self.tree[self.size + index] = value

        for index in range(self.size - 1, 0, -1):
            self.tree[index] = (
                self.tree[index * 2]
                + self.tree[index * 2 + 1]
            )

    def update(self, index: int, value: int) -> None:
        if not 0 <= index < self.size:
            raise IndexError("Segment-tree index out of range")

        position = self.size + index
        self.tree[position] = value

        position //= 2

        while position:
            self.tree[position] = (
                self.tree[position * 2]
                + self.tree[position * 2 + 1]
            )
            position //= 2

    def query(self, left: int, right: int) -> int:
        """Inclusive range query."""
        if left < 0 or right < left or right >= self.size:
            raise ValueError("Invalid range")

        left += self.size
        right += self.size
        result = 0

        while left <= right:
            if left % 2 == 1:
                result += self.tree[left]
                left += 1

            if right % 2 == 0:
                result += self.tree[right]
                right -= 1

            left //= 2
            right //= 2

        return result


# ---------------------------------------------------------------------------
# 21. Prefix sums for stock or sensor time series
# ---------------------------------------------------------------------------

def cumulative_changes(values: Sequence[int]) -> list[int]:
    """
    If values represent daily changes, their prefix sum gives cumulative
    change from the beginning of the observation period.
    """
    return build_prefix_sum(values)


def maximum_subarray_sum(values: Sequence[int]) -> int:
    """
    Kadane's algorithm is closely related to prefix sums.

    For each ending position:
        best ending here = current prefix - minimum previous prefix.
    """
    if not values:
        raise ValueError("At least one value is required")

    current_prefix = 0
    minimum_prefix = 0
    best = values[0]

    for value in values:
        current_prefix += value
        best = max(best, current_prefix - minimum_prefix)
        minimum_prefix = min(minimum_prefix, current_prefix)

    return best


# ---------------------------------------------------------------------------
# 22. Prefix/suffix distinction
# ---------------------------------------------------------------------------

def build_suffix_sum(values: Sequence[int]) -> list[int]:
    """
    suffix[i] is the sum of values[i:].

    Prefix sums naturally answer ranges relative to the beginning.
    Suffix sums naturally answer ranges relative to the end.
    """
    suffix = [0] * (len(values) + 1)

    for index in range(len(values) - 1, -1, -1):
        suffix[index] = suffix[index + 1] + values[index]

    return suffix


# ---------------------------------------------------------------------------
# 23. Testing and correctness checks
# ---------------------------------------------------------------------------

def brute_force_rectangle_sum(
    matrix: Sequence[Sequence[int]],
    top: int,
    left: int,
    bottom: int,
    right: int,
) -> int:
    return sum(
        matrix[row][column]
        for row in range(top, bottom + 1)
        for column in range(left, right + 1)
    )


def test_1d_prefix_sum() -> None:
    random = Random(123)

    for _ in range(100):
        size = random.randint(1, 30)
        values = [random.randint(-20, 20) for _ in range(size)]
        prefix = build_prefix_sum(values)

        for _ in range(50):
            left = random.randint(0, size - 1)
            right = random.randint(left, size - 1)

            assert prefix_range_sum(prefix, left, right) == (
                naive_range_sum(values, left, right)
            )


def test_2d_prefix_sum() -> None:
    random = Random(456)

    for _ in range(50):
        rows = random.randint(1, 8)
        columns = random.randint(1, 8)

        matrix = [
            [random.randint(-10, 10) for _ in range(columns)]
            for _ in range(rows)
        ]

        prefix = build_2d_prefix(matrix)

        for _ in range(20):
            top = random.randint(0, rows - 1)
            bottom = random.randint(top, rows - 1)
            left = random.randint(0, columns - 1)
            right = random.randint(left, columns - 1)

            assert rectangle_sum(
                prefix,
                top,
                left,
                bottom,
                right,
            ) == brute_force_rectangle_sum(
                matrix,
                top,
                left,
                bottom,
                right,
            )


def run_tests() -> None:
    test_1d_prefix_sum()
    test_2d_prefix_sum()

    assert count_subarrays_with_sum([1, 1, 1], 2) == 2
    assert count_subarrays_with_sum([1, -1, 1], 1) == 3
    assert count_subarrays_divisible_by([4, 5, 0, -2, -3, 1], 5) == 7

    assert longest_subarray_with_sum(
        [1, -1, 5, -2, 3],
        3,
    ) == (0, 3)

    assert apply_range_additions(
        5,
        [(1, 3, 2)],
    ) == [0, 2, 2, 2, 0]

    values = [1, 2, 3, 4, 5]
    fenwick = FenwickTree(values)
    segment = SegmentTree(values)

    assert fenwick.range_sum(1, 4) == 14
    assert segment.query(1, 4) == 14

    print("\nAll correctness tests passed.")


# ---------------------------------------------------------------------------
# 24. Complexity reference
# ---------------------------------------------------------------------------

def print_complexity_reference() -> None:
    print(
        """
Complexity reference

Technique                       Build/Update        Query
----------------------------------------------------------------
Naive range sum                 O(n)                O(k)
1D prefix sum                   O(n)                O(1)
2D prefix sum                   O(rows*cols)       O(1)
3D prefix sum                   O(volume)           O(1)
Difference array               O(number_updates)   O(n) finalization
Fenwick tree                   O(n log n)           O(log n)
Segment tree                   O(n)                O(log n)

Memory:
1D prefix sum: O(n)
2D prefix sum: O(rows * columns)
3D prefix sum: O(depth * rows * columns)

Prefix sums are particularly effective when the data is static and many
range queries must be answered.
"""
    )


# ---------------------------------------------------------------------------
# 25. Practical checklist
# ---------------------------------------------------------------------------

def print_problem_solving_checklist() -> None:
    print(
        """
Prefix-sum recognition checklist

1. Is the operation additive or otherwise invertible?
2. Are there many range queries?
3. Is the underlying data mostly static?
4. Can preprocessing be performed once?
5. Can a range be expressed as:
       prefix[right + 1] - prefix[left]
6. For a matrix, does the problem ask for repeated rectangle sums?
7. For many range updates, would a difference array be appropriate?
8. If updates and queries are mixed, would a Fenwick tree or segment tree
   be more appropriate?
9. Are integer overflow and numeric precision relevant?
10. Are index conventions consistent throughout the implementation?
"""
    )


def main() -> None:
    print("PREFIX SUM STUDY PROGRAM")
    print("=" * 60)

    demonstrate_basic_prefix_sum()
    demonstrate_negative_values()
    demonstrate_counting()
    demonstrate_conditional_counting()
    demonstrate_statistics()
    demonstrate_weighted_queries()
    demonstrate_prefix_xor()
    demonstrate_2d_prefix()
    demonstrate_3d_prefix()
    demonstrate_subarray_sum_count()
    demonstrate_difference_array()
    demonstrate_fenwick_tree()
    demonstrate_performance_difference()

    query_structure = PrefixRangeQuery([10, 20, 30, 40, 50])
    print("\nImmutable query structure")
    print("Sum [1, 3] :", query_structure.query(1, 3))

    print("\nLongest target-sum subarray")
    print(
        "Result:",
        longest_subarray_with_sum([1, -1, 5, -2, 3], 3),
    )

    print("\nMaximum subarray sum")
    print(
        "Result:",
        maximum_subarray_sum([-2, 3, -1, 4, -5]),
    )

    print("\nCoordinate-compressed intervals")
    print(
        aggregate_intervals(
            [(10, 20, 2), (15, 25, 3), (22, 30, 1)]
        )
    )

    run_tests()
    print_complexity_reference()
    print_problem_solving_checklist()


if __name__ == "__main__":
    main()
