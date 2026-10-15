#!/usr/bin/env python3
"""
Priority queues, heap-backed scheduling, and priority-based processing.

Run with:
    python priority_queue.py

Uses only the Python standard library. Demonstrates heap ordering,
stable scheduling, task reprioritization, lazy deletion, bounded queues,
event simulation, top-k selection, and tests.
"""

from __future__ import annotations

import heapq
import itertools
import random
import unittest
from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, TypeVar


T = TypeVar("T")


def demonstrate_heap_fundamentals() -> None:
    print("\n=== Heap fundamentals ===")

    # heapq implements a min-heap: the smallest key is removed first.
    priorities = [8, 3, 10, 1, 6, 2]
    heapq.heapify(priorities)
    print("Heap representation:", priorities)

    ordered = [heapq.heappop(priorities) for _ in range(len(priorities))]
    print("Ascending removal order:", ordered)

    # Negated priorities provide max-heap behavior on older Python versions.
    scores = [42, 91, 67, 91, 35]
    max_heap = [-score for score in scores]
    heapq.heapify(max_heap)
    print("Descending score order:",
          [-heapq.heappop(max_heap) for _ in range(len(max_heap))])

    # Tuples compare lexicographically, so a unique sequence number prevents
    # Python from comparing arbitrary task objects when priorities tie.
    entries = []
    sequence = itertools.count()
    heapq.heappush(entries, (2, next(sequence), {"job": "compile"}))
    heapq.heappush(entries, (1, next(sequence), {"job": "test"}))
    heapq.heappush(entries, (2, next(sequence), {"job": "deploy"}))

    while entries:
        priority, _, task = heapq.heappop(entries)
        print(f"priority={priority}, task={task['job']}")


@dataclass(frozen=True)
class Task:
    task_id: str
    description: str
    priority: int
    estimated_seconds: int
    created_at: int

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("Task ID cannot be empty")
        if not self.description.strip():
            raise ValueError("Task description cannot be empty")
        if not 0 <= self.priority <= 100:
            raise ValueError("Priority must be between 0 and 100")
        if self.estimated_seconds < 0:
            raise ValueError("Estimated duration cannot be negative")


class PriorityTaskQueue:
    """
    Stable, updateable task queue.

    Higher numeric priority executes first. Equal priorities use insertion
    order. A versioned entry and lazy deletion avoid mutating heap entries
    in place, which would invalidate heap ordering.
    """

    def __init__(self, max_size: int | None = None) -> None:
        if max_size is not None and max_size < 1:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._heap: list[tuple[int, int, int, str, Task]] = []
        self._entries: dict[str, tuple[int, Task]] = {}
        self._sequence = itertools.count()

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, task_id: str) -> bool:
        return task_id in self._entries

    def submit(self, task: Task) -> None:
        if task.task_id in self._entries:
            raise ValueError(f"Duplicate task ID: {task.task_id}")
        if self.max_size is not None and len(self) >= self.max_size:
            raise OverflowError("Priority queue capacity reached")
        self._insert(task)

    def _insert(self, task: Task) -> None:
        version = next(self._sequence)
        self._entries[task.task_id] = (version, task)
        # Negation changes a min-heap into a max-priority scheduler.
        heapq.heappush(
            self._heap,
            (-task.priority, version, version, task.task_id, task),
        )

    def reprioritize(self, task_id: str, new_priority: int) -> None:
        if not 0 <= new_priority <= 100:
            raise ValueError("Priority must be between 0 and 100")
        current = self._entries.get(task_id)
        if current is None:
            raise KeyError(f"Unknown task: {task_id}")

        old_task = current[1]
        updated = Task(
            task_id=old_task.task_id,
            description=old_task.description,
            priority=new_priority,
            estimated_seconds=old_task.estimated_seconds,
            created_at=old_task.created_at,
        )
        # Replacing the dictionary entry makes its former heap entry stale.
        self._insert(updated)

    def cancel(self, task_id: str) -> Task:
        try:
            _, task = self._entries.pop(task_id)
        except KeyError as exc:
            raise KeyError(f"Unknown task: {task_id}") from exc
        return task

    def peek(self) -> Task:
        self._discard_stale_entries()
        if not self._heap:
            raise IndexError("Peek from an empty priority queue")
        return self._heap[0][4]

    def pop(self) -> Task:
        while self._heap:
            _, version, _, task_id, task = heapq.heappop(self._heap)
            current = self._entries.get(task_id)
            if current is not None and current[0] == version:
                del self._entries[task_id]
                return task
        raise IndexError("Pop from an empty priority queue")

    def _discard_stale_entries(self) -> None:
        while self._heap:
            _, version, _, task_id, _ = self._heap[0]
            current = self._entries.get(task_id)
            if current is not None and current[0] == version:
                break
            heapq.heappop(self._heap)

    def compact(self) -> None:
        """Rebuild the heap when repeated updates leave many stale entries."""
        self._heap = [
            (-task.priority, version, version, task_id, task)
            for task_id, (version, task) in self._entries.items()
        ]
        heapq.heapify(self._heap)

    def snapshot(self) -> list[Task]:
        """Return tasks in execution order without changing the live queue."""
        return sorted(
            (task for _, task in self._entries.values()),
            key=lambda task: (-task.priority, task.created_at, task.task_id),
        )


