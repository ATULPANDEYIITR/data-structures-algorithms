"""
Difference Arrays
=================

A comprehensive standalone study file for learning difference arrays from
beginner level through advanced range-update techniques.

Core idea:
    For an array a, define a difference array d such that

        d[0] = a[0]
        d[i] = a[i] - a[i - 1]       for i > 0

A range addition [left, right] += value can then be represented by only
two boundary changes:

    d[left]  += value
    d[right + 1] -= value

when right + 1 is inside the difference array.

A prefix sum of d reconstructs the updated array.

This converts each range update from O(n) to O(1), followed by one
O(n) reconstruction pass.

The examples below progress from basic arithmetic to:
- construction and reconstruction
- range additions
- range assignment using a related technique
- range increments with final point queries
- 2D difference arrays
- multiple test cases
- coordinate compression
- interval coverage
- imos-style event processing
- performance comparisons
- validation and testing
- common edge cases
"""

from __future__ import annotations

from dataclasses import dataclass
from random import randint, seed
from time import perf_counter
from typing import Iterable, List, Sequence, Tuple


# ---------------------------------------------------------------------------
# 1. FUNDAMENTAL DIFFERENCE ARRAY
# ---------------------------------------------------------------------------

def build_difference_array(values: Sequence[int]) -> List[int]:
    """Return the first-order difference array of values."""
    if not values:
        return []

    difference = [0] * len(values)
    difference[0] = values[0]

    for index in range(1, len(values)):
        difference[index] = values[index] - values[index - 1]

    return difference


def reconstruct_from_difference(difference: Sequence[int]) -> List[int]:
    """Reconstruct the original array using prefix sums."""
    if not difference:
        return []

    values = [0] * len(difference)
    running_value = 0

    for index, change in enumerate(difference):
        running_value += change
        values[index] = running_value

    return values


def demonstrate_fundamentals() -> None:
    values = [10, 13, 13, 20, 17]

    difference = build_difference_array(values)
    reconstructed = reconstruct_from_difference(difference)

    print("Original array:      ", values)
    print("Difference array:    ", difference)
    print("Reconstructed array: ", reconstructed)

    assert reconstructed == values


# ---------------------------------------------------------------------------
# 2. WHY RANGE UPDATES BECOME O(1)
# ---------------------------------------------------------------------------

def apply_range_update_difference(
    difference: List[int],
    left: int,
    right: int,
    amount: int,
) -> None:
    """
    Record values[left:right + 1] += amount in O(1).

    The caller must later reconstruct the final array with a prefix sum.

    A sentinel element is useful because right + 1 may equal n.
    """
    if not 0 <= left <= right:
        raise ValueError("Require 0 <= left <= right.")

    if right >= len(difference) - 1:
        raise IndexError("Difference array must contain a sentinel slot.")

    difference[left] += amount
    difference[right + 1] -= amount


def range_additions_difference(
    values: Sequence[int],
    updates: Iterable[Tuple[int, int, int]],
) -> List[int]:
    """
    Apply inclusive range additions efficiently.

    Each update is (left, right, amount).

    Complexity:
        update recording: O(1) each
        reconstruction:   O(n)
        total:             O(n + q)
    """
    n = len(values)
    if n == 0:
        return []

    difference = [0] * (n + 1)

    # Encode the initial array itself into difference form.
    initial_difference = build_difference_array(values)
    for index, value in enumerate(initial_difference):
        difference[index] = value

    for left, right, amount in updates:
        if not 0 <= left <= right < n:
            raise IndexError(f"Invalid range [{left}, {right}] for n={n}.")
        apply_range_update_difference(difference, left, right, amount)

    result = [0] * n
    running_value = 0

    for index in range(n):
        running_value += difference[index]
        result[index] = running_value

    return result


def range_additions_naive(
    values: Sequence[int],
    updates: Iterable[Tuple[int, int, int]],
) -> List[int]:
    """Reference implementation that updates every element in each range."""
    result = list(values)

    for left, right, amount in updates:
        if not 0 <= left <= right < len(result):
            raise IndexError(f"Invalid range [{left}, {right}].")

        for index in range(left, right + 1):
            result[index] += amount

    return result


