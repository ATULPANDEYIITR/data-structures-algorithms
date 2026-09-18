"""
Two Pointer Technique
=====================

A standalone study file covering the two-pointer technique from beginner
concepts through advanced applications.

The examples intentionally use only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def explain_two_pointers() -> None:
    """Print the core idea without requiring any external material."""
    print(
        """
TWO POINTER TECHNIQUE

Two pointers are two positions used to traverse or manipulate a sequence.

Common forms:
1. Opposite-direction pointers:
       left  ->    <- right

2. Same-direction pointers:
       slow -> fast ->

3. Sliding-window pointers:
       left -> [window] <- right

The technique is especially useful when:
- an array is sorted,
- a problem concerns pairs,
- a sequence must be reversed,
- elements must be partitioned,
- duplicates must be removed,
- a contiguous range must be maintained.

The key idea is not merely "use two variables".
The important part is designing a rule that lets one or both pointers
move without reconsidering discarded positions.
"""
    )


# ============================================================================
# 2. SIMPLE OPPOSITE-DIRECTION TRAVERSAL
# ============================================================================

def reverse_in_place(values: list[int]) -> None:
    """
    Reverse a list in place.

    Time: O(n)
    Extra space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left < right:
        values[left], values[right] = values[right], values[left]
        left += 1
        right -= 1


def is_palindrome(text: str) -> bool:
    """
    Determine whether a string is a palindrome using two pointers.

    Punctuation and case are ignored in this educational example.
    """
    cleaned = "".join(character.lower() for character in text if character.isalnum())

    left = 0
    right = len(cleaned) - 1

    while left < right:
        if cleaned[left] != cleaned[right]:
            return False
        left += 1
        right -= 1

    return True


def demonstrate_basic_two_pointers() -> None:
    values = [1, 2, 3, 4, 5]
    print("Original:", values)
    reverse_in_place(values)
    print("Reversed:", values)

    examples = [
        "level",
        "A man, a plan, a canal: Panama",
        "python",
    ]

    for text in examples:
        print(f"Palindrome? {text!r}: {is_palindrome(text)}")


# ============================================================================
# 3. SORTED ARRAY + TARGET SUM
# ============================================================================

