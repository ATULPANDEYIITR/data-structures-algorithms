"""
Deque Engineering: Double-Ended Queues and Sliding Window Extrema

A self-contained Python learning program covering:
- Deque operations and their complexity.
- Circular-buffer implementation with fixed capacity.
- Monotonic increasing and decreasing deques.
- Sliding window maximum and minimum in O(n) time.
- Combined maximum/minimum processing.
- Input validation, edge cases, brute-force verification, and benchmarks.

Run with Python 3.10 or later:
    python deque_engineering.py
"""

from collections import deque
from dataclasses import dataclass
from random import Random
from time import perf_counter
from typing import Iterable, Sequence


def validate_integer_sequence(values: Iterable[int]) -> list[int]:
    """Materialize an iterable and reject booleans and non-integer values."""
    result = list(values)
    if any(not isinstance(value, int) or isinstance(value, bool)
           for value in result):
        raise TypeError("Every sequence element must be an integer.")
    return result


def validate_window_size(values: Sequence[int], k: int) -> None:
    """A window must contain at least one element and fit in the sequence."""
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("Window size must be an integer.")
    if not values:
        raise ValueError("The input sequence must not be empty.")
    if not 1 <= k <= len(values):
        raise ValueError("Window size must be between 1 and len(values).")


def demonstrate_standard_deque() -> None:
    print("\n=== Double-ended queue operations ===")

    items: deque[int] = deque([20, 30, 40])

    items.appendleft(10)
    items.append(50)
    print("After insertion at both ends:", list(items))

    left = items.popleft()
    right = items.pop()
    print("Removed from the front:", left)
    print("Removed from the back:", right)
    print("Remaining:", list(items))

    # Indexing near either end is efficient, but arbitrary middle access
    # takes linear time. A deque is not a replacement for every list.
    print("First element:", items[0])
    print("Last element:", items[-1])

    items.rotate(1)
    print("After rotating right:", list(items))

    bounded: deque[int] = deque(maxlen=3)
    for value in (1, 2, 3, 4):
        bounded.append(value)
    print("Bounded deque after automatic eviction:", list(bounded))

    # maxlen is convenient for retention, but silent eviction makes it
    # inappropriate when every item must be preserved.


@dataclass
class CircularDeque:
    """Fixed-capacity circular buffer with explicit overflow behavior."""

    capacity: int

    def __post_init__(self) -> None:
        if (not isinstance(self.capacity, int)
                or isinstance(self.capacity, bool)
                or self.capacity <= 0):
            raise ValueError("Capacity must be a positive integer.")
        self._buffer: list[int | None] = [None] * self.capacity
        self._head = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def _check_not_full(self) -> None:
        if self._size == self.capacity:
            raise OverflowError("Circular deque is full.")

    def appendleft(self, value: int) -> None:
        self._check_not_full()
        self._head = (self._head - 1) % self.capacity
        self._buffer[self._head] = value
        self._size += 1

    def append(self, value: int) -> None:
        self._check_not_full()
        tail = (self._head + self._size) % self.capacity
        self._buffer[tail] = value
        self._size += 1

    def popleft(self) -> int:
        if not self:
            raise IndexError("Cannot remove from an empty deque.")
        value = self._buffer[self._head]
        self._buffer[self._head] = None
        self._head = (self._head + 1) % self.capacity
        self._size -= 1
        assert value is not None
        return value

    def pop(self) -> int:
        if not self:
            raise IndexError("Cannot remove from an empty deque.")
        tail = (self._head + self._size - 1) % self.capacity
        value = self._buffer[tail]
        self._buffer[tail] = None
        self._size -= 1
        assert value is not None
        return value

    def to_list(self) -> list[int]:
        return [
            self._buffer[(self._head + offset) % self.capacity]
            for offset in range(self._size)
        ]  # type: ignore[misc]