def demonstrate_range_updates() -> None:
    values = [5, 5, 5, 5, 5, 5]

    updates = [
        (1, 4, 3),
        (0, 2, 10),
        (3, 5, -2),
    ]

    efficient = range_additions_difference(values, updates)
    reference = range_additions_naive(values, updates)

    print("\nRange updates")
    print("Initial:  ", values)
    print("Updates:  ", updates)
    print("Result:   ", efficient)

    assert efficient == reference


# ---------------------------------------------------------------------------
# 3. SENTINEL TECHNIQUE
# ---------------------------------------------------------------------------

def difference_with_sentinel(n: int) -> List[int]:
    """
    Create a zero-initialized difference array of size n + 1.

    The extra position n stores a boundary subtraction after an update
    ending at n - 1. It does not belong to the final data array.
    """
    if n < 0:
        raise ValueError("Array length cannot be negative.")
    return [0] * (n + 1)


def demonstrate_sentinel() -> None:
    n = 5
    difference = difference_with_sentinel(n)

    # Add 7 to the entire [0, 4] range.
    difference[0] += 7
    difference[5] -= 7

    result = []
    running = 0

    for index in range(n):
        running += difference[index]
        result.append(running)

    print("\nSentinel example:", result)
    assert result == [7, 7, 7, 7, 7]


# ---------------------------------------------------------------------------
# 4. DIFFERENCE ARRAY STARTING FROM ZERO
# ---------------------------------------------------------------------------

