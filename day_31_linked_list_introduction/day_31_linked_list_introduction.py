"""
Linked List Introduction
========================

A self-contained progression from linked-list fundamentals to practical
implementations.

The program demonstrates:
- Nodes and references
- Dynamic memory allocation in Python
- Singly linked lists
- Array/list versus linked-list behavior
- Traversal and searching
- Insertion and deletion
- Edge cases and validation
- Reverse traversal by reversing links
- Cycle detection
- Finding the middle node
- Removing duplicates
- A small practical task-list case study
- Complexity measurements and design considerations

Python objects are dynamically allocated. A node stores a value and a
reference to another Node object. The reference is not a raw memory address;
Python manages object memory and reference lifetime automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterator, Optional


@dataclass
class Node:
    """One element of a singly linked list."""

    value: int
    next: Optional["Node"] = None


class SinglyLinkedList:
    """
    A singly linked list with a head reference and an optional tail reference.

    The tail reference allows append() to run in O(1) time. Without it,
    appending would require traversal from the head and would be O(n).
    """

    def __init__(self, values: Optional[Iterator[int]] = None) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.size = 0

        if values is not None:
            for value in values:
                self.append(value)

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[int]:
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self) -> str:
        return " -> ".join(map(str, self)) if self.size else "EMPTY"

    def append(self, value: int) -> None:
        """Add a node after the current tail."""
        new_node = Node(value)

        if self.head is None:
            self.head = self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node

        self.size += 1

    def prepend(self, value: int) -> None:
        """Insert a node before the current head."""
        new_node = Node(value, self.head)
        self.head = new_node

        if self.tail is None:
            self.tail = new_node

        self.size += 1

    def insert_after(self, target: int, value: int) -> bool:
        """
        Insert a node after the first node containing target.

        Returns False when target does not exist.
        """
        current = self.head

        while current is not None:
            if current.value == target:
                new_node = Node(value, current.next)
                current.next = new_node

                if self.tail is current:
                    self.tail = new_node

                self.size += 1
                return True

            current = current.next

        return False

    def find(self, value: int) -> Optional[Node]:
        """Return the first matching node, or None."""
        current = self.head

        while current is not None:
            if current.value == value:
                return current
            current = current.next

        return None

    def contains(self, value: int) -> bool:
        return self.find(value) is not None

    def delete_first(self, value: int) -> bool:
        """Delete the first node containing value."""
        if self.head is None:
            return False

        if self.head.value == value:
            self.head = self.head.next
            self.size -= 1

            if self.size == 0:
                self.tail = None

            return True

        previous = self.head
        current = self.head.next

        while current is not None:
            if current.value == value:
                previous.next = current.next

                if current is self.tail:
                    self.tail = previous

                self.size -= 1
                return True

            previous = current
            current = current.next

        return False

    def delete_at(self, index: int) -> int:
        """
        Delete and return the node at index.

        Unlike an array, reaching an arbitrary index requires traversal.
        """
        if index < 0 or index >= self.size:
            raise IndexError("linked-list index out of range")

        if index == 0:
            assert self.head is not None
            value = self.head.value
            self.head = self.head.next
            self.size -= 1

            if self.size == 0:
                self.tail = None

            return value

        previous = self.head
        assert previous is not None

        for _ in range(index - 1):
            assert previous.next is not None
            previous = previous.next

        current = previous.next
        assert current is not None

        previous.next = current.next

        if current is self.tail:
            self.tail = previous

        self.size -= 1
        return current.value

    def reverse(self) -> None:
        """
        Reverse the links in place.

        The three references are necessary because changing current.next
        before saving the old next node would lose the remainder of the list.
        """
        previous: Optional[Node] = None
        current = self.head

        self.tail = self.head

        while current is not None:
            next_node = current.next
            current.next = previous
            previous = current
            current = next_node

        self.head = previous

    def middle(self) -> Optional[int]:
        """
        Return the middle value using slow and fast references.

        For an even number of nodes this returns the second middle node.
        """
        slow = self.head
        fast = self.head

        while fast is not None and fast.next is not None:
            assert slow is not None
            slow = slow.next
            fast = fast.next.next

        return None if slow is None else slow.value

    def has_cycle(self) -> bool:
        """
        Floyd's tortoise-and-hare algorithm.

        A cycle makes the fast reference eventually meet the slow reference.
        """
        slow = self.head
        fast = self.head

        while fast is not None and fast.next is not None:
            assert slow is not None
            slow = slow.next
            fast = fast.next.next

            if slow is fast:
                return True

        return False

    def remove_duplicates(self) -> None:
        """
        Remove duplicate values while preserving first-occurrence order.

        The set provides average O(1) membership checks, making the complete
        operation O(n) rather than repeatedly scanning the list.
        """
        seen: set[int] = set()
        previous: Optional[Node] = None
        current = self.head

        while current is not None:
            if current.value in seen:
                assert previous is not None
                previous.next = current.next

                if current is self.tail:
                    self.tail = previous

                self.size -= 1
            else:
                seen.add(current.value)
                previous = current

            current = current.next


def demonstrate_node_references() -> None:
    print("\n=== Node Structure and References ===")

    first = Node(10)
    second = Node(20)
    third = Node(30)

    first.next = second
    second.next = third

    print("first.value:", first.value)
    print("first.next.value:", first.next.value)
    print("second.next.value:", second.next.value)
    print("third.next:", third.next)

    print(
        "Conceptual structure:",
        "first -> second -> third -> None",
    )


def demonstrate_array_comparison() -> None:
    print("\n=== Python List Versus Linked List ===")

    array = [10, 20, 30, 40]
    linked = SinglyLinkedList(array)

    print("Array:", array)
    print("Linked list:", linked)

    print("Array index access [2]:", array[2])

    current = linked.head
    for _ in range(2):
        assert current is not None
        current = current.next

    assert current is not None
    print("Linked-list index 2 after traversal:", current.value)

    print(
        "Array index access is typically O(1), while linked-list "
        "index access is O(n)."
    )


def demonstrate_basic_operations() -> None:
    print("\n=== Basic Linked-List Operations ===")

    numbers = SinglyLinkedList()

    print("Initially:", numbers)

    numbers.append(20)
    numbers.append(30)
    numbers.prepend(10)

    print("After append/append/prepend:", numbers)
    print("Size:", len(numbers))
    print("Contains 20:", numbers.contains(20))
    print("Contains 99:", numbers.contains(99))

    inserted = numbers.insert_after(20, 25)
    print("Inserted 25 after 20:", inserted, numbers)

    deleted = numbers.delete_first(25)
    print("Deleted 25:", deleted, numbers)

    removed_value = numbers.delete_at(1)
    print("Deleted index 1:", removed_value, numbers)


def demonstrate_edge_cases() -> None:
    print("\n=== Edge Cases and Validation ===")

    empty = SinglyLinkedList()

    print("Empty list:", empty)
    print("Delete from empty:", empty.delete_first(100))
    print("Find in empty:", empty.find(100))
    print("Middle of empty:", empty.middle())

    try:
        empty.delete_at(0)
    except IndexError as exc:
        print("Invalid index rejected:", exc)

    single = SinglyLinkedList([42])

    print("Single-node list:", single)
    print("Single-node middle:", single.middle())

    single.reverse()
    print("Single-node after reverse:", single)

    print(
        "A common mistake is assuming an invalid index behaves like a "
        "Python list lookup. This implementation deliberately raises "
        "IndexError."
    )


def demonstrate_reverse_and_middle() -> None:
    print("\n=== Reverse and Middle-Node Algorithms ===")

    values = SinglyLinkedList([10, 20, 30, 40, 50, 60])

    print("Original:", values)
    print("Middle:", values.middle())

    values.reverse()

    print("Reversed:", values)
    print("Middle after reverse:", values.middle())


def demonstrate_cycle_detection() -> None:
    print("\n=== Cycle Detection ===")

    linked = SinglyLinkedList([1, 2, 3, 4])

    print("Normal list has cycle:", linked.has_cycle())

    assert linked.tail is not None
    assert linked.head is not None
    assert linked.head.next is not None
    linked.tail.next = linked.head.next

    print("After connecting tail to second node:", linked.has_cycle())

    # Restore the structure so no later operation accidentally traverses
    # forever. In a real implementation, cycle creation would normally be
    # restricted to diagnostic or specialized data-structure code.
    linked.tail.next = None

    print("Cycle removed:", linked.has_cycle())


def demonstrate_duplicates() -> None:
    print("\n=== Duplicate Removal ===")

    values = SinglyLinkedList([7, 3, 7, 2, 3, 9, 2, 9, 9])

    print("Before:", values)
    values.remove_duplicates()
    print("After:", values)
    print("Size:", len(values))


@dataclass
class Task:
    """A realistic record stored inside a linked-list node."""

    task_id: int
    title: str
    priority: str


@dataclass
class TaskNode:
    """Linked-list node specialized for the task-management example."""

    task: Task
    next: Optional["TaskNode"] = None


class TaskQueue:
    """
    FIFO task queue implemented with linked nodes.

    enqueue() adds at the tail and dequeue() removes from the head, so both
    operations avoid shifting the remaining records.
    """

    def __init__(self) -> None:
        self.head: Optional[TaskNode] = None
        self.tail: Optional[TaskNode] = None
        self.size = 0

    def enqueue(self, task: Task) -> None:
        node = TaskNode(task)

        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node

        self.size += 1

    def dequeue(self) -> Task:
        if self.head is None:
            raise IndexError("cannot dequeue from an empty task queue")

        node = self.head
        self.head = node.next
        self.size -= 1

        if self.head is None:
            self.tail = None

        return node.task

    def peek(self) -> Optional[Task]:
        return None if self.head is None else self.head.task

    def __iter__(self) -> Iterator[Task]:
        current = self.head

        while current is not None:
            yield current.task
            current = current.next


def demonstrate_task_queue() -> None:
    print("\n=== Practical Linked-List Case: Task Queue ===")

    queue = TaskQueue()

    queue.enqueue(Task(101, "Review pull request", "high"))
    queue.enqueue(Task(102, "Run integration tests", "medium"))
    queue.enqueue(Task(103, "Update documentation", "low"))

    print("Queue contents:")
    for task in queue:
        print(f"  {task.task_id}: {task.title} [{task.priority}]")

    print("Next task:", queue.peek())

    while queue.size:
        task = queue.dequeue()
        print("Processing:", task.title)


def benchmark_access_patterns() -> None:
    print("\n=== Access Pattern Demonstration ===")

    count = 50_000
    target_index = count - 1

    array = list(range(count))
    linked = SinglyLinkedList(range(count))

    start = perf_counter()
    array_value = array[target_index]
    array_time = perf_counter() - start

    start = perf_counter()
    current = linked.head

    for _ in range(target_index):
        assert current is not None
        current = current.next

    assert current is not None
    linked_value = current.value
    linked_time = perf_counter() - start

    print("Array result:", array_value)
    print("Linked-list result:", linked_value)
    print(f"Array index access time: {array_time:.8f} seconds")
    print(f"Linked-list traversal time: {linked_time:.8f} seconds")
    print(
        "The exact timings depend on hardware and runtime, but the "
        "algorithmic difference is the important observation."
    )


def demonstrate_complexity() -> None:
    print("\n=== Operation Complexity ===")

    complexity = {
        "Access by index": "O(n) for a singly linked list",
        "Search by value": "O(n)",
        "Insert at head": "O(1)",
        "Delete at head": "O(1)",
        "Append with tail reference": "O(1)",
        "Append without tail reference": "O(n)",
        "Insert after known node": "O(1)",
        "Delete after known previous node": "O(1)",
        "Reverse": "O(n)",
        "Cycle detection": "O(n) time, O(1) extra space",
    }

    for operation, complexity_value in complexity.items():
        print(f"{operation}: {complexity_value}")


def demonstrate_memory_model() -> None:
    print("\n=== Memory and Reference Model ===")

    first = Node(100)
    second = Node(200)
    first.next = second

    print("Node objects are separate Python objects.")
    print("first.value:", first.value)
    print("first.next.value:", first.next.value)
    print("first.next is second:", first.next is second)

    print(
        "Python manages allocation and garbage collection. The linked-list "
        "algorithm still has explicit logical links, even though the "
        "programmer does not manipulate raw addresses."
    )

    # Removing the only remaining reference to second through first would
    # make the second node eligible for garbage collection if no other
    # references exist.
    first.next = None
    print("Link removed. first.next:", first.next)


def run_assertions() -> None:
    """Small executable checks for important invariants."""

    linked = SinglyLinkedList([1, 2, 3])

    assert len(linked) == 3
    assert linked.head is not None
    assert linked.tail is not None
    assert linked.head.value == 1
    assert linked.tail.value == 3

    linked.prepend(0)
    assert list(linked) == [0, 1, 2, 3]

    assert linked.insert_after(2, 99)
    assert list(linked) == [0, 1, 2, 99, 3]

    assert linked.delete_first(99)
    assert list(linked) == [0, 1, 2, 3]

    linked.reverse()
    assert list(linked) == [3, 2, 1, 0]

    assert not linked.has_cycle()

    duplicate_list = SinglyLinkedList([1, 1, 2, 2, 3])
    duplicate_list.remove_duplicates()
    assert list(duplicate_list) == [1, 2, 3]

    print("\nAll internal assertions passed.")


def main() -> None:
    print("=" * 72)
    print("LINKED LIST INTRODUCTION")
    print("=" * 72)

    demonstrate_node_references()
    demonstrate_array_comparison()
    demonstrate_basic_operations()
    demonstrate_edge_cases()
    demonstrate_reverse_and_middle()
    demonstrate_cycle_detection()
    demonstrate_duplicates()
    demonstrate_task_queue()
    demonstrate_memory_model()
    demonstrate_complexity()
    benchmark_access_patterns()
    run_assertions()


if __name__ == "__main__":
    main()
