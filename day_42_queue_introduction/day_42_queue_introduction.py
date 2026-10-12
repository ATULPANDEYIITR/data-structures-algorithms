"""
Queue Introduction
==================
A self-contained progression from basic FIFO behavior to array-based and
linked-list queue implementations.

The examples use a service-desk ticket queue because FIFO behavior is natural:
the ticket that enters the queue first is the ticket processed first.

Run:
    python queue_introduction.py
"""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from typing import Generic, Iterable, Iterator, Optional, TypeVar


T = TypeVar("T")


def print_title(title: str) -> None:
    print(f"\n{'=' * 72}")
    print(title)
    print("=" * 72)


# ---------------------------------------------------------------------------
# FIFO fundamentals
# ---------------------------------------------------------------------------

def demonstrate_fifo() -> None:
    print_title("FIFO Behavior")

    queue: list[str] = []

    for ticket in ("INC-1001", "INC-1002", "INC-1003"):
        queue.append(ticket)

    print("Arrival order:", queue)

    first = queue.pop(0)
    print("Processed first:", first)
    print("Remaining:", queue)

    # FIFO means First In, First Out. The earliest inserted item leaves first.
    while queue:
        print("Processing:", queue.pop(0))

    # pop(0) is easy to understand, but it shifts all remaining list elements.
    # That makes repeated front removal O(n), which matters for large queues.


# ---------------------------------------------------------------------------
# Python's deque: practical production-oriented queue
# ---------------------------------------------------------------------------

def demonstrate_deque() -> None:
    print_title("Practical Queue with collections.deque")

    queue: deque[str] = deque()

    queue.append("INC-2001")
    queue.append("INC-2002")
    queue.append("INC-2003")

    print("Queue:", list(queue))
    print("Front:", queue[0])

    processed = queue.popleft()
    print("Dequeued:", processed)
    print("Queue after dequeue:", list(queue))

    queue.appendleft("URGENT-2000")
    print("After front insertion:", list(queue))

    print("Contains INC-2003:", "INC-2003" in queue)

    # append() and popleft() are designed for efficient queue behavior.
    # Both are O(1) at the deque ends.


# ---------------------------------------------------------------------------
# Array-based queue
# ---------------------------------------------------------------------------