def two_sum_sorted(values: Sequence[int], target: int) -> tuple[int, int] | None:
    """
    Find two values in a sorted sequence whose sum equals target.

    Returns their indices.

    Why the pointer movement works:
    - If values[left] + values[right] is too small, increasing left is the
      only useful direction because the sequence is sorted.
    - If the sum is too large, decreasing right is the only useful direction.

    Time: O(n)
    Extra space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left < right:
        current_sum = values[left] + values[right]

        if current_sum == target:
            return left, right

        if current_sum < target:
            left += 1
        else:
            right -= 1

    return None


def two_sum_sorted_all_pairs(
    values: Sequence[int], target: int
) -> list[tuple[int, int]]:
    """
    Return every distinct value-pair whose sum equals target.

    This version skips duplicate values.

    Example:
        [1, 1, 2, 3, 3], target=4
        -> [(1, 3)]
    """
    left = 0
    right = len(values) - 1
    pairs: list[tuple[int, int]] = []

    while left < right:
        current_sum = values[left] + values[right]

        if current_sum == target:
            pairs.append((values[left], values[right]))

            left_value = values[left]
            right_value = values[right]

            while left < right and values[left] == left_value:
                left += 1

            while left < right and values[right] == right_value:
                right -= 1

        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return pairs


def demonstrate_sorted_pair_search() -> None:
    values = [1, 2, 4, 7, 9, 12, 15]
    target = 16

    result = two_sum_sorted(values, target)
    print("\nSorted pair search")
    print("Values:", values)
    print("Target:", target)
    print("Indices:", result)

    if result is not None:
        first, second = result
        print("Pair:", values[first], values[second])

    duplicate_values = [1, 1, 2, 2, 3, 3, 4, 4]
    print(
        "Distinct pairs:",
        two_sum_sorted_all_pairs(duplicate_values, 5),
    )


# ============================================================================
# 4. UNSORTED TWO-SUM COMPARISON
# ============================================================================

def two_sum_hash(values: Sequence[int], target: int) -> tuple[int, int] | None:
    """
    Two Sum for an unsorted sequence using a hash table.

    Time: O(n) average
    Extra space: O(n)

    This demonstrates an important trade-off:
    two pointers are excellent for sorted data, but hashing is often better
    when the input is unsorted and reordering is undesirable.
    """
    seen: dict[int, int] = {}

    for index, value in enumerate(values):
        complement = target - value

        if complement in seen:
            return seen[complement], index

        seen[value] = index

    return None


def two_sum_by_sorting(
    values: Sequence[int], target: int
) -> tuple[int, int] | None:
    """
    Solve Two Sum by sorting value/index pairs first.

    Time: O(n log n)
    Extra space: O(n)

    Sorting destroys the original ordering unless indices are preserved.
    """
    indexed = sorted((value, index) for index, value in enumerate(values))

    left = 0
    right = len(indexed) - 1

    while left < right:
        current_sum = indexed[left][0] + indexed[right][0]

        if current_sum == target:
            return indexed[left][1], indexed[right][1]

        if current_sum < target:
            left += 1
        else:
            right -= 1

    return None


def demonstrate_strategy_comparison() -> None:
    values = [11, 3, 7, 2, 9, 14]
    target = 16

    print("\nUnsorted Two Sum")
    print("Hash table:", two_sum_hash(values, target))
    print("Sort + two pointers:", two_sum_by_sorting(values, target))


# ============================================================================
# 5. REMOVE DUPLICATES FROM A SORTED ARRAY
# ============================================================================

def remove_duplicates_sorted(values: list[int]) -> int:
    """
    Remove duplicates in place from a sorted list.

    The first `unique_count` positions contain the unique values.

    This is the classic slow/fast pointer pattern.

    slow points to the location where the next unique value belongs.
    fast scans every element.

    Time: O(n)
    Extra space: O(1)
    """
    if not values:
        return 0

    slow = 1

    for fast in range(1, len(values)):
        if values[fast] != values[slow - 1]:
            values[slow] = values[fast]
            slow += 1

    return slow


def demonstrate_duplicate_removal() -> None:
    values = [1, 1, 2, 2, 2, 3, 4, 4, 5]
    length = remove_duplicates_sorted(values)

    print("\nRemove duplicates")
    print("Unique length:", length)
    print("Unique prefix:", values[:length])


# ============================================================================
# 6. MOVE ZEROES
# ============================================================================

def move_zeroes(values: list[int]) -> None:
    """
    Move zeroes to the end while preserving non-zero relative order.

    slow marks the next position where a non-zero value should be placed.
    fast scans the complete array.

    Time: O(n)
    Extra space: O(1)
    """
    slow = 0

    for fast in range(len(values)):
        if values[fast] != 0:
            values[slow], values[fast] = values[fast], values[slow]
            slow += 1


# ============================================================================
# 7. PARTITIONING
# ============================================================================

def partition_by_pivot(values: list[int], pivot: int) -> int:
    """
    Partition values so elements less than pivot appear before elements
    greater than or equal to pivot.

    The function does not promise stable ordering.

    Returns the boundary index.

    Time: O(n)
    Extra space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        while left <= right and values[left] < pivot:
            left += 1

        while left <= right and values[right] >= pivot:
            right -= 1

        if left <= right:
            values[left], values[right] = values[right], values[left]
            left += 1
            right -= 1

    return left


def dutch_national_flag(values: list[int]) -> None:
    """
    Three-way partition for a list containing only 0, 1, and 2.

    Regions:
        [0 ... low-1]       -> 0
        [low ... mid-1]     -> 1
        [mid ... high]      -> unknown
        [high+1 ... end]    -> 2

    Time: O(n)
    Extra space: O(1)
    """
    low = 0
    mid = 0
    high = len(values) - 1

    while mid <= high:
        if values[mid] == 0:
            values[low], values[mid] = values[mid], values[low]
            low += 1
            mid += 1

        elif values[mid] == 1:
            mid += 1

        elif values[mid] == 2:
            values[mid], values[high] = values[high], values[mid]
            high -= 1

        else:
            raise ValueError("Dutch National Flag input must contain only 0, 1, and 2.")


