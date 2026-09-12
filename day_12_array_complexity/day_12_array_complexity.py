"""
Array Complexity
================

A self-contained study and executable demonstration of:

- Arrays and array-like structures
- Indexing and traversal
- Random access
- Searching
- Updating
- Insertion and deletion
- Static arrays
- Dynamic arrays
- Resizing and amortized analysis
- Time and space complexity
- Best, average, and worst cases
- Common array algorithms
- Two-dimensional arrays
- Prefix sums
- Two-pointer techniques
- Sliding windows
- Binary search
- Sorting complexity
- Memory layout and cache locality
- In-place versus auxiliary-space algorithms
- Python list behavior as a dynamic array
- Edge cases
- Common mistakes
- Performance measurement
- Testing and verification

The examples use only Python's standard library.
"""

from __future__ import annotations

import math
import random
import sys
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Sequence


# =============================================================================
# 1. COMPLEXITY FUNDAMENTALS
# =============================================================================

def demonstrate_complexity_notation() -> None:
    """
    Big-O describes how resource consumption grows as input size grows.

    Common complexity classes:

        O(1)       constant
        O(log n)   logarithmic
        O(n)       linear
        O(n log n) linearithmic
        O(n^2)     quadratic
        O(2^n)     exponential

    The functions below demonstrate representative operations.
    """

    def constant_operation(values: Sequence[int]) -> int:
        # Accessing one known index does not depend on the array length.
        return values[0] if values else 0

    def linear_operation(values: Sequence[int]) -> int:
        # Every element may be inspected.
        return sum(values)

    def quadratic_operation(values: Sequence[int]) -> int:
        # Each element is compared with every other element.
        comparisons = 0
        for _ in values:
            for _ in values:
                comparisons += 1
        return comparisons

    values = list(range(10))

    print("O(1):", constant_operation(values))
    print("O(n):", linear_operation(values))
    print("O(n^2) operation count:", quadratic_operation(values))


# =============================================================================
# 2. BASIC ARRAY MODEL
# =============================================================================

def demonstrate_basic_array_model() -> None:
    """
    A conceptual array stores elements in indexed positions.

    For a zero-based array:

        index:  0   1   2   3
        value: 10  20  30  40

    If the element size is fixed, the address of an element can be calculated
    directly from its base address and index.

        address = base + index * element_size

    This direct address calculation explains why array indexing is O(1).
    """

    values = [10, 20, 30, 40]

    print("Array:", values)
    print("First element:", values[0])
    print("Third element:", values[2])
    print("Last element:", values[-1])

    try:
        print(values[100])
    except IndexError as error:
        print("Invalid index:", error)


# =============================================================================
# 3. ARRAY OPERATION COMPLEXITIES
# =============================================================================

def array_operation_complexity_table() -> None:
    """
    Conceptual complexity table for a conventional contiguous array.

    Operation                 Time
    ------------------------------------------------
    Access by index           O(1)
    Update by index           O(1)
    Traverse                  O(n)
    Linear search             O(n)
    Binary search             O(log n), sorted data
    Insert at end             O(1) amortized dynamic array
    Insert at beginning       O(n)
    Insert in middle          O(n)
    Delete at end             O(1)
    Delete at beginning       O(n)
    Delete in middle          O(n)
    """

    table = [
        ("Access by index", "O(1)"),
        ("Update by index", "O(1)"),
        ("Traversal", "O(n)"),
        ("Linear search", "O(n)"),
        ("Binary search", "O(log n), sorted array"),
        ("Append, dynamic array", "O(1) amortized"),
        ("Insert at beginning", "O(n)"),
        ("Insert in middle", "O(n)"),
        ("Delete at end", "O(1)"),
        ("Delete at beginning", "O(n)"),
        ("Delete in middle", "O(n)"),
    ]

    for operation, complexity in table:
        print(f"{operation:<28} {complexity}")


# =============================================================================
# 4. ACCESS AND UPDATE
# =============================================================================

def array_access_and_update(values: list[int]) -> None:
    """
    Index access and indexed replacement are O(1).

    The array does not need to be scanned to find a known index.
    """

    if not values:
        return

    values[0] = 999
    print("After O(1) update:", values)

    middle_index = len(values) // 2
    print("Middle element:", values[middle_index])


# =============================================================================
# 5. TRAVERSAL
# =============================================================================

def traverse_array(values: Sequence[int]) -> int:
    """
    Traversal is O(n) because each element is processed once.

    Auxiliary space is O(1) when only a running total is maintained.
    """

    total = 0

    for value in values:
        total += value

    return total


# =============================================================================
# 6. LINEAR SEARCH
# =============================================================================

def linear_search(values: Sequence[int], target: int) -> int:
    """
    Linear search:

    Best case:    O(1), target is first
    Average case: O(n)
    Worst case:   O(n), target is absent or last
    Space:        O(1)
    """

    for index, value in enumerate(values):
        if value == target:
            return index

    return -1


def demonstrate_linear_search() -> None:
    values = [17, 4, 29, 8, 13, 42]

    print("First:", linear_search(values, 17))
    print("Middle:", linear_search(values, 29))
    print("Last:", linear_search(values, 42))
    print("Absent:", linear_search(values, 100))


# =============================================================================
# 7. BINARY SEARCH
# =============================================================================

def binary_search(values: Sequence[int], target: int) -> int:
    """
    Binary search requires sorted data.

    Each iteration discards approximately half the remaining search space.

    Time:
        Best:    O(1)
        Average: O(log n)
        Worst:   O(log n)

    Space:
        O(1) for this iterative implementation.
    """

    left = 0
    right = len(values) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            return middle

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def demonstrate_binary_search() -> None:
    sorted_values = [2, 5, 8, 12, 16, 21, 30, 45]

    for target in [2, 16, 45, 100]:
        print(target, "->", binary_search(sorted_values, target))


# =============================================================================
# 8. STATIC ARRAY IMPLEMENTATION
# =============================================================================

class StaticArray:
    """
    Fixed-capacity array abstraction.

    A static array cannot grow beyond its original capacity.

    Appending to an unused position is O(1).
    Insertion requiring shifting is O(n).
    Deletion requiring shifting is O(n).
    """

    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError("Capacity cannot be negative.")

        self._data: list[Optional[int]] = [None] * capacity
        self._size = 0

    @property
    def capacity(self) -> int:
        return len(self._data)

    @property
    def size(self) -> int:
        return self._size

    def append(self, value: int) -> None:
        if self._size == self.capacity:
            raise OverflowError("Static array is full.")

        self._data[self._size] = value
        self._size += 1

    def get(self, index: int) -> int:
        self._validate_index(index)
        value = self._data[index]
        assert value is not None
        return value

    def set(self, index: int, value: int) -> None:
        self._validate_index(index)
        self._data[index] = value

    def insert(self, index: int, value: int) -> None:
        if index < 0 or index > self._size:
            raise IndexError("Insertion index out of range.")

        if self._size == self.capacity:
            raise OverflowError("Static array is full.")

        # Shift elements one position to the right.
        for position in range(self._size, index, -1):
            self._data[position] = self._data[position - 1]

        self._data[index] = value
        self._size += 1

    def delete(self, index: int) -> int:
        self._validate_index(index)

        deleted = self.get(index)

        # Shift all following elements one position to the left.
        for position in range(index, self._size - 1):
            self._data[position] = self._data[position + 1]

        self._data[self._size - 1] = None
        self._size -= 1

        return deleted

    def _validate_index(self, index: int) -> None:
        if index < 0 or index >= self._size:
            raise IndexError("Array index out of range.")

    def to_list(self) -> list[int]:
        return [value for value in self._data[:self._size] if value is not None]


