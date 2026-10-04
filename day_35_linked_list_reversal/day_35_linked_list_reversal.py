from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Iterator, List, Tuple
import random
import sys


@dataclass
class Node:
    value: int
    next: Optional["Node"] = None


class LinkedList:
    """Singly linked list with iterative, recursive, and group reversal."""

    def __init__(self, values: Iterable[int] = ()) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size = 0
        for value in values:
            self.append(value)

    def append(self, value: int) -> None:
        new_node = Node(value)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def to_list(self) -> List[int]:
        result: List[int] = []
        current = self.head
        seen: set[int] = set()

        # A cycle would make traversal non-terminating, so detect one explicitly.
        while current is not None:
            identity = id(current)
            if identity in seen:
                raise RuntimeError("Cycle detected during traversal")
            seen.add(identity)
            result.append(current.value)
            current = current.next

        return result

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return " -> ".join(map(str, self.to_list())) + " -> None"

    def reverse_iterative(self) -> None:
        """
        Reverse links in-place.

        At every iteration:
        previous -> already reversed prefix
        current  -> first node not yet reversed
        next_node -> saved remainder of the original list

        Time: O(n)
        Extra space: O(1)
        """
        previous: Optional[Node] = None
        current = self.head

        old_head = self.head

        while current is not None:
            next_node = current.next
            current.next = previous
            previous = current
            current = next_node

        self.head = previous
        self.tail = old_head

    @staticmethod
    def _reverse_recursive(
        current: Optional[Node],
        previous: Optional[Node],
    ) -> Optional[Node]:
        """
        Recursive pointer reversal.

        The original next pointer must be saved before redirecting current.next.
        The recursion consumes the original list toward its tail.
        """
        if current is None:
            return previous

        next_node = current.next
        current.next = previous
        return LinkedList._reverse_recursive(next_node, current)

    def reverse_recursive(self) -> None:
        if self.head is None:
            return

        old_head = self.head
        self.head = self._reverse_recursive(self.head, None)
        self.tail = old_head

    def reverse_recursive_classic(self) -> None:
        """
        Alternative recursive formulation.

        The recursive call reverses the suffix. Once it returns, the current
        node is attached after its original successor.
        """

        def reverse(node: Optional[Node]) -> Optional[Node]:
            if node is None or node.next is None:
                return node

            new_head = reverse(node.next)

            assert node.next is not None
            node.next.next = node
            node.next = None

            return new_head

        if self.head is None:
            return

        old_head = self.head
        self.head = reverse(self.head)
        self.tail = old_head

    def reverse_in_groups(self, k: int) -> None:
        """
        Reverse consecutive groups of exactly k nodes.

        The final group is reversed only when it contains k nodes.
        For example:

            1 2 3 4 5 6 7, k=3
            -> 3 2 1 6 5 4 7

        Time: O(n)
        Extra space: O(1)
        """
        if k <= 1 or self.head is None:
            return
        if k > len(self):
            return

        dummy = Node(0, self.head)
        group_previous: Node = dummy

        while True:
            kth = group_previous

            for _ in range(k):
                if kth.next is None:
                    self.head = dummy.next
                    self._refresh_tail()
                    return
                kth = kth.next

            group_next = kth.next

            previous = group_next
            current = group_previous.next

            while current is not group_next:
                assert current is not None
                next_node = current.next
                current.next = previous
                previous = current
                current = next_node

            old_group_head = group_previous.next
            group_previous.next = kth

            assert old_group_head is not None
            group_previous = old_group_head

    def reverse_in_groups_recursive(self, k: int) -> None:
        """
        Recursive k-group reversal.

        Unlike the iterative version, the call stack stores one frame per group.
        The implementation reverses a group only after confirming that k nodes
        exist, so a short final group remains unchanged.
        """
        if k <= 1 or self.head is None:
            return

        def reverse_groups(
            head: Optional[Node],
            group_size: int,
        ) -> Optional[Node]:
            if head is None:
                return None

            probe = head
            for _ in range(group_size):
                if probe is None:
                    return head
                probe = probe.next

            previous: Optional[Node] = None
            current = head

            for _ in range(group_size):
                assert current is not None
                next_node = current.next
                current.next = previous
                previous = current
                current = next_node

            head.next = reverse_groups(current, group_size)
            return previous

        old_head = self.head
        self.head = reverse_groups(self.head, k)
        self.tail = old_head
        self._refresh_tail()

    def _refresh_tail(self) -> None:
        if self.head is None:
            self.tail = None
            return

        current = self.head
        while current.next is not None:
            current = current.next
        self.tail = current

    def validate(self) -> None:
        """Check size, acyclicity, and tail correctness."""
        count = 0
        current = self.head
        visited: set[int] = set()
        last: Optional[Node] = None

        while current is not None:
            identity = id(current)
            if identity in visited:
                raise AssertionError("Linked list contains a cycle")
            visited.add(identity)
            count += 1
            last = current
            current = current.next

        if count != self._size:
            raise AssertionError(
                f"Size mismatch: metadata={self._size}, actual={count}"
            )

        if last is not self.tail:
            raise AssertionError("Tail pointer is inconsistent")

        if self.tail is not None and self.tail.next is not None:
            raise AssertionError("Tail must point to None")


def reverse_array_reference(values: List[int]) -> List[int]:
    """Reference implementation used only to validate linked-list reversal."""
    return list(reversed(values))


def expected_group_reversal(values: List[int], k: int) -> List[int]:
    """Array-based oracle for the linked-list k-group operation."""
    if k <= 1:
        return values.copy()

    result: List[int] = []
    for start in range(0, len(values), k):
        group = values[start:start + k]
        if len(group) == k:
            result.extend(reversed(group))
        else:
            result.extend(group)
    return result