class ArrayQueue(Generic[T]):
    """
    Queue implemented using a fixed-size circular array.

    A circular representation avoids shifting every element after dequeue.
    """

    def __init__(self, capacity: int = 8) -> None:
        if capacity <= 0:
            raise ValueError("Queue capacity must be positive")

        self._items: list[Optional[T]] = [None] * capacity
        self._capacity = capacity
        self._front = 0
        self._rear = 0
        self._size = 0

    def enqueue(self, item: T) -> None:
        if self.is_full():
            raise OverflowError("Queue is full")

        self._items[self._rear] = item
        self._rear = (self._rear + 1) % self._capacity
        self._size += 1

    def dequeue(self) -> T:
        if self.is_empty():
            raise IndexError("Cannot dequeue from an empty queue")

        item = self._items[self._front]
        self._items[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1

        assert item is not None
        return item

    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("Cannot peek at an empty queue")

        item = self._items[self._front]
        assert item is not None
        return item

    def is_empty(self) -> bool:
        return self._size == 0

    def is_full(self) -> bool:
        return self._size == self._capacity

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        for offset in range(self._size):
            index = (self._front + offset) % self._capacity
            item = self._items[index]
            assert item is not None
            yield item

    def __repr__(self) -> str:
        return f"ArrayQueue({list(self)!r})"


def demonstrate_array_queue() -> None:
    print_title("Array-Based Queue")

    queue = ArrayQueue[str](capacity=4)

    for ticket in ("PAY-101", "PAY-102", "PAY-103", "PAY-104"):
        queue.enqueue(ticket)

    print("Full queue:", queue)
    print("Front:", queue.peek())

    print("Dequeued:", queue.dequeue())
    print("Dequeued:", queue.dequeue())

    # The rear wraps around to unused positions at the beginning of the array.
    # No element shifting is required.
    queue.enqueue("PAY-105")
    queue.enqueue("PAY-106")

    print("After wrap-around:", queue)

    try:
        queue.enqueue("PAY-107")
        queue.enqueue("PAY-108")
        queue.enqueue("PAY-109")
    except OverflowError as exc:
        print("Expected capacity error:", exc)

    while not queue.is_empty():
        print("Processing:", queue.dequeue())

    try:
        queue.dequeue()
    except IndexError as exc:
        print("Expected empty-queue error:", exc)


# ---------------------------------------------------------------------------
# Linked-list queue
# ---------------------------------------------------------------------------

@dataclass
class QueueNode(Generic[T]):
    value: T
    next: Optional["QueueNode[T]"] = None


class LinkedQueue(Generic[T]):
    """
    Queue backed by linked nodes.

    Keeping both front and rear references makes enqueue and dequeue O(1).
    """

    def __init__(self) -> None:
        self._front: Optional[QueueNode[T]] = None
        self._rear: Optional[QueueNode[T]] = None
        self._size = 0

    def enqueue(self, item: T) -> None:
        node = QueueNode(item)

        if self._rear is None:
            # The queue was empty, so the new node becomes both endpoints.
            self._front = node
            self._rear = node
        else:
            self._rear.next = node
            self._rear = node

        self._size += 1

    def dequeue(self) -> T:
        if self._front is None:
            raise IndexError("Cannot dequeue from an empty queue")

        node = self._front
        self._front = node.next

        self._size -= 1

        if self._front is None:
            # Removing the last node must clear rear as well.
            self._rear = None

        return node.value

    def peek(self) -> T:
        if self._front is None:
            raise IndexError("Cannot peek at an empty queue")

        return self._front.value

    def is_empty(self) -> bool:
        return self._front is None

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        current = self._front

        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self) -> str:
        return f"LinkedQueue({list(self)!r})"


def demonstrate_linked_queue() -> None:
    print_title("Linked-List Queue")

    queue = LinkedQueue[str]()

    for ticket in ("NET-301", "NET-302", "NET-303"):
        queue.enqueue(ticket)

    print("Queue:", queue)
    print("Front:", queue.peek())

    print("Dequeued:", queue.dequeue())
    print("Queue:", queue)

    print("Dequeued:", queue.dequeue())
    print("Dequeued:", queue.dequeue())
    print("Queue empty:", queue.is_empty())

    try:
        queue.peek()
    except IndexError as exc:
        print("Expected empty-queue error:", exc)


# ---------------------------------------------------------------------------
# Queue behavior in a realistic service workflow
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SupportTicket:
    ticket_id: str
    customer: str
    issue: str


class SupportTicketQueue:
    """
    Domain-specific FIFO queue.

    The generic queue implementation is deliberately hidden behind a small
    service interface so application code does not depend on its internals.
    """

    def __init__(self) -> None:
        self._queue: deque[SupportTicket] = deque()
        self._known_ids: set[str] = set()

    def submit(self, ticket: SupportTicket) -> None:
        if not ticket.ticket_id.strip():
            raise ValueError("Ticket ID cannot be empty")

        if ticket.ticket_id in self._known_ids:
            raise ValueError(f"Duplicate ticket ID: {ticket.ticket_id}")

        if not ticket.issue.strip():
            raise ValueError("Ticket issue cannot be empty")

        self._queue.append(ticket)
        self._known_ids.add(ticket.ticket_id)

    def process_next(self) -> SupportTicket:
        if not self._queue:
            raise IndexError("No support tickets are waiting")

        ticket = self._queue.popleft()
        self._known_ids.remove(ticket.ticket_id)
        return ticket

    def pending_count(self) -> int:
        return len(self._queue)

    def peek_next(self) -> SupportTicket:
        if not self._queue:
            raise IndexError("No support tickets are waiting")
        return self._queue[0]


