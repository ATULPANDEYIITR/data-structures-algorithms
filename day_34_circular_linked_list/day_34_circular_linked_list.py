from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Optional, TypeVar


T = TypeVar("T")


# ============================================================
# Circular Singly Linked List
# ============================================================

@dataclass
class SinglyNode(Generic[T]):
    value: T
    next: Optional["SinglyNode[T]"] = None


class CircularSinglyLinkedList(Generic[T]):
    """
    A circular singly linked list stores a tail pointer.

    The tail points to the final node, while tail.next points
    back to the first node. There is deliberately no None
    pointer at the end of the list.

    Keeping the tail pointer makes insertion at the front and
    back O(1), while searching and arbitrary-position operations
    remain O(n).
    """

    def __init__(self, values: Iterable[T] = ()) -> None:
        self.tail: Optional[SinglyNode[T]] = None
        self._size = 0

        for value in values:
            self.append(value)

    @property
    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.tail is None

    def head(self) -> Optional[SinglyNode[T]]:
        return None if self.tail is None else self.tail.next

    def append(self, value: T) -> None:
        """Insert after the current tail, making the new node the tail."""
        new_node = SinglyNode(value)

        if self.tail is None:
            new_node.next = new_node
            self.tail = new_node
        else:
            new_node.next = self.tail.next
            self.tail.next = new_node
            self.tail = new_node

        self._size += 1

    def prepend(self, value: T) -> None:
        """Insert immediately before the current head."""
        new_node = SinglyNode(value)

        if self.tail is None:
            new_node.next = new_node
            self.tail = new_node
        else:
            new_node.next = self.tail.next
            self.tail.next = new_node

        self._size += 1

    def insert_after(self, target: T, value: T) -> bool:
        """Insert value after the first node containing target."""
        if self.tail is None:
            return False

        current = self.head()

        for _ in range(self._size):
            assert current is not None

            if current.value == target:
                new_node = SinglyNode(value)
                new_node.next = current.next
                current.next = new_node

                if current is self.tail:
                    self.tail = new_node

                self._size += 1
                return True

            current = current.next

        return False

    def insert_at(self, index: int, value: T) -> None:
        """
        Insert at a zero-based position.

        index == 0 inserts at the head.
        index == size inserts at the tail.
        """
        if index < 0 or index > self._size:
            raise IndexError("index must be between 0 and size")

        if index == 0:
            self.prepend(value)
            return

        if index == self._size:
            self.append(value)
            return

        current = self.head()
        assert current is not None

        for _ in range(index - 1):
            assert current.next is not None
            current = current.next

        new_node = SinglyNode(value)
        new_node.next = current.next
        current.next = new_node
        self._size += 1

    def remove_first(self, value: T) -> bool:
        """Remove the first occurrence of value."""
        if self.tail is None:
            return False

        previous = self.tail
        current = self.tail.next

        for _ in range(self._size):
            assert current is not None

            if current.value == value:
                if self._size == 1:
                    self.tail = None
                else:
                    previous.next = current.next

                    if current is self.tail:
                        self.tail = previous

                self._size -= 1
                return True

            previous = current
            current = current.next

        return False

    def remove_at(self, index: int) -> T:
        """Remove and return the node at a zero-based position."""
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

        if self._size == 1:
            assert self.tail is not None
            value = self.tail.value
            self.tail = None
            self._size = 0
            return value

        if index == 0:
            assert self.tail is not None
            head = self.tail.next
            assert head is not None
            self.tail.next = head.next
            self._size -= 1
            return head.value

        previous = self.tail
        current = self.tail.next

        for _ in range(index):
            assert current is not None
            previous = current
            current = current.next

        assert current is not None
        previous.next = current.next

        if current is self.tail:
            self.tail = previous

        self._size -= 1
        return current.value

    def rotate(self, steps: int = 1) -> None:
        """
        Rotate the logical head.

        Moving tail forward by one makes the old second node the
        new head. This is O(1) per step and demonstrates why a
        circular list can naturally represent cyclic state.
        """
        if self.tail is None or self._size == 0:
            return

        self.tail = self.tail.next

        if steps > 1:
            for _ in range(steps - 1):
                self.tail = self.tail.next

    def find(self, value: T) -> int:
        """Return the first matching index, or -1 if absent."""
        if self.tail is None:
            return -1

        current = self.head()

        for index in range(self._size):
            assert current is not None

            if current.value == value:
                return index

            current = current.next

        return -1

    def to_list(self) -> list[T]:
        """Convert the circular structure into a finite Python list."""
        result: list[T] = []

        if self.tail is None:
            return result

        current = self.head()

        for _ in range(self._size):
            assert current is not None
            result.append(current.value)
            current = current.next

        return result

    def traverse_once(self) -> list[T]:
        """
        Traverse exactly one logical cycle.

        A circular list must not use `while current is not None`
        because no node has a None next pointer.
        """
        return self.to_list()

    def validate_structure(self) -> None:
        """
        Verify circular invariants.

        This catches accidental None links, incorrect size tracking,
        broken cycles, and a tail that does not belong to the cycle.
        """
        if self.tail is None:
            if self._size != 0:
                raise AssertionError("empty list has non-zero size")
            return

        if self._size <= 0:
            raise AssertionError("non-empty list must have positive size")

        head = self.tail.next

        if head is None:
            raise AssertionError("tail.next must never be None")

        current = head
        visited = 0

        while visited < self._size:
            if current is None:
                raise AssertionError("circular list contains a None link")

            current = current.next
            visited += 1

        if current is not head:
            raise AssertionError("list does not return to its head")

    def __iter__(self):
        if self.tail is None:
            return

        current = self.head()

        for _ in range(self._size):
            assert current is not None
            yield current.value
            current = current.next

    def __str__(self) -> str:
        if self.tail is None:
            return "EMPTY"

        values = self.to_list()
        return " -> ".join(map(str, values)) + " -> HEAD"


