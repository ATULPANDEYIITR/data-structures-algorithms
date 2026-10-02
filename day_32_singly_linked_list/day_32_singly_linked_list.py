from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Iterator


@dataclass
class Node:
    """A single node containing a value and a reference to the next node."""
    value: int
    next: Optional["Node"] = None


class SinglyLinkedList:
    """
    A singly linked list with traversal, insertion, deletion, searching,
    updating, and reversal operations.

    The list stores only a head reference. Each node points forward to the
    next node, while the final node points to None.
    """

    def __init__(self, values: Iterable[int] = ()) -> None:
        self.head: Optional[Node] = None
        self._size = 0

        # Building through append keeps construction behavior identical
        # to ordinary user-driven insertion.
        for value in values:
            self.append(value)

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self.head is not None

    def __iter__(self) -> Iterator[int]:
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __str__(self) -> str:
        return " -> ".join(map(str, self))

    def to_list(self) -> list[int]:
        return list(self)

    def is_empty(self) -> bool:
        return self.head is None

    def append(self, value: int) -> None:
        """Insert a value at the end of the list."""
        new_node = Node(value)

        if self.head is None:
            self.head = new_node
            self._size += 1
            return

        current = self.head
        while current.next is not None:
            current = current.next

        current.next = new_node
        self._size += 1

    def prepend(self, value: int) -> None:
        """Insert a value at the beginning in O(1) time."""
        self.head = Node(value, self.head)
        self._size += 1

    def insert_at(self, index: int, value: int) -> None:
        """
        Insert value before the current element at index.

        Valid insertion indexes are 0 through size. Index size means append.
        """
        if index < 0 or index > self._size:
            raise IndexError(
                f"insertion index {index} out of range for size {self._size}"
            )

        if index == 0:
            self.prepend(value)
            return

        if index == self._size:
            self.append(value)
            return

        previous = self.head
        assert previous is not None

        for _ in range(index - 1):
            assert previous.next is not None
            previous = previous.next

        new_node = Node(value, previous.next)
        previous.next = new_node
        self._size += 1

    def insert_after(self, target: int, value: int) -> bool:
        """
        Insert value after the first occurrence of target.

        Returns False if target does not exist.
        """
        current = self.head

        while current is not None:
            if current.value == target:
                current.next = Node(value, current.next)
                self._size += 1
                return True
            current = current.next

        return False

    def delete_at(self, index: int) -> int:
        """Delete and return the value at index."""
        if index < 0 or index >= self._size:
            raise IndexError(
                f"deletion index {index} out of range for size {self._size}"
            )

        if index == 0:
            assert self.head is not None
            removed = self.head
            self.head = removed.next
            self._size -= 1
            return removed.value

        previous = self.head
        assert previous is not None

        for _ in range(index - 1):
            assert previous.next is not None
            previous = previous.next

        removed = previous.next
        assert removed is not None

        previous.next = removed.next
        self._size -= 1
        return removed.value

    def delete_value(self, value: int) -> bool:
        """Delete the first node containing value."""
        if self.head is None:
            return False

        if self.head.value == value:
            self.head = self.head.next
            self._size -= 1
            return True

        previous = self.head
        current = self.head.next

        while current is not None:
            if current.value == value:
                previous.next = current.next
                self._size -= 1
                return True

            previous = current
            current = current.next

        return False

    def delete_all(self, value: int) -> int:
        """Delete every node containing value and return the removal count."""
        removed_count = 0

        # Removing matching head nodes requires repeatedly advancing head.
        while self.head is not None and self.head.value == value:
            self.head = self.head.next
            self._size -= 1
            removed_count += 1

        if self.head is None:
            return removed_count

        previous = self.head
        current = self.head.next

        while current is not None:
            if current.value == value:
                previous.next = current.next
                current = previous.next
                self._size -= 1
                removed_count += 1
            else:
                previous = current
                current = current.next

        return removed_count

    def search(self, value: int) -> int:
        """
        Return the first zero-based index containing value.

        Returns -1 when value is absent.
        """
        current = self.head
        index = 0

        while current is not None:
            if current.value == value:
                return index

            current = current.next
            index += 1

        return -1

    def contains(self, value: int) -> bool:
        return self.search(value) != -1

    def update_at(self, index: int, new_value: int) -> int:
        """Replace the value at index and return the old value."""
        if index < 0 or index >= self._size:
            raise IndexError(
                f"update index {index} out of range for size {self._size}"
            )

        current = self.head
        assert current is not None

        for _ in range(index):
            assert current.next is not None
            current = current.next

        old_value = current.value
        current.value = new_value
        return old_value

    def update_first(self, old_value: int, new_value: int) -> bool:
        """Update the first occurrence of old_value."""
        current = self.head

        while current is not None:
            if current.value == old_value:
                current.value = new_value
                return True

            current = current.next

        return False

    def reverse(self) -> None:
        """
        Reverse the links in place.

        At each step:
        previous <- current <- next_node

        The current node is detached from its old forward direction and
        redirected toward the already-reversed prefix.
        """
        previous: Optional[Node] = None
        current = self.head

        while current is not None:
            next_node = current.next
            current.next = previous
            previous = current
            current = next_node

        self.head = previous

    def reverse_recursive(self) -> None:
        """Reverse recursively. This uses O(n) call-stack space."""

        def reverse_node(
            current: Optional[Node],
            previous: Optional[Node],
        ) -> Optional[Node]:
            if current is None:
                return previous

            next_node = current.next
            current.next = previous
            return reverse_node(next_node, current)

        self.head = reverse_node(self.head, None)

    def get(self, index: int) -> int:
        """Return the value at index without modifying the list."""
        if index < 0 or index >= self._size:
            raise IndexError(
                f"access index {index} out of range for size {self._size}"
            )

        current = self.head
        assert current is not None

        for _ in range(index):
            assert current.next is not None
            current = current.next

        return current.value

    def clear(self) -> None:
        """
        Remove all references from the list.

        Python's garbage collector can reclaim the former nodes once no other
        references to them remain.
        """
        self.head = None
        self._size = 0

    def validate_integrity(self) -> bool:
        """
        Verify size consistency and detect accidental cycles.

        Floyd's tortoise-and-hare algorithm detects a cycle using O(1) space.
        """
        slow = self.head
        fast = self.head

        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next

            if slow is fast:
                return False

        count = 0
        current = self.head

        while current is not None:
            count += 1
            current = current.next

        return count == self._size

    def node_at(self, index: int) -> Node:
        """Return the actual node, primarily for diagnostics and demonstrations."""
        if index < 0 or index >= self._size:
            raise IndexError("node index out of range")

        current = self.head
        assert current is not None

        for _ in range(index):
            assert current.next is not None
            current = current.next

        return current


