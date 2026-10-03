"""
Doubly Linked List: complete executable study and implementation.

This script builds a production-oriented doubly linked list from first principles.
It demonstrates:
- Previous and next pointers
- Forward and backward traversal
- Head, tail, and size management
- Insertion at both ends and arbitrary positions
- Deletion by value and position
- Search and indexed access
- Reverse traversal
- Safe mutation while iterating
- Node unlinking
- Comparison with singly linked lists
- Invariant validation
- Edge cases and failure handling
- Complexity characteristics
- A realistic browser-history use case

Run with:
    python doubly_linked_list.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Iterable, Optional


@dataclass
class Node:
    """
    A node contains a value plus two directional links.

    prev points toward the node immediately before this node.
    next points toward the node immediately after this node.

    Keeping both links synchronized is the central correctness requirement
    of a doubly linked list.
    """

    value: str
    prev: Optional["Node"] = None
    next: Optional["Node"] = None


class DoublyLinkedList:
    """A mutable doubly linked list with head/tail access."""

    def __init__(self, values: Optional[Iterable[str]] = None) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size = 0

        if values is not None:
            for value in values:
                self.append(value)

    @property
    def size(self) -> int:
        """Return the number of nodes currently stored."""
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def append(self, value: str) -> Node:
        """
        Insert a new node after the current tail.

        For an empty list, the new node becomes both head and tail.
        Otherwise, the old tail points forward to the new node and the
        new node points backward to the old tail.
        """
        new_node = Node(value)

        if self.tail is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

        self._size += 1
        return new_node

    def prepend(self, value: str) -> Node:
        """
        Insert a new node before the current head.

        The new node becomes the head, while its next pointer references
        the previous head.
        """
        new_node = Node(value)

        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

        self._size += 1
        return new_node

    def _node_at(self, index: int) -> Node:
        """
        Return the node at index.

        The traversal starts from whichever end is closer, which is an
        important advantage of a doubly linked list when indexed access
        must be implemented without an array.
        """
        self._validate_index(index)

        if index <= self._size // 2:
            current = self.head
            for _ in range(index):
                assert current is not None
                current = current.next
        else:
            current = self.tail
            for _ in range(self._size - 1, index, -1):
                assert current is not None
                current = current.prev

        assert current is not None
        return current

    def _validate_index(self, index: int, allow_end: bool = False) -> None:
        maximum = self._size if allow_end else self._size - 1

        if not isinstance(index, int):
            raise TypeError("index must be an integer")

        if index < 0 or index > maximum:
            if allow_end:
                raise IndexError(
                    f"index must be between 0 and {self._size}, got {index}"
                )
            raise IndexError(
                f"index must be between 0 and {self._size - 1}, got {index}"
            )

    def insert_at(self, index: int, value: str) -> Node:
        """
        Insert a value before the node currently occupying index.

        index == size means insertion at the end.
        """
        self._validate_index(index, allow_end=True)

        if index == 0:
            return self.prepend(value)

        if index == self._size:
            return self.append(value)

        current = self._node_at(index)
        previous = current.prev

        assert previous is not None

        new_node = Node(value=value, prev=previous, next=current)
        previous.next = new_node
        current.prev = new_node

        self._size += 1
        return new_node

    def remove_node(self, node: Node) -> str:
        """
        Remove a specific node in O(1) time once that node is known.

        The method reconnects the predecessor and successor directly.
        It also clears the removed node's links so accidental reuse is
        easier to detect during debugging.
        """
        previous = node.prev
        following = node.next

        if previous is None:
            self.head = following
        else:
            previous.next = following

        if following is None:
            self.tail = previous
        else:
            following.prev = previous

        node.prev = None
        node.next = None

        self._size -= 1

        if self._size == 0:
            self.head = self.tail = None

        return node.value

    def pop_front(self) -> str:
        if self.head is None:
            raise IndexError("cannot remove from an empty list")
        return self.remove_node(self.head)

    def pop_back(self) -> str:
        if self.tail is None:
            raise IndexError("cannot remove from an empty list")
        return self.remove_node(self.tail)

    def remove_at(self, index: int) -> str:
        return self.remove_node(self._node_at(index))

    def remove_first(self, value: str) -> bool:
        """
        Search from the head and remove the first matching value.

        Search is O(n); the actual unlink operation is O(1).
        """
        current = self.head

        while current is not None:
            if current.value == value:
                self.remove_node(current)
                return True
            current = current.next

        return False

    def remove_all(self, value: str) -> int:
        """
        Remove every node containing value.

        Saving current.next before unlinking is essential because
        remove_node clears the removed node's links.
        """
        removed = 0
        current = self.head

        while current is not None:
            following = current.next

            if current.value == value:
                self.remove_node(current)
                removed += 1

            current = following

        return removed

    def find(self, value: str) -> Optional[Node]:
        current = self.head

        while current is not None:
            if current.value == value:
                return current
            current = current.next

        return None

    def forward(self) -> Generator[str, None, None]:
        current = self.head

        while current is not None:
            yield current.value
            current = current.next

    def backward(self) -> Generator[str, None, None]:
        current = self.tail

        while current is not None:
            yield current.value
            current = current.prev

    def values_forward(self) -> list[str]:
        return list(self.forward())

    def values_backward(self) -> list[str]:
        return list(self.backward())

    def clear(self) -> None:
        """
        Detach every node.

        Python's garbage collector does not require this level of cleanup,
        but explicitly clearing links makes the ownership transition clear
        and helps prevent accidental retention when Node references exist.
        """
        current = self.head

        while current is not None:
            following = current.next
            current.prev = None
            current.next = None
            current = following

        self.head = None
        self.tail = None
        self._size = 0

    def validate(self) -> None:
        """
        Verify structural invariants.

        A correct doubly linked list must satisfy:
        - Empty list => head and tail are both None.
        - Non-empty list => head.prev is None.
        - Non-empty list => tail.next is None.
        - current.next.prev is current.
        - current.prev.next is current.
        - Forward and backward node counts match size.
        """
        if self._size == 0:
            if self.head is not None or self.tail is not None:
                raise AssertionError("empty list has a non-empty endpoint")
            return

        if self.head is None or self.tail is None:
            raise AssertionError("non-empty list must have head and tail")

        if self.head.prev is not None:
            raise AssertionError("head.prev must be None")

        if self.tail.next is not None:
            raise AssertionError("tail.next must be None")

        count_forward = 0
        previous = None
        current = self.head

        while current is not None:
            if current.prev is not previous:
                raise AssertionError("broken previous link")

            if current.next is not None and current.next.prev is not current:
                raise AssertionError("broken forward/backward relationship")

            previous = current
            current = current.next
            count_forward += 1

            if count_forward > self._size:
                raise AssertionError("cycle detected during forward traversal")

        if previous is not self.tail:
            raise AssertionError("tail does not terminate forward traversal")

        count_backward = 0
        following = None
        current = self.tail

        while current is not None:
            if current.next is not following:
                raise AssertionError("broken next link")

            if current.prev is not None and current.prev.next is not current:
                raise AssertionError("broken backward/forward relationship")

            following = current
            current = current.prev
            count_backward += 1

            if count_backward > self._size:
                raise AssertionError("cycle detected during backward traversal")

        if following is not self.head:
            raise AssertionError("head does not terminate backward traversal")

        if count_forward != self._size or count_backward != self._size:
            raise AssertionError("stored size does not match node count")

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Generator[str, None, None]:
        yield from self.forward()

    def __reversed__(self) -> Generator[str, None, None]:
        yield from self.backward()

    def __str__(self) -> str:
        if self.is_empty():
            return "HEAD <-> TAIL"

        return "HEAD <-> " + " <-> ".join(self.forward()) + " <-> TAIL"


class BrowserHistory:
    """
    A realistic use case for a doubly linked list.

    Each history entry points to both the previous and next page. Going
    backward follows prev; going forward follows next. Visiting a new page
    after going backward discards the old forward history, which is modeled
    by detaching the remaining nodes from the current position.
    """

    def __init__(self, homepage: str) -> None:
        if not homepage.strip():
            raise ValueError("homepage cannot be empty")

        self.current = Node(homepage)

    def visit(self, url: str) -> None:
        if not url.strip():
            raise ValueError("URL cannot be empty")

        new_page = Node(url, prev=self.current)

        # A new visit invalidates the forward history.
        self.current.next = None
        self.current.next = new_page
        self.current = new_page

    def back(self) -> str:
        if self.current.prev is not None:
            self.current = self.current.prev
        return self.current.value

    def forward(self) -> str:
        if self.current.next is not None:
            self.current = self.current.next
        return self.current.value

    def path_to_current(self) -> list[str]:
        """
        Walk backward, then reverse the collected values.

        This demonstrates that backward pointers can reconstruct the active
        navigation path without restarting from the first page.
        """
        path = []
        current = self.current

        while current is not None:
            path.append(current.value)
            current = current.prev

        path.reverse()
        return path


def show_structure(title: str, linked_list: DoublyLinkedList) -> None:
    print(f"\n{title}")
    print(f"  Size: {linked_list.size}")
    print(f"  Forward:  {linked_list.values_forward()}")
    print(f"  Backward: {linked_list.values_backward()}")
    print(f"  Structure: {linked_list}")
    linked_list.validate()
    print("  Invariants: valid")


def demonstrate_core_operations() -> None:
    print("=== Core doubly linked list operations ===")

    items = DoublyLinkedList(["commit-A", "commit-B", "commit-C"])
    show_structure("Initial list", items)

    items.prepend("commit-0")
    show_structure("After prepend", items)

    items.append("commit-D")
    show_structure("After append", items)

    items.insert_at(2, "security-fix")
    show_structure("After insertion at index 2", items)

    removed = items.remove_at(3)
    print(f"\nRemoved at index 3: {removed}")
    show_structure("After indexed deletion", items)

    print(f"\nSearching for commit-C: {items.find('commit-C') is not None}")
    print(f"Removing commit-B: {items.remove_first('commit-B')}")
    show_structure("After deleting the first matching value", items)

    items.append("release")
    items.append("release")
    removed_count = items.remove_all("release")
    print(f"\nRemoved duplicate release nodes: {removed_count}")
    show_structure("After remove_all", items)


def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases and failure handling ===")

    linked_list = DoublyLinkedList()

    try:
        linked_list.pop_front()
    except IndexError as exc:
        print(f"Empty-list deletion rejected: {exc}")

    try:
        linked_list.remove_at(0)
    except IndexError as exc:
        print(f"Invalid index rejected: {exc}")

    linked_list.append("only-node")
    show_structure("Single-node list", linked_list)

    linked_list.pop_front()
    show_structure("After deleting the only node", linked_list)

    for bad_index in (-1, 0):
        try:
            linked_list.insert_at(bad_index, "value")
        except IndexError as exc:
            print(f"Invalid insertion index {bad_index} rejected: {exc}")


def demonstrate_node_level_o1_deletion() -> None:
    print("\n=== O(1) node unlinking when a node reference is available ===")

    linked_list = DoublyLinkedList(
        ["authentication", "authorization", "logging", "monitoring"]
    )

    logging_node = linked_list.find("logging")
    assert logging_node is not None

    print(f"Before unlink: {linked_list.values_forward()}")
    linked_list.remove_node(logging_node)
    print(f"After unlink:  {linked_list.values_forward()}")
    print(
        "The deletion itself only updates the predecessor and successor "
        "links; finding the node was the O(n) part."
    )

    linked_list.validate()


def demonstrate_browser_history() -> None:
    print("\n=== Browser-history case study ===")

    history = BrowserHistory("https://example.com")

    for page in (
        "https://example.com/products",
        "https://example.com/products/database",
        "https://example.com/docs",
    ):
        history.visit(page)

    print("Current:", history.current.value)
    print("Path:", history.path_to_current())

    print("Back:", history.back())
    print("Back:", history.back())
    print("Forward:", history.forward())

    history.visit("https://example.com/security")
    print("After visiting a new page:", history.current.value)
    print("Path:", history.path_to_current())

    # The old forward page is no longer reachable from the current node.
    print("Forward after new visit:", history.forward())


def demonstrate_comparison() -> None:
    print("\n=== Singly linked versus doubly linked lists ===")

    comparison = {
        "Node links": {
            "singly linked": "next only",
            "doubly linked": "prev and next",
        },
        "Forward traversal": {
            "singly linked": "direct",
            "doubly linked": "direct",
        },
        "Backward traversal": {
            "singly linked": "not direct; normally requires restarting from head",
            "doubly linked": "direct through prev",
        },
        "Known-node deletion": {
            "singly linked": "requires predecessor or a special deletion technique",
            "doubly linked": "direct unlink using prev and next",
        },
        "Per-node memory": {
            "singly linked": "one link",
            "doubly linked": "two links",
        },
        "Pointer maintenance": {
            "singly linked": "simpler",
            "doubly linked": "more complex because both directions must remain consistent",
        },
    }

    for category, values in comparison.items():
        print(f"\n{category}:")
        for implementation, description in values.items():
            print(f"  {implementation}: {description}")


def demonstrate_complexity() -> None:
    print("\n=== Complexity model ===")

    complexity = {
        "prepend": "O(1)",
        "append": "O(1) when tail is maintained",
        "remove first": "O(n) because a search may be necessary",
        "remove known node": "O(1)",
        "find": "O(n)",
        "forward traversal": "O(n)",
        "backward traversal": "O(n)",
        "indexed access": "O(n), starting from the nearer endpoint",
        "insert at known node": "O(1)",
    }

    for operation, cost in complexity.items():
        print(f"{operation:25} {cost}")

    print(
        "\nDoubly linked lists trade additional pointer memory and mutation "
        "complexity for efficient bidirectional navigation and O(1) local "
        "insertion/deletion when the affected node is already known."
    )


def demonstrate_safe_mutation() -> None:
    print("\n=== Safe mutation during traversal ===")

    linked_list = DoublyLinkedList(
        ["keep", "remove", "keep", "remove", "keep"]
    )

    current = linked_list.head

    while current is not None:
        following = current.next

        if current.value == "remove":
            linked_list.remove_node(current)

        current = following

    show_structure("After removing while traversing", linked_list)


def run_self_tests() -> None:
    print("\n=== Self-tests ===")

    linked_list = DoublyLinkedList()
    assert linked_list.is_empty()
    assert len(linked_list) == 0

    linked_list.append("B")
    linked_list.prepend("A")
    linked_list.append("D")
    linked_list.insert_at(2, "C")

    assert linked_list.values_forward() == ["A", "B", "C", "D"]
    assert linked_list.values_backward() == ["D", "C", "B", "A"]

    linked_list.validate()

    assert linked_list.remove_first("B")
    assert linked_list.values_forward() == ["A", "C", "D"]

    assert linked_list.remove_at(1) == "C"
    assert linked_list.values_forward() == ["A", "D"]

    assert linked_list.pop_back() == "D"
    assert linked_list.pop_front() == "A"
    assert linked_list.is_empty()

    history = BrowserHistory("home")
    history.visit("docs")
    history.visit("search")
    assert history.back() == "docs"
    assert history.forward() == "search"

    print("All self-tests passed.")


def main() -> None:
    demonstrate_core_operations()
    demonstrate_edge_cases()
    demonstrate_node_level_o1_deletion()
    demonstrate_browser_history()
    demonstrate_comparison()
    demonstrate_complexity()
    demonstrate_safe_mutation()
    run_self_tests()

    print("\n=== Final note on correctness ===")
    print(
        "The defining invariant of this implementation is that every "
        "adjacent pair agrees in both directions: A.next is B exactly when "
        "B.prev is A. The validate() method checks that relationship after "
        "mutations."
    )


if __name__ == "__main__":
    main()
