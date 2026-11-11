#!/usr/bin/env python3
"""
Heap Operations and Priority Queue
Python 3.10+

Implements:
- Min-heap and max-heap
- Insertion and deletion
- Heapify and bottom-up construction
- Extract-min and extract-max
- Peek and priority queue operations
- Heap sorting
- Validation and invariant checking
- Complexity demonstrations
- Automated tests and edge cases
"""

from __future__ import annotations

import heapq
import random
import unittest
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Iterable, TypeVar

T = TypeVar("T")


class HeapType(Enum):
    MIN = "min"
    MAX = "max"


class HeapError(Exception):
    """Base exception for heap operations."""


class EmptyHeapError(HeapError):
    """Raised when removing an item from an empty heap."""


class InvalidHeapError(HeapError):
    """Raised when heap input is invalid."""


@dataclass
class BinaryHeap(Generic[T]):
    heap_type: HeapType = HeapType.MIN
    data: list[T] = field(default_factory=list)

    def __post_init__(self):
        self.data = list(self.data)
        self.heapify()

    def _higher_priority(self, a: T, b: T) -> bool:
        return a < b if self.heap_type == HeapType.MIN else a > b

    def _validate_value(self, value: T) -> None:
        try:
            _ = value < value
            _ = value > value
        except TypeError as exc:
            raise InvalidHeapError(
                "Heap elements must support consistent comparisons."
            ) from exc

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2

            if not self._higher_priority(
                self.data[index], self.data[parent]
            ):
                break

            self.data[index], self.data[parent] = (
                self.data[parent],
                self.data[index],
            )
            index = parent

    def _sift_down(self, index: int, size: int | None = None) -> None:
        if size is None:
            size = len(self.data)

        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            best = index

            if (
                left < size
                and self._higher_priority(
                    self.data[left], self.data[best]
                )
            ):
                best = left

            if (
                right < size
                and self._higher_priority(
                    self.data[right], self.data[best]
                )
            ):
                best = right

            if best == index:
                break

            self.data[index], self.data[best] = (
                self.data[best],
                self.data[index],
            )
            index = best

    def heapify(self) -> None:
        """Build a heap in O(n) time."""
        for index in range(len(self.data) // 2 - 1, -1, -1):
            self._sift_down(index)

    def insert(self, value: T) -> None:
        self._validate_value(value)
        self.data.append(value)
        self._sift_up(len(self.data) - 1)

    def peek(self) -> T:
        if not self.data:
            raise EmptyHeapError("Cannot peek into an empty heap.")
        return self.data[0]

    def extract(self) -> T:
        if not self.data:
            raise EmptyHeapError("Cannot extract from an empty heap.")

        root = self.data[0]
        last = self.data.pop()

        if self.data:
            self.data[0] = last
            self._sift_down(0)

        return root

    def delete_at(self, index: int) -> T:
        if not 0 <= index < len(self.data):
            raise IndexError("Heap index is out of range.")

        removed = self.data[index]
        last = self.data.pop()

        if index < len(self.data):
            self.data[index] = last

            if (
                index > 0
                and self._higher_priority(
                    self.data[index],
                    self.data[(index - 1) // 2],
                )
            ):
                self._sift_up(index)
            else:
                self._sift_down(index)

        return removed

    def delete_value(self, value: T) -> bool:
        """Delete the first matching value. O(n) search plus O(log n) repair."""
        try:
            index = self.data.index(value)
        except ValueError:
            return False

        self.delete_at(index)
        return True

    def update(self, index: int, value: T) -> None:
        """Replace an item and restore the heap invariant."""
        if not 0 <= index < len(self.data):
            raise IndexError("Heap index is out of range.")

        self._validate_value(value)
        old_value = self.data[index]
        self.data[index] = value

        if self._higher_priority(value, old_value):
            self._sift_up(index)
        else:
            self._sift_down(index)

    def is_valid(self) -> bool:
        for child in range(1, len(self.data)):
            parent = (child - 1) // 2

            if self._higher_priority(
                self.data[child], self.data[parent]
            ):
                return False

        return True

    def sorted_values(self) -> list[T]:
        """Return priority order without modifying the original heap."""
        clone = BinaryHeap(self.heap_type, self.data.copy())
        return [clone.extract() for _ in range(len(clone))]

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        return f"BinaryHeap({self.heap_type.value}, {self.data})"


@dataclass(frozen=True)
class Task:
    task_id: str
    description: str
    priority: int

    def __post_init__(self):
        if not self.task_id.strip():
            raise ValueError("Task ID cannot be empty.")
        if not self.description.strip():
            raise ValueError("Task description cannot be empty.")
        if not isinstance(self.priority, int):
            raise TypeError("Priority must be an integer.")


class TaskPriorityQueue:
    """
    Higher numerical priority is processed first.
    Sequence numbers provide deterministic FIFO ordering for ties.
    """

    def __init__(self):
        self._heap: list[tuple[int, int, Task]] = []
        self._sequence = 0
        self._active_ids: set[str] = set()

    def enqueue(self, task: Task) -> None:
        if task.task_id in self._active_ids:
            raise ValueError(f"Duplicate active task: {task.task_id}")

        heapq.heappush(
            self._heap,
            (-task.priority, self._sequence, task),
        )
        self._sequence += 1
        self._active_ids.add(task.task_id)

    def dequeue(self) -> Task:
        if not self._heap:
            raise EmptyHeapError("Task queue is empty.")

        _, _, task = heapq.heappop(self._heap)
        self._active_ids.remove(task.task_id)
        return task

    def peek(self) -> Task:
        if not self._heap:
            raise EmptyHeapError("Task queue is empty.")
        return self._heap[0][2]

    def __len__(self) -> int:
        return len(self._heap)


def heap_sort(values: Iterable[int], reverse: bool = False) -> list[int]:
    """Heap-based sorting with O(n log n) time."""
    heap = BinaryHeap(
        HeapType.MAX if reverse else HeapType.MIN,
        list(values),
    )
    return [heap.extract() for _ in range(len(heap))]


def demonstrate_heap_operations() -> None:
    print("\nMIN HEAP OPERATIONS")

    min_heap = BinaryHeap(HeapType.MIN)

    for value in [40, 10, 30, 5, 20, 50]:
        min_heap.insert(value)

    print("Heap:", min_heap.data)
    print("Minimum:", min_heap.peek())
    print("Extracted:", min_heap.extract())

    min_heap.delete_value(30)
    print("After deleting 30:", min_heap.data)

    min_heap.insert(2)
    print("After inserting 2:", min_heap.data)
    print("Valid heap:", min_heap.is_valid())

    print("\nMAX HEAP OPERATIONS")

    max_heap = BinaryHeap(
        HeapType.MAX,
        [40, 10, 30, 5, 20, 50],
    )

    print("Heap:", max_heap.data)
    print("Maximum:", max_heap.peek())
    print("Extracted:", max_heap.extract())
    print("Descending order:", max_heap.sorted_values())

    print("\nHEAP SORT")
    values = [12, 4, 19, 1, 8, 15, 3]
    print("Input:", values)
    print("Ascending:", heap_sort(values))
    print("Descending:", heap_sort(values, reverse=True))

    print("\nPRIORITY QUEUE")

    queue = TaskPriorityQueue()

    queue.enqueue(Task("T101", "Database backup", 3))
    queue.enqueue(Task("T102", "Security incident", 10))
    queue.enqueue(Task("T103", "System monitoring", 5))
    queue.enqueue(Task("T104", "Critical outage", 10))

    print("Next task:", queue.peek())

    while queue:
        print("Processing:", queue.dequeue())


class HeapTests(unittest.TestCase):

    def test_min_heap(self):
        heap = BinaryHeap(HeapType.MIN, [9, 4, 7, 1, 3])
        self.assertTrue(heap.is_valid())
        self.assertEqual(heap.extract(), 1)
        self.assertEqual(heap.extract(), 3)

    def test_max_heap(self):
        heap = BinaryHeap(HeapType.MAX, [9, 4, 7, 1, 3])
        self.assertEqual(heap.extract(), 9)
        self.assertTrue(heap.is_valid())

    def test_insert_and_delete(self):
        heap = BinaryHeap(HeapType.MIN)
        heap.insert(10)
        heap.insert(5)
        heap.insert(20)

        self.assertTrue(heap.delete_value(10))
        self.assertFalse(heap.delete_value(100))
        self.assertTrue(heap.is_valid())
        self.assertEqual(heap.extract(), 5)

    def test_update(self):
        heap = BinaryHeap(HeapType.MIN, [5, 10, 15])
        heap.update(2, 1)
        self.assertEqual(heap.peek(), 1)

    def test_heapify(self):
        values = [15, 3, 20, 8, 1, 12]
        heap = BinaryHeap(HeapType.MIN, values)
        self.assertEqual(heap.sorted_values(), sorted(values))

    def test_empty_heap(self):
        heap = BinaryHeap()

        with self.assertRaises(EmptyHeapError):
            heap.extract()

        with self.assertRaises(EmptyHeapError):
            heap.peek()

    def test_invalid_index(self):
        heap = BinaryHeap(HeapType.MIN, [1, 2])

        with self.assertRaises(IndexError):
            heap.delete_at(10)

    def test_priority_queue(self):
        queue = TaskPriorityQueue()
        queue.enqueue(Task("A", "Normal", 1))
        queue.enqueue(Task("B", "Critical", 10))
        self.assertEqual(queue.dequeue().task_id, "B")

    def test_duplicate_task(self):
        queue = TaskPriorityQueue()
        task = Task("A", "Task", 1)
        queue.enqueue(task)

        with self.assertRaises(ValueError):
            queue.enqueue(task)


def randomized_validation() -> None:
    """Compare heap extraction with Python's sorting behavior."""
    random.seed(42)

    for _ in range(100):
        values = [random.randint(-1000, 1000) for _ in range(100)]

        heap = BinaryHeap(HeapType.MIN, values)
        assert heap.sorted_values() == sorted(values)
        assert heap.is_valid()

        max_heap = BinaryHeap(HeapType.MAX, values)
        assert max_heap.sorted_values() == sorted(
            values, reverse=True
        )
        assert max_heap.is_valid()

    print("100 randomized heap tests passed.")


if __name__ == "__main__":
    demonstrate_heap_operations()
    randomized_validation()

    unittest.main(argv=["heap_operations.py"], exit=False)