def demonstrate_static_array() -> None:
    array = StaticArray(5)

    for value in [10, 20, 30]:
        array.append(value)

    print("Static array:", array.to_list())
    array.insert(1, 15)
    print("After insertion:", array.to_list())
    print("Deleted:", array.delete(2))
    print("After deletion:", array.to_list())

    try:
        full = StaticArray(1)
        full.append(100)
        full.append(200)
    except OverflowError as error:
        print("Static capacity error:", error)


# =============================================================================
# 9. DYNAMIC ARRAY IMPLEMENTATION
# =============================================================================

class DynamicArray:
    """
    Educational dynamic-array implementation.

    The logical size is the number of stored elements.
    The capacity is the amount of allocated storage.

    When capacity is exhausted, the array grows and elements are copied.

    A single resize can cost O(n), but append is O(1) amortized when capacity
    grows geometrically.
    """

    def __init__(self, initial_capacity: int = 4):
        if initial_capacity < 1:
            raise ValueError("Initial capacity must be positive.")

        self._data: list[Optional[int]] = [None] * initial_capacity
        self._size = 0

    @property
    def size(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._data)

    def append(self, value: int) -> None:
        if self._size == self.capacity:
            self._resize(self.capacity * 2)

        self._data[self._size] = value
        self._size += 1

    def _resize(self, new_capacity: int) -> None:
        old_capacity = self.capacity
        new_data: list[Optional[int]] = [None] * new_capacity

        # Resizing costs O(n) because existing elements are copied.
        for index in range(self._size):
            new_data[index] = self._data[index]

        self._data = new_data

        print(
            f"Resize: {old_capacity} -> {new_capacity}, "
            f"elements copied: {self._size}"
        )

    def get(self, index: int) -> int:
        self._validate_index(index)
        value = self._data[index]
        assert value is not None
        return value

    def set(self, index: int, value: int) -> None:
        self._validate_index(index)
        self._data[index] = value

    def insert(self, index: int, value: int) -> None:
        if index < 0 or index > self._size:
            raise IndexError("Insertion index out of range.")

        if self._size == self.capacity:
            self._resize(self.capacity * 2)

        for position in range(self._size, index, -1):
            self._data[position] = self._data[position - 1]

        self._data[index] = value
        self._size += 1

    def pop(self) -> int:
        if self._size == 0:
            raise IndexError("Cannot pop from an empty array.")

        self._size -= 1
        value = self._data[self._size]
        self._data[self._size] = None

        assert value is not None
        return value

    def delete(self, index: int) -> int:
        self._validate_index(index)

        deleted = self.get(index)

        for position in range(index, self._size - 1):
            self._data[position] = self._data[position + 1]

        self._size -= 1
        self._data[self._size] = None

        return deleted

    def to_list(self) -> list[int]:
        return [
            value
            for value in self._data[:self._size]
            if value is not None
        ]

    def _validate_index(self, index: int) -> None:
        if index < 0 or index >= self._size:
            raise IndexError("Array index out of range.")


def demonstrate_dynamic_array() -> None:
    array = DynamicArray(2)

    for value in range(1, 9):
        array.append(value)
        print(
            f"append({value}): size={array.size}, capacity={array.capacity}"
        )

    array.insert(2, 99)
    print("After insertion:", array.to_list())

    print("Deleted:", array.delete(2))
    print("After deletion:", array.to_list())
    print("Popped:", array.pop())
    print("Final:", array.to_list())


# =============================================================================
# 10. AMORTIZED ANALYSIS
# =============================================================================

def count_dynamic_array_copies(number_of_elements: int) -> int:
    """
    For geometric growth by a factor of two, total copying over n appends is
    O(n), not O(n^2).

    Approximate resize-copy counts:

        1 + 2 + 4 + 8 + ... < 2n

    Therefore n append operations perform O(n) total copying, giving:

        O(n) / n = O(1) amortized cost per append.
    """

    if number_of_elements <= 0:
        return 0

    capacity = 1
    size = 0
    copies = 0

    while size < number_of_elements:
        if size == capacity:
            copies += size
            capacity *= 2

        size += 1

    return copies


def demonstrate_amortized_analysis() -> None:
    for n in [1, 2, 4, 8, 16, 100, 1000]:
        copies = count_dynamic_array_copies(n)
        print(
            f"n={n:<5} total resize copies={copies:<6} "
            f"copies/n={copies / n:.2f}"
        )


# =============================================================================
# 11. INSERTION COMPLEXITY
# =============================================================================

def insert_at_beginning(values: list[int], value: int) -> None:
    """
    Beginning insertion requires shifting n elements.

    Time: O(n)
    """
    values.append(0)

    for index in range(len(values) - 1, 0, -1):
        values[index] = values[index - 1]

    values[0] = value


def insert_at_index(values: list[int], index: int, value: int) -> None:
    """
    Middle insertion shifts elements after the insertion point.

    Worst case: O(n)
    Best case for insertion at the end: O(1) amortized.
    """

    if index < 0 or index > len(values):
        raise IndexError("Insertion index out of range.")

    values.append(0)

    for position in range(len(values) - 1, index, -1):
        values[position] = values[position - 1]

    values[index] = value


def demonstrate_insertions() -> None:
    values = [10, 20, 30, 40]

    insert_at_beginning(values, 5)
    print("Beginning insertion:", values)

    insert_at_index(values, 3, 25)
    print("Middle insertion:", values)

    insert_at_index(values, len(values), 50)
    print("End insertion:", values)


# =============================================================================
# 12. DELETION COMPLEXITY
# =============================================================================

def delete_at_index(values: list[int], index: int) -> int:
    """
    Deleting from an array requires shifting later elements left.

    Worst case: O(n)
    Deleting the final element can be O(1).
    """

    if index < 0 or index >= len(values):
        raise IndexError("Deletion index out of range.")

    deleted = values[index]

    for position in range(index, len(values) - 1):
        values[position] = values[position + 1]

    values.pop()

    return deleted


def demonstrate_deletion() -> None:
    values = [10, 20, 30, 40, 50]

    print("Deleted:", delete_at_index(values, 0))
    print("After front deletion:", values)

    print("Deleted:", delete_at_index(values, 2))
    print("After middle deletion:", values)

    print("Deleted:", delete_at_index(values, len(values) - 1))
    print("After end deletion:", values)


