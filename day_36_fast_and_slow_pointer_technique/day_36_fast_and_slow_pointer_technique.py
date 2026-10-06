from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable, List, Tuple, Dict, Set
import random
import time


# Fast and Slow Pointer Technique
# --------------------------------
# The technique uses two references that move through a sequence at different
# speeds. The most common configuration moves slow by one step and fast by two.
#
# The key advantage is that the algorithm often solves a problem in O(n) time
# with O(1) auxiliary space, without first computing the length of a linked
# list or storing every visited node.


@dataclass
class ListNode:
    value: int
    next: Optional["ListNode"] = None


def build_linked_list(values: Iterable[int]) -> Optional[ListNode]:
    """Build a normal singly linked list from an iterable."""
    iterator = iter(values)

    try:
        first_value = next(iterator)
    except StopIteration:
        return None

    head = ListNode(first_value)
    tail = head

    for value in iterator:
        tail.next = ListNode(value)
        tail = tail.next

    return head


def linked_list_to_string(head: Optional[ListNode], limit: int = 50) -> str:
    """
    Convert a linked list to a readable representation.

    A limit protects this debugging helper from looping forever when the
    supplied list contains a cycle.
    """
    values = []
    current = head
    seen: Set[int] = set()

    while current is not None and len(values) < limit:
        identity = id(current)

        if identity in seen:
            values.append(f"cycle->{current.value}")
            break

        seen.add(identity)
        values.append(str(current.value))
        current = current.next

    if current is not None and len(values) == limit:
        values.append("...")

    return " -> ".join(values)


def middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Return the middle node using the fast and slow pointer technique.

    For an even-length list this implementation returns the second middle:
        1 -> 2 -> 3 -> 4
                    ^ slow
    """
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

    return slow


def first_middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Return the first middle node for an even-length list.

    The loop stops one step earlier than the usual second-middle algorithm.
    """
    if head is None:
        return None

    slow = head
    fast = head.next

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

    return slow


def has_cycle(head: Optional[ListNode]) -> bool:
    """Detect a cycle with Floyd's tortoise-and-hare algorithm."""
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            return True

    return False


