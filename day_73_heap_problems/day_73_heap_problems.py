#!/usr/bin/env python3
"""
Heap Problems: Kth Largest/Smallest, Top-K, K-Way Merge,
Running Median, and Streaming Kth Largest.

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import heapq
import random
import unittest
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Sequence, TypeVar

T = TypeVar("T")


class HeapError(Exception):
    """Base exception for heap operations."""


class EmptyHeapError(HeapError):
    """Raised when an operation requires a nonempty heap."""


class InvalidInputError(HeapError):
    """Raised when input violates operation constraints."""


class BinaryHeap:
    """Generic binary heap with configurable ordering."""

    def __init__(self, values: Iterable[T] = (), *, reverse: bool = False):
        self._data = list(values)
        self._reverse = reverse
        self._heapify()

    def _before(self, a: T, b: T) -> bool:
        return a > b if self._reverse else a < b

    def _heapify(self) -> None:
        for index in range(len(self._data) // 2 - 1, -1, -1):
            self._sift_down(index)

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if not self._before(self._data[index], self._data[parent]):
                break
            self._data[index], self._data[parent] = (
                self._data[parent], self._data[index]
            )
            index = parent

    def _sift_down(self, index: int) -> None:
        size = len(self._data)

        while True:
            left = 2 * index + 1
            right = left + 1
            best = index

            if left < size and self._before(
                self._data[left], self._data[best]
            ):
                best = left

            if right < size and self._before(
                self._data[right], self._data[best]
            ):
                best = right

            if best == index:
                break

            self._data[index], self._data[best] = (
                self._data[best], self._data[index]
            )
            index = best

    def push(self, value: T) -> None:
        self._data.append(value)
        self._sift_up(len(self._data) - 1)

    def peek(self) -> T:
        if not self._data:
            raise EmptyHeapError("Cannot inspect an empty heap.")
        return self._data[0]

    def pop(self) -> T:
        if not self._data:
            raise EmptyHeapError("Cannot remove from an empty heap.")

        root = self._data[0]
        last = self._data.pop()

        if self._data:
            self._data[0] = last
            self._sift_down(0)

        return root

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def __repr__(self) -> str:
        return f"BinaryHeap({self._data!r}, reverse={self._reverse})"


def _validate_k(values: Sequence[T], k: int) -> None:
    if not isinstance(k, int) or isinstance(k, bool):
        raise InvalidInputError("k must be an integer.")

    if not 1 <= k <= len(values):
        raise InvalidInputError(
            f"k must be between 1 and {len(values)}."
        )


def kth_largest(values: Sequence[int], k: int) -> int:
    """Find kth largest element using a min-heap of size k."""

    _validate_k(values, k)

    heap = list(values[:k])
    heapq.heapify(heap)

    for value in values[k:]:
        if value > heap[0]:
            heapq.heapreplace(heap, value)

    return heap[0]


def kth_smallest(values: Sequence[int], k: int) -> int:
    """Find kth smallest element using a max-heap of size k."""

    _validate_k(values, k)

    heap = [-value for value in values[:k]]
    heapq.heapify(heap)

    for value in values[k:]:
        if value < -heap[0]:
            heapq.heapreplace(heap, -value)

    return -heap[0]


def top_k_largest(values: Iterable[int], k: int) -> list[int]:
    """Return k largest values in descending order."""

    if not isinstance(k, int) or isinstance(k, bool) or k < 0:
        raise InvalidInputError("k must be a nonnegative integer.")

    if k == 0:
        return []

    heap: list[int] = []

    for value in values:
        if len(heap) < k:
            heapq.heappush(heap, value)
        elif value > heap[0]:
            heapq.heapreplace(heap, value)

    return sorted(heap, reverse=True)


def top_k_frequent(values: Iterable[T], k: int) -> list[tuple[T, int]]:
    """Return frequent values using frequency aggregation and a heap."""

    if not isinstance(k, int) or isinstance(k, bool) or k < 0:
        raise InvalidInputError("k must be a nonnegative integer.")

    counts = Counter(values)

    if k == 0:
        return []

    # Counter elements must be hashable. Sorting by frequency and value
    # representation provides deterministic ordering for arbitrary types.
    return sorted(
        counts.items(),
        key=lambda item: (-item[1], repr(item[0]))
    )[:k]


def merge_sorted_arrays(
    arrays: Sequence[Sequence[int]]
) -> list[int]:
    """Merge sorted arrays using a k-way min-heap."""

    heap: list[tuple[int, int, int]] = []

    for array_index, array in enumerate(arrays):
        if any(array[i] > array[i + 1] for i in range(len(array) - 1)):
            raise InvalidInputError(
                f"Input array {array_index} is not sorted."
            )

        if array:
            heapq.heappush(
                heap, (array[0], array_index, 0)
            )

    result: list[int] = []

    while heap:
        value, array_index, element_index = heapq.heappop(heap)
        result.append(value)

        next_index = element_index + 1
        if next_index < len(arrays[array_index]):
            heapq.heappush(
                heap,
                (
                    arrays[array_index][next_index],
                    array_index,
                    next_index
                )
            )

    return result


def merge_sorted_iterators(
    iterators: Iterable[Iterator[int]]
) -> Iterator[int]:
    """Memory-efficient merge of sorted iterators."""

    heap: list[tuple[int, int, Iterator[int]]] = []

    for index, iterator in enumerate(iterators):
        iterator = iter(iterator)
        try:
            value = next(iterator)
            heapq.heappush(heap, (value, index, iterator))
        except StopIteration:
            continue

    while heap:
        value, index, iterator = heapq.heappop(heap)
        yield value

        try:
            next_value = next(iterator)
            heapq.heappush(
                heap, (next_value, index, iterator)
            )
        except StopIteration:
            pass


class RunningMedian:
    """
    Maintains a median using two heaps.

    lower: max-heap containing the smaller half.
    upper: min-heap containing the larger half.
    """

    def __init__(self):
        self._lower: list[int] = []
        self._upper: list[int] = []

    def add(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidInputError("RunningMedian accepts integers.")

        if not self._lower or value <= -self._lower[0]:
            heapq.heappush(self._lower, -value)
        else:
            heapq.heappush(self._upper, value)

        # Keep the lower heap equal in size or one element larger.
        if len(self._lower) > len(self._upper) + 1:
            heapq.heappush(
                self._upper, -heapq.heappop(self._lower)
            )
        elif len(self._upper) > len(self._lower):
            heapq.heappush(
                self._lower, -heapq.heappop(self._upper)
            )

    def median(self) -> float:
        if not self._lower:
            raise EmptyHeapError("No values have been processed.")

        if len(self._lower) > len(self._upper):
            return float(-self._lower[0])

        return (-self._lower[0] + self._upper[0]) / 2.0

    def __len__(self) -> int:
        return len(self._lower) + len(self._upper)


class KthLargestStream:
    """Maintains kth largest element in a continuously updated stream."""

    def __init__(self, k: int, initial: Iterable[int] = ()):
        if not isinstance(k, int) or isinstance(k, bool) or k < 1:
            raise InvalidInputError("k must be a positive integer.")

        self.k = k
        self._heap: list[int] = []

        for value in initial:
            self.add(value)

    def add(self, value: int) -> Optional[int]:
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidInputError("Stream values must be integers.")

        if len(self._heap) < self.k:
            heapq.heappush(self._heap, value)
        elif value > self._heap[0]:
            heapq.heapreplace(self._heap, value)

        return self._heap[0] if len(self._heap) == self.k else None


@dataclass(frozen=True)
class HeapEvent:
    sequence: int
    value: int
    median: float
    kth_largest: Optional[int]


class StreamProcessor:
    """Processes an integer stream and records derived statistics."""

    def __init__(self, k: int):
        self.median_tracker = RunningMedian()
        self.kth_tracker = KthLargestStream(k)
        self.events: list[HeapEvent] = []
        self._sequence = 0

    def process(self, value: int) -> HeapEvent:
        self.median_tracker.add(value)
        kth = self.kth_tracker.add(value)

        self._sequence += 1

        event = HeapEvent(
            sequence=self._sequence,
            value=value,
            median=self.median_tracker.median(),
            kth_largest=kth
        )

        self.events.append(event)
        return event

    def process_many(self, values: Iterable[int]) -> list[HeapEvent]:
        return [self.process(value) for value in values]


def demo() -> None:
    values = [12, 3, 5, 7, 19, 4, 8, 15]

    print("Kth largest:", kth_largest(values, 3))
    print("Kth smallest:", kth_smallest(values, 3))
    print("Top 4:", top_k_largest(values, 4))

    print(
        "Top frequent:",
        top_k_frequent([1, 1, 2, 2, 2, 3, 4, 4], 3)
    )

    arrays = [
        [1, 4, 7, 10],
        [2, 5, 8],
        [3, 6, 9, 11]
    ]

    print("Merged arrays:", merge_sorted_arrays(arrays))

    median = RunningMedian()
    for value in [5, 15, 1, 3]:
        median.add(value)
        print(f"Added {value}, median={median.median()}")

    processor = StreamProcessor(k=3)

    for event in processor.process_many(
        [10, 20, 5, 30, 15, 40]
    ):
        print(event)


class HeapTests(unittest.TestCase):

    def test_binary_min_heap(self):
        heap = BinaryHeap([8, 3, 5, 1])
        self.assertEqual(
            [heap.pop() for _ in range(4)],
            [1, 3, 5, 8]
        )

    def test_binary_max_heap(self):
        heap = BinaryHeap([8, 3, 5, 1], reverse=True)
        self.assertEqual(
            [heap.pop() for _ in range(4)],
            [8, 5, 3, 1]
        )

    def test_kth_elements(self):
        values = [3, 2, 1, 5, 6, 4]
        self.assertEqual(kth_largest(values, 2), 5)
        self.assertEqual(kth_smallest(values, 2), 2)

    def test_duplicates(self):
        self.assertEqual(kth_largest([5, 5, 4, 4], 2), 5)

    def test_top_k(self):
        self.assertEqual(top_k_largest([4, 1, 7, 3], 2), [7, 4])

    def test_top_frequent(self):
        self.assertEqual(
            top_k_frequent([1, 1, 2, 2, 2, 3], 2),
            [(2, 3), (1, 2)]
        )

    def test_merge(self):
        self.assertEqual(
            merge_sorted_arrays([[1, 4], [2, 5], [3, 6]]),
            [1, 2, 3, 4, 5, 6]
        )

    def test_merge_empty(self):
        self.assertEqual(merge_sorted_arrays([[], []]), [])

    def test_merge_invalid(self):
        with self.assertRaises(InvalidInputError):
            merge_sorted_arrays([[3, 1]])

    def test_running_median(self):
        tracker = RunningMedian()
        for value in [5, 15, 1, 3]:
            tracker.add(value)

        self.assertEqual(tracker.median(), 4.0)

    def test_kth_stream(self):
        tracker = KthLargestStream(3, [4, 5, 8, 2])
        self.assertEqual(tracker.add(3), 4)
        self.assertEqual(tracker.add(10), 5)

    def test_empty_heap(self):
        with self.assertRaises(EmptyHeapError):
            BinaryHeap().pop()

    def test_invalid_k(self):
        with self.assertRaises(InvalidInputError):
            kth_largest([1, 2], 3)

    def test_randomized_kth(self):
        random.seed(42)

        for _ in range(100):
            values = [
                random.randint(-100, 100)
                for _ in range(random.randint(1, 50))
            ]

            k = random.randint(1, len(values))

            self.assertEqual(
                kth_largest(values, k),
                sorted(values, reverse=True)[k - 1]
            )

            self.assertEqual(
                kth_smallest(values, k),
                sorted(values)[k - 1]
            )


if __name__ == "__main__":
    demo()
    print("\nRunning unit tests...")
    unittest.main(argv=["heap_problems.py"], exit=False)
