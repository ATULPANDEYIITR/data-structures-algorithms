"""
HEAP INTRODUCTION
Complete Binary Trees, Min-Heaps, Max-Heaps, Heap Representation,
Heap Properties, Heap Operations, and Priority Queue Applications.

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import heapq
import json
import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Generic, Iterable, TypeVar

T = TypeVar("T")


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("heap_engine")


class HeapType(Enum):
    MIN = "min"
    MAX = "max"


@dataclass
class HeapStatistics:
    insertions: int = 0
    removals: int = 0
    comparisons: int = 0
    swaps: int = 0


class BinaryHeap(Generic[T]):
    """
    Array-based binary heap.

    For index i:
        Parent       = (i - 1) // 2
        Left child   = 2 * i + 1
        Right child  = 2 * i + 2

    Min-heap:
        Parent <= children

    Max-heap:
        Parent >= children
    """

    def __init__(
        self,
        heap_type: HeapType = HeapType.MIN,
        values: Iterable[T] | None = None
    ):
        self.heap_type = heap_type
        self.data: list[T] = list(values or [])
        self.stats = HeapStatistics()

        if self.data:
            self._heapify()

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __iter__(self):
        return iter(self.data)

    def _higher_priority(self, first: T, second: T) -> bool:
        self.stats.comparisons += 1

        if self.heap_type == HeapType.MIN:
            return first < second

        return first > second

    def parent(self, index: int) -> int:
        if index <= 0 or index >= len(self.data):
            raise IndexError("Invalid child index")
        return (index - 1) // 2

    def left_child(self, index: int) -> int | None:
        child = 2 * index + 1
        return child if child < len(self.data) else None

    def right_child(self, index: int) -> int | None:
        child = 2 * index + 2
        return child if child < len(self.data) else None

    def _swap(self, first: int, second: int) -> None:
        self.data[first], self.data[second] = (
            self.data[second],
            self.data[first]
        )
        self.stats.swaps += 1

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent_index = (index - 1) // 2

            if not self._higher_priority(
                self.data[index],
                self.data[parent_index]
            ):
                break

            self._swap(index, parent_index)
            index = parent_index

    def _sift_down(self, index: int) -> None:
        size = len(self.data)

        while True:
            highest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if (
                left < size
                and self._higher_priority(
                    self.data[left],
                    self.data[highest]
                )
            ):
                highest = left

            if (
                right < size
                and self._higher_priority(
                    self.data[right],
                    self.data[highest]
                )
            ):
                highest = right

            if highest == index:
                break

            self._swap(index, highest)
            index = highest

    def _heapify(self) -> None:
        """Build a heap in O(n) using bottom-up heap construction."""
        for index in range(len(self.data) // 2 - 1, -1, -1):
            self._sift_down(index)

    def peek(self) -> T:
        if not self.data:
            raise IndexError("Cannot peek at an empty heap")
        return self.data[0]

    def push(self, value: T) -> None:
        self.data.append(value)
        self.stats.insertions += 1
        self._sift_up(len(self.data) - 1)

    def pop(self) -> T:
        if not self.data:
            raise IndexError("Cannot remove from an empty heap")

        if len(self.data) == 1:
            self.stats.removals += 1
            return self.data.pop()

        result = self.data[0]
        self.data[0] = self.data.pop()
        self.stats.removals += 1
        self._sift_down(0)

        return result

    def replace_root(self, value: T) -> T:
        if not self.data:
            raise IndexError("Cannot replace root of an empty heap")

        previous = self.data[0]
        self.data[0] = value
        self._sift_down(0)
        return previous

    def validate(self) -> bool:
        """Check the heap-order property."""
        for index in range(1, len(self.data)):
            parent_index = (index - 1) // 2

            if self._higher_priority(
                self.data[index],
                self.data[parent_index]
            ):
                return False

        return True

    def tree_levels(self) -> list[list[T]]:
        """Return the array representation grouped by tree levels."""
        levels = []
        start = 0
        width = 1

        while start < len(self.data):
            levels.append(self.data[start:start + width])
            start += width
            width *= 2

        return levels

    def display(self) -> None:
        print(f"\n{self.heap_type.value.upper()}-HEAP")
        print("Array:", self.data)

        for level_number, level in enumerate(self.tree_levels()):
            print(f"Level {level_number}: {level}")

    def statistics(self) -> dict[str, int]:
        return {
            "size": len(self.data),
            "insertions": self.stats.insertions,
            "removals": self.stats.removals,
            "comparisons": self.stats.comparisons,
            "swaps": self.stats.swaps
        }


@dataclass(order=True)
class Task:
    priority: int
    sequence: int
    name: str = field(compare=False)
    status: str = field(default="pending", compare=False)


class TaskScheduler:
    """
    Lower numeric priority represents greater urgency.
    Sequence numbers provide stable ordering for equal priorities.
    """

    def __init__(self):
        self.queue: list[Task] = []
        self.sequence = 0
        self.completed: list[Task] = []

    def schedule(self, name: str, priority: int) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Task name cannot be empty")

        if isinstance(priority, bool) or not isinstance(priority, int):
            raise TypeError("Priority must be an integer")

        if not 1 <= priority <= 10:
            raise ValueError("Priority must be between 1 and 10")

        task = Task(
            priority=priority,
            sequence=self.sequence,
            name=name.strip()
        )

        self.sequence += 1
        heapq.heappush(self.queue, task)

    def execute_next(self) -> Task:
        if not self.queue:
            raise IndexError("No pending tasks")

        task = heapq.heappop(self.queue)
        task.status = "completed"
        self.completed.append(task)
        return task

    def pending_tasks(self) -> list[Task]:
        return sorted(self.queue)

    def cancel(self, task_name: str) -> bool:
        for index, task in enumerate(self.queue):
            if task.name == task_name:
                self.queue.pop(index)
                heapq.heapify(self.queue)
                return True

        return False


def heap_sort(values: Iterable[int]) -> list[int]:
    """Heap-based ascending sorting."""
    heap = BinaryHeap(HeapType.MIN, values)
    return [heap.pop() for _ in range(len(heap))]


def demonstrate_complete_binary_tree() -> None:
    print("\nCOMPLETE BINARY TREE")

    values = [10, 20, 30, 40, 50, 60, 70]

    for index, value in enumerate(values):
        parent = None if index == 0 else values[(index - 1) // 2]
        left = values[2 * index + 1] if 2 * index + 1 < len(values) else None
        right = values[2 * index + 2] if 2 * index + 2 < len(values) else None

        print({
            "node": value,
            "parent": parent,
            "left": left,
            "right": right
        })


def demonstrate_heap_operations() -> None:
    values = [40, 10, 30, 50, 20, 60, 70]

    min_heap = BinaryHeap(HeapType.MIN, values)
    max_heap = BinaryHeap(HeapType.MAX, values)

    min_heap.display()
    max_heap.display()

    print("\nMIN-HEAP ROOT:", min_heap.peek())
    print("MAX-HEAP ROOT:", max_heap.peek())

    min_heap.push(5)
    print("\nAfter inserting 5:")
    min_heap.display()

    print("\nRemoved minimum:", min_heap.pop())
    min_heap.display()

    print("\nMin-heap valid:", min_heap.validate())
    print("Max-heap valid:", max_heap.validate())

    print("\nMin-heap statistics:", min_heap.statistics())


def demonstrate_priority_queue() -> None:
    scheduler = TaskScheduler()

    scheduler.schedule("Database backup", 4)
    scheduler.schedule("Security incident", 1)
    scheduler.schedule("Generate report", 7)
    scheduler.schedule("Production outage", 1)
    scheduler.schedule("Update documentation", 9)

    print("\nPENDING TASKS")

    for task in scheduler.pending_tasks():
        print(task)

    print("\nEXECUTION ORDER")

    while scheduler.queue:
        task = scheduler.execute_next()
        print(
            f"Executing: {task.name}, "
            f"priority={task.priority}, "
            f"sequence={task.sequence}"
        )


def demonstrate_edge_cases() -> None:
    print("\nEDGE CASES")

    empty_heap = BinaryHeap()

    try:
        empty_heap.pop()
    except IndexError as error:
        print("Expected empty-heap error:", error)

    single = BinaryHeap(HeapType.MIN, [42])
    print("Single element:", single.pop())

    duplicates = BinaryHeap(HeapType.MIN, [5, 5, 5, 2, 2])
    print("Duplicate values:", [duplicates.pop() for _ in range(len(duplicates))])

    negative = BinaryHeap(HeapType.MAX, [-10, -5, -20])
    print("Maximum among negative values:", negative.pop())

    try:
        TaskScheduler().schedule("Invalid priority", 15)
    except ValueError as error:
        print("Expected validation error:", error)


def demonstrate_heap_sort() -> None:
    values = [12, 4, 19, 1, 8, 3, 15]

    print("\nHEAP SORT")
    print("Original:", values)
    print("Sorted:", heap_sort(values))


def save_results(filename: str = "heap_results.json") -> None:
    values = [45, 12, 78, 3, 24, 56, 9]

    heap = BinaryHeap(HeapType.MIN, values)

    result = {
        "heap_type": heap.heap_type.value,
        "heap_array": heap.data,
        "sorted_values": heap_sort(values),
        "valid": heap.validate(),
        "statistics": heap.statistics()
    }

    # Restrict the output to a local filename rather than an arbitrary path.
    safe_name = Path(filename).name

    if safe_name != filename or safe_name in {"", ".", ".."}:
        raise ValueError("Only a local filename is permitted")

    Path(safe_name).write_text(
        json.dumps(result, indent=4),
        encoding="utf-8"
    )

    print(f"\nResults saved to {safe_name}")


def run_tests() -> None:
    min_heap = BinaryHeap(HeapType.MIN, [9, 4, 7, 1, 3])
    assert min_heap.peek() == 1
    assert min_heap.validate()

    min_heap.push(0)
    assert min_heap.pop() == 0

    max_heap = BinaryHeap(HeapType.MAX, [9, 4, 7, 1, 3])
    assert max_heap.peek() == 9
    assert max_heap.validate()

    assert heap_sort([5, 1, 4, 2, 3]) == [1, 2, 3, 4, 5]
    assert heap_sort([]) == []

    print("\nAll assertions passed.")


def main() -> None:
    print("=" * 60)
    print("HEAP INTRODUCTION AND IMPLEMENTATION")
    print("=" * 60)

    demonstrate_complete_binary_tree()
    demonstrate_heap_operations()
    demonstrate_priority_queue()
    demonstrate_edge_cases()
    demonstrate_heap_sort()
    run_tests()
    save_results()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TypeError) as error:
        logger.exception("Application failed: %s", error)
        raise