# ============================================================================
# 8. THREE-SUM
# ============================================================================

def three_sum(values: Sequence[int], target: int) -> list[tuple[int, int, int]]:
    """
    Return unique triples whose values sum to target.

    Strategy:
    1. Sort.
    2. Fix one value.
    3. Solve the remaining two-sum problem with two pointers.
    4. Skip duplicates.

    Time: O(n^2)
    Extra space: O(n) for the sorted copy and output.
    """
    numbers = sorted(values)
    triples: list[tuple[int, int, int]] = []

    for index in range(len(numbers) - 2):
        if index > 0 and numbers[index] == numbers[index - 1]:
            continue

        left = index + 1
        right = len(numbers) - 1

        while left < right:
            current_sum = numbers[index] + numbers[left] + numbers[right]

            if current_sum == target:
                triples.append(
                    (numbers[index], numbers[left], numbers[right])
                )

                left_value = numbers[left]
                right_value = numbers[right]

                while left < right and numbers[left] == left_value:
                    left += 1

                while left < right and numbers[right] == right_value:
                    right -= 1

            elif current_sum < target:
                left += 1
            else:
                right -= 1

    return triples


# ============================================================================
# 9. FOUR-SUM
# ============================================================================

def four_sum(
    values: Sequence[int], target: int
) -> list[tuple[int, int, int, int]]:
    """
    Generalize the two-pointer idea to four values.

    Two values are fixed, and two pointers solve the remaining pair.

    Time: O(n^3)
    Extra space: O(n) for sorting/output.
    """
    numbers = sorted(values)
    results: list[tuple[int, int, int, int]] = []
    n = len(numbers)

    for first in range(n - 3):
        if first > 0 and numbers[first] == numbers[first - 1]:
            continue

        for second in range(first + 1, n - 2):
            if second > first + 1 and numbers[second] == numbers[second - 1]:
                continue

            left = second + 1
            right = n - 1

            while left < right:
                current_sum = (
                    numbers[first]
                    + numbers[second]
                    + numbers[left]
                    + numbers[right]
                )

                if current_sum == target:
                    results.append(
                        (
                            numbers[first],
                            numbers[second],
                            numbers[left],
                            numbers[right],
                        )
                    )

                    left_value = numbers[left]
                    right_value = numbers[right]

                    while left < right and numbers[left] == left_value:
                        left += 1

                    while left < right and numbers[right] == right_value:
                        right -= 1

                elif current_sum < target:
                    left += 1
                else:
                    right -= 1

    return results


# ============================================================================
# 10. CONTAINER WITH MOST WATER
# ============================================================================

def max_container_area(heights: Sequence[int]) -> int:
    """
    Find the maximum area formed by two vertical lines.

    Area = min(height[left], height[right]) * (right - left)

    The shorter line limits the area. Moving the taller line inward cannot
    improve the limiting height, so the shorter side must be moved.

    Time: O(n)
    Extra space: O(1)
    """
    if len(heights) < 2:
        return 0

    left = 0
    right = len(heights) - 1
    best_area = 0

    while left < right:
        width = right - left
        limiting_height = min(heights[left], heights[right])
        best_area = max(best_area, width * limiting_height)

        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1

    return best_area


# ============================================================================
# 11. SORTED SQUARES
# ============================================================================

def sorted_squares(values: Sequence[int]) -> list[int]:
    """
    Return squares in sorted order when the input is already sorted.

    Negative values can have large absolute values, so compare absolute
    magnitudes at both ends.

    Time: O(n)
    Extra space: O(n) for the result.
    """
    result = [0] * len(values)
    left = 0
    right = len(values) - 1
    write = len(values) - 1

    while left <= right:
        left_square = values[left] * values[left]
        right_square = values[right] * values[right]

        if left_square > right_square:
            result[write] = left_square
            left += 1
        else:
            result[write] = right_square
            right -= 1

        write -= 1

    return result