def demonstrate_basics() -> None:
    print("\n=== Basic construction and traversal ===")

    linked_list = SinglyLinkedList([10, 20, 30, 40])

    print("List:", linked_list)
    print("As Python list:", linked_list.to_list())
    print("Size:", len(linked_list))
    print("Empty:", linked_list.is_empty())

    print("Traversal using iteration:")
    for value in linked_list:
        print(f"  visited {value}")


def demonstrate_insertions() -> None:
    print("\n=== Insertion ===")

    linked_list = SinglyLinkedList([20, 30])

    linked_list.prepend(10)
    print("After prepend(10):", linked_list)

    linked_list.append(40)
    print("After append(40):", linked_list)

    linked_list.insert_at(2, 25)
    print("After insert_at(2, 25):", linked_list)

    linked_list.insert_after(30, 35)
    print("After insert_after(30, 35):", linked_list)

    try:
        linked_list.insert_at(99, 500)
    except IndexError as error:
        print("Invalid insertion handled:", error)


def demonstrate_search_and_update() -> None:
    print("\n=== Searching and updating ===")

    linked_list = SinglyLinkedList([15, 25, 35, 45, 55])

    print("List:", linked_list)
    print("Index of 35:", linked_list.search(35))
    print("Index of 999:", linked_list.search(999))
    print("Contains 45:", linked_list.contains(45))

    old = linked_list.update_at(1, 27)
    print(f"Updated index 1 from {old} to 27:", linked_list)

    changed = linked_list.update_first(45, 47)
    print("Updated first 45:", changed)
    print("List:", linked_list)

    try:
        linked_list.update_at(10, 100)
    except IndexError as error:
        print("Invalid update handled:", error)


def demonstrate_deletion() -> None:
    print("\n=== Deletion ===")

    linked_list = SinglyLinkedList([10, 20, 30, 40, 50])

    removed = linked_list.delete_at(0)
    print(f"delete_at(0) removed {removed}:", linked_list)

    removed = linked_list.delete_at(2)
    print(f"delete_at(2) removed {removed}:", linked_list)

    print("delete_value(40):", linked_list.delete_value(40))
    print("After deleting first 40:", linked_list)

    duplicates = SinglyLinkedList([5, 5, 7, 5, 9, 5])
    removed_count = duplicates.delete_all(5)
    print(f"Removed {removed_count} occurrences of 5:", duplicates)

    print("Deleting missing value:", linked_list.delete_value(999))

    try:
        linked_list.delete_at(100)
    except IndexError as error:
        print("Invalid deletion handled:", error)


def demonstrate_reversal() -> None:
    print("\n=== Reversal ===")

    linked_list = SinglyLinkedList([1, 2, 3, 4, 5])
    print("Original:", linked_list)

    linked_list.reverse()
    print("After iterative reverse:", linked_list)

    linked_list.reverse_recursive()
    print("After recursive reverse:", linked_list)