# ============================================================
# Circular Doubly Linked List
# ============================================================

@dataclass
class DoublyNode(Generic[T]):
    value: T
    prev: Optional["DoublyNode[T]"] = None
    next: Optional["DoublyNode[T]"] = None


class CircularDoublyLinkedList(Generic[T]):
    """
    A circular doubly linked list gives every node two links.

    The final node points forward to the first node, and the first
    node points backward to the final node. This allows traversal
    in both directions without a terminating None link.
    """

    def __init__(self, values: Iterable[T] = ()) -> None:
        self.head_node: Optional[DoublyNode[T]] = None
        self._size = 0

        for value in values:
            self.append(value)

    @property
    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.head_node is None

    def head(self) -> Optional[DoublyNode[T]]:
        return self.head_node

    def tail(self) -> Optional[DoublyNode[T]]:
        if self.head_node is None:
            return None
        return self.head_node.prev

    def append(self, value: T) -> None:
        new_node = DoublyNode(value)

        if self.head_node is None:
            new_node.next = new_node
            new_node.prev = new_node
            self.head_node = new_node
        else:
            tail = self.head_node.prev
            assert tail is not None

            new_node.prev = tail
            new_node.next = self.head_node
            tail.next = new_node
            self.head_node.prev = new_node

        self._size += 1

    def prepend(self, value: T) -> None:
        self.append(value)
        assert self.head_node is not None
        self.head_node = self.head_node.prev

    def insert_after(self, target: T, value: T) -> bool:
        if self.head_node is None:
            return False

        current = self.head_node

        for _ in range(self._size):
            if current.value == target:
                self._insert_after_node(current, value)
                return True

            assert current.next is not None
            current = current.next

        return False

    def _insert_after_node(self, node: DoublyNode[T], value: T) -> None:
        new_node = DoublyNode(value)

        assert node.next is not None

        successor = node.next

        new_node.prev = node
        new_node.next = successor
        node.next = new_node
        successor.prev = new_node

        self._size += 1

    def insert_at(self, index: int, value: T) -> None:
        if index < 0 or index > self._size:
            raise IndexError("index must be between 0 and size")

        if self._size == 0 or index == self._size:
            self.append(value)
            return

        if index == 0:
            self.prepend(value)
            return

        node = self.node_at(index)
        assert node.prev is not None
        self._insert_after_node(node.prev, value)

    def node_at(self, index: int) -> DoublyNode[T]:
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

        if index <= self._size // 2:
            assert self.head_node is not None
            current = self.head_node

            for _ in range(index):
                assert current.next is not None
                current = current.next

            return current

        tail = self.tail()
        assert tail is not None
        current = tail

        for _ in range(self._size - 1, index, -1):
            assert current.prev is not None
            current = current.prev

        return current

    def remove_node(self, node: DoublyNode[T]) -> T:
        if self._size == 0:
            raise IndexError("cannot remove from an empty list")

        if self._size == 1:
            if node is not self.head_node:
                raise ValueError("node does not belong to this list")

            value = node.value
            self.head_node = None
            node.next = None
            node.prev = None
            self._size = 0
            return value

        assert node.prev is not None
        assert node.next is not None

        node.prev.next = node.next
        node.next.prev = node.prev

        if node is self.head_node:
            self.head_node = node.next

        value = node.value
        node.next = None
        node.prev = None
        self._size -= 1
        return value

    def remove_first(self, value: T) -> bool:
        if self.head_node is None:
            return False

        current = self.head_node

        for _ in range(self._size):
            if current.value == value:
                self.remove_node(current)
                return True

            assert current.next is not None
            current = current.next

        return False

    def remove_at(self, index: int) -> T:
        return self.remove_node(self.node_at(index))

    def forward(self) -> list[T]:
        result: list[T] = []

        if self.head_node is None:
            return result

        current = self.head_node

        for _ in range(self._size):
            result.append(current.value)
            assert current.next is not None
            current = current.next

        return result

    def backward(self) -> list[T]:
        result: list[T] = []

        if self.head_node is None:
            return result

        tail = self.tail()
        assert tail is not None

        current = tail

        for _ in range(self._size):
            result.append(current.value)
            assert current.prev is not None
            current = current.prev

        return result

    def validate_structure(self) -> None:
        if self.head_node is None:
            if self._size != 0:
                raise AssertionError("empty list has non-zero size")
            return

        if self._size <= 0:
            raise AssertionError("non-empty list has invalid size")

        head = self.head_node
        tail = head.prev

        if tail is None:
            raise AssertionError("head.prev must point to the tail")

        if tail.next is not head:
            raise AssertionError("tail.next must point to head")

        current = head

        for _ in range(self._size):
            if current.next is None or current.prev is None:
                raise AssertionError("circular doubly list has a broken link")

            if current.next.prev is not current:
                raise AssertionError("next.prev invariant is broken")

            if current.prev.next is not current:
                raise AssertionError("prev.next invariant is broken")

            current = current.next

        if current is not head:
            raise AssertionError("forward traversal did not return to head")

    def __iter__(self):
        if self.head_node is None:
            return

        current = self.head_node

        for _ in range(self._size):
            yield current.value
            assert current.next is not None
            current = current.next

    def __str__(self) -> str:
        if self.head_node is None:
            return "EMPTY"

        return " <-> ".join(map(str, self.forward())) + " <-> HEAD"


