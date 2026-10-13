from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from typing import Iterable, Optional
import random


class QueueFullError(Exception):
    """Raised when an enqueue operation is attempted on a full circular queue."""


class QueueEmptyError(Exception):
    """Raised when an operation requires an element from an empty queue."""


class InvalidCapacityError(ValueError):
    """Raised when a circular queue receives an invalid capacity."""


class CircularQueue:
    """
    Fixed-capacity circular queue implemented with a Python list.

    The queue stores elements in a fixed array and uses two logical pointers:
    front identifies the oldest element, while rear identifies the position
    where the next element will be inserted.

    The implementation deliberately maintains an explicit size value. This
    removes the ambiguity between front == rear meaning "empty" and
    front == rear meaning "full".
    """

    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise InvalidCapacityError("Capacity must be an integer.")
        if capacity <= 0:
            raise InvalidCapacityError("Capacity must be greater than zero.")

        self._data: list[Optional[object]] = [None] * capacity
        self._capacity = capacity
        self._front = 0
        self._rear = 0
        self._size = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def front(self) -> int:
        return self._front

    @property
    def rear(self) -> int:
        return self._rear

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        return self._size == 0

    @property
    def is_full(self) -> bool:
        return self._size == self._capacity

    def _next_index(self, index: int) -> int:
        """Wrap an array index back to zero after the final slot."""
        return (index + 1) % self._capacity

    def enqueue(self, value: object) -> None:
        """
        Add an element at the rear.

        Overflow is detected before modifying the underlying array.
        """
        if self.is_full:
            raise QueueFullError(
                f"Cannot enqueue {value!r}: circular queue is full."
            )

        self._data[self._rear] = value
        self._rear = self._next_index(self._rear)
        self._size += 1

    def dequeue(self) -> object:
        """
        Remove and return the oldest element.

        The slot is cleared after removal so that stale object references are
        not retained unnecessarily.
        """
        if self.is_empty:
            raise QueueEmptyError("Cannot dequeue: circular queue is empty.")

        value = self._data[self._front]
        self._data[self._front] = None
        self._front = self._next_index(self._front)
        self._size -= 1

        return value

    def peek(self) -> object:
        """Return the oldest element without removing it."""
        if self.is_empty:
            raise QueueEmptyError("Cannot peek: circular queue is empty.")
        return self._data[self._front]

    def clear(self) -> None:
        """Reset the queue while retaining its allocated capacity."""
        self._data = [None] * self._capacity
        self._front = 0
        self._rear = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        """
        Iterate from logical front to logical rear.

        Physical array order is intentionally ignored because the queue can
        wrap around the end of the array.
        """
        index = self._front
        for _ in range(self._size):
            yield self._data[index]
            index = self._next_index(index)

    def to_list(self) -> list[object]:
        return list(self)

    def raw_storage(self) -> list[Optional[object]]:
        """Return a snapshot of physical storage for teaching/debugging."""
        return self._data.copy()

    def __repr__(self) -> str:
        return (
            f"CircularQueue(capacity={self._capacity}, "
            f"front={self._front}, rear={self._rear}, "
            f"size={self._size}, items={self.to_list()})"
        )


def demonstrate_basic_operations() -> None:
    print("\n=== Basic Circular Queue Operations ===")

    queue = CircularQueue(5)

    for value in ["A", "B", "C"]:
        queue.enqueue(value)

    print("After enqueue:", queue)
    print("Peek:", queue.peek())
    print("Dequeue:", queue.dequeue())
    print("After dequeue:", queue)

    queue.enqueue("D")
    queue.enqueue("E")
    queue.enqueue("F")

    print("After wrap-around enqueue:", queue)
    print("Logical order:", queue.to_list())
    print("Physical storage:", queue.raw_storage())
    print("Front index:", queue.front)
    print("Rear index:", queue.rear)