# =============================================================================
# 13. DUPLICATE DETECTION
# =============================================================================

def contains_duplicate_quadratic(values: Sequence[int]) -> bool:
    """
    Compare every pair.

    Time: O(n^2)
    Extra space: O(1)
    """

    for first in range(len(values)):
        for second in range(first + 1, len(values)):
            if values[first] == values[second]:
                return True

    return False


def contains_duplicate_hashing(values: Sequence[int]) -> bool:
    """
    Hash-based approach.

    Average time: O(n)
    Extra space: O(n)
    """

    seen: set[int] = set()

    for value in values:
        if value in seen:
            return True

        seen.add(value)

    return False


def demonstrate_duplicate_tradeoff() -> None:
    values = [4, 8, 15, 16, 23, 42, 15]

    print(
        "Quadratic duplicate detection:",
        contains_duplicate_quadratic(values),
    )
    print(
        "Hash-based duplicate detection:",
        contains_duplicate_hashing(values),
    )


# =============================================================================
# 14. IN-PLACE REVERSAL
# =============================================================================

def reverse_in_place(values: list[int]) -> None:
    """
    In-place two-pointer reversal.

    Time: O(n)
    Auxiliary space: O(1)
    """

    left = 0
    right = len(values) - 1

    while left < right:
        values[left], values[right] = values[right], values[left]
        left += 1
        right -= 1


def reverse_with_copy(values: Sequence[int]) -> list[int]:
    """
    Copy-based reversal.

    Time: O(n)
    Auxiliary space: O(n)
    """

    return list(reversed(values))


def demonstrate_space_tradeoff() -> None:
    values = [1, 2, 3, 4, 5]

    reverse_in_place(values)
    print("In-place:", values)

    copied = reverse_with_copy(values)
    print("Copied:", copied)


# =============================================================================
# 15. PREFIX SUMS
# =============================================================================

def build_prefix_sums(values: Sequence[int]) -> list[int]:
    """
    Prefix sum construction.

    Time: O(n)
    Space: O(n)

    prefix[i] stores the sum of elements before index i.

    This allows range-sum queries in O(1) after O(n) preprocessing.
    """

    prefix = [0] * (len(values) + 1)

    for index, value in enumerate(values):
        prefix[index + 1] = prefix[index] + value

    return prefix


def range_sum(prefix: Sequence[int], left: int, right: int) -> int:
    """
    Inclusive range sum.

    sum(values[left:right+1])
    becomes:

        prefix[right + 1] - prefix[left]

    Time: O(1).
    """

    if left < 0 or right < left or right >= len(prefix) - 1:
        raise IndexError("Invalid range.")

    return prefix[right + 1] - prefix[left]


def demonstrate_prefix_sums() -> None:
    values = [5, 2, 7, 3, 9, 1]
    prefix = build_prefix_sums(values)

    print("Values:", values)
    print("Prefix:", prefix)
    print("Range [1, 4]:", range_sum(prefix, 1, 4))


# =============================================================================
# 16. TWO-POINTER TECHNIQUE
# =============================================================================

def pair_sum_sorted(values: Sequence[int], target: int) -> Optional[tuple[int, int]]:
    """
    Find two values whose sum equals target.

    Requires sorted input.

    Time: O(n)
    Extra space: O(1)
    """

    left = 0
    right = len(values) - 1

    while left < right:
        total = values[left] + values[right]

        if total == target:
            return values[left], values[right]

        if total < target:
            left += 1
        else:
            right -= 1

    return None


def demonstrate_two_pointers() -> None:
    values = [1, 2, 4, 7, 9, 13, 18]

    print("Pair:", pair_sum_sorted(values, 16))
    print("Absent pair:", pair_sum_sorted(values, 100))


# =============================================================================
# 17. SLIDING WINDOW
# =============================================================================

def maximum_sum_fixed_window(values: Sequence[int], window_size: int) -> int:
    """
    Maximum sum of any contiguous window of fixed length.

    Naive approach: O(n * k)
    Sliding-window approach: O(n)

    Space: O(1).
    """

    if window_size <= 0:
        raise ValueError("Window size must be positive.")

    if window_size > len(values):
        raise ValueError("Window cannot exceed array length.")

    current_sum = sum(values[:window_size])
    maximum = current_sum

    for index in range(window_size, len(values)):
        current_sum += values[index]
        current_sum -= values[index - window_size]
        maximum = max(maximum, current_sum)

    return maximum


def demonstrate_sliding_window() -> None:
    values = [2, 1, 5, 1, 3, 2]
    print("Maximum window sum:", maximum_sum_fixed_window(values, 3))


# =============================================================================
# 18. KADANE'S ALGORITHM
# =============================================================================

def maximum_subarray_sum(values: Sequence[int]) -> int:
    """
    Kadane's algorithm finds the maximum sum of a non-empty contiguous
    subarray.

    Time: O(n)
    Space: O(1)

    Important edge case:
    An all-negative array still returns its largest single element.
    """

    if not values:
        raise ValueError("Array must not be empty.")

    current = values[0]
    best = values[0]

    for value in values[1:]:
        current = max(value, current + value)
        best = max(best, current)

    return best


def demonstrate_kadane() -> None:
    examples = [
        [5, -2, 3, 4, -10, 8],
        [-8, -3, -5, -2],
        [1, 2, 3, 4],
    ]

    for values in examples:
        print(values, "->", maximum_subarray_sum(values))


# =============================================================================
# 19. TWO-DIMENSIONAL ARRAYS
# =============================================================================

def matrix_traversal(matrix: Sequence[Sequence[int]]) -> int:
    """
    For an r x c matrix:

        Time: O(r * c)
        Extra space: O(1)

    Every cell is visited once.
    """

    total = 0

    for row in matrix:
        for value in row:
            total += value

    return total


def demonstrate_matrix() -> None:
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    print("Matrix total:", matrix_traversal(matrix))


# =============================================================================
# 20. CORRECT MATRIX CREATION
# =============================================================================

def create_matrix(rows: int, columns: int, initial_value: int = 0) -> list[list[int]]:
    """
    Creates independent rows.

    The comprehension is important. It creates a new list for every row.
    """

    if rows < 0 or columns < 0:
        raise ValueError("Dimensions cannot be negative.")

    return [
        [initial_value for _ in range(columns)]
        for _ in range(rows)
    ]


def demonstrate_matrix_aliasing() -> None:
    correct = create_matrix(3, 3)

    # This creates three references to the SAME inner list.
    incorrect = [[0] * 3] * 3

    correct[0][0] = 99
    incorrect[0][0] = 99

    print("Correct independent rows:", correct)
    print("Aliased rows:", incorrect)


# =============================================================================
# 21. LINEAR SORTING EXAMPLE: SELECTION SORT
# =============================================================================

