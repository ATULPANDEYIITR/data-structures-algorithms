from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable
import random


@dataclass
class ListNode:
    value: int
    next: Optional["ListNode"] = None


@dataclass
class RandomNode:
    value: int
    next: Optional["RandomNode"] = None
    random: Optional["RandomNode"] = None


def build_list(values: Iterable[int]) -> Optional[ListNode]:
    """Build a singly linked list while preserving input order."""
    head = tail = None

    for value in values:
        node = ListNode(value)
        if head is None:
            head = node
        else:
            tail.next = node
        tail = node

    return head


def list_to_values(head: Optional[ListNode], limit: int = 100) -> list[int]:
    """
    Convert a linked list to Python values.

    The limit protects debugging code from accidentally looping forever
    when a malformed cyclic list is supplied.
    """
    values = []
    current = head

    while current is not None and len(values) < limit:
        values.append(current.value)
        current = current.next

    if current is not None:
        values.append("...")
    return values


def print_list(title: str, head: Optional[ListNode]) -> None:
    print(f"{title}: {' -> '.join(map(str, list_to_values(head)))}")


def length(head: Optional[ListNode]) -> int:
    count = 0
    current = head

    while current:
        count += 1
        current = current.next

    return count


def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Reverse links in place.

    Time: O(n)
    Extra space: O(1)
    """
    previous = None
    current = head

    while current:
        following = current.next
        current.next = previous
        previous = current
        current = following

    return previous


def intersection_by_reference(
    head_a: Optional[ListNode],
    head_b: Optional[ListNode],
) -> Optional[ListNode]:
    """
    Find the intersection node of two singly linked lists.

    Intersection means shared node identity, not equal values.

    The two-pointer technique makes both pointers traverse the combined
    lengths, eliminating the need to explicitly calculate lengths.

    Time: O(m + n)
    Extra space: O(1)
    """
    if head_a is None or head_b is None:
        return None

    pointer_a = head_a
    pointer_b = head_b

    while pointer_a is not pointer_b:
        pointer_a = pointer_a.next if pointer_a else head_b
        pointer_b = pointer_b.next if pointer_b else head_a

    return pointer_a


def intersection_using_lengths(
    head_a: Optional[ListNode],
    head_b: Optional[ListNode],
) -> Optional[ListNode]:
    """
    Alternative intersection algorithm.

    The longer list is advanced by the difference in lengths, after which
    both pointers move together.

    Time: O(m + n)
    Extra space: O(1)
    """
    length_a = length(head_a)
    length_b = length(head_b)

    current_a = head_a
    current_b = head_b

    if length_a > length_b:
        for _ in range(length_a - length_b):
            current_a = current_a.next
    elif length_b > length_a:
        for _ in range(length_b - length_a):
            current_b = current_b.next

    while current_a is not current_b:
        current_a = current_a.next
        current_b = current_b.next

    return current_a


def merge_sorted_lists(
    head_a: Optional[ListNode],
    head_b: Optional[ListNode],
) -> Optional[ListNode]:
    """
    Merge two already sorted linked lists by reusing existing nodes.

    No new data nodes are allocated.

    Time: O(m + n)
    Extra space: O(1)
    """
    dummy = ListNode(0)
    tail = dummy

    left = head_a
    right = head_b

    while left and right:
        if left.value <= right.value:
            tail.next = left
            left = left.next
        else:
            tail.next = right
            right = right.next
        tail = tail.next

    tail.next = left if left else right
    return dummy.next


def split_list(head: Optional[ListNode]) -> tuple[Optional[ListNode], Optional[ListNode]]:
    """
    Split a list into two approximately equal halves.

    The slow/fast pointer technique avoids first calculating the length.
    """
    if head is None or head.next is None:
        return head, None

    slow = head
    fast = head.next

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    second = slow.next
    slow.next = None

    return head, second


def merge_sort(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Stable merge sort for a singly linked list.

    Linked lists are particularly suitable for merge sort because merging
    only requires changing links and does not require random access.

    Time: O(n log n)
    Extra algorithmic space: O(log n) recursion stack.
    """
    if head is None or head.next is None:
        return head

    left, right = split_list(head)

    left = merge_sort(left)
    right = merge_sort(right)

    return merge_sorted_lists(left, right)