def demonstrate_wrap_around() -> None:
    print("\n=== Wrap-Around Behavior ===")

    queue = CircularQueue(4)

    for value in [10, 20, 30, 40]:
        queue.enqueue(value)

    print("Full queue:", queue)
    print("Physical storage:", queue.raw_storage())

    print("Removing:", queue.dequeue())
    print("Removing:", queue.dequeue())

    print("After two removals:", queue)
    print("Physical storage:", queue.raw_storage())

    queue.enqueue(50)
    queue.enqueue(60)

    print("After inserting 50 and 60:", queue)
    print("Physical storage:", queue.raw_storage())
    print("Logical order:", queue.to_list())

    assert queue.to_list() == [30, 40, 50, 60]
    assert queue.is_full


def demonstrate_overflow_and_underflow() -> None:
    print("\n=== Overflow and Underflow ===")

    queue = CircularQueue(2)

    queue.enqueue("first")
    queue.enqueue("second")

    try:
        queue.enqueue("third")
    except QueueFullError as exc:
        print("Overflow handled:", exc)

    print("Dequeued:", queue.dequeue())
    print("Dequeued:", queue.dequeue())

    try:
        queue.dequeue()
    except QueueEmptyError as exc:
        print("Underflow handled:", exc)

    try:
        queue.peek()
    except QueueEmptyError as exc:
        print("Empty peek handled:", exc)


def demonstrate_state_invariants() -> None:
    print("\n=== Queue Invariants ===")

    queue = CircularQueue(3)

    operations = [
        ("enqueue", "A"),
        ("enqueue", "B"),
        ("dequeue", None),
        ("enqueue", "C"),
        ("enqueue", "D"),
        ("dequeue", None),
        ("enqueue", "E"),
    ]

    for operation, value in operations:
        if operation == "enqueue":
            queue.enqueue(value)
            print(f"enqueue({value!r}) -> {queue}")
        else:
            removed = queue.dequeue()
            print(f"dequeue() -> {removed!r}; {queue}")

        assert 0 <= queue.size <= queue.capacity
        assert queue.is_empty == (queue.size == 0)
        assert queue.is_full == (queue.size == queue.capacity)

    print("Final logical order:", queue.to_list())


@dataclass
class PrintJob:
    job_id: int
    document: str
    pages: int

    def __repr__(self) -> str:
        return f"PrintJob(id={self.job_id}, document={self.document!r}, pages={self.pages})"


class PrinterSpool:
    """
    A realistic circular-buffer use case.

    Jobs are processed in FIFO order. Completed slots can immediately be
    reused, so the storage requirement depends on the configured queue
    capacity rather than on the total number of jobs ever processed.
    """

    def __init__(self, capacity: int) -> None:
        self.jobs = CircularQueue(capacity)
        self.completed_jobs = 0

    def submit(self, job: PrintJob) -> bool:
        try:
            self.jobs.enqueue(job)
            return True
        except QueueFullError:
            return False

    def process_next(self) -> Optional[PrintJob]:
        if self.jobs.is_empty:
            return None

        job = self.jobs.dequeue()
        self.completed_jobs += 1
        return job


def demonstrate_printer_spool() -> None:
    print("\n=== Printer Spool Case Study ===")

    spool = PrinterSpool(3)

    jobs = [
        PrintJob(101, "quarterly-report.pdf", 18),
        PrintJob(102, "network-diagram.pdf", 6),
        PrintJob(103, "invoice-batch.pdf", 32),
        PrintJob(104, "security-audit.pdf", 12),
    ]

    for job in jobs:
        accepted = spool.submit(job)
        status = "accepted" if accepted else "rejected: queue full"
        print(job, "->", status)

    while True:
        job = spool.process_next()
        if job is None:
            break
        print("Processing:", job)

    print("Completed jobs:", spool.completed_jobs)


class ResizableCircularQueue(CircularQueue):
    """
    A dynamically growing circular queue.

    The fixed queue provides predictable memory usage. This variant doubles
    its storage when full, while preserving logical FIFO ordering.
    """

    def enqueue(self, value: object) -> None:
        if self.is_full:
            self._resize(self._capacity * 2)
        super().enqueue(value)

    def _resize(self, new_capacity: int) -> None:
        if new_capacity <= self._capacity:
            raise ValueError("New capacity must exceed current capacity.")

        ordered = self.to_list()
        self._data = ordered + [None] * (new_capacity - len(ordered))
        self._capacity = new_capacity
        self._front = 0
        self._rear = self._size


