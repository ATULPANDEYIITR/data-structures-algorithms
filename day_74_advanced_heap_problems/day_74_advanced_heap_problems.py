#!/usr/bin/env python3
"""
Advanced Heap Problems
Topics:
1. Median from Data Stream
2. CPU Task Scheduling
3. Merge K Sorted Lists
4. Greedy Optimization: Maximum Capital
5. Greedy Optimization: Minimum Refueling Stops
6. Heap validation, edge cases, and performance testing

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import heapq
import itertools
import random
import statistics
import unittest

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Iterable


# ============================================================
# 1. MEDIAN FROM DATA STREAM
# ============================================================

class MedianFinder:
    """
    Two-heap median maintenance.

    lower: Max heap represented using negative values.
    upper: Min heap.

    Invariant:
        len(lower) == len(upper)
        OR len(lower) == len(upper) + 1

    Time:
        Insert: O(log n)
        Median: O(1)
    """

    def __init__(self) -> None:
        self.lower: list[int] = []
        self.upper: list[int] = []

    def add_number(self, number: int) -> None:
        if not isinstance(number, int) or isinstance(number, bool):
            raise TypeError("MedianFinder accepts integers only")

        heapq.heappush(self.lower, -number)

        # Move the largest lower-half value into the upper half.
        if self.upper and -self.lower[0] > self.upper[0]:
            value = -heapq.heappop(self.lower)
            heapq.heappush(self.upper, value)

        # Keep the lower heap equal in size or one element larger.
        if len(self.lower) > len(self.upper) + 1:
            heapq.heappush(
                self.upper,
                -heapq.heappop(self.lower)
            )
        elif len(self.upper) > len(self.lower):
            heapq.heappush(
                self.lower,
                -heapq.heappop(self.upper)
            )

    def find_median(self) -> float:
        if not self.lower:
            raise ValueError("Cannot calculate median of empty stream")

        if len(self.lower) > len(self.upper):
            return float(-self.lower[0])

        return (-self.lower[0] + self.upper[0]) / 2.0

    def __len__(self) -> int:
        return len(self.lower) + len(self.upper)


# ============================================================
# 2. CPU TASK SCHEDULING
# ============================================================

class TaskState(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"


@dataclass(order=True)
class Task:
    """
    Tasks are ordered by priority and submission sequence.

    Smaller priority values represent higher priority.
    """
    priority: int
    sequence: int
    task_id: str = field(compare=False)
    duration: int = field(compare=False)
    state: TaskState = field(
        default=TaskState.WAITING,
        compare=False
    )


class TaskScheduler:
    """
    Priority-based non-preemptive CPU scheduler.

    Time complexity:
        Submission: O(log n)
        Execution selection: O(log n)
    """

    def __init__(self) -> None:
        self.queue: list[Task] = []
        self.sequence = itertools.count()
        self.completed: list[Task] = []
        self.identifiers: set[str] = set()

    def submit(
        self,
        task_id: str,
        priority: int,
        duration: int
    ) -> None:

        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")

        if task_id in self.identifiers:
            raise ValueError("Duplicate task ID")

        if priority < 0:
            raise ValueError("Priority cannot be negative")

        if duration <= 0:
            raise ValueError("Duration must be positive")

        task = Task(
            priority=priority,
            sequence=next(self.sequence),
            task_id=task_id,
            duration=duration
        )

        heapq.heappush(self.queue, task)
        self.identifiers.add(task_id)

    def execute_next(self) -> Optional[Task]:
        if not self.queue:
            return None

        task = heapq.heappop(self.queue)
        task.state = TaskState.RUNNING

        # Simulate completion of a non-preemptive task.
        task.state = TaskState.COMPLETED
        self.completed.append(task)

        return task

    def execute_all(self) -> list[str]:
        execution_order = []

        while self.queue:
            task = self.execute_next()
            if task:
                execution_order.append(task.task_id)

        return execution_order

    def pending_tasks(self) -> list[str]:
        return [
            task.task_id
            for task in sorted(self.queue)
        ]


# ============================================================
# 3. MERGE K SORTED LISTS
# ============================================================

def merge_k_sorted_lists(
    lists: Iterable[Iterable[int]]
) -> list[int]:
    """
    Merge multiple sorted input sequences using a min heap.

    Only one current element from each sequence is stored.

    Time: O(N log K)
    Auxiliary space: O(K + N) including the output.
    """

    sequences = [list(sequence) for sequence in lists]

    for sequence in sequences:
        if any(
            sequence[i] > sequence[i + 1]
            for i in range(len(sequence) - 1)
        ):
            raise ValueError("Every input sequence must be sorted")

    heap = []

    for list_index, sequence in enumerate(sequences):
        if sequence:
            heapq.heappush(
                heap,
                (sequence[0], list_index, 0)
            )

    result = []

    while heap:
        value, list_index, element_index = heapq.heappop(heap)
        result.append(value)

        next_index = element_index + 1

        if next_index < len(sequences[list_index]):
            next_value = sequences[list_index][next_index]

            heapq.heappush(
                heap,
                (next_value, list_index, next_index)
            )

    return result


# ============================================================
# 4. GREEDY OPTIMIZATION: MAXIMUM CAPITAL
# ============================================================

@dataclass(frozen=True)
class Project:
    project_id: str
    required_capital: int
    profit: int


def maximize_capital(
    initial_capital: int,
    projects: Iterable[Project],
    max_projects: int
) -> tuple[int, list[str]]:
    """
    Select affordable projects with maximum available profit.

    Strategy:
        1. Sort projects by required capital.
        2. Insert affordable projects into a max heap.
        3. Select the most profitable project.
        4. Repeat until the project limit is reached.

    Time: O(N log N + K log N)
    """

    if initial_capital < 0:
        raise ValueError("Initial capital cannot be negative")

    if max_projects < 0:
        raise ValueError("Project limit cannot be negative")

    project_list = list(projects)

    if any(
        not p.project_id
        or p.required_capital < 0
        or p.profit < 0
        for p in project_list
    ):
        raise ValueError("Invalid project data")

    identifiers = [p.project_id for p in project_list]

    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Project IDs must be unique")

    project_list.sort(key=lambda p: p.required_capital)

    available: list[tuple[int, int, Project]] = []
    selected = []

    capital = initial_capital
    index = 0

    for _ in range(min(max_projects, len(project_list))):

        while (
            index < len(project_list)
            and project_list[index].required_capital <= capital
        ):
            project = project_list[index]

            heapq.heappush(
                available,
                (-project.profit, index, project)
            )

            index += 1

        if not available:
            break

        negative_profit, _, project = heapq.heappop(available)

        profit = -negative_profit

        # A zero-profit project cannot improve the objective.
        if profit == 0:
            break

        capital += profit
        selected.append(project.project_id)

    return capital, selected


# ============================================================
# 5. GREEDY OPTIMIZATION: MINIMUM REFUELING STOPS
# ============================================================

@dataclass(frozen=True)
class FuelStation:
    position: int
    fuel: int


def minimum_refueling_stops(
    target: int,
    initial_fuel: int,
    stations: Iterable[FuelStation]
) -> tuple[int, list[int]]:
    """
    Find the minimum number of refueling stops.

    At each point where fuel is insufficient, choose the previously
    passed station offering the largest fuel quantity.

    Time: O(N log N)
    """

    if target < 0 or initial_fuel < 0:
        raise ValueError("Target and fuel must be non-negative")

    station_list = sorted(
        stations,
        key=lambda station: station.position
    )

    if any(
        station.position < 0
        or station.position > target
        or station.fuel < 0
        for station in station_list
    ):
        raise ValueError("Invalid station")

    if any(
        station_list[i].position == station_list[i + 1].position
        for i in range(len(station_list) - 1)
    ):
        raise ValueError("Station positions must be unique")

    max_fuel_heap: list[tuple[int, int]] = []
    reachable = initial_fuel
    stops = []

    for index, station in enumerate(station_list):

        # Cannot reach this station with the available fuel.
        while reachable < station.position:

            if not max_fuel_heap:
                return -1, []

            negative_fuel, selected_index = heapq.heappop(
                max_fuel_heap
            )

            reachable += -negative_fuel
            stops.append(selected_index)

        heapq.heappush(
            max_fuel_heap,
            (-station.fuel, index)
        )

    while reachable < target:

        if not max_fuel_heap:
            return -1, []

        negative_fuel, selected_index = heapq.heappop(
            max_fuel_heap
        )

        reachable += -negative_fuel
        stops.append(selected_index)

    return len(stops), stops


# ============================================================
# 6. TASK DEADLINE SCHEDULING
# ============================================================

@dataclass(frozen=True)
class DeadlineTask:
    task_id: str
    deadline: int
    profit: int


def maximize_deadline_profit(
    tasks: Iterable[DeadlineTask]
) -> tuple[int, list[str]]:
    """
    Schedule unit-duration jobs before deadlines.

    Each deadline is a maximum number of available time slots.
    """

    task_list = list(tasks)

    if any(
        not task.task_id
        or task.deadline <= 0
        or task.profit < 0
        for task in task_list
    ):
        raise ValueError("Invalid deadline task")

    ids = [task.task_id for task in task_list]

    if len(ids) != len(set(ids)):
        raise ValueError("Task IDs must be unique")

    task_list.sort(key=lambda task: task.deadline)

    selected_heap = []
    total_profit = 0

    for task in task_list:
        heapq.heappush(
            selected_heap,
            (task.profit, task.task_id)
        )

        total_profit += task.profit

        if len(selected_heap) > task.deadline:
            removed_profit, _ = heapq.heappop(selected_heap)
            total_profit -= removed_profit

    selected_ids = [
        task_id
        for _, task_id in sorted(
            selected_heap,
            key=lambda item: item[1]
        )
    ]

    return total_profit, selected_ids


# ============================================================
# 7. AUTOMATED TESTS
# ============================================================

class HeapProblemTests(unittest.TestCase):

    def test_median_stream(self):
        finder = MedianFinder()

        for number in [5, 15, 1, 3]:
            finder.add_number(number)

        self.assertEqual(finder.find_median(), 4.0)

    def test_negative_median(self):
        finder = MedianFinder()

        finder.add_number(-5)
        finder.add_number(-1)

        self.assertEqual(finder.find_median(), -3.0)

    def test_empty_median(self):
        with self.assertRaises(ValueError):
            MedianFinder().find_median()

    def test_merge_k_lists(self):
        result = merge_k_sorted_lists([
            [1, 4, 7],
            [2, 5, 8],
            [3, 6, 9]
        ])

        self.assertEqual(result, list(range(1, 10)))

    def test_invalid_sorted_list(self):
        with self.assertRaises(ValueError):
            merge_k_sorted_lists([[3, 1]])

    def test_task_scheduler(self):
        scheduler = TaskScheduler()

        scheduler.submit("A", 3, 10)
        scheduler.submit("B", 1, 5)
        scheduler.submit("C", 2, 7)

        self.assertEqual(
            scheduler.execute_all(),
            ["B", "C", "A"]
        )

    def test_duplicate_task(self):
        scheduler = TaskScheduler()

        scheduler.submit("A", 1, 5)

        with self.assertRaises(ValueError):
            scheduler.submit("A", 2, 3)

    def test_maximum_capital(self):
        projects = [
            Project("P1", 0, 1),
            Project("P2", 1, 2),
            Project("P3", 1, 3),
            Project("P4", 5, 10)
        ]

        capital, selected = maximize_capital(
            0,
            projects,
            3
        )

        self.assertEqual(capital, 6)
        self.assertEqual(len(selected), 3)

    def test_minimum_refueling(self):
        stations = [
            FuelStation(10, 60),
            FuelStation(20, 30),
            FuelStation(30, 30),
            FuelStation(60, 40)
        ]

        stops, selected = minimum_refueling_stops(
            100,
            10,
            stations
        )

        self.assertEqual(stops, 2)
        self.assertEqual(len(selected), 2)

    def test_unreachable_target(self):
        stops, _ = minimum_refueling_stops(
            100,
            10,
            []
        )

        self.assertEqual(stops, -1)

    def test_deadline_profit(self):
        tasks = [
            DeadlineTask("A", 2, 100),
            DeadlineTask("B", 1, 19),
            DeadlineTask("C", 2, 27),
            DeadlineTask("D", 1, 25),
            DeadlineTask("E", 3, 15)
        ]

        profit, selected = maximize_deadline_profit(tasks)

        self.assertEqual(profit, 142)
        self.assertEqual(len(selected), 3)


# ============================================================
# 8. DEMONSTRATION
# ============================================================

def main() -> None:

    print("\nADVANCED HEAP PROBLEMS")
    print("=" * 55)

    print("\n1. Median from Data Stream")

    finder = MedianFinder()

    for number in [12, 4, 5, 3, 8, 7]:
        finder.add_number(number)
        print(
            f"Inserted {number:2d} | "
            f"Current median: {finder.find_median():.2f}"
        )

    print("\n2. Priority Task Scheduling")

    scheduler = TaskScheduler()

    scheduler.submit("Database Backup", 3, 20)
    scheduler.submit("Security Scan", 1, 10)
    scheduler.submit("Report Generation", 2, 15)

    print("Execution order:", scheduler.execute_all())

    print("\n3. Merge K Sorted Lists")

    merged = merge_k_sorted_lists([
        [1, 4, 7],
        [2, 5, 8],
        [3, 6, 9]
    ])

    print("Merged:", merged)

    print("\n4. Maximum Capital")

    projects = [
        Project("Infrastructure", 0, 2),
        Project("Analytics", 1, 5),
        Project("Security", 2, 8),
        Project("Cloud Migration", 5, 10)
    ]

    capital, selected = maximize_capital(
        1,
        projects,
        3
    )

    print("Selected projects:", selected)
    print("Final capital:", capital)

    print("\n5. Minimum Refueling Stops")

    stations = [
        FuelStation(10, 60),
        FuelStation(20, 30),
        FuelStation(30, 30),
        FuelStation(60, 40)
    ]

    stops, selected = minimum_refueling_stops(
        100,
        10,
        stations
    )

    print("Minimum stops:", stops)
    print("Selected station indices:", selected)

    print("\n6. Deadline Profit Optimization")

    deadline_tasks = [
        DeadlineTask("A", 2, 100),
        DeadlineTask("B", 1, 19),
        DeadlineTask("C", 2, 27),
        DeadlineTask("D", 1, 25),
        DeadlineTask("E", 3, 15)
    ]

    profit, jobs = maximize_deadline_profit(deadline_tasks)

    print("Selected jobs:", jobs)
    print("Maximum profit:", profit)

    print("\n7. Automated Validation")

    unittest.main(argv=["heap_problems.py"], exit=False)


if __name__ == "__main__":
    main()