def selection_sort(values: list[int]) -> None:
    """
    Selection sort.

    Best case:    O(n^2)
    Average case: O(n^2)
    Worst case:   O(n^2)
    Space:        O(1) auxiliary

    Useful educationally, but generally inferior to optimized sorting
    algorithms for large inputs.
    """

    n = len(values)

    for start in range(n - 1):
        minimum_index = start

        for index in range(start + 1, n):
            if values[index] < values[minimum_index]:
                minimum_index = index

        values[start], values[minimum_index] = (
            values[minimum_index],
            values[start],
        )


# =============================================================================
# 22. INSERTION SORT
# =============================================================================

def insertion_sort(values: list[int]) -> None:
    """
    Insertion sort.

    Best case: O(n), already sorted or nearly sorted
    Average:    O(n^2)
    Worst:      O(n^2)
    Space:      O(1)

    It is often useful for small or nearly sorted datasets.
    """

    for index in range(1, len(values)):
        current = values[index]
        position = index - 1

        while position >= 0 and values[position] > current:
            values[position + 1] = values[position]
            position -= 1

        values[position + 1] = current


# =============================================================================
# 23. MERGE SORT
# =============================================================================

def merge_sort(values: Sequence[int]) -> list[int]:
    """
    Merge sort.

    Time: O(n log n) in best, average, and worst cases.
    Auxiliary space: O(n).

    It uses divide and conquer.
    """

    if len(values) <= 1:
        return list(values)

    middle = len(values) // 2

    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])

    return merge_sorted_arrays(left, right)


def merge_sorted_arrays(left: Sequence[int], right: Sequence[int]) -> list[int]:
    result: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])

    return result


# =============================================================================
# 24. QUICK SORT
# =============================================================================

def quick_sort(values: list[int]) -> None:
    """
    In-place quicksort using a Lomuto-style partition.

    Average time: O(n log n)
    Worst time:   O(n^2)
    Auxiliary stack: O(log n) average, O(n) worst case.

    Pivot selection strongly influences behavior.
    """

    def partition(left: int, right: int) -> int:
        pivot = values[right]
        boundary = left

        for index in range(left, right):
            if values[index] <= pivot:
                values[boundary], values[index] = (
                    values[index],
                    values[boundary],
                )
                boundary += 1

        values[boundary], values[right] = (
            values[right],
            values[boundary],
        )

        return boundary

    def sort(left: int, right: int) -> None:
        if left >= right:
            return

        pivot_index = partition(left, right)
        sort(left, pivot_index - 1)
        sort(pivot_index + 1, right)

    sort(0, len(values) - 1)


# =============================================================================
# 25. SORTING COMPARISON
# =============================================================================

def demonstrate_sorting_complexities() -> None:
    print("Sorting complexity comparison:")
    print("Selection sort: O(n^2)")
    print("Insertion sort: best O(n), average/worst O(n^2)")
    print("Merge sort:      O(n log n), O(n) auxiliary space")
    print("Quicksort:       average O(n log n), worst O(n^2)")


# =============================================================================
# 26. PREFIX-SUM SPACE TRADE-OFF
# =============================================================================

def naive_range_sum(values: Sequence[int], left: int, right: int) -> int:
    """
    Direct range summation.

    Time per query: O(k), where k is range length.
    Extra space: O(1).
    """

    if left < 0 or right < left or right >= len(values):
        raise IndexError("Invalid range.")

    return sum(values[left:right + 1])


def compare_range_sum_strategies() -> None:
    values = list(range(1, 1001))
    prefix = build_prefix_sums(values)

    print("Naive:", naive_range_sum(values, 100, 900))
    print("Prefix:", range_sum(prefix, 100, 900))


# =============================================================================
# 27. MEMORY COMPLEXITY
# =============================================================================

@dataclass
class MemoryExample:
    """
    Conceptual examples of memory growth.
    """

    array_size: int

    def fixed_storage(self) -> int:
        # One conceptual storage slot per element.
        return self.array_size

    def copied_storage(self) -> int:
        # Original + copied array may temporarily coexist.
        return self.array_size * 2


def demonstrate_space_complexity() -> None:
    example = MemoryExample(1000)

    print("O(n) logical storage:", example.fixed_storage())
    print("Approximate simultaneous copied storage:", example.copied_storage())


# =============================================================================
# 28. STATIC VERSUS DYNAMIC ARRAYS
# =============================================================================

def compare_static_and_dynamic_arrays() -> None:
    comparison = [
        ("Capacity", "Fixed", "Can grow"),
        ("Random access", "O(1)", "O(1)"),
        ("End append", "O(1) if space exists", "O(1) amortized"),
        ("Middle insertion", "O(n)", "O(n)"),
        ("Middle deletion", "O(n)", "O(n)"),
        ("Resize", "Not supported", "O(n) occasionally"),
        ("Memory flexibility", "Low", "High"),
        ("Capacity planning", "Required", "Usually automatic"),
    ]

    print(f"{'Property':<24} {'Static':<25} {'Dynamic':<25}")
    print("-" * 74)

    for property_name, static, dynamic in comparison:
        print(f"{property_name:<24} {static:<25} {dynamic:<25}")


# =============================================================================
# 29. PYTHON LIST AS A DYNAMIC ARRAY
# =============================================================================

def demonstrate_python_list() -> None:
    """
    Python's list behaves conceptually like a dynamic array.

    Index access is O(1).
    append() is O(1) amortized.
    insert(0, value) is O(n).
    pop() from the end is O(1).
    pop(0) is O(n).
    """

    values: list[int] = []

    for number in range(5):
        values.append(number)

    print("Python list:", values)
    print("Index access:", values[3])

    values.append(5)
    print("After append:", values)

    values.insert(0, -1)
    print("After front insertion:", values)

    values.pop()
    print("After end deletion:", values)

    values.pop(0)
    print("After front deletion:", values)


# =============================================================================
# 30. APPEND VERSUS FRONT INSERTION
# =============================================================================

def measure_operation(
    operation: Callable[[], None],
    repetitions: int = 1,
) -> float:
    """
    Measures wall-clock time.

    Timing is affected by operating-system scheduling, hardware, interpreter
    state, caching, and other environmental factors. It should be used for
    empirical investigation rather than as a replacement for complexity
    analysis.
    """

    start = time.perf_counter()

    for _ in range(repetitions):
        operation()

    return time.perf_counter() - start


def demonstrate_operation_timing() -> None:
    size = 20_000

    append_time = measure_operation(
        lambda: [number for number in range(size)],
    )

    front_insert_time = measure_operation(
        lambda: build_front_insert_list(size),
    )

    print(f"Build with appends/comprehension: {append_time:.6f}s")
    print(f"Repeated front insertion:         {front_insert_time:.6f}s")


def build_front_insert_list(size: int) -> list[int]:
    values: list[int] = []

    for number in range(size):
        values.insert(0, number)

    return values


# =============================================================================
# 31. ARRAY ACCESS VERSUS SEARCH
# =============================================================================