def partition_list(
    head: Optional[ListNode],
    pivot: int,
) -> Optional[ListNode]:
    """
    Partition a linked list around a pivot.

    Nodes with values below the pivot are placed before nodes whose values
    are greater than or equal to the pivot. Relative order inside both
    groups is preserved.

    This is a stable partition and runs in O(n) time with O(1) auxiliary
    node storage.
    """
    less_dummy = ListNode(0)
    greater_dummy = ListNode(0)

    less_tail = less_dummy
    greater_tail = greater_dummy

    current = head

    while current:
        following = current.next
        current.next = None

        if current.value < pivot:
            less_tail.next = current
            less_tail = current
        else:
            greater_tail.next = current
            greater_tail = current

        current = following

    less_tail.next = greater_dummy.next
    return less_dummy.next


def detect_cycle(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Floyd's tortoise-and-hare algorithm.

    Returns the first node of a cycle when one exists.

    Time: O(n)
    Extra space: O(1)
    """
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            break
    else:
        return None

    slow = head

    while slow is not fast:
        slow = slow.next
        fast = fast.next

    return slow


def copy_random_list(head: Optional[RandomNode]) -> Optional[RandomNode]:
    """
    Deep-copy a linked list where every node has next and random pointers.

    The implementation uses the O(1)-extra-space interleaving technique.

    Phase A:
        Insert the copied node immediately after each original node.

    Phase B:
        Use the interleaved structure to assign copied random pointers.

    Phase C:
        Separate original and copied lists.

    Time: O(n)
    Extra space: O(1), excluding the newly created copy nodes.
    """
    if head is None:
        return None

    current = head

    while current:
        copy = RandomNode(current.value, current.next)
        current.next = copy
        current = copy.next

    current = head

    while current:
        copy = current.next

        if current.random is not None:
            copy.random = current.random.next

        current = copy.next

    copied_head = head.next
    current = head

    while current:
        copy = current.next
        original_next = copy.next

        current.next = original_next
        copy.next = original_next.next if original_next else None

        current = original_next

    return copied_head


def random_list_to_tuples(
    head: Optional[RandomNode],
) -> list[tuple[int, Optional[int]]]:
    """Represent each node as (value, random_target_value) for inspection."""
    result = []
    current = head

    while current:
        result.append((
            current.value,
            current.random.value if current.random else None,
        ))
        current = current.next

    return result


def build_random_example() -> Optional[RandomNode]:
    """
    Create a random-pointer list with deliberately nontrivial references.

    Random pointers can point forward, backward, to themselves, or nowhere.
    """
    nodes = [RandomNode(value) for value in [7, 13, 11, 10, 1]]

    for left, right in zip(nodes, nodes[1:]):
        left.next = right

    nodes[0].random = None
    nodes[1].random = nodes[0]
    nodes[2].random = nodes[4]
    nodes[3].random = nodes[2]
    nodes[4].random = nodes[4]

    return nodes[0]


def flatten_multilevel_list(head: Optional["MultiNode"]) -> Optional["MultiNode"]:
    """
    Flatten a multilevel doubly linked list.

    Each node can have next and child. The child list is inserted immediately
    after the node, and its tail is connected to the original next node.

    An explicit stack avoids recursion-depth problems.

    Time: O(n)
    Extra space: O(h), where h is the nesting depth.
    """
    if head is None:
        return None

    stack = [head]
    previous = None

    while stack:
        current = stack.pop()

        if previous:
            previous.next = current
            current.prev = previous

        if current.next:
            stack.append(current.next)

        if current.child:
            stack.append(current.child)
            current.child = None

        previous = current

    return head


@dataclass
class MultiNode:
    value: int
    prev: Optional["MultiNode"] = None
    next: Optional["MultiNode"] = None
    child: Optional["MultiNode"] = None


def build_multilevel_example() -> Optional[MultiNode]:
    """
    Build:

        1 - 2 - 3 - 4
            |
            5 - 6
                |
                7

    The flattened order should be 1, 2, 5, 6, 7, 3, 4.
    """
    nodes = {i: MultiNode(i) for i in range(1, 8)}

    for a, b in [(1, 2), (2, 3), (3, 4)]:
        nodes[a].next = nodes[b]
        nodes[b].prev = nodes[a]

    nodes[2].child = nodes[5]

    nodes[5].next = nodes[6]
    nodes[6].prev = nodes[5]

    nodes[6].child = nodes[7]

    return nodes[1]


def multi_values(head: Optional[MultiNode]) -> list[int]:
    values = []
    current = head

    while current:
        values.append(current.value)
        current = current.next

    return values


def reverse_k_group(
    head: Optional[ListNode],
    k: int,
) -> Optional[ListNode]:
    """
    Reverse nodes in groups of k.

    A final group smaller than k remains unchanged.

    This demonstrates careful pointer manipulation after the core list
    algorithms have been established.

    Time: O(n)
    Extra space: O(1)
    """
    if k <= 1 or head is None:
        return head

    dummy = ListNode(0, head)
    group_previous = dummy

    while True:
        kth = group_previous

        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next

        group_next = kth.next

        previous = group_next
        current = group_previous.next

        while current is not group_next:
            following = current.next
            current.next = previous
            previous = current
            current = following

        old_group_head = group_previous.next
        group_previous.next = kth
        group_previous = old_group_head


def assert_no_cycle(head: Optional[ListNode]) -> None:
    if detect_cycle(head) is not None:
        raise AssertionError("Expected an acyclic linked list")


def demonstrate_intersection() -> None:
    shared = build_list([8, 10, 12])

    first = build_list([3, 7])
    second = build_list([99, 1, 5])

    tail = first
    while tail.next:
        tail = tail.next
    tail.next = shared

    tail = second
    while tail.next:
        tail = tail.next
    tail.next = shared

    result = intersection_by_reference(first, second)

    print("Intersection by node identity:")
    print(f"  value={result.value if result else None}")
    print(f"  same object as shared={result is shared}")

    result_by_length = intersection_using_lengths(first, second)
    print(f"Length-alignment result={result_by_length.value if result_by_length else None}")


def demonstrate_sorting_and_merging() -> None:
    unsorted = build_list([7, 2, 9, 1, 5, 2, 8, 3])
    print_list("Before merge sort", unsorted)

    sorted_head = merge_sort(unsorted)
    print_list("After merge sort", sorted_head)

    left = build_list([1, 4, 7, 10])
    right = build_list([2, 3, 8, 9])

    merged = merge_sorted_lists(left, right)
    print_list("Merged sorted lists", merged)


def demonstrate_partitioning() -> None:
    data = build_list([1, 4, 3, 2, 5, 2])
    partitioned = partition_list(data, 3)

    print_list("Stable partition around 3", partitioned)


def demonstrate_random_copy() -> None:
    original = build_random_example()
    copied = copy_random_list(original)

    print("Random-pointer original:")
    print(f"  {random_list_to_tuples(original)}")

    print("Random-pointer deep copy:")
    print(f"  {random_list_to_tuples(copied)}")

    assert original is not copied
    assert random_list_to_tuples(original) == random_list_to_tuples(copied)

    original.value = 700
    assert copied.value == 7
    print("  Deep-copy independence verified.")


def demonstrate_flattening() -> None:
    multilevel = build_multilevel_example()

    print(f"Multilevel flattened order: {multi_values(flatten_multilevel_list(multilevel))}")


def demonstrate_edge_cases() -> None:
    print("Edge cases:")

    empty = None
    singleton = build_list([42])

    print(f"  Empty intersection: {intersection_by_reference(empty, singleton)}")
    print(f"  Singleton reverse: {list_to_values(reverse_list(singleton))}")

    empty_sort = merge_sort(None)
    print(f"  Empty merge sort: {empty_sort}")

    one = build_list([10])
    print(f"  Partition singleton: {list_to_values(partition_list(one, 10))}")

    k_group = build_list([1, 2, 3, 4, 5])
    print(f"  k=3 reversal: {list_to_values(reverse_k_group(k_group, 3))}")

    try:
        reverse_k_group(build_list([1, 2]), 0)
        print("  Invalid k handled by leaving the list unchanged.")
    except ValueError:
        print("  Invalid k rejected.")


def run_small_random_sort_check() -> None:
    """
    A lightweight property-style check.

    Each generated linked list is sorted and compared with Python's sorted()
    result. This is useful for catching pointer mistakes in merge sort.
    """
    rng = random.Random(42)

    for _ in range(100):
        values = [rng.randint(-20, 20) for _ in range(rng.randint(0, 20))]
        head = merge_sort(build_list(values))
        actual = list_to_values(head)

        if actual != sorted(values):
            raise AssertionError(
                f"Merge sort mismatch: expected {sorted(values)}, got {actual}"
            )

    print("Merge-sort randomized verification: passed 100 cases.")


def main() -> None:
    print("=== Advanced Linked List Algorithms ===\n")

    demonstrate_intersection()
    print()

    demonstrate_sorting_and_merging()
    print()

    demonstrate_partitioning()
    print()

    demonstrate_random_copy()
    print()

    demonstrate_flattening()
    print()

    demonstrate_edge_cases()
    print()

    run_small_random_sort_check()
    print()

    advanced = build_list([1, 2, 3, 4, 5, 6, 7])
    advanced = reverse_k_group(advanced, 3)
    print_list("Reverse every group of three", advanced)

    print("\nAll demonstrations completed successfully.")


if __name__ == "__main__":
    main()