def process_zero_array_range_additions(
    n: int,
    updates: Sequence[Tuple[int, int, int]],
) -> List[int]:
    """
    Common competitive-programming form:

    Start with n zeros and apply q range additions.
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    difference = [0] * (n + 1)

    for left, right, amount in updates:
        if not (0 <= left <= right < n):
            raise IndexError("Update range is outside the array.")
        difference[left] += amount
        difference[right + 1] -= amount

    result = [0] * n
    running = 0

    for index in range(n):
        running += difference[index]
        result[index] = running

    return result


# ---------------------------------------------------------------------------
# 5. POINT QUERIES AFTER MANY RANGE UPDATES
# ---------------------------------------------------------------------------

def final_point_values(
    n: int,
    updates: Sequence[Tuple[int, int, int]],
    query_indices: Sequence[int],
) -> List[int]:
    """
    If all updates are known before the queries, process every update in O(1)
    and compute all final point values in O(n).

    If only selected points are needed and coordinates are sparse, coordinate
    compression can reduce the amount of work; see the later example.
    """
    values = process_zero_array_range_additions(n, updates)

    for index in query_indices:
        if not 0 <= index < n:
            raise IndexError(f"Point {index} is outside [0, {n - 1}].")

    return [values[index] for index in query_indices]


# ---------------------------------------------------------------------------
# 6. RANGE SUMS AFTER UPDATES
# ---------------------------------------------------------------------------

def range_add_then_range_sum(
    values: Sequence[int],
    updates: Sequence[Tuple[int, int, int]],
    queries: Sequence[Tuple[int, int]],
) -> List[int]:
    """
    Difference arrays efficiently handle a batch of range additions.

    Once the final array is reconstructed, a second prefix-sum array can
    answer static range-sum queries in O(1).

    This is efficient when:
        all updates happen first
        all queries happen afterward

    It is NOT a substitute for a Fenwick tree or segment tree when updates
    and queries are interleaved dynamically.
    """
    final_values = range_additions_difference(values, updates)

    prefix = [0] * (len(final_values) + 1)

    for index, value in enumerate(final_values):
        prefix[index + 1] = prefix[index] + value

    answers = []

    for left, right in queries:
        if not 0 <= left <= right < len(final_values):
            raise IndexError("Invalid query range.")

        answers.append(prefix[right + 1] - prefix[left])

    return answers


# ---------------------------------------------------------------------------
# 7. DIFFERENCE ARRAYS FOR FREQUENCY / INTERVAL COVERAGE
# ---------------------------------------------------------------------------

def interval_coverage(
    intervals: Sequence[Tuple[int, int]],
    maximum_coordinate: int,
) -> List[int]:
    """
    Count how many inclusive intervals cover each integer coordinate.

    Each interval [left, right] contributes:
        +1 at left
        -1 at right + 1

    This is often called a sweep-line or imos-style technique.
    """
    if maximum_coordinate < 0:
        raise ValueError("maximum_coordinate must be non-negative.")

    difference = [0] * (maximum_coordinate + 2)

    for left, right in intervals:
        if not 0 <= left <= right <= maximum_coordinate:
            raise IndexError("Interval is outside the coordinate range.")

        difference[left] += 1
        difference[right + 1] -= 1

    coverage = [0] * (maximum_coordinate + 1)
    running = 0

    for coordinate in range(maximum_coordinate + 1):
        running += difference[coordinate]
        coverage[coordinate] = running

    return coverage


def demonstrate_interval_coverage() -> None:
    intervals = [(1, 4), (2, 6), (4, 5)]

    coverage = interval_coverage(intervals, 7)

    print("\nInterval coverage")
    print("Intervals:", intervals)
    print("Coverage: ", coverage)

    assert coverage == [0, 1, 2, 2, 3, 2, 1, 0]


# ---------------------------------------------------------------------------
# 8. EVENT COUNTING
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TimeInterval:
    start: int
    end: int


def maximum_concurrent_intervals(
    intervals: Sequence[TimeInterval],
) -> Tuple[int, int]:
    """
    Find the maximum number of active half-open intervals [start, end).

    Half-open intervals make an interval ending at t inactive at t, while
    another interval starting at t is active.

    For integer coordinates this can be implemented with events.
    """
    if not intervals:
        return 0, 0

    events = {}

    for interval in intervals:
        if interval.start > interval.end:
            raise ValueError("start cannot exceed end.")

        events[interval.start] = events.get(interval.start, 0) + 1
        events[interval.end] = events.get(interval.end, 0) - 1

    active = 0
    maximum = 0
    maximum_time = min(events)

    for time in sorted(events):
        active += events[time]

        if active > maximum:
            maximum = active
            maximum_time = time

    return maximum, maximum_time


# ---------------------------------------------------------------------------
# 9. DIFFERENCE ARRAY FOR RANGE ASSIGNMENT
# ---------------------------------------------------------------------------

def range_assignments_offline(
    n: int,
    assignments: Sequence[Tuple[int, int, int]],
) -> List[int]:
    """
    Range assignment is different from range addition.

    For:
        array[left:right + 1] = value

    simple first-order addition markers are insufficient because assignment
    overwrites earlier values.

    One offline strategy is to process assignments from right to left while
    using a disjoint-set "next unassigned position" structure. Each position
    is assigned once.

    Complexity is approximately O((n + q) alpha(n)).
    """
    if n < 0:
        raise ValueError("n must be non-negative.")

    result = [0] * n

    # parent[i] points to the next potentially unassigned position.
    parent = list(range(n + 1))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for left, right, value in reversed(assignments):
        if not 0 <= left <= right < n:
            raise IndexError("Invalid assignment range.")

        position = find(left)

        while position <= right:
            result[position] = value
            parent[position] = find(position + 1)
            position = find(position)

    return result


def demonstrate_assignment_distinction() -> None:
    assignments = [
        (0, 4, 10),
        (1, 3, 20),
        (2, 2, 30),
    ]

    result = range_assignments_offline(5, assignments)

    print("\nRange assignment:", result)
    assert result == [10, 20, 30, 20, 10]


# ---------------------------------------------------------------------------
# 10. TWO-DIMENSIONAL DIFFERENCE ARRAYS
# ---------------------------------------------------------------------------

def add_rectangle_2d(
    difference: List[List[int]],
    top: int,
    left: int,
    bottom: int,
    right: int,
    amount: int,
) -> None:
    """
    Add amount to every cell in inclusive rectangle:

        top <= row <= bottom
        left <= column <= right

    Four corner changes encode the rectangle.
    """
    rows = len(difference) - 1
    columns = len(difference[0]) - 1 if difference else 0

    if not (0 <= top <= bottom < rows):
        raise IndexError("Invalid row range.")

    if not (0 <= left <= right < columns):
        raise IndexError("Invalid column range.")

    difference[top][left] += amount
    difference[bottom + 1][left] -= amount
    difference[top][right + 1] -= amount
    difference[bottom + 1][right + 1] += amount


def rectangle_updates_2d(
    rows: int,
    columns: int,
    updates: Sequence[Tuple[int, int, int, int, int]],
) -> List[List[int]]:
    """
    Apply rectangle additions offline.

    Each update is:
        (top, left, bottom, right, amount)

    Time:
        O(q + rows * columns)
    """
    if rows < 0 or columns < 0:
        raise ValueError("Dimensions cannot be negative.")

    difference = [
        [0] * (columns + 1)
        for _ in range(rows + 1)
    ]

    for top, left, bottom, right, amount in updates:
        add_rectangle_2d(
            difference,
            top,
            left,
            bottom,
            right,
            amount,
        )

    result = [[0] * columns for _ in range(rows)]

    for row in range(rows):
        for column in range(columns):
            above = result[row - 1][column] if row > 0 else 0
            left_value = result[row][column - 1] if column > 0 else 0
            diagonal = (
                result[row - 1][column - 1]
                if row > 0 and column > 0
                else 0
            )

            result[row][column] = (
                difference[row][column]
                + above
                + left_value
                - diagonal
            )

    return result


def demonstrate_2d() -> None:
    updates = [
        (0, 0, 1, 2, 5),
        (1, 1, 2, 3, 3),
    ]

    result = rectangle_updates_2d(3, 4, updates)

    expected = [
        [5, 5, 5, 0],
        [5, 8, 8, 3],
        [0, 3, 3, 3],
    ]

    print("\n2D difference array:")
    for row in result:
        print(row)

    assert result == expected


# ---------------------------------------------------------------------------
# 11. TWO-DIMENSIONAL INTUITION
# ---------------------------------------------------------------------------

def explain_2d_corner_markers() -> None:
    """
    A rectangle update uses inclusion-exclusion:

        + at (top, left)
        - below the rectangle
        - right of the rectangle
        + diagonally below/right

    The final two-dimensional prefix sum causes the four markers to combine
    into exactly the desired rectangle.
    """
    print(
        "\n2D rule: "
        "D[top][left] += x, "
        "D[bottom+1][left] -= x, "
        "D[top][right+1] -= x, "
        "D[bottom+1][right+1] += x"
    )


# ---------------------------------------------------------------------------
# 12. COORDINATE COMPRESSION FOR HUGE COORDINATES
# ---------------------------------------------------------------------------

def compressed_interval_additions(
    intervals: Sequence[Tuple[int, int, int]],
) -> List[Tuple[int, int, int]]:
    """
    Apply additions to huge integer coordinate intervals without allocating
    an array for every coordinate.

    Intervals use the half-open convention [left, right).

    Return segments:
        (segment_start, segment_end, accumulated_value)

    Example:
        [10, 1_000_000_000) does not require a billion-element array.
    """
    if not intervals:
        return []

    coordinates = sorted(
        {
            coordinate
            for left, right, _ in intervals
            for coordinate in (left, right)
        }
    )

    index_of = {
        coordinate: index
        for index, coordinate in enumerate(coordinates)
    }

    difference = [0] * (len(coordinates) + 1)

    for left, right, amount in intervals:
        if left >= right:
            raise ValueError("Require left < right.")

        difference[index_of[left]] += amount
        difference[index_of[right]] -= amount

    segments = []
    running = 0

    for index in range(len(coordinates) - 1):
        running += difference[index]

        start = coordinates[index]
        end = coordinates[index + 1]

        if running != 0:
            segments.append((start, end, running))

    return segments


def demonstrate_coordinate_compression() -> None:
    intervals = [
        (10, 1_000_000_000, 5),
        (500, 700, 3),
        (600, 900, -2),
    ]

    segments = compressed_interval_additions(intervals)

    print("\nCompressed interval segments:")
    for segment in segments:
        print(segment)


# ---------------------------------------------------------------------------
# 13. DIFFERENCE ARRAYS AS DISCRETE DERIVATIVES
# ---------------------------------------------------------------------------

def discrete_derivative(values: Sequence[int]) -> List[int]:
    """
    A first-order difference array behaves like a discrete derivative.

    Prefix summation is the corresponding reconstruction operation.

    Continuous analogy:
        derivative -> change/rate
        integral   -> accumulation

    The analogy is conceptual, not an assertion that discrete and continuous
    calculus are identical.
    """
    return build_difference_array(values)


def demonstrate_derivative_view() -> None:
    values = [2, 2, 2, 7, 7, 4]

    derivative = discrete_derivative(values)
    recovered = reconstruct_from_difference(derivative)

    print("\nDiscrete derivative:", derivative)
    print("Recovered values:   ", recovered)


# ---------------------------------------------------------------------------
# 14. SECOND-ORDER DIFFERENCE ARRAYS
# ---------------------------------------------------------------------------

def second_difference(values: Sequence[int]) -> List[int]:
    """
    Compute a second-order discrete difference.

    First difference:
        d[i] = a[i] - a[i - 1]

    Second difference:
        dd[i] = d[i] - d[i - 1]

    Second differences are useful when updates involve arithmetic progressions
    or linear changes rather than constant range additions.
    """
    first = build_difference_array(values)
    return build_difference_array(first)


def demonstrate_second_difference() -> None:
    values = [1, 3, 5, 7, 9]

    first = build_difference_array(values)
    second = second_difference(values)

    print("\nValues:  ", values)
    print("First:   ", first)
    print("Second:  ", second)


# ---------------------------------------------------------------------------
# 15. RANGE UPDATE WITH AN ARITHMETIC PROGRESSION
# ---------------------------------------------------------------------------

def add_arithmetic_progression(
    difference_of_difference: List[int],
    left: int,
    right: int,
    first_value: int,
    common_difference: int,
) -> None:
    """
    Demonstrate the boundary principle for a linear range update.

    We want:

        a[left]     += first_value
        a[left + 1] += first_value + d
        ...
        a[right]    += first_value + (right-left)d

    If D is the first difference of a, a linear update changes D by a
    constant amount across the interval. A second-order difference array
    therefore needs only boundary corrections.

    This implementation stores second differences explicitly and then
    performs two prefix sums.

    Let k = right - left.

    The update sequence has first difference:
        first_value at left
        d afterward

    Boundary markers in the second difference are:

        DD[left]       += first_value
        DD[left + 1]    += d - first_value
        DD[right + 1]   -= d
        DD[right + 2]   -= 0

    A simpler and less error-prone implementation for general use is to
    encode the sequence's first differences directly, shown below.
    """
    if not 0 <= left <= right:
        raise ValueError("Invalid range.")

    # First element contribution.
    difference_of_difference[left] += first_value

    if left + 1 < len(difference_of_difference):
        difference_of_difference[left + 1] += common_difference - first_value

    if right + 2 < len(difference_of_difference):
        difference_of_difference[right + 2] -= common_difference


def range_linear_updates(
    n: int,
    updates: Sequence[Tuple[int, int, int, int]],
) -> List[int]:
    """
    Apply linear/arithmetic-progression updates.

    Each update:
        (left, right, first_value, common_difference)

    The implementation uses a second-order difference representation.

    Two prefix passes reconstruct the final values.
    """
    if n < 0:
        raise ValueError("n cannot be negative.")

    second_difference = [0] * (n + 2)

    for left, right, first_value, common_difference in updates:
        if not 0 <= left <= right < n:
            raise IndexError("Invalid range.")

        add_arithmetic_progression(
            second_difference,
            left,
            right,
            first_value,
            common_difference,
        )

    first_difference = [0] * (n + 1)
    running_first = 0

    for index in range(n + 1):
        running_first += second_difference[index]
        first_difference[index] = running_first

    result = [0] * n
    running_value = 0

    for index in range(n):
        running_value += first_difference[index]
        result[index] = running_value

    return result


def demonstrate_linear_updates() -> None:
    result = range_linear_updates(
        7,
        [
            (1, 4, 10, 2),
            (0, 2, 3, -1),
        ],
    )

    # First update: 0, 10, 12, 14, 16, 0, 0
    # Second update: 3, 2, 1, 0, 0, 0, 0
    expected = [3, 12, 13, 14, 16, 0, 0]

    print("\nArithmetic-progression range update:", result)
    assert result == expected


# ---------------------------------------------------------------------------
# 16. DIFFERENCE ARRAYS AND PREFIX SUMS
# ---------------------------------------------------------------------------

def prefix_sum(values: Sequence[int]) -> List[int]:
    """Return an inclusive prefix sum array."""
    result = []
    running = 0

    for value in values:
        running += value
        result.append(running)

    return result


def demonstrate_inverse_operations() -> None:
    values = [4, -1, 8, 8, 12]

    difference = build_difference_array(values)
    recovered = prefix_sum(difference)

    print("\nOriginal:    ", values)
    print("Difference:  ", difference)
    print("Prefix sum:  ", recovered)

    assert recovered == values


# ---------------------------------------------------------------------------
# 17. RANDOMIZED TESTING
# ---------------------------------------------------------------------------

def randomized_correctness_test(
    test_cases: int = 300,
    maximum_n: int = 30,
    maximum_updates: int = 40,
) -> None:
    """
    Compare the optimized implementation against the simple reference.

    Randomized differential testing is especially useful for boundary-heavy
    algorithms because off-by-one mistakes are common.
    """
    for _ in range(test_cases):
        n = randint(0, maximum_n)

        values = [randint(-20, 20) for _ in range(n)]

        updates = []

        if n > 0:
            number_of_updates = randint(0, maximum_updates)

            for _ in range(number_of_updates):
                left = randint(0, n - 1)
                right = randint(left, n - 1)
                amount = randint(-20, 20)
                updates.append((left, right, amount))

        efficient = range_additions_difference(values, updates)
        reference = range_additions_naive(values, updates)

        if efficient != reference:
            raise AssertionError(
                f"Mismatch:\n"
                f"values={values}\n"
                f"updates={updates}\n"
                f"efficient={efficient}\n"
                f"reference={reference}"
            )

    print(f"\nRandomized tests passed: {test_cases}")


# ---------------------------------------------------------------------------
# 18. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    cases = [
        ("empty", [], []),
        ("single element", [7], []),
        ("negative values", [-5, -2, -9], [(0, 2, 4)]),
        ("single-point update", [1, 2, 3], [(1, 1, 10)]),
        ("whole-array update", [1, 2, 3], [(0, 2, 5)]),
    ]

    print("\nEdge cases:")

    for name, values, updates in cases:
        result = range_additions_difference(values, updates)
        print(f"{name:20s} -> {result}")


# ---------------------------------------------------------------------------
# 19. PERFORMANCE COMPARISON
# ---------------------------------------------------------------------------

def performance_demo() -> None:
    """
    Demonstrate the asymptotic advantage.

    The benchmark is intentionally moderate so the script remains practical
    on ordinary computers. Exact timings depend on hardware and Python
    runtime implementation.
    """
    n = 20_000
    q = 4_000

    updates = []

    for _ in range(q):
        left = randint(0, n - 1)
        right = randint(left, n - 1)
        amount = randint(-10, 10)
        updates.append((left, right, amount))

    values = [0] * n

    start = perf_counter()
    naive = range_additions_naive(values, updates)
    naive_time = perf_counter() - start

    start = perf_counter()
    efficient = range_additions_difference(values, updates)
    efficient_time = perf_counter() - start

    assert naive == efficient

    print("\nPerformance comparison")
    print(f"n={n}, updates={q}")
    print(f"Naive time:       {naive_time:.6f} seconds")
    print(f"Difference time:  {efficient_time:.6f} seconds")

    if efficient_time > 0:
        print(f"Measured ratio:   {naive_time / efficient_time:.2f}x")


# ---------------------------------------------------------------------------
# 20. COMPLEXITY TABLE
# ---------------------------------------------------------------------------

def print_complexity_table() -> None:
    print(
        """