# ============================================================================
# 12. MERGING TWO SORTED ARRAYS
# ============================================================================

def merge_sorted_arrays(
    first: Sequence[int], second: Sequence[int]
) -> list[int]:
    """
    Merge two sorted sequences.

    This is the same fundamental pointer principle used in merge sort.

    Time: O(n + m)
    Extra space: O(n + m)
    """
    left = 0
    right = 0
    merged: list[int] = []

    while left < len(first) and right < len(second):
        if first[left] <= second[right]:
            merged.append(first[left])
            left += 1
        else:
            merged.append(second[right])
            right += 1

    merged.extend(first[left:])
    merged.extend(second[right:])

    return merged


# ============================================================================
# 13. INTERSECTION OF SORTED ARRAYS
# ============================================================================

def intersection_sorted(
    first: Sequence[int], second: Sequence[int]
) -> list[int]:
    """Return distinct values present in both sorted sequences."""
    left = 0
    right = 0
    result: list[int] = []

    while left < len(first) and right < len(second):
        if first[left] == second[right]:
            if not result or result[-1] != first[left]:
                result.append(first[left])
            left += 1
            right += 1

        elif first[left] < second[right]:
            left += 1

        else:
            right += 1

    return result


# ============================================================================
# 14. STRING COMPRESSION WITH TWO POINTERS
# ============================================================================

def compress_runs(text: str) -> str:
    """
    Run-length encode consecutive characters.

    Example:
        aaabbc -> a3b2c1

    The read pointer finds a run.
    The write operation records the run's character and length.
    """
    if not text:
        return ""

    result: list[str] = []
    read = 0

    while read < len(text):
        run_start = read
        current = text[read]

        while read < len(text) and text[read] == current:
            read += 1

        result.append(current)
        result.append(str(read - run_start))

    return "".join(result)


# ============================================================================
# 15. SLIDING WINDOW: A RELATED TWO-POINTER PATTERN
# ============================================================================

def longest_substring_without_repeating(text: str) -> int:
    """
    Find the length of the longest substring without repeated characters.

    This is a two-pointer sliding-window algorithm.

    right expands the window.
    left contracts it until the invariant is restored.

    Time: O(n)
    Extra space: O(k), where k is the number of distinct characters.
    """
    last_seen: dict[str, int] = {}
    left = 0
    best = 0

    for right, character in enumerate(text):
        if character in last_seen and last_seen[character] >= left:
            left = last_seen[character] + 1

        last_seen[character] = right
        best = max(best, right - left + 1)

    return best


def minimum_size_subarray_sum(
    target: int, values: Sequence[int]
) -> int:
    """
    Find the shortest contiguous subarray with sum >= target.

    IMPORTANT:
    This standard shrinking-window solution requires non-negative values.
    Negative numbers invalidate its monotonic window reasoning.
    """
    left = 0
    current_sum = 0
    best = len(values) + 1

    for right, value in enumerate(values):
        if value < 0:
            raise ValueError(
                "This sliding-window implementation requires non-negative values."
            )

        current_sum += value

        while current_sum >= target:
            best = min(best, right - left + 1)
            current_sum -= values[left]
            left += 1

    return 0 if best == len(values) + 1 else best


# ============================================================================
# 16. LINKED-LIST TWO POINTERS
# ============================================================================

@dataclass
class ListNode:
    value: int
    next: "ListNode | None" = None


def has_cycle(head: ListNode | None) -> bool:
    """
    Floyd's tortoise-and-hare cycle detection.

    slow moves one step.
    fast moves two steps.

    If a cycle exists, they eventually meet.

    Time: O(n)
    Extra space: O(1)
    """
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            return True

    return False