def demonstrate_circular_deque() -> None:
    print("\n=== Circular-buffer implementation ===")

    items = CircularDeque(4)
    items.append(10)
    items.append(20)
    items.appendleft(5)
    items.append(30)
    print("Full buffer:", items.to_list())

    print("Removed from front:", items.popleft())
    items.append(40)  # Reuses a slot freed at the front.
    print("After wraparound:", items.to_list())

    try:
        items.append(50)
    except OverflowError as error:
        print("Expected overflow:", error)

    print("Removed from back:", items.pop())
    print("Final contents:", items.to_list())


def sliding_window_maximum(values: Iterable[int], k: int) -> list[int]:
    """
    Return the maximum of each contiguous window in O(n) time.

    Store indices rather than values so that expired elements can be
    identified precisely. Candidate values decrease from front to back.
    """
    numbers = validate_integer_sequence(values)
    validate_window_size(numbers, k)

    candidates: deque[int] = deque()
    result: list[int] = []

    for index, value in enumerate(numbers):
        # Remove indices that no longer belong to the current window.
        while candidates and candidates[0] <= index - k:
            candidates.popleft()

        # A new value makes every smaller or equal candidate behind it
        # permanently irrelevant to future maximum queries.
        while (candidates
               and numbers[candidates[-1]] <= value):
            candidates.pop()

        candidates.append(index)

        if index >= k - 1:
            result.append(numbers[candidates[0]])

    return result


def sliding_window_minimum(values: Iterable[int], k: int) -> list[int]:
    """
    Return the minimum of each contiguous window in O(n) time.

    The deque maintains increasing candidate values.
    """
    numbers = validate_integer_sequence(values)
    validate_window_size(numbers, k)

    candidates: deque[int] = deque()
    result: list[int] = []

    for index, value in enumerate(numbers):
        while candidates and candidates[0] <= index - k:
            candidates.popleft()

        # Larger or equal trailing candidates cannot become the minimum
        # while the newer, smaller candidate remains inside the window.
        while (candidates
               and numbers[candidates[-1]] >= value):
            candidates.pop()

        candidates.append(index)

        if index >= k - 1:
            result.append(numbers[candidates[0]])

    return result


def sliding_window_extrema(
    values: Iterable[int], k: int
) -> list[tuple[int, int]]:
    """Return (minimum, maximum) for each window in a single traversal."""
    numbers = validate_integer_sequence(values)
    validate_window_size(numbers, k)

    minimum_candidates: deque[int] = deque()
    maximum_candidates: deque[int] = deque()
    result: list[tuple[int, int]] = []

    for index, value in enumerate(numbers):
        expired_index = index - k

        while (minimum_candidates
               and minimum_candidates[0] <= expired_index):
            minimum_candidates.popleft()

        while (maximum_candidates
               and maximum_candidates[0] <= expired_index):
            maximum_candidates.popleft()

        while (minimum_candidates
               and numbers[minimum_candidates[-1]] >= value):
            minimum_candidates.pop()

        while (maximum_candidates
               and numbers[maximum_candidates[-1]] <= value):
            maximum_candidates.pop()

        minimum_candidates.append(index)
        maximum_candidates.append(index)

        if index >= k - 1:
            result.append((
                numbers[minimum_candidates[0]],
                numbers[maximum_candidates[0]],
            ))

    return result


def brute_force_maximum(values: Sequence[int], k: int) -> list[int]:
    """Reference implementation with O(n*k) time for verification."""
    validate_window_size(values, k)
    return [
        max(values[start:start + k])
        for start in range(len(values) - k + 1)
    ]


def brute_force_minimum(values: Sequence[int], k: int) -> list[int]:
    validate_window_size(values, k)
    return [
        min(values[start:start + k])
        for start in range(len(values) - k + 1)
    ]


def demonstrate_monotonic_deques() -> None:
    print("\n=== Monotonic deque trace ===")

    values = [4, 2, 12, 3, 8, 7, 9]
    k = 3
    candidates: deque[int] = deque()

    print("Index | Value | Candidate indices | Candidate values")
    for index, value in enumerate(values):
        while candidates and candidates[0] <= index - k:
            candidates.popleft()

        while candidates and values[candidates[-1]] <= value:
            candidates.pop()

        candidates.append(index)

        candidate_values = [values[i] for i in candidates]
        print(
            f"{index:5} | {value:5} | "
            f"{list(candidates)!s:18} | {candidate_values}"
        )

        if index >= k - 1:
            print("      Window maximum:", values[candidates[0]])