Complexity reference

Operation                                      Difference Array
----------------------------------------------------------------
Construct from n values                        O(n)
Single range addition                          O(1)
q range additions                              O(q)
Reconstruct final array                        O(n)
q updates + final reconstruction               O(n + q)
Final point query after reconstruction          O(1)
Static range sum after prefix sums             O(1)
Building 2D rectangle markers                  O(1) per update
Reconstructing an r x c matrix                 O(r * c)
Coordinate-compressed interval processing     O(q log q)
"""
    )


# ---------------------------------------------------------------------------
# 21. VALIDATION HELPERS
# ---------------------------------------------------------------------------

def validate_range(left: int, right: int, length: int) -> None:
    """Centralized inclusive-range validation."""
    if length < 0:
        raise ValueError("length must be non-negative.")

    if not 0 <= left <= right < length:
        raise IndexError(
            f"Expected 0 <= left <= right < {length}, "
            f"received [{left}, {right}]."
        )


def demonstrate_validation() -> None:
    print("\nValidation example:")

    try:
        validate_range(4, 2, 5)
    except (ValueError, IndexError) as error:
        print("Rejected invalid range:", error)

    try:
        range_additions_difference(
            [1, 2, 3],
            [(0, 5, 10)],
        )
    except (ValueError, IndexError) as error:
        print("Rejected out-of-bounds update:", error)


# ---------------------------------------------------------------------------
# 22. IMPORTANT DISTINCTION: INCLUSIVE VS HALF-OPEN RANGES
# ---------------------------------------------------------------------------

def demonstrate_range_conventions() -> None:
    """
    Inclusive:
        [left, right]
        boundary is right + 1

    Half-open:
        [left, right)
        boundary is right

    Mixing these conventions is a major source of off-by-one bugs.
    """
    inclusive = (2, 5)
    half_open = (2, 6)

    print("\nRange conventions")
    print("Inclusive [2, 5] contains:", list(range(inclusive[0], inclusive[1] + 1)))
    print("Half-open [2, 6) contains:", list(range(half_open[0], half_open[1])))


# ---------------------------------------------------------------------------
# 23. PRACTICAL EXAMPLE: FLIGHT BOOKING / CAPACITY LOAD
# ---------------------------------------------------------------------------

def flight_capacity_load(
    number_of_days: int,
    bookings: Sequence[Tuple[int, int, int]],
) -> List[int]:
    """
    Compute total passenger load per day.

    Each booking is:
        (start_day, end_day, passengers)

    This models a common range-addition problem.
    """
    return process_zero_array_range_additions(number_of_days, bookings)


def demonstrate_flight_capacity() -> None:
    bookings = [
        (0, 2, 100),
        (1, 4, 50),
        (3, 5, 80),
    ]

    load = flight_capacity_load(6, bookings)

    print("\nDaily passenger load:", load)
    assert load == [100, 150, 150, 130, 130, 80]


# ---------------------------------------------------------------------------
# 24. PRACTICAL EXAMPLE: SERVER TRAFFIC WINDOWS
# ---------------------------------------------------------------------------

def traffic_per_minute(
    minutes: int,
    traffic_windows: Sequence[Tuple[int, int, int]],
) -> List[int]:
    """
    Add a traffic rate to each inclusive time window.

    Example:
        (10, 20, 50) means +50 requests per minute from minute 10 through 20.
    """
    return process_zero_array_range_additions(minutes, traffic_windows)


def demonstrate_server_traffic() -> None:
    traffic = traffic_per_minute(
        10,
        [
            (0, 4, 10),
            (2, 6, 20),
            (5, 9, 15),
        ],
    )

    print("\nTraffic profile:", traffic)


# ---------------------------------------------------------------------------
# 25. COMMON MISTAKES
# ---------------------------------------------------------------------------

def print_common_mistakes() -> None:
    print(
        """
