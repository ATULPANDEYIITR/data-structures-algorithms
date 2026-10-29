from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import heapq
import random
import sys
import time
from typing import Iterable, Sequence


class HeapType(Enum):
    MAX = "max"
    MIN = "min"


@dataclass(frozen=True)
class SortMetrics:
    comparisons: int
    swaps: int
    elapsed_ns: int


class HeapSorter:
    """In-place heap sort with optional instrumentation."""

    def __init__(self, heap_type: HeapType = HeapType.MAX) -> None:
        self.heap_type = heap_type
        self.comparisons = 0
        self.swaps = 0

    def _greater(self, a: int, b: int) -> bool:
        self.comparisons += 1
        return a > b

    def _less(self, a: int, b: int) -> bool:
        self.comparisons += 1
        return a < b

    def _swap(self, values: list[int], i: int, j: int) -> None:
        values[i], values[j] = values[j], values[i]
        self.swaps += 1

    def _sift_down_max(self, values: list[int], root: int, size: int) -> None:
        while True:
            left = 2 * root + 1
            right = left + 1
            largest = root

            if left < size and self._greater(values[left], values[largest]):
                largest = left

            if right < size and self._greater(values[right], values[largest]):
                largest = right

            if largest == root:
                return

            self._swap(values, root, largest)
            root = largest

    def _sift_down_min(self, values: list[int], root: int, size: int) -> None:
        while True:
            left = 2 * root + 1
            right = left + 1
            smallest = root

            if left < size and self._less(values[left], values[smallest]):
                smallest = left

            if right < size and self._less(values[right], values[smallest]):
                smallest = right

            if smallest == root:
                return

            self._swap(values, root, smallest)
            root = smallest

    def sort(self, values: list[int]) -> SortMetrics:
        if not isinstance(values, list):
            raise TypeError("HeapSorter.sort requires a list")
        if any(not isinstance(x, int) or isinstance(x, bool) for x in values):
            raise TypeError("All elements must be integers")

        self.comparisons = 0
        self.swaps = 0
        started = time.perf_counter_ns()

        n = len(values)

        if n < 2:
            return SortMetrics(
                self.comparisons,
                self.swaps,
                time.perf_counter_ns() - started,
            )

        # Bottom-up heap construction costs O(n), unlike repeated insertion.
        if self.heap_type is HeapType.MAX:
            for root in range(n // 2 - 1, -1, -1):
                self._sift_down_max(values, root, n)

            # Move the maximum to the sorted suffix one element at a time.
            for end in range(n - 1, 0, -1):
                self._swap(values, 0, end)
                self._sift_down_max(values, 0, end)
        else:
            for root in range(n // 2 - 1, -1, -1):
                self._sift_down_min(values, root, n)

            for end in range(n - 1, 0, -1):
                self._swap(values, 0, end)
                self._sift_down_min(values, 0, end)

            # A min-heap naturally produces descending order when extracting
            # the minimum into the right side, so reverse for ascending output.
            values.reverse()

        elapsed = time.perf_counter_ns() - started
        return SortMetrics(self.comparisons, self.swaps, elapsed)


def merge_sort(values: Sequence[int]) -> list[int]:
    """Reference implementation for comparison; O(n log n) auxiliary space."""
    if len(values) <= 1:
        return list(values)

    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    result: list[int] = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(values: list[int]) -> None:
    """In-place 3-way quicksort reference implementation."""
    def partition(lo: int, hi: int) -> tuple[int, int]:
        pivot = values[(lo + hi) // 2]
        lt, current, gt = lo, lo, hi

        while current <= gt:
            if values[current] < pivot:
                values[lt], values[current] = values[current], values[lt]
                lt += 1
                current += 1
            elif values[current] > pivot:
                values[current], values[gt] = values[gt], values[current]
                gt -= 1
            else:
                current += 1

        return lt, gt

    def sort(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        lt, gt = partition(lo, hi)
        sort(lo, lt - 1)
        sort(gt + 1, hi)

    if values:
        quick_sort_recursion_limit = max(1000, len(values) * 2)
        old_limit = sys.getrecursionlimit()
        try:
            sys.setrecursionlimit(max(old_limit, quick_sort_recursion_limit))
            sort(0, len(values) - 1)
        finally:
            sys.setrecursionlimit(old_limit)


def validate_input(values: Iterable[int]) -> list[int]:
    materialized = list(values)

    if len(materialized) > 1_000_000:
        raise ValueError("Input exceeds the configured 1,000,000-element limit")

    if any(not isinstance(x, int) or isinstance(x, bool) for x in materialized):
        raise TypeError("Input must contain integers only")

    return materialized


def compare_algorithms(values: Sequence[int]) -> None:
    heap_values = list(values)
    merge_values = list(values)
    quick_values = list(values)

    heap_sorter = HeapSorter()
    heap_metrics = heap_sorter.sort(heap_values)

    started = time.perf_counter_ns()
    merge_values = merge_sort(merge_values)
    merge_time = time.perf_counter_ns() - started

    started = time.perf_counter_ns()
    quick_sort(quick_values)
    quick_time = time.perf_counter_ns() - started

    expected = sorted(values)

    assert heap_values == expected
    assert merge_values == expected
    assert quick_values == expected

    print("\nAlgorithm comparison")
    print("-" * 72)
    print(f"{'Algorithm':<14}{'Time (µs)':>14}{'Extra space':>20}{'Worst case':>20}")
    print("-" * 72)
    print(
        f"{'Heap Sort':<14}"
        f"{heap_metrics.elapsed_ns / 1_000:>14.2f}"
        f"{'O(1)':>20}"
        f"{'O(n log n)':>20}"
    )
    print(
        f"{'Merge Sort':<14}"
        f"{merge_time / 1_000:>14.2f}"
        f"{'O(n)':>20}"
        f"{'O(n log n)':>20}"
    )
    print(
        f"{'Quick Sort':<14}"
        f"{quick_time / 1_000:>14.2f}"
        f"{'O(log n) avg':>20}"
        f"{'O(n log n)':>20}"
    )

    print(f"\nHeap comparisons: {heap_metrics.comparisons}")
    print(f"Heap swaps:       {heap_metrics.swaps}")


def demonstrate_priority_queue() -> None:
    """Show the heap structure behind Python's priority-queue implementation."""
    tasks = [
        (2, "database backup"),
        (5, "security alert"),
        (1, "routine report"),
        (4, "service restart"),
        (3, "metrics export"),
    ]

    queue: list[tuple[int, str]] = []
    for priority, task in tasks:
        heapq.heappush(queue, (-priority, task))

    print("\nPriority queue using heapq")
    while queue:
        priority, task = heapq.heappop(queue)
        print(f"priority={-priority}: {task}")


def run_tests() -> None:
    cases = [
        [],
        [1],
        [2, 1],
        [5, 5, 5, 5],
        [9, 1, 8, 2, 7, 3, 6, 4, 5],
        [-4, -1, -7, 3, 0, 3, -4],
        [2**31 - 1, -2**31, 0, 42],
    ]

    for case in cases:
        expected = sorted(case)
        result = list(case)
        HeapSorter().sort(result)
        assert result == expected, (case, result, expected)

    rng = random.Random(20261029)
    for _ in range(100):
        case = [rng.randint(-1000, 1000) for _ in range(rng.randint(0, 200))]
        result = list(case)
        HeapSorter().sort(result)
        assert result == sorted(case)

    descending = [5, 4, 3, 2, 1]
    HeapSorter(HeapType.MIN).sort(descending)
    assert descending == [1, 2, 3, 4, 5]

    try:
        HeapSorter().sort([1, "2"])  # type: ignore[list-item]
    except TypeError:
        pass
    else:
        raise AssertionError("Invalid input was not rejected")

    print("All heap-sort tests passed.")


def main() -> None:
    run_tests()

    sample = [12, 7, 3, 19, 4, 7, -2, 15, 0, 9]
    sorter = HeapSorter()
    metrics = sorter.sort(sample)

    print("\nSorted sample:")
    print(sample)
    print(f"Comparisons: {metrics.comparisons}")
    print(f"Swaps:       {metrics.swaps}")
    print(f"Time:        {metrics.elapsed_ns} ns")

    compare_algorithms(sample)
    demonstrate_priority_queue()


if __name__ == "__main__":
    main()