# ============================================================
# Realistic Case Study: Round-Robin Scheduler
# ============================================================

@dataclass
class Process:
    pid: str
    burst_time: int
    remaining_time: int


class RoundRobinScheduler:
    """
    A circular singly linked list is a natural representation for
    a scheduler that repeatedly visits runnable processes.

    The scheduler advances to the next process after every time
    quantum. A completed process is removed from the circle, while
    an unfinished process remains available for another round.
    """

    def __init__(self, quantum: int) -> None:
        if quantum <= 0:
            raise ValueError("quantum must be positive")

        self.quantum = quantum
        self.queue = CircularSinglyLinkedList[Process]()

    def add_process(self, pid: str, burst_time: int) -> None:
        if not pid.strip():
            raise ValueError("process ID cannot be empty")

        if burst_time <= 0:
            raise ValueError("burst time must be positive")

        process = Process(pid, burst_time, burst_time)
        self.queue.append(process)

    def run(self) -> list[str]:
        execution_log: list[str] = []

        while not self.queue.is_empty():
            current = self.queue.head()
            assert current is not None

            process = current.value
            consumed = min(self.quantum, process.remaining_time)
            process.remaining_time -= consumed

            execution_log.append(
                f"{process.pid}: ran {consumed} unit(s), "
                f"{process.remaining_time} remaining"
            )

            if process.remaining_time == 0:
                self.queue.remove_at(0)
            else:
                self.queue.rotate(1)

        return execution_log