Common mistakes

1. Forgetting the subtraction at right + 1.
2. Allocating n instead of n + 1 when right can be n - 1.
3. Confusing inclusive [left, right] with half-open [left, right).
4. Forgetting the final prefix-sum reconstruction.
5. Applying the technique to dynamic update/query workloads where a
   Fenwick tree or segment tree is more appropriate.
6. Using an integer array when coordinate values are too large for direct
   allocation.
7. Forgetting that difference arrays solve range ADDITION naturally, not
   arbitrary range assignment.
8. Mishandling empty arrays.
9. Allowing left > right.
10. Ignoring integer overflow in fixed-width languages such as C++.
"""
    )


# ---------------------------------------------------------------------------
# 26. WHEN TO USE A DIFFERENCE ARRAY
# ---------------------------------------------------------------------------

def print_design_guidance() -> None:
    print(
        """
Use a difference array when:

- Updates affect contiguous ranges.
- Updates are additions/increments/decrements.
- Many updates are known before the final state is required.
- You can afford an O(n) reconstruction pass.

Prefer another data structure when:

- Updates and queries are interleaved.
- You need range sums immediately after every update.
- You need minimum/maximum queries under dynamic updates.
- You need arbitrary range assignment with online queries.
- You need persistence or complex query operations.

Typical alternatives:
- Prefix sums: static range queries.
- Fenwick tree: dynamic point/range aggregate patterns.
- Segment tree: richer dynamic range queries and updates.
- Lazy segment tree: complex range updates plus range queries.
- Sweep line + coordinate compression: huge sparse coordinate domains.
"""
    )


# ---------------------------------------------------------------------------
# 27. MAIN EDUCATIONAL DRIVER
# ---------------------------------------------------------------------------

def main() -> None:
    seed(42)

    print("=" * 72)
    print("DIFFERENCE ARRAYS: COMPLETE PYTHON STUDY")
    print("=" * 72)

    demonstrate_fundamentals()
    demonstrate_range_updates()
    demonstrate_sentinel()

    point_results = final_point_values(
        8,
        [
            (0, 3, 5),
            (2, 6, 10),
            (5, 7, -3),
        ],
        [0, 2, 5, 7],
    )
    print("\nFinal point values:", point_results)

    sums = range_add_then_range_sum(
        [1, 2, 3, 4, 5],
        [(1, 3, 10)],
        [(0, 2), (2, 4), (1, 3)],
    )
    print("Range sums after updates:", sums)

    demonstrate_interval_coverage()

    concurrency = maximum_concurrent_intervals(
        [
            TimeInterval(1, 5),
            TimeInterval(2, 7),
            TimeInterval(4, 6),
            TimeInterval(5, 8),
        ]
    )
    print("\nMaximum concurrent intervals:", concurrency)

    demonstrate_assignment_distinction()
    demonstrate_2d()
    explain_2d_corner_markers()
    demonstrate_coordinate_compression()
    demonstrate_derivative_view()
    demonstrate_second_difference()
    demonstrate_linear_updates()
    demonstrate_inverse_operations()
    demonstrate_range_conventions()
    demonstrate_flight_capacity()
    demonstrate_server_traffic()
    demonstrate_validation()
    demonstrate_edge_cases()
    print_common_mistakes()
    print_design_guidance()
    print_complexity_table()

    # Differential tests provide confidence that the optimized implementation
    # agrees with a deliberately simple O(nq) implementation.
    randomized_correctness_test()

    performance_demo()

    print("\nAll demonstrations completed successfully.")


if __name__ == "__main__":
    main()