def demonstrate_access_vs_search() -> None:
    values = list(range(100_000))

    # Direct access uses the index and is O(1).
    direct = values[90_000]

    # Searching for a value requires scanning in the worst case and is O(n).
    searched = linear_search(values, 90_000)

    print("Direct access result:", direct)
    print("Linear search result:", searched)


# =============================================================================
# 32. BEST, AVERAGE, AND WORST CASES
# =============================================================================

def explain_cases_with_search() -> None:
    values = list(range(10))

    best_case = linear_search(values, 0)
    average_case = linear_search(values, 5)
    worst_case = linear_search(values, 9)
    absent_case = linear_search(values, 100)

    print("Best case:", best_case)
    print("Average-style case:", average_case)
    print("Worst successful case:", worst_case)
    print("Worst unsuccessful case:", absent_case)


# =============================================================================
# 33. EDGE CASE HANDLING
# =============================================================================

def demonstrate_edge_cases() -> None:
    cases = [
        [],
        [1],
        [1, 1, 1],
        [-5, -2, -9],
        [0],
    ]

    for values in cases:
        print("Array:", values)

        if values:
            print("Minimum:", min(values))
            print("Maximum:", max(values))
            print("Sum:", sum(values))
        else:
            print("Empty array: no minimum or maximum.")


# =============================================================================
# 34. SAFE MIN/MAX IMPLEMENTATION
# =============================================================================

def find_minimum(values: Sequence[int]) -> int:
    """
    O(n) time and O(1) extra space.

    Explicitly rejects an empty array because a minimum does not exist.
    """

    if not values:
        raise ValueError("Cannot find minimum of an empty array.")

    minimum = values[0]

    for value in values[1:]:
        if value < minimum:
            minimum = value

    return minimum


def find_maximum(values: Sequence[int]) -> int:
    """
    O(n) time and O(1) extra space.
    """

    if not values:
        raise ValueError("Cannot find maximum of an empty array.")

    maximum = values[0]

    for value in values[1:]:
        if value > maximum:
            maximum = value

    return maximum


# =============================================================================
# 35. SECOND-LARGEST ELEMENT
# =============================================================================

def second_largest_distinct(values: Sequence[int]) -> int:
    """
    Finds the second-largest DISTINCT value.

    Time: O(n)
    Extra space: O(1)

    Raises ValueError if fewer than two distinct values exist.
    """

    if len(values) < 2:
        raise ValueError("At least two values are required.")

    largest: Optional[int] = None
    second: Optional[int] = None

    for value in values:
        if largest is None or value > largest:
            second = largest
            largest = value
        elif value != largest and (second is None or value > second):
            second = value

    if second is None:
        raise ValueError("At least two distinct values are required.")

    return second


def demonstrate_second_largest() -> None:
    for values in [
        [10, 5, 8, 10, 7],
        [-4, -1, -8],
        [5, 5, 5],
    ]:
        try:
            print(values, "->", second_largest_distinct(values))
        except ValueError as error:
            print(values, "->", error)


# =============================================================================
# 36. ROTATING AN ARRAY
# =============================================================================

def rotate_right(values: list[int], steps: int) -> None:
    """
    Rotates an array to the right in O(n) time and O(1) auxiliary space.

    The modulo operation handles steps larger than the array length.
    """

    n = len(values)

    if n == 0:
        return

    steps %= n

    if steps == 0:
        return

    def reverse_range(left: int, right: int) -> None:
        while left < right:
            values[left], values[right] = values[right], values[left]
            left += 1
            right -= 1

    reverse_range(0, n - 1)
    reverse_range(0, steps - 1)
    reverse_range(steps, n - 1)


def demonstrate_rotation() -> None:
    values = [1, 2, 3, 4, 5, 6]
    rotate_right(values, 2)
    print("Rotated:", values)


# =============================================================================
# 37. STABLE PARTITION
# =============================================================================

def move_zeros_to_end(values: list[int]) -> None:
    """
    Moves zero values to the end while preserving the relative order of
    non-zero values.

    Time: O(n)
    Auxiliary space: O(1)
    """

    write_index = 0

    for read_index in range(len(values)):
        if values[read_index] != 0:
            values[write_index], values[read_index] = (
                values[read_index],
                values[write_index],
            )
            write_index += 1


def demonstrate_partition() -> None:
    values = [0, 1, 0, 3, 12, 0, 5]
    move_zeros_to_end(values)
    print("Zeros moved:", values)


# =============================================================================
# 38. MERGING SORTED ARRAYS
# =============================================================================

def merge_sorted_arrays_in_linear_time(
    first: Sequence[int],
    second: Sequence[int],
) -> list[int]:
    """
    Merging two sorted arrays takes O(n + m) time.

    Output storage is O(n + m).
    """

    result: list[int] = []
    first_index = 0
    second_index = 0

    while first_index < len(first) and second_index < len(second):
        if first[first_index] <= second[second_index]:
            result.append(first[first_index])
            first_index += 1
        else:
            result.append(second[second_index])
            second_index += 1

    result.extend(first[first_index:])
    result.extend(second[second_index:])

    return result


# =============================================================================
# 39. COUNTING OCCURRENCES
# =============================================================================

def count_occurrences(values: Sequence[int], target: int) -> int:
    """
    Counts occurrences in O(n) time and O(1) extra space.
    """

    count = 0

    for value in values:
        if value == target:
            count += 1

    return count


# =============================================================================
# 40. FREQUENCY TABLE TRADE-OFF
# =============================================================================

def frequency_table(values: Sequence[int]) -> dict[int, int]:
    """
    Hash-map frequency counting.

    Time: O(n) average.
    Space: O(k), where k is the number of distinct values.
    """

    frequencies: dict[int, int] = {}

    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1

    return frequencies


# =============================================================================
# 41. CACHE LOCALITY CONCEPT
# =============================================================================

def sequential_sum(values: Sequence[int]) -> int:
    """
    Sequential traversal has good locality for contiguous storage.

    Time: O(n).
    """

    total = 0

    for value in values:
        total += value

    return total


def strided_sum(values: Sequence[int], stride: int) -> int:
    """
    Also O(n) relative to the number of visited elements, but access patterns
    can differ significantly at the hardware level.

    Algorithmic Big-O alone does not describe every hardware performance
    effect.
    """

    if stride <= 0:
        raise ValueError("Stride must be positive.")

    total = 0

    for index in range(0, len(values), stride):
        total += values[index]

    return total


# =============================================================================
# 42. SPACE COMPLEXITY: INPUT VERSUS AUXILIARY SPACE
# =============================================================================

def copy_array(values: Sequence[int]) -> list[int]:
    """
    Output space is O(n).

    When discussing auxiliary space, it is important to distinguish memory
    required for the result from additional temporary memory.
    """

    return list(values)


def in_place_increment(values: list[int]) -> None:
    """
    Modifies the input directly.

    Time: O(n)
    Auxiliary space: O(1)
    """

    for index in range(len(values)):
        values[index] += 1


# =============================================================================
# 43. RECURSIVE BINARY SEARCH
# =============================================================================