def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases ===")

    cases = [
        ([7], 1),
        ([3, 3, 3, 3], 2),
        ([-8, -2, -10, -4], 2),
        ([9, 1, 8, 2, 7, 3], 6),
        ([1, 5, 2, 6, 3, 7], 1),
    ]

    for values, k in cases:
        print(f"values={values}, k={k}")
        print("  maximum:", sliding_window_maximum(values, k))
        print("  minimum:", sliding_window_minimum(values, k))
        print("  extrema:", sliding_window_extrema(values, k))

    invalid_cases = [
        ([], 1),
        ([1, 2], 0),
        ([1, 2], 3),
        ([1, 2], True),
        ([1, 2.5], 1),
    ]

    for values, k in invalid_cases:
        try:
            sliding_window_maximum(values, k)
        except (TypeError, ValueError) as error:
            print(f"Rejected values={values}, k={k}: {error}")


def run_property_tests() -> None:
    """Compare optimized algorithms against brute force on deterministic data."""
    print("\n=== Automated correctness checks ===")

    generator = Random(20261014)
    tested_sequences = 0
    tested_windows = 0

    fixed_cases = [
        [1],
        [5, 4, 3, 2, 1],
        [1, 2, 3, 4, 5],
        [4, 4, 4, 4, 4],
        [-3, -7, -1, -9, -2],
        [0, -1, 0, -1, 0],
    ]

    for length in range(1, 35):
        generated = [
            generator.randint(-100, 100)
            for _ in range(length)
        ]
        fixed_cases.append(generated)

    for values in fixed_cases:
        tested_sequences += 1
        for k in range(1, len(values) + 1):
            actual_max = sliding_window_maximum(values, k)
            actual_min = sliding_window_minimum(values, k)
            actual_extrema = sliding_window_extrema(values, k)

            assert actual_max == brute_force_maximum(values, k)
            assert actual_min == brute_force_minimum(values, k)
            assert actual_extrema == list(zip(actual_min, actual_max))
            tested_windows += 1

    print(f"Sequences verified: {tested_sequences}")
    print(f"Window configurations verified: {tested_windows}")
    print("All comparisons passed.")


def benchmark() -> None:
    """Compare asymptotic behavior without relying on precise timing values."""
    print("\n=== Performance comparison ===")

    generator = Random(91)
    values = [generator.randint(-1_000_000, 1_000_000)
              for _ in range(50_000)]
    k = 500

    start = perf_counter()
    optimized = sliding_window_maximum(values, k)
    optimized_seconds = perf_counter() - start

    smaller_values = values[:2_000]
    smaller_k = min(k, 40)

    start = perf_counter()
    reference = brute_force_maximum(smaller_values, smaller_k)
    reference_seconds = perf_counter() - start

    assert optimized == sliding_window_maximum(values, k)
    assert reference == sliding_window_maximum(smaller_values, smaller_k)

    print(f"Optimized: n={len(values)}, k={k}, "
          f"windows={len(optimized)}, time={optimized_seconds:.6f}s")
    print(f"Reference: n={len(smaller_values)}, k={smaller_k}, "
          f"time={reference_seconds:.6f}s")
    print("The reference uses a smaller input to limit benchmark runtime.")


def main() -> None:
    demonstrate_standard_deque()
    demonstrate_circular_deque()
    demonstrate_monotonic_deques()

    values = [1, 3, -1, -3, 5, 3, 6, 7]
    k = 3

    print("\n=== Sliding-window analysis ===")
    print("Input:", values)
    print("Window size:", k)
    print("Maximum:", sliding_window_maximum(values, k))
    print("Minimum:", sliding_window_minimum(values, k))
    print("Minimum and maximum:", sliding_window_extrema(values, k))

    demonstrate_edge_cases()
    run_property_tests()
    benchmark()


if __name__ == "__main__":
    main()