def cycle_meeting_node(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Return the node where Floyd's two pointers first meet.

    A meeting proves that a cycle exists, but the meeting node is not
    necessarily the first node of the cycle.
    """
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            return slow

    return None


def cycle_entry_node(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    Find the first node belonging to a cycle.

    After slow and fast meet:
        - reset one pointer to the head
        - move both one node at a time
        - their next meeting point is the cycle entry
    """
    meeting = cycle_meeting_node(head)

    if meeting is None:
        return None

    pointer_from_head = head
    pointer_from_cycle = meeting

    while pointer_from_head is not pointer_from_cycle:
        pointer_from_head = pointer_from_head.next
        pointer_from_cycle = pointer_from_cycle.next

    return pointer_from_head


def cycle_length(head: Optional[ListNode]) -> int:
    """Return the length of the cycle, or zero when no cycle exists."""
    meeting = cycle_meeting_node(head)

    if meeting is None:
        return 0

    length = 1
    current = meeting.next

    while current is not meeting:
        current = current.next
        length += 1

    return length


def distance_to_cycle_entry(head: Optional[ListNode]) -> int:
    """Return the number of edges from head to the cycle entry."""
    entry = cycle_entry_node(head)

    if entry is None:
        return -1

    distance = 0
    current = head

    while current is not entry:
        current = current.next
        distance += 1

    return distance


def remove_cycle(head: Optional[ListNode]) -> bool:
    """
    Remove a cycle in-place.

    Returns True when a cycle was removed and False when the list was already
    acyclic.

    Once the entry node is known, walk around the cycle until the node whose
    next reference points back to the entry is found.
    """
    entry = cycle_entry_node(head)

    if entry is None:
        return False

    tail_of_cycle = entry

    while tail_of_cycle.next is not entry:
        tail_of_cycle = tail_of_cycle.next

    tail_of_cycle.next = None
    return True


def cycle_entry_with_cycle_size(
    head: Optional[ListNode],
) -> Tuple[Optional[ListNode], int, int]:
    """
    Return:
        (cycle entry, distance from head to entry, cycle length)
    """
    entry = cycle_entry_node(head)

    if entry is None:
        return None, -1, 0

    distance = 0
    current = head

    while current is not entry:
        current = current.next
        distance += 1

    length = 1
    current = entry.next

    while current is not entry:
        current = current.next
        length += 1

    return entry, distance, length


def nth_from_end(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    """
    Find the nth node from the end using a fixed gap between two pointers.

    n=1 means the final node.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    fast = head

    for _ in range(n):
        if fast is None:
            return None
        fast = fast.next

    slow = head

    while fast is not None:
        slow = slow.next
        fast = fast.next

    return slow


def remove_nth_from_end(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    """Remove the nth node from the end using a dummy node and two pointers."""
    if n <= 0:
        raise ValueError("n must be positive")

    dummy = ListNode(0, head)
    fast = dummy

    for _ in range(n):
        if fast.next is None:
            return head
        fast = fast.next

    slow = dummy

    while fast.next is not None:
        slow = slow.next
        fast = fast.next

    if slow.next is not None:
        slow.next = slow.next.next

    return dummy.next


def is_palindrome(head: Optional[ListNode]) -> bool:
    """
    Determine whether a singly linked list is a palindrome.

    The list is split at its midpoint, the second half is reversed, and the
    two halves are compared. This achieves O(n) time and O(1) extra space.

    The second half is restored before returning so the operation is
    non-destructive.
    """
    if head is None or head.next is None:
        return True

    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

    second_half = reverse_list(slow)
    comparison = second_half
    first_half = head
    result = True

    while comparison is not None:
        if first_half.value != comparison.value:
            result = False
            break

        first_half = first_half.next
        comparison = comparison.next

    reverse_list(second_half)
    return result


def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """Reverse a singly linked list iteratively."""
    previous = None
    current = head

    while current is not None:
        following = current.next
        current.next = previous
        previous = current
        current = following

    return previous


def intersection_node(
    head_a: Optional[ListNode],
    head_b: Optional[ListNode],
) -> Optional[ListNode]:
    """
    Find the first physically shared node between two singly linked lists.

    Pointer switching causes both pointers to travel the same total distance:
        A + nonshared(B) + shared
        B + nonshared(A) + shared
    """
    pointer_a = head_a
    pointer_b = head_b

    while pointer_a is not pointer_b:
        pointer_a = head_b if pointer_a is None else pointer_a.next
        pointer_b = head_a if pointer_b is None else pointer_b.next

    return pointer_a


def find_duplicate_floyd(values: List[int]) -> int:
    """
    Find the duplicate in an array containing n+1 integers from 1..n.

    The array can be interpreted as a functional graph:
        index -> values[index]

    A duplicate creates a cycle. Floyd's algorithm finds the cycle entry,
    which corresponds to the duplicated value.

    The input validation makes the mathematical assumptions explicit.
    """
    n = len(values) - 1

    if n < 1:
        raise ValueError("At least two values are required")

    if any(value < 1 or value > n for value in values):
        raise ValueError("Every value must be in the range 1..n")

    slow = values[0]
    fast = values[values[0]]

    while slow != fast:
        slow = values[slow]
        fast = values[values[fast]]

    finder = 0

    while finder != slow:
        finder = values[finder]
        slow = values[slow]

    return finder


def build_cyclic_list(values: List[int], entry_index: int) -> Optional[ListNode]:
    """Build a linked list whose final node points to entry_index."""
    if not values:
        return None

    if not 0 <= entry_index < len(values):
        raise ValueError("entry_index is outside the list")

    nodes = [ListNode(value) for value in values]

    for index in range(len(nodes) - 1):
        nodes[index].next = nodes[index + 1]

    nodes[-1].next = nodes[entry_index]
    return nodes[0]


def demonstrate_middle_finding() -> None:
    print("\nMIDDLE ELEMENT FINDING")

    for values in ([10], [10, 20], [10, 20, 30], [10, 20, 30, 40], [10, 20, 30, 40, 50]):
        head = build_linked_list(values)
        second = middle_node(head)
        first = first_middle_node(head)

        print(
            f"{values} -> second-middle={second.value if second else None}, "
            f"first-middle={first.value if first else None}"
        )


def demonstrate_cycle_detection_and_removal() -> None:
    print("\nCYCLE DETECTION AND REMOVAL")

    head = build_cyclic_list([10, 20, 30, 40, 50, 60], 2)

    print("Cycle exists:", has_cycle(head))

    meeting = cycle_meeting_node(head)
    entry, distance, length = cycle_entry_with_cycle_size(head)

    print("Meeting node:", meeting.value if meeting else None)
    print("Cycle entry:", entry.value if entry else None)
    print("Distance to entry:", distance)
    print("Cycle length:", length)

    removed = remove_cycle(head)

    print("Cycle removed:", removed)
    print("Cycle exists after removal:", has_cycle(head))
    print("Linear list:", linked_list_to_string(head))


def demonstrate_gap_based_search() -> None:
    print("\nFIXED-GAP FAST/SLOW POINTER")

    head = build_linked_list([11, 22, 33, 44, 55, 66, 77])

    for n in [1, 3, 7, 8]:
        node = nth_from_end(head, n)
        print(f"{n}th from end:", node.value if node else None)

    updated = remove_nth_from_end(head, 3)
    print("After removing third from end:", linked_list_to_string(updated))


def demonstrate_palindrome() -> None:
    print("\nPALINDROME DETECTION")

    for values in (
        [1, 2, 3, 2, 1],
        [1, 2, 2, 1],
        [1, 2, 3, 4],
        [7],
        [],
    ):
        head = build_linked_list(values)
        print(f"{values} -> {is_palindrome(head)}")


def demonstrate_intersection() -> None:
    print("\nLIST INTERSECTION")

    shared = build_linked_list([100, 200, 300])

    head_a = build_linked_list([1, 2])
    tail_a = head_a
    while tail_a.next is not None:
        tail_a = tail_a.next
    tail_a.next = shared

    head_b = build_linked_list([7, 8, 9])
    tail_b = head_b
    while tail_b.next is not None:
        tail_b = tail_b.next
    tail_b.next = shared

    result = intersection_node(head_a, head_b)
    print("Intersection node:", result.value if result else None)


def demonstrate_duplicate_detection() -> None:
    print("\nDUPLICATE DETECTION AS A FUNCTIONAL GRAPH")

    examples = [
        [1, 3, 4, 2, 2],
        [3, 1, 3, 4, 2],
        [1, 1],
        [2, 2, 2, 2, 2],
    ]

    for values in examples:
        print(f"{values} -> duplicate={find_duplicate_floyd(values)}")


def benchmark_constant_space_cycle_detection() -> None:
    """
    Demonstrate that the cycle detector does not need a visited set.

    The benchmark is intentionally modest so the script remains practical on
    ordinary machines. Timing varies with hardware and Python runtime.
    """
    print("\nCYCLE DETECTION PERFORMANCE DEMONSTRATION")

    size = 100_000
    head = build_cyclic_list(list(range(size)), size // 2)

    start = time.perf_counter()
    result = has_cycle(head)
    elapsed = time.perf_counter() - start

    print(f"Nodes: {size}")
    print(f"Cycle detected: {result}")
    print(f"Elapsed time: {elapsed:.6f} seconds")
    print("Auxiliary pointer state remains O(1).")


def explain_invariants_in_runtime() -> None:
    """
    Show the movement rule directly.

    For a non-cyclic list, fast reaches the end first.
    For a cyclic list, the relative speed of the two pointers eventually
    forces them to occupy the same node.
    """
    print("\nPOINTER MOVEMENT")

    head = build_linked_list([5, 10, 15, 20, 25, 30])
    slow = head
    fast = head
    step = 0

    while fast is not None and fast.next is not None:
        step += 1
        slow = slow.next
        fast = fast.next.next

        print(
            f"step={step}: "
            f"slow={slow.value if slow else None}, "
            f"fast={fast.value if fast else None}"
        )


def test_core_behaviors() -> None:
    """Small executable checks covering important edge cases."""
    assert middle_node(None) is None
    assert middle_node(build_linked_list([1])).value == 1
    assert middle_node(build_linked_list([1, 2])).value == 2
    assert middle_node(build_linked_list([1, 2, 3, 4])).value == 3

    assert not has_cycle(None)

    linear = build_linked_list([1, 2, 3])
    assert not has_cycle(linear)
    assert cycle_entry_node(linear) is None

    cyclic = build_cyclic_list([1, 2, 3, 4], 1)
    assert has_cycle(cyclic)
    assert cycle_entry_node(cyclic).value == 2
    assert cycle_length(cyclic) == 3
    assert distance_to_cycle_entry(cyclic) == 1

    assert remove_cycle(cyclic)
    assert not has_cycle(cyclic)
    assert not remove_cycle(cyclic)

    assert find_duplicate_floyd([1, 3, 4, 2, 2]) == 2
    assert find_duplicate_floyd([3, 1, 3, 4, 2]) == 3

    assert nth_from_end(build_linked_list([1, 2, 3]), 1).value == 3
    assert nth_from_end(build_linked_list([1, 2, 3]), 3).value == 1
    assert nth_from_end(build_linked_list([1, 2, 3]), 4) is None

    assert is_palindrome(build_linked_list([1, 2, 3, 2, 1]))
    assert is_palindrome(build_linked_list([1, 2, 2, 1]))
    assert not is_palindrome(build_linked_list([1, 2, 3]))

    updated = remove_nth_from_end(build_linked_list([1, 2, 3]), 3)
    assert linked_list_to_string(updated) == "2 -> 3"

    print("\nALL CORE TESTS PASSED")


def main() -> None:
    print("FAST AND SLOW POINTER TECHNIQUE")
    print("=" * 60)

    demonstrate_middle_finding()
    demonstrate_cycle_detection_and_removal()
    demonstrate_gap_based_search()
    demonstrate_palindrome()
    demonstrate_intersection()
    demonstrate_duplicate_detection()
    explain_invariants_in_runtime()
    test_core_behaviors()
    benchmark_constant_space_cycle_detection()

    print("\nKEY COMPLEXITY PROPERTIES")
    print("Middle finding: O(n) time, O(1) auxiliary space")
    print("Cycle detection: O(n) time, O(1) auxiliary space")
    print("Cycle entry: O(n) time, O(1) auxiliary space")
    print("Cycle removal: O(n) time, O(1) auxiliary space")
    print("Nth from end: O(n) time, O(1) auxiliary space")
    print("Palindrome check: O(n) time, O(1) auxiliary space")
    print("Array duplicate detection: O(n) time, O(1) auxiliary space")


if __name__ == "__main__":
    main()