def binary_search_recursive(
    values: Sequence[int],
    target: int,
    left: int,
    right: int,
) -> int:
    """
    Recursive binary search.

    Time: O(log n)
    Auxiliary call-stack space: O(log n).

    The iterative version uses O(1) auxiliary space.
    """

    if left > right:
        return -1

    middle = left + (right - left) // 2

    if values[middle] == target:
        return middle

    if values[middle] < target:
        return binary_search_recursive(
            values, target, middle + 1, right
        )

    return binary_search_recursive(
        values, target, left, middle - 1
    )


# =============================================================================
# 44. INTEGER OVERFLOW DISCUSSION
# =============================================================================

def demonstrate_large_integer_sum() -> None:
    """
    Python integers automatically expand to represent large integers.

    In fixed-width languages, an integer sum can overflow if the result
    exceeds the available integer range.

    This matters when translating algorithms between languages.
    """

    values = [10**100, 10**100, -10**100]
    print("Large integer sum:", sum(values))


# =============================================================================
# 45. AMORTIZED VERSUS WORST-CASE COMPLEXITY
# =============================================================================

def demonstrate_amortized_append_concept() -> None:
    """
    Dynamic-array append has:

        Individual worst-case: O(n)
        Amortized:              O(1)

    The distinction is important.

    Amortized analysis asks about the average cost over a sequence of
    operations under a defined growth strategy. It is not the same thing as
    probabilistic average-case analysis.
    """

    array = DynamicArray(1)

    for number in range(8):
        before_capacity = array.capacity
        array.append(number)
        after_capacity = array.capacity

        if after_capacity != before_capacity:
            print(
                f"append caused resize: {before_capacity} -> "
                f"{after_capacity}"
            )


# =============================================================================
# 46. RESERVATION AND PREALLOCATION
# =============================================================================

def preallocate_and_fill(size: int) -> list[int]:
    """
    Preallocation can reduce resizing overhead when the final size is known.

    Python's list implementation manages capacity internally, so this
    function demonstrates the general principle rather than exposing Python's
    private allocation strategy.
    """

    result = [0] * size

    for index in range(size):
        result[index] = index * index

    return result


# =============================================================================
# 47. COMMON ARRAY MISTAKE: OFF-BY-ONE
# =============================================================================

def safe_sum_first_k(values: Sequence[int], k: int) -> int:
    """
    Correctly handles the first k elements.

    Valid k values are 0 through len(values).
    """

    if k < 0 or k > len(values):
        raise ValueError("k must be between 0 and len(values).")

    total = 0

    for index in range(k):
        total += values[index]

    return total


# =============================================================================
# 48. COMMON ARRAY MISTAKE: MUTATING WHILE ITERATING
# =============================================================================

def remove_even_values_safely(values: list[int]) -> None:
    """
    Removing while iterating forward can skip elements because indexes shift.

    Iterating over a copy avoids that problem.

    Time: O(n)
    Extra space: O(n) because a temporary copy is used.
    """

    for value in values[:]:
        if value % 2 == 0:
            values.remove(value)


def remove_even_values_in_place(values: list[int]) -> None:
    """
    Two-pointer compaction avoids the temporary copy.

    Time: O(n)
    Auxiliary space: O(1).
    """

    write_index = 0

    for value in values:
        if value % 2 != 0:
            values[write_index] = value
            write_index += 1

    del values[write_index:]


# =============================================================================
# 49. TESTING ARRAY ALGORITHMS
# =============================================================================

def run_assertion_tests() -> None:
    """
    Lightweight correctness tests using Python assertions.
    """

    assert linear_search([10, 20, 30], 20) == 1
    assert linear_search([10, 20, 30], 99) == -1

    sorted_values = [1, 3, 5, 7, 9]
    assert binary_search(sorted_values, 1) == 0
    assert binary_search(sorted_values, 9) == 4
    assert binary_search(sorted_values, 8) == -1

    assert maximum_subarray_sum([5, -2, 3, 4]) == 10
    assert maximum_subarray_sum([-4, -2, -7]) == -2

    assert pair_sum_sorted([1, 2, 4, 8], 10) == (2, 8)

    values = [1, 2, 3, 4]
    reverse_in_place(values)
    assert values == [4, 3, 2, 1]

    values = [1, 0, 2, 0, 3]
    move_zeros_to_end(values)
    assert values == [1, 2, 3, 0, 0]

    assert merge_sorted_arrays_in_linear_time(
        [1, 3, 5],
        [2, 4, 6],
    ) == [1, 2, 3, 4, 5, 6]

    assert second_largest_distinct([5, 1, 8, 8, 4]) == 5

    assert maximum_sum_fixed_window([2, 1, 5, 1, 3, 2], 3) == 9

    assert range_sum(build_prefix_sums([1, 2, 3, 4]), 1, 3) == 9

    print("All assertion tests passed.")


# =============================================================================
# 50. RANDOMIZED CROSS-CHECKING
# =============================================================================

def randomized_algorithm_test(seed: int = 42, rounds: int = 100) -> None:
    """
    Randomized testing compares an optimized algorithm with a simple
    reference implementation.

    This is useful for finding edge cases that manually selected examples
    may miss.
    """

    random_generator = random.Random(seed)

    for _ in range(rounds):
        length = random_generator.randint(0, 30)
        values = [
            random_generator.randint(-20, 20)
            for _ in range(length)
        ]

        assert find_minimum(values) == min(values) if values else True
        assert find_maximum(values) == max(values) if values else True

        sorted_values = sorted(values)

        for target in range(-5, 6):
            expected = (
                target in sorted_values
            )

            actual = binary_search(sorted_values, target) != -1

            assert actual == expected

    print(f"Randomized tests passed: {rounds} rounds.")


# =============================================================================
# 51. PROPERTY: SORTING DOES NOT CHANGE MULTISET
# =============================================================================

def verify_sort_preserves_elements(
    original: Sequence[int],
    sorting_function: Callable[[list[int]], None],
) -> bool:
    """
    Tests that an in-place sorting algorithm preserves all values.

    Time depends on sorting_function.
    Verification adds O(n log n) here because sorted copies are compared.
    """

    values = list(original)
    expected = sorted(original)

    sorting_function(values)

    return values == expected


# =============================================================================
# 52. COMPLEXITY GROWTH CALCULATOR
# =============================================================================

def theoretical_operation_counts(n: int) -> dict[str, float]:
    """
    Illustrates how common growth rates scale.

    These are mathematical models, not exact execution-time predictions.
    """

    if n < 1:
        raise ValueError("n must be positive.")

    return {
        "O(1)": 1,
        "O(log n)": math.log2(n),
        "O(n)": n,
        "O(n log n)": n * math.log2(n),
        "O(n^2)": n * n,
    }


def demonstrate_growth_rates() -> None:
    for n in [10, 100, 1000, 10_000]:
        print(f"\nn = {n}")

        for name, value in theoretical_operation_counts(n).items():
            print(f"{name:<12}: {value:,.2f}")