def demonstrate_pointer_mechanics() -> None:
    print("\n=== Link mechanics ===")

    linked_list = SinglyLinkedList(["A", "B", "C", "D"])

    current = linked_list.head
    while current is not None:
        next_value = current.next.value if current.next is not None else "None"
        print(f"Node value={current.value!r}, next={next_value!r}")
        current = current.next

    print("\nReversing the same links in place:")
    linked_list.reverse()

    current = linked_list.head
    while current is not None:
        next_value = current.next.value if current.next is not None else "None"
        print(f"Node value={current.value!r}, next={next_value!r}")
        current = current.next


def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases ===")

    empty = SinglyLinkedList()
    print("Empty list:", empty)
    print("Search empty list:", empty.search(10))
    print("Delete missing value from empty list:", empty.delete_value(10))

    empty.prepend(42)
    print("After inserting into empty list:", empty)

    removed = empty.delete_at(0)
    print("Removed only element:", removed)
    print("List after removing only element:", empty)

    single = SinglyLinkedList([99])
    single.reverse()
    print("Reversed single-node list:", single)

    duplicate_values = SinglyLinkedList([3, 3, 3])
    print("Before deleting duplicates:", duplicate_values)
    print("Removed:", duplicate_values.delete_all(3))
    print("After deleting duplicates:", duplicate_values)

    for operation_name, operation in [
        ("get(-1)", lambda: single.get(-1)),
        ("get(4)", lambda: single.get(4)),
        ("insert_at(-1, 10)", lambda: single.insert_at(-1, 10)),
    ]:
        try:
            operation()
        except IndexError as error:
            print(f"{operation_name} handled:", error)


def demonstrate_integrity() -> None:
    print("\n=== Structural integrity ===")

    linked_list = SinglyLinkedList([1, 2, 3, 4])
    print("Valid structure:", linked_list.validate_integrity())

    # A deliberately corrupted structure demonstrates why cycle detection
    # matters in linked-list implementations.
    tail = linked_list.node_at(3)
    tail.next = linked_list.head

    print("Cycle detected after deliberate corruption:",
          not linked_list.validate_integrity())

    # Restore the structure so the demonstration leaves the object usable.
    tail.next = None
    print("Structure restored:", linked_list.validate_integrity())


def demonstrate_complexity() -> None:
    print("\n=== Operation complexity ===")

    print("prepend: O(1)")
    print("append without a tail pointer: O(n)")
    print("insert_at: O(n) worst case")
    print("insert_after after searching: O(n)")
    print("delete_at: O(n) worst case")
    print("delete_value: O(n)")
    print("search: O(n)")
    print("update_at: O(n)")
    print("reverse iteratively: O(n) time, O(1) auxiliary space")
    print("reverse recursively: O(n) time, O(n) call-stack space")
    print("index access: O(n)")
    print("Linked-list node storage: O(n)")

    print(
        "\nA singly linked list is useful when sequential traversal and "
        "frequent front insertions are more important than random access."
    )


def run_tests() -> None:
    print("\n=== Verification tests ===")

    values = SinglyLinkedList([10, 20, 30])
    assert values.to_list() == [10, 20, 30]

    values.prepend(5)
    assert values.to_list() == [5, 10, 20, 30]

    values.append(40)
    assert values.to_list() == [5, 10, 20, 30, 40]

    values.insert_at(2, 15)
    assert values.to_list() == [5, 10, 15, 20, 30, 40]

    assert values.insert_after(30, 35)
    assert values.to_list() == [5, 10, 15, 20, 30, 35, 40]

    assert values.search(20) == 3
    assert values.search(999) == -1

    assert values.update_at(3, 21) == 20
    assert values.get(3) == 21

    assert values.update_first(21, 20)
    assert values.delete_value(20)
    assert values.to_list() == [5, 10, 15, 30, 35, 40]

    assert values.delete_at(0) == 5
    assert values.to_list() == [10, 15, 30, 35, 40]

    values.reverse()
    assert values.to_list() == [40, 35, 30, 15, 10]

    values.reverse_recursive()
    assert values.to_list() == [10, 15, 30, 35, 40]

    assert values.validate_integrity()

    print("All tests passed.")


def main() -> None:
    print("SINGLY LINKED LIST: COMPLETE PYTHON DEMONSTRATION")

    demonstrate_basics()
    demonstrate_insertions()
    demonstrate_search_and_update()
    demonstrate_deletion()
    demonstrate_reversal()
    demonstrate_pointer_mechanics()
    demonstrate_edge_cases()
    demonstrate_integrity()
    demonstrate_complexity()
    run_tests()


if __name__ == "__main__":
    main()