def demonstrate_dynamic_capacity() -> None:
    print("\n=== Dynamic Circular Queue ===")

    queue = ResizableCircularQueue(3)

    for value in ["A", "B", "C", "D", "E", "F"]:
        queue.enqueue(value)
        print(f"enqueue({value!r}) -> capacity={queue.capacity}, items={queue.to_list()}")

    while not queue.is_empty:
        print("dequeue ->", queue.dequeue())


def compare_against_deque() -> None:
    print("\n=== Differential Check Against collections.deque ===")

    random.seed(42)

    circular = CircularQueue(8)
    reference = deque()

    for step in range(1000):
        if random.random() < 0.58:
            value = random.randint(-1000, 1000)

            if len(reference) < 8:
                circular.enqueue(value)
                reference.append(value)
            else:
                try:
                    circular.enqueue(value)
                except QueueFullError:
                    pass
                else:
                    raise AssertionError("Circular queue accepted an overflow.")

        elif reference:
            expected = reference.popleft()
            actual = circular.dequeue()
            assert actual == expected
        else:
            try:
                circular.dequeue()
            except QueueEmptyError:
                pass
            else:
                raise AssertionError("Circular queue dequeued from an empty state.")

        assert circular.to_list() == list(reference)
        assert circular.size == len(reference)

    print("1000 randomized operations matched the reference queue.")


def demonstrate_complexity() -> None:
    print("\n=== Complexity Characteristics ===")
    print("enqueue: O(1) for a fixed-capacity queue")
    print("dequeue: O(1)")
    print("peek:    O(1)")
    print("clear:   O(n) because allocated slots are reset")
    print("iteration/to_list: O(n)")
    print("fixed-capacity storage: O(n)")
    print("dynamic resize: O(n) only when capacity must grow")


def validate_capacity_inputs() -> None:
    print("\n=== Input Validation ===")

    invalid_values = [0, -1, 2.5, True, "5"]

    for value in invalid_values:
        try:
            CircularQueue(value)  # type: ignore[arg-type]
        except InvalidCapacityError as exc:
            print(f"capacity={value!r} rejected: {exc}")


def run_self_tests() -> None:
    print("\n=== Self-Test Suite ===")

    queue = CircularQueue(3)

    assert queue.is_empty
    assert not queue.is_full

    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)

    assert queue.is_full
    assert queue.to_list() == [1, 2, 3]

    try:
        queue.enqueue(4)
    except QueueFullError:
        pass
    else:
        raise AssertionError("Overflow test failed.")

    assert queue.dequeue() == 1
    assert queue.dequeue() == 2

    queue.enqueue(4)
    queue.enqueue(5)

    assert queue.to_list() == [3, 4, 5]
    assert queue.front == 2
    assert queue.rear == 2

    assert queue.dequeue() == 3
    assert queue.dequeue() == 4
    assert queue.dequeue() == 5
    assert queue.is_empty

    try:
        queue.dequeue()
    except QueueEmptyError:
        pass
    else:
        raise AssertionError("Underflow test failed.")

    queue.enqueue("reusable")
    queue.clear()

    assert queue.is_empty
    assert queue.size == 0
    assert queue.front == 0
    assert queue.rear == 0

    print("All self-tests passed.")


def main() -> None:
    print("CIRCULAR QUEUE: FIXED-BUFFER FIFO IMPLEMENTATION")

    demonstrate_basic_operations()
    demonstrate_wrap_around()
    demonstrate_overflow_and_underflow()
    demonstrate_state_invariants()
    demonstrate_printer_spool()
    demonstrate_dynamic_capacity()
    compare_against_deque()
    demonstrate_complexity()
    validate_capacity_inputs()
    run_self_tests()


if __name__ == "__main__":
    main()