# ============================================================
# Demonstrations
# ============================================================

def demonstrate_circular_singly() -> None:
    print("\n=== Circular Singly Linked List ===")

    numbers = CircularSinglyLinkedList([10, 20, 30])
    numbers.validate_structure()

    print("Initial:", numbers)
    print("Traversal:", numbers.traverse_once())

    numbers.prepend(5)
    print("After prepend(5):", numbers)

    numbers.append(40)
    print("After append(40):", numbers)

    numbers.insert_after(20, 25)
    print("After insert_after(20, 25):", numbers)

    numbers.insert_at(3, 27)
    print("After insert_at(3, 27):", numbers)

    numbers.remove_first(25)
    print("After remove_first(25):", numbers)

    removed = numbers.remove_at(0)
    print(f"Removed index 0 ({removed}):", numbers)

    numbers.rotate()
    print("After one rotation:", numbers)

    numbers.validate_structure()

    print("Find 30:", numbers.find(30))
    print("Find 999:", numbers.find(999))


def demonstrate_circular_doubly() -> None:
    print("\n=== Circular Doubly Linked List ===")

    routes = CircularDoublyLinkedList(["A", "B", "C", "D"])
    routes.validate_structure()

    print("Forward:", routes.forward())
    print("Backward:", routes.backward())

    routes.prepend("START")
    print("After prepend:", routes.forward())

    routes.insert_after("B", "B2")
    print("After insert_after(B, B2):", routes.forward())

    routes.remove_first("C")
    print("After remove_first(C):", routes.forward())

    routes.remove_at(0)
    print("After removing head:", routes.forward())
    print("Backward traversal:", routes.backward())

    routes.validate_structure()


def demonstrate_edge_cases() -> None:
    print("\n=== Edge Cases ===")

    singly = CircularSinglyLinkedList[int]()

    print("Empty traversal:", singly.traverse_once())
    print("Remove from empty:", singly.remove_first(10))

    singly.append(42)
    print("Single-node traversal:", singly.traverse_once())

    singly.remove_at(0)
    print("After removing only node:", singly.traverse_once())

    doubly = CircularDoublyLinkedList(["only"])
    print("Single-node forward:", doubly.forward())
    print("Single-node backward:", doubly.backward())

    doubly.remove_at(0)
    print("Doubly list after removing only node:", doubly.forward())

    try:
        singly.remove_at(0)
    except IndexError as exc:
        print("Expected error:", exc)

    try:
        CircularSinglyLinkedList([1, 2]).insert_at(5, 10)
    except IndexError as exc:
        print("Expected insertion error:", exc)


def demonstrate_round_robin() -> None:
    print("\n=== Round-Robin Scheduler ===")

    scheduler = RoundRobinScheduler(quantum=2)

    scheduler.add_process("P1", 5)
    scheduler.add_process("P2", 3)
    scheduler.add_process("P3", 4)

    for event in scheduler.run():
        print(event)


def demonstrate_complexity() -> None:
    print("\n=== Operational Complexity ===")

    print("Circular singly list:")
    print("  Access by position: O(n)")
    print("  Search:             O(n)")
    print("  Append with tail:   O(1)")
    print("  Prepend with tail:  O(1)")
    print("  Delete by value:    O(n)")
    print("  Delete known node:  O(1) only when predecessor is already known")

    print("\nCircular doubly list:")
    print("  Access by position: O(n), with direction chosen by index")
    print("  Search:             O(n)")
    print("  Append:             O(1)")
    print("  Prepend:            O(1)")
    print("  Delete known node:  O(1)")
    print("  Extra memory:       one additional prev reference per node")


def main() -> None:
    demonstrate_circular_singly()
    demonstrate_circular_doubly()
    demonstrate_edge_cases()
    demonstrate_round_robin()
    demonstrate_complexity()


if __name__ == "__main__":
    main()