# =============================================================================
# 53. WHY O(n + n) BECOMES O(n)
# =============================================================================

def two_linear_passes(values: Sequence[int]) -> tuple[int, int]:
    """
    Two sequential passes:

        O(n) + O(n) = O(2n) = O(n)

    Constant factors are omitted in asymptotic Big-O notation.
    """

    total = 0
    maximum = values[0] if values else 0

    for value in values:
        total += value

    for value in values:
        maximum = max(maximum, value)

    return total, maximum


# =============================================================================
# 54. WHY O(n^2 + n) BECOMES O(n^2)
# =============================================================================

def quadratic_plus_linear(values: Sequence[int]) -> int:
    """
    The dominant term determines asymptotic growth:

        O(n^2 + n) = O(n^2)
    """

    operations = 0

    for _ in values:
        for _ in values:
            operations += 1

    for _ in values:
        operations += 1

    return operations


# =============================================================================
# 55. NESTED LOOPS ARE NOT ALWAYS O(n^2)
# =============================================================================

def triangular_loop(values: Sequence[int]) -> int:
    """
    This has approximately n(n-1)/2 iterations, which is O(n^2).
    """

    operations = 0

    for first in range(len(values)):
        for second in range(first + 1, len(values)):
            operations += 1

    return operations


def logarithmic_loop(n: int) -> int:
    """
    Repeatedly halving n produces O(log n) iterations.
    """

    if n < 1:
        raise ValueError("n must be positive.")

    count = 0

    while n > 1:
        n //= 2
        count += 1

    return count


# =============================================================================
# 56. COMPLEXITY OF ARRAY SLICING
# =============================================================================

def demonstrate_slicing() -> None:
    """
    In Python, list slicing creates a new list.

        values[a:b]

    therefore takes O(k) time and O(k) space for a slice containing k items.

    This differs from simple indexing, which is O(1).
    """

    values = list(range(100))
    subset = values[20:70]

    print("Slice length:", len(subset))
    print("Original unchanged:", values[20] == subset[0])


# =============================================================================
# 57. SLICING VERSUS INDEX ITERATION
# =============================================================================

def sum_slice(values: Sequence[int], start: int, end: int) -> int:
    """
    Creates a slice first.

    Extra temporary space: O(k).
    """

    return sum(values[start:end])


def sum_by_indices(
    values: Sequence[int],
    start: int,
    end: int,
) -> int:
    """
    Avoids creating a temporary slice.

    Extra space: O(1).
    """

    total = 0

    for index in range(start, end):
        total += values[index]

    return total


# =============================================================================
# 58. STATIC ARRAY MEMORY MODEL
# =============================================================================

def static_memory_model(
    capacity: int,
    element_size_bytes: int,
) -> int:
    """
    Simplified contiguous-storage model:

        total bytes = capacity * element size

    Real implementations may have alignment and metadata overhead.
    """

    if capacity < 0 or element_size_bytes < 0:
        raise ValueError("Values cannot be negative.")

    return capacity * element_size_bytes


# =============================================================================
# 59. DYNAMIC ARRAY CAPACITY VERSUS SIZE
# =============================================================================

def demonstrate_size_capacity_difference() -> None:
    array = DynamicArray(8)

    for value in range(3):
        array.append(value)

    print("Logical size:", array.size)
    print("Allocated capacity:", array.capacity)
    print("Unused capacity:", array.capacity - array.size)


# =============================================================================
# 60. SHRINKING DYNAMIC ARRAYS
# =============================================================================