def demonstrate_basic_reversal() -> None:
    print("\n=== Iterative reversal ===")
    linked = LinkedList([10, 20, 30, 40, 50])
    print("Before:", linked)
    linked.reverse_iterative()
    linked.validate()
    print("After: ", linked)

    print("\n=== Recursive reversal ===")
    linked = LinkedList([10, 20, 30, 40, 50])
    print("Before:", linked)
    linked.reverse_recursive()
    linked.validate()
    print("After: ", linked)


def demonstrate_recursive_variants() -> None:
    print("\n=== Comparing recursive formulations ===")

    original = [1, 2, 3, 4, 5, 6]

    first = LinkedList(original)
    first.reverse_recursive()

    second = LinkedList(original)
    second.reverse_recursive_classic()

    expected = reverse_array_reference(original)

    print("Expected:", expected)
    print("Pointer-accumulator recursion:", first.to_list())
    print("Suffix recursion:            ", second.to_list())

    assert first.to_list() == expected
    assert second.to_list() == expected


def demonstrate_group_reversal() -> None:
    print("\n=== Iterative reverse in groups ===")

    for values, k in [
        ([1, 2, 3, 4, 5, 6, 7, 8], 3),
        ([1, 2, 3, 4, 5, 6], 2),
        ([1, 2, 3, 4, 5], 4),
        ([1, 2, 3], 5),
    ]:
        linked = LinkedList(values)
        linked.reverse_in_groups(k)
        linked.validate()

        expected = expected_group_reversal(values, k)

        print(f"{values}, k={k} -> {linked.to_list()}")
        assert linked.to_list() == expected

    print("\n=== Recursive reverse in groups ===")

    values = [1, 2, 3, 4, 5, 6, 7]
    k = 3

    linked = LinkedList(values)
    linked.reverse_in_groups_recursive(k)
    linked.validate()

    print(f"{values}, k={k} -> {linked.to_list()}")
    assert linked.to_list() == expected_group_reversal(values, k)


def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases ===")

    cases: List[Tuple[List[int], int]] = [
        ([], 3),
        ([1], 1),
        ([1], 2),
        ([1, 2], 1),
        ([1, 2, 3], 2),
        ([1, 2, 3, 4], 4),
    ]

    for values, k in cases:
        linked = LinkedList(values)
        linked.reverse_in_groups(k)
        linked.validate()
        print(f"{values}, k={k} -> {linked.to_list()}")

    print("\n=== Invalid k ===")
    for invalid_k in [0, -1]:
        linked = LinkedList([1, 2, 3])
        linked.reverse_in_groups(invalid_k)
        print(f"k={invalid_k}: unchanged -> {linked.to_list()}")


def demonstrate_pointer_invariant() -> None:
    print("\n=== Pointer invariant ===")

    values = [4, 8, 15, 16, 23, 42]
    linked = LinkedList(values)

    previous: Optional[Node] = None
    current = linked.head
    steps = 0

    while current is not None:
        next_node = current.next

        # This is the central operation in iterative reversal:
        # the edge leaving current is redirected toward the reversed prefix.
        current.next = previous

        previous = current
        current = next_node
        steps += 1

    linked.head = previous
    linked.tail = Node(0) if False else None
    linked._refresh_tail()
    linked.validate()

    print("Nodes processed:", steps)
    print("Reversed:", linked.to_list())


def run_property_checks() -> None:
    print("\n=== Randomized correctness checks ===")

    rng = random.Random(20261005)

    for _ in range(250):
        length = rng.randint(0, 30)
        values = [rng.randint(-100, 100) for _ in range(length)]

        iterative = LinkedList(values)
        iterative.reverse_iterative()
        assert iterative.to_list() == list(reversed(values))
        iterative.validate()

        recursive = LinkedList(values)
        recursive.reverse_recursive()
        assert recursive.to_list() == list(reversed(values))
        recursive.validate()

        k = rng.randint(1, 10)
        grouped = LinkedList(values)
        grouped.reverse_in_groups(k)
        assert grouped.to_list() == expected_group_reversal(values, k)
        grouped.validate()

    print("250 randomized cases passed.")


def demonstrate_recursion_limit() -> None:
    print("\n=== Recursion depth consideration ===")

    # Python recursion is not appropriate for extremely long linked lists.
    # The iterative algorithm keeps constant auxiliary memory and does not
    # consume one Python stack frame per node.
    length = min(1000, sys.getrecursionlimit() // 2)
    linked = LinkedList(range(length))
    linked.reverse_iterative()
    linked.validate()
    print(f"Iteratively reversed {length} nodes without recursion.")


def explain_complexity() -> None:
    print("\n=== Complexity ===")
    print("Iterative reversal:        O(n) time, O(1) auxiliary space")
    print("Recursive reversal:        O(n) time, O(n) call-stack space")
    print("Iterative k-group reversal: O(n) time, O(1) auxiliary space")
    print("Recursive k-group reversal: O(n) time, O(n/k) call-stack space")


def main() -> None:
    print("LINKED LIST REVERSAL LAB")
    print("=========================")

    demonstrate_basic_reversal()
    demonstrate_recursive_variants()
    demonstrate_group_reversal()
    demonstrate_edge_cases()
    demonstrate_pointer_invariant()
    run_property_checks()
    demonstrate_recursion_limit()
    explain_complexity()

    print("\nAll demonstrations completed successfully.")


if __name__ == "__main__":
    main()