def demonstrate_service_queue() -> None:
    print_title("Realistic FIFO Service Queue")

    queue = SupportTicketQueue()

    queue.submit(SupportTicket("T-5001", "Asha", "Unable to access payroll"))
    queue.submit(SupportTicket("T-5002", "Rahul", "Report export fails"))
    queue.submit(SupportTicket("T-5003", "Meera", "Password reset required"))

    print("Next ticket:", queue.peek_next())
    print("Pending:", queue.pending_count())

    while queue.pending_count():
        ticket = queue.process_next()
        print(
            f"Serving {ticket.ticket_id}: "
            f"{ticket.customer} - {ticket.issue}"
        )

    try:
        queue.process_next()
    except IndexError as exc:
        print("Expected workflow error:", exc)


# ---------------------------------------------------------------------------
# Complexity comparison
# ---------------------------------------------------------------------------

def explain_complexity() -> None:
    print_title("Queue Implementation Complexity")

    print("list.append():                O(1) amortized")
    print("list.pop(0):                  O(n)")
    print("deque.append():               O(1)")
    print("deque.popleft():              O(1)")
    print("circular ArrayQueue enqueue:  O(1)")
    print("circular ArrayQueue dequeue:  O(1)")
    print("LinkedQueue enqueue:          O(1)")
    print("LinkedQueue dequeue:          O(1)")
    print("LinkedQueue peek:             O(1)")

    # The key implementation distinction is not FIFO itself. FIFO is the
    # behavior. The data structure determines how efficiently that behavior
    # is maintained.


# ---------------------------------------------------------------------------
# Validation and invariant testing
# ---------------------------------------------------------------------------

def verify_queue_invariants() -> None:
    print_title("Queue Invariant Checks")

    queue = ArrayQueue[int](3)

    assert queue.is_empty()
    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)

    assert queue.is_full()
    assert queue.peek() == 10
    assert queue.dequeue() == 10
    assert queue.dequeue() == 20

    queue.enqueue(40)

    # Circular storage should preserve logical FIFO order even though the
    # physical rear position has wrapped around.
    assert list(queue) == [30, 40]

    assert queue.dequeue() == 30
    assert queue.dequeue() == 40
    assert queue.is_empty()

    linked = LinkedQueue[int]()
    linked.enqueue(1)
    assert linked.dequeue() == 1
    assert linked.is_empty()

    # After removing the final linked node, rear must also be cleared.
    linked.enqueue(2)
    assert linked.peek() == 2
    assert linked.dequeue() == 2
    assert linked.is_empty()

    print("All queue invariants passed.")


# ---------------------------------------------------------------------------
# Interactive queue simulation
# ---------------------------------------------------------------------------

def run_interactive_simulation() -> None:
    print_title("Interactive Queue Simulation")

    queue: deque[str] = deque()

    print("Commands: enqueue <value>, dequeue, peek, show, quit")

    while True:
        try:
            command = input("queue> ").strip()
        except EOFError:
            print()
            break

        if not command:
            continue

        action, _, argument = command.partition(" ")

        if action == "enqueue":
            value = argument.strip()

            if not value:
                print("A queue value is required.")
                continue

            queue.append(value)
            print(f"Enqueued: {value}")

        elif action == "dequeue":
            if not queue:
                print("Queue is empty.")
            else:
                print(f"Dequeued: {queue.popleft()}")

        elif action == "peek":
            if not queue:
                print("Queue is empty.")
            else:
                print(f"Front: {queue[0]}")

        elif action == "show":
            print("Queue:", list(queue))

        elif action in {"quit", "exit"}:
            break

        else:
            print("Unknown command.")


def main() -> None:
    demonstrate_fifo()
    demonstrate_deque()
    demonstrate_array_queue()
    demonstrate_linked_queue()
    demonstrate_service_queue()
    explain_complexity()
    verify_queue_invariants()

    # The interactive part is opt-in so the script remains suitable for
    # automated execution and testing.
    print("\nInteractive simulation is available through run_interactive_simulation().")


if __name__ == "__main__":
    main()