def find_cycle_start(head: ListNode | None) -> ListNode | None:
    """
    Find the first node of a linked-list cycle.

    After slow and fast meet, place one pointer at the head.
    Advancing both one step at a time makes them meet at the cycle entry.
    """
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            pointer = head

            while pointer is not slow:
                pointer = pointer.next
                slow = slow.next

            return pointer

    return None


# ============================================================================
# 17. ADVANCED: TRAPPING RAIN WATER
# ============================================================================

def trap_rain_water(heights: Sequence[int]) -> int:
    """
    Calculate trapped rain water using two pointers.

    left_max and right_max track the highest boundary encountered from
    each direction.

    At any point, the smaller boundary determines the water level.

    Time: O(n)
    Extra space: O(1)
    """
    if len(heights) < 3:
        return 0

    left = 0
    right = len(heights) - 1
    left_max = 0
    right_max = 0
    water = 0

    while left <= right:
        if heights[left] <= heights[right]:
            if heights[left] >= left_max:
                left_max = heights[left]
            else:
                water += left_max - heights[left]
            left += 1
        else:
            if heights[right] >= right_max:
                right_max = heights[right]
            else:
                water += right_max - heights[right]
            right -= 1

    return water


# ============================================================================
# 18. ADVANCED: THREE-WAY PARTITION
# ============================================================================

def three_way_partition(
    values: list[int], low_value: int, high_value: int
) -> None:
    """
    Partition into three regions:

        < low_value
        [low_value, high_value]
        > high_value

    This generalizes the Dutch National Flag idea.
    """
    low = 0
    current = 0
    high = len(values) - 1

    while current <= high:
        if values[current] < low_value:
            values[low], values[current] = values[current], values[low]
            low += 1
            current += 1

        elif values[current] > high_value:
            values[current], values[high] = values[high], values[current]
            high -= 1

        else:
            current += 1


# ============================================================================
# 19. EDGE CASES AND VALIDATION
# ============================================================================

def demonstrate_edge_cases() -> None:
    cases = [
        [],
        [1],
        [1, 1, 1],
        [-5, -3, -1, 0, 2, 4],
    ]

    print("\nEdge cases")

    for values in cases:
        print(
            "values=",
            values,
            "two_sum_target_0=",
            two_sum_sorted(values, 0),
            "squares=",
            sorted_squares(values),
        )

    print("Empty palindrome:", is_palindrome(""))
    print("Empty compression:", compress_runs(""))


# ============================================================================
# 20. COMPLEXITY REFERENCE
# ============================================================================