class ShrinkingDynamicArray:
    """
    Demonstrates growth and shrinkage.

    A production implementation normally avoids shrinking on every deletion
    because that could cause repeated grow/shrink cycles.

    Here, capacity is reduced when usage falls below one quarter.
    """

    def __init__(self, capacity: int = 4):
        if capacity < 1:
            raise ValueError("Capacity must be positive.")

        self.data: list[Optional[int]] = [None] * capacity
        self.size = 0

    @property
    def capacity(self) -> int:
        return len(self.data)

    def append(self, value: int) -> None:
        if self.size == self.capacity:
            self.resize(self.capacity * 2)

        self.data[self.size] = value
        self.size += 1

    def pop(self) -> int:
        if self.size == 0:
            raise IndexError("Empty array.")

        self.size -= 1
        value = self.data[self.size]
        self.data[self.size] = None

        if self.size > 0 and self.size <= self.capacity // 4:
            new_capacity = max(1, self.capacity // 2)
            if new_capacity >= self.size:
                self.resize(new_capacity)

        assert value is not None
        return value

    def resize(self, new_capacity: int) -> None:
        if new_capacity < self.size:
            raise ValueError("New capacity cannot be below size.")

        new_data: list[Optional[int]] = [None] * new_capacity

        for index in range(self.size):
            new_data[index] = self.data[index]

        self.data = new_data


def demonstrate_shrinking() -> None:
    array = ShrinkingDynamicArray(4)

    for value in range(20):
        array.append(value)

    print("Before shrinking:", array.size, array.capacity)

    while array.size > 2:
        array.pop()

    print("After shrinking:", array.size, array.capacity)


# =============================================================================
# 61. ARRAY API DESIGN
# =============================================================================

class SafeIntArray:
    """
    A small API demonstrating encapsulation.

    The internal storage is private by convention. Public methods define the
    supported operations and centralize validation.
    """

    def __init__(self, values: Iterable[int] = ()):
        self._values = list(values)

    def get(self, index: int) -> int:
        self._validate(index)
        return self._values[index]

    def set(self, index: int, value: int) -> None:
        self._validate(index)
        self._values[index] = value

    def append(self, value: int) -> None:
        self._values.append(value)

    def values(self) -> list[int]:
        return self._values.copy()

    def _validate(self, index: int) -> None:
        if not 0 <= index < len(self._values):
            raise IndexError("Index out of range.")


# =============================================================================
# 62. PERFORMANCE PRINCIPLE: CHOOSE THE RIGHT OPERATION
# =============================================================================

def choose_array_operation_examples() -> None:
    """
    Demonstrates how algorithm choice follows workload.

    If most operations are:
        - index access: arrays are strong
        - end append: dynamic arrays are strong
        - front insertion: arrays may be inefficient
        - membership tests: hashing may be preferable
        - sorted lookup: binary search can help
    """

    print("Frequent index access -> array")
    print("Frequent end append -> dynamic array")
    print("Frequent front insertion -> consider another data structure")
    print("Frequent membership lookup -> consider a set")
    print("Sorted data + lookup -> binary search")


# =============================================================================
# 63. SECURITY AND ROBUSTNESS
# =============================================================================

def validate_external_array_request(
    requested_size: int,
    maximum_allowed_size: int = 1_000_000,
) -> list[int]:
    """
    Security and reliability consideration:

    Never blindly allocate memory based on untrusted input.

    A malicious or accidental huge size can cause excessive memory use.
    """

    if requested_size < 0:
        raise ValueError("Size cannot be negative.")

    if requested_size > maximum_allowed_size:
        raise ValueError("Requested size exceeds configured limit.")

    return [0] * requested_size


# =============================================================================
# 64. NUMERICAL EDGE CASES
# =============================================================================

def average(values: Sequence[float]) -> float:
    """
    Average calculation.

    Time: O(n)
    Extra space: O(1)

    Empty input is explicitly rejected.
    """

    if not values:
        raise ValueError("Cannot calculate an average of an empty array.")

    return sum(values) / len(values)


# =============================================================================
# 65. ARRAY OF ARRAYS AND IRREGULAR SHAPES
# =============================================================================

def matrix_dimensions(matrix: Sequence[Sequence[int]]) -> tuple[int, int]:
    """
    Returns dimensions when the matrix is rectangular.

    A list of lists can also be jagged, unlike a traditional rectangular
    matrix.
    """

    rows = len(matrix)

    if rows == 0:
        return 0, 0

    columns = len(matrix[0])

    if any(len(row) != columns for row in matrix):
        raise ValueError("Matrix is not rectangular.")

    return rows, columns


# =============================================================================
# 66. REAL-WORLD APPLICATION EXAMPLES
# =============================================================================

def real_world_array_examples() -> None:
    examples = {
        "Sensor readings": "Sequential numeric measurements",
        "Image pixels": "Two-dimensional indexed data",
        "Audio samples": "Ordered signal values",
        "Scores": "Indexed collections of results",
        "Time-series data": "Values ordered by time",
        "Database buffers": "Contiguous blocks of data",
        "Lookup tables": "Direct access using an index",
        "Machine-learning tensors": "Multi-dimensional numerical arrays",
    }

    for application, description in examples.items():
        print(f"{application}: {description}")


# =============================================================================
# 67. COMPLEXITY CHECKLIST
# =============================================================================

def complexity_checklist() -> None:
    """
    A practical process for analyzing an array algorithm.
    """

    checklist = [
        "Identify the input size n.",
        "Count how many times each loop can execute.",
        "Check whether loops are sequential or nested.",
        "Check whether the problem size is halved or reduced.",
        "Account for array slicing and copying.",
        "Account for sorting and searching costs.",
        "Identify temporary arrays and auxiliary structures.",
        "Separate input/output storage from auxiliary space.",
        "Analyze best, average, and worst cases when they differ.",
        "Consider amortized cost for dynamic-array operations.",
    ]

    for item in checklist:
        print("-", item)


# =============================================================================
# 68. COMPLETE DEMONSTRATION SUITE
# =============================================================================

def run_demonstrations() -> None:
    """
    Runs the educational demonstrations in a logical progression.
    """

    print("\n=== Complexity fundamentals ===")
    demonstrate_complexity_notation()

    print("\n=== Basic array model ===")
    demonstrate_basic_array_model()

    print("\n=== Operation complexity ===")
    array_operation_complexity_table()

    print("\n=== Access and update ===")
    array_access_and_update([10, 20, 30, 40])

    print("\n=== Traversal ===")
    print(traverse_array([1, 2, 3, 4, 5]))

    print("\n=== Linear search ===")
    demonstrate_linear_search()

    print("\n=== Binary search ===")
    demonstrate_binary_search()

    print("\n=== Static array ===")
    demonstrate_static_array()

    print("\n=== Dynamic array ===")
    demonstrate_dynamic_array()

    print("\n=== Amortized analysis ===")
    demonstrate_amortized_analysis()

    print("\n=== Insertions ===")
    demonstrate_insertions()

    print("\n=== Deletions ===")
    demonstrate_deletion()

    print("\n=== Duplicate detection ===")
    demonstrate_duplicate_tradeoff()

    print("\n=== In-place versus copied reversal ===")
    demonstrate_space_tradeoff()

    print("\n=== Prefix sums ===")
    demonstrate_prefix_sums()

    print("\n=== Two pointers ===")
    demonstrate_two_pointers()

    print("\n=== Sliding window ===")
    demonstrate_sliding_window()

    print("\n=== Kadane's algorithm ===")
    demonstrate_kadane()

    print("\n=== Two-dimensional arrays ===")
    demonstrate_matrix()

    print("\n=== Matrix aliasing ===")
    demonstrate_matrix_aliasing()

    print("\n=== Sorting complexity ===")
    demonstrate_sorting_complexities()

    sample = [7, 2, 9, 1, 5, 3]

    selection = sample.copy()
    selection_sort(selection)
    print("Selection sort:", selection)

    insertion = sample.copy()
    insertion_sort(insertion)
    print("Insertion sort:", insertion)

    merge = merge_sort(sample)
    print("Merge sort:", merge)

    quick = sample.copy()
    quick_sort(quick)
    print("Quick sort:", quick)

    print("\n=== Range sum strategies ===")
    compare_range_sum_strategies()

    print("\n=== Space complexity ===")
    demonstrate_space_complexity()

    print("\n=== Static versus dynamic ===")
    compare_static_and_dynamic_arrays()

    print("\n=== Python list ===")
    demonstrate_python_list()

    print("\n=== Timing ===")
    demonstrate_operation_timing()

    print("\n=== Access versus search ===")
    demonstrate_access_vs_search()

    print("\n=== Best and worst cases ===")
    explain_cases_with_search()

    print("\n=== Edge cases ===")
    demonstrate_edge_cases()

    print("\n=== Second largest ===")
    demonstrate_second_largest()

    print("\n=== Rotation ===")
    demonstrate_rotation()

    print("\n=== Partition ===")
    demonstrate_partition()

    print("\n=== Size versus capacity ===")
    demonstrate_size_capacity_difference()

    print("\n=== Shrinking ===")
    demonstrate_shrinking()

    print("\n=== Growth rates ===")
    demonstrate_growth_rates()

    print("\n=== Slicing ===")
    demonstrate_slicing()

    print("\n=== Amortized append ===")
    demonstrate_amortized_append_concept()

    print("\n=== Array operation selection ===")
    choose_array_operation_examples()

    print("\n=== Real-world applications ===")
    real_world_array_examples()

    print("\n=== Complexity checklist ===")
    complexity_checklist()


# =============================================================================
# 69. MAIN ENTRY POINT
# =============================================================================

def main() -> None:
    """
    Main program entry point.

    Assertions run before demonstrations so correctness checks occur before
    the educational output.
    """

    print("=" * 80)
    print("ARRAY COMPLEXITY STUDY SCRIPT")
    print("=" * 80)

    run_assertion_tests()
    randomized_algorithm_test()

    print("\n=== Additional demonstrations ===")
    run_demonstrations()

    print("\n=== Final verification ===")

    original = [9, 1, 8, 2, 7, 3]
    assert verify_sort_preserves_elements(original, selection_sort)
    assert verify_sort_preserves_elements(original, insertion_sort)
    assert verify_sort_preserves_elements(original, quick_sort)

    print("Sorting verification passed.")

    print(
        "Python version:",
        sys.version.split()[0],
    )


if __name__ == "__main__":
    main()