def demonstrate_task_scheduling() -> None:
    print("\n=== Task scheduling ===")
    queue = PriorityTaskQueue(max_size=8)

    tasks = [
        Task("JOB-101", "Run security scan", 90, 45, 1),
        Task("JOB-102", "Generate weekly report", 30, 60, 2),
        Task("JOB-103", "Restore failed service", 100, 15, 3),
        Task("JOB-104", "Run integration tests", 70, 35, 4),
        Task("JOB-105", "Refresh dashboard cache", 30, 10, 5),
    ]

    for task in tasks:
        queue.submit(task)

    queue.reprioritize("JOB-102", 85)
    queue.cancel("JOB-104")

    print("Scheduled execution order:")
    for task in queue.snapshot():
        print(
            f"{task.task_id}: priority={task.priority}, "
            f"duration={task.estimated_seconds}s, {task.description}"
        )

    print("Next task:", queue.peek().task_id)

    print("Processing tasks:")
    while queue:
        print("Executing", queue.pop().task_id)


@dataclass(order=True)
class ScheduledEvent:
    event_time: int
    sequence: int
    event_type: str = field(compare=False)
    payload: dict[str, str] = field(default_factory=dict, compare=False)


def simulate_event_loop() -> None:
    print("\n=== Time-based event simulation ===")
    events: list[ScheduledEvent] = []
    sequence = itertools.count()

    def schedule(time: int, event_type: str, **payload: str) -> None:
        if time < 0:
            raise ValueError("Event time cannot be negative")
        heapq.heappush(
            events,
            ScheduledEvent(time, next(sequence), event_type, payload),
        )

    schedule(12, "deployment_finished", service="payments")
    schedule(4, "health_check", service="payments")
    schedule(4, "health_check", service="orders")
    schedule(8, "retry", service="payments")

    current_time = 0
    while events:
        event = heapq.heappop(events)
        current_time = event.event_time
        print(
            f"t={current_time:02d}: {event.event_type} "
            f"{event.payload}"
        )

        # Event handlers can schedule follow-up work without sorting the
        # entire event collection after every insertion.
        if event.event_type == "retry":
            schedule(current_time + 3, "retry_timeout",
                     service=event.payload["service"])


def demonstrate_top_k_and_merging() -> None:
    print("\n=== Top-k selection and merging ===")
    measurements = [17, 92, 38, 92, 11, 76, 54, 99, 23]
    print("Three largest measurements:", heapq.nlargest(3, measurements))

    sorted_partitions = [
        [2, 8, 15, 27],
        [1, 9, 16, 31],
        [3, 7, 18, 24],
    ]
    merged = list(heapq.merge(*sorted_partitions))
    print("Merged sorted partitions:", merged)


def demonstrate_priority_fairness() -> None:
    print("\n=== Priority and fairness ===")

    jobs = [
        {"name": "interactive-request", "priority": 80},
        {"name": "interactive-request-2", "priority": 80},
        {"name": "background-index", "priority": 10},
    ]
    queue: list[tuple[int, int, dict[str, object]]] = []
    for position, job in enumerate(jobs):
        heapq.heappush(queue, (-int(job["priority"]), position, job))

    while queue:
        _, _, job = heapq.heappop(queue)
        print(job["name"], "priority", job["priority"])

    # A heap alone cannot prevent starvation. One policy is aging:
    # effective_priority = min(max_priority, base_priority + wait // interval).
    # Aging must be incorporated into selection or periodically reheapified;
    # changing priorities silently while entries remain in a heap is unsafe.


class PriorityQueueTests(unittest.TestCase):
    def test_highest_priority_first(self) -> None:
        queue = PriorityTaskQueue()
        queue.submit(Task("A", "low", 10, 1, 1))
        queue.submit(Task("B", "high", 90, 1, 2))
        self.assertEqual(queue.pop().task_id, "B")
        self.assertEqual(queue.pop().task_id, "A")

    def test_stable_ties(self) -> None:
        queue = PriorityTaskQueue()
        queue.submit(Task("A", "first", 50, 1, 1))
        queue.submit(Task("B", "second", 50, 1, 2))
        self.assertEqual([queue.pop().task_id, queue.pop().task_id], ["A", "B"])

    def test_reprioritization(self) -> None:
        queue = PriorityTaskQueue()
        queue.submit(Task("A", "first", 20, 1, 1))
        queue.submit(Task("B", "second", 70, 1, 2))
        queue.reprioritize("A", 95)
        self.assertEqual(queue.pop().task_id, "A")
        self.assertEqual(queue.pop().task_id, "B")

    def test_cancellation_and_stale_entries(self) -> None:
        queue = PriorityTaskQueue()
        queue.submit(Task("A", "cancelled", 99, 1, 1))
        queue.cancel("A")
        queue.submit(Task("B", "active", 10, 1, 2))
        self.assertEqual(queue.pop().task_id, "B")
        with self.assertRaises(IndexError):
            queue.pop()

    def test_capacity_and_duplicate_ids(self) -> None:
        queue = PriorityTaskQueue(max_size=1)
        task = Task("A", "first", 50, 1, 1)
        queue.submit(task)
        with self.assertRaises(OverflowError):
            queue.submit(Task("B", "second", 40, 1, 2))
        with self.assertRaises(ValueError):
            queue.submit(task)

    def test_invalid_priority(self) -> None:
        with self.assertRaises(ValueError):
            Task("A", "invalid", 101, 1, 1)

    def test_compaction_preserves_live_tasks(self) -> None:
        queue = PriorityTaskQueue()
        queue.submit(Task("A", "first", 10, 1, 1))
        queue.submit(Task("B", "second", 20, 1, 2))
        queue.reprioritize("A", 30)
        queue.compact()
        self.assertEqual(queue.pop().task_id, "A")
        self.assertEqual(queue.pop().task_id, "B")


def run_tests() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        PriorityQueueTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


def main() -> None:
    random.seed(7)
    demonstrate_heap_fundamentals()
    demonstrate_task_scheduling()
    simulate_event_loop()
    demonstrate_top_k_and_merging()
    demonstrate_priority_fairness()
    print("\n=== Automated tests ===")
    run_tests()


if __name__ == "__main__":
    main()