def print_complexity_reference() -> None:
    print(
        """
Complexity reference:

Basic reverse                  O(n)       O(1)
Palindrome                     O(n)       O(n) after normalization
Sorted two-sum                 O(n)       O(1)
Hash-table two-sum             O(n)*      O(n)
Sort + two pointers            O(n log n) O(n)
Remove duplicates              O(n)       O(1)
Move zeroes                    O(n)       O(1)
Partition                      O(n)       O(1)
Dutch National Flag            O(n)       O(1)
Three-sum                      O(n^2)     O(n)
Four-sum                       O(n^3)     O(n)
Container with most water      O(n)       O(1)
Sorted squares                 O(n)       O(n)
Merge sorted arrays            O(n+m)     O(n+m)
Sliding window                 O(n)*      O(k)
Cycle detection                O(n)       O(1)
Trapping rain water            O(n)       O(1)

* Average-case hash-table/sliding-window complexity under normal assumptions.
"""


# ============================================================================
# 21. TESTS
# ============================================================================

def run_assertions() -> None:
    values = [1, 2, 3, 4, 5]
    reverse_in_place(values)
    assert values == [5, 4, 3, 2, 1]

    assert is_palindrome("racecar")
    assert not is_palindrome("python")

    assert two_sum_sorted([1, 2, 4, 7, 9], 11) == (1, 4)
    assert two_sum_sorted([1, 2, 3], 100) is None

    assert two_sum_hash([2, 7, 11, 15], 9) == (0, 1)

    values = [1, 1, 2, 2, 3]
    length = remove_duplicates_sorted(values)
    assert values[:length] == [1, 2, 3]

    values = [0, 1, 0, 3, 12]
    move_zeroes(values)
    assert values == [1, 3, 12, 0, 0]

    values = [4, 1, 3, 2, 5]
    boundary = partition_by_pivot(values, 3)
    assert all(value < 3 for value in values[:boundary])
    assert all(value >= 3 for value in values[boundary:])

    values = [2, 0, 2, 1, 1, 0]
    dutch_national_flag(values)
    assert values == [0, 0, 1, 1, 2, 2]

    assert three_sum([-1, 0, 1, 2, -1, -4], 0) == [
        (-1, -1, 2),
        (-1, 0, 1),
    ]

    assert four_sum([1, 0, -1, 0, -2, 2], 0) == [
        (-2, -1, 1, 2),
        (-2, 0, 0, 2),
        (-1, 0, 0, 1),
    ]

    assert max_container_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert sorted_squares([-7, -3, -1, 4, 8]) == [1, 9, 16, 49, 64]
    assert merge_sorted_arrays([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
    assert intersection_sorted([1, 2, 2, 4], [2, 2, 3, 4]) == [2, 4]
    assert compress_runs("aaabbc") == "a3b2c1"

    assert longest_substring_without_repeating("abcabcbb") == 3
    assert longest_substring_without_repeating("bbbbb") == 1
    assert minimum_size_subarray_sum(7, [2, 3, 1, 2, 4, 3]) == 2

    node1 = ListNode(1)
    node2 = ListNode(2)
    node3 = ListNode(3)
    node4 = ListNode(4)
    node1.next = node2
    node2.next = node3
    node3.next = node4
    node4.next = node2

    assert has_cycle(node1)
    assert find_cycle_start(node1) is node2

    assert trap_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    values = [1, 5, 2, 8, 3, 4, 9]
    three_way_partition(values, 3, 5)
    assert all(value < 3 for value in values[:2])
    assert all(3 <= value <= 5 for value in values[2:6])
    assert all(value > 5 for value in values[6:])


# ============================================================================
# 22. MAIN DEMONSTRATION
# ============================================================================

def main() -> None:
    explain_two_pointers()
    demonstrate_basic_two_pointers()
    demonstrate_sorted_pair_search()
    demonstrate_strategy_comparison()
    demonstrate_duplicate_removal()

    values = [0, 4, 0, 3, 2, 0, 8]
    move_zeroes(values)
    print("\nMove zeroes:", values)

    values = [4, 1, 7, 2, 8, 3, 5]
    boundary = partition_by_pivot(values, 5)
    print("Partitioned:", values, "boundary:", boundary)

    values = [2, 0, 2, 1, 1, 0]
    dutch_national_flag(values)
    print("Dutch National Flag:", values)

    print("\nThree Sum:", three_sum([-1, 0, 1, 2, -1, -4], 0))
    print("Four Sum:", four_sum([1, 0, -1, 0, -2, 2], 0))

    print(
        "\nMaximum container area:",
        max_container_area([1, 8, 6, 2, 5, 4, 8, 3, 7]),
    )

    print(
        "Sorted squares:",
        sorted_squares([-7, -3, -1, 4, 8]),
    )

    print(
        "Merged arrays:",
        merge_sorted_arrays([1, 3, 5], [2, 4, 6]),
    )

    print(
        "Intersection:",
        intersection_sorted([1, 2, 2, 4], [2, 2, 3, 4]),
    )

    print("Run-length compression:", compress_runs("aaabbccccd"))

    print(
        "Longest unique substring:",
        longest_substring_without_repeating("pwwkew"),
    )

    print(
        "Minimum size subarray:",
        minimum_size_subarray_sum(7, [2, 3, 1, 2, 4, 3]),
    )

    print(
        "Trapped rain water:",
        trap_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]),
    )

    demonstrate_edge_cases()
    print_complexity_reference()

    run_assertions()
    print("\nAll built-in assertions passed.")


if __name__ == "__main__":
    main()
