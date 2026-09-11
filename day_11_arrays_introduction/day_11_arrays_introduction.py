"""
Arrays Introduction: From Fundamentals to Advanced Operations

This standalone study script teaches arrays from absolute beginner level through
advanced implementation details. It covers:

1. What an array is
2. Array terminology and characteristics
3. Memory representation
4. Indexing and negative indexing
5. Traversal
6. Updating elements
7. Insertion
8. Deletion
9. Searching
10. Linear search
11. Binary search
12. Complexity analysis
13. Python lists versus typed arrays
14. Fixed-size arrays
15. Dynamic arrays and resizing
16. A complete dynamic array implementation
17. Two-dimensional arrays
18. Jagged arrays
19. Searching and duplicate handling
20. Edge cases and validation
21. Common mistakes
22. Practical algorithms
23. Testing
24. Performance measurements
25. Production-oriented considerations

The examples use only Python's standard library.
"""

from __future__ import annotations

from array import array
import random
import sys
import time
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar


# ============================================================================
# 1. FUNDAMENTAL CONCEPT: WHAT IS AN ARRAY?
# ============================================================================

print("=" * 80)
print("1. WHAT IS AN ARRAY?")
print("=" * 80)

# An array is a data structure that stores multiple values under one name.
# In traditional array implementations, elements are stored in contiguous
# memory locations and have the same data type.
#
# Example:
#
#   index:    0    1    2    3    4
#   value:   10   20   30   40   50
#
# The first element is at index 0, not index 1.

numbers = [10, 20, 30, 40, 50]

print("Array-like structure:", numbers)
print("Number of elements:", len(numbers))
print("First element:", numbers[0])
print("Last element:", numbers[4])


# ============================================================================
# 2. ARRAY TERMINOLOGY
# ============================================================================

print("\n" + "=" * 80)
print("2. ARRAY TERMINOLOGY")
print("=" * 80)

# Important terminology:
#
# Element:
#   A single value stored in an array.
#
# Index:
#   The numerical position used to access an element.
#
# Length/size:
#   Number of logical elements currently stored.
#
# Capacity:
#   Number of elements that can be stored before additional memory is needed.
#   This distinction is particularly important for dynamic arrays.
#
# Traversal:
#   Visiting elements one by one.
#
# Insertion:
#   Adding an element.
#
# Deletion:
#   Removing an element.
#
# Update:
#   Replacing an existing element.
#
# Search:
#   Finding an element or its position.

students = ["Asha", "Ravi", "Meera", "Kabir"]

print("Element at index 0:", students[0])
print("Element at index 2:", students[2])
print("Length:", len(students))


# ============================================================================
# 3. INDEXING
# ============================================================================

print("\n" + "=" * 80)
print("3. INDEXING")
print("=" * 80)

values = [100, 200, 300, 400, 500]

# Positive indexes start at zero.
for index in range(len(values)):
    print(f"Index {index}: {values[index]}")

# Python also supports negative indexes.
# -1 means the final element, -2 means the second-to-last element, and so on.
print("Last element using -1:", values[-1])
print("Second-last element using -2:", values[-2])

# Valid positive indexes are:
# 0 through len(array) - 1.
#
# Attempting an invalid index raises IndexError.

try:
    print(values[10])
except IndexError as error:
    print("Invalid index:", error)


# ============================================================================
# 4. MEMORY REPRESENTATION
# ============================================================================

print("\n" + "=" * 80)
print("4. MEMORY REPRESENTATION")
print("=" * 80)

# Traditional fixed-type arrays store elements in contiguous memory.
#
# If each element requires B bytes and the first element starts at address A,
# the address of element i can conceptually be calculated as:
#
#     address(i) = A + i * B
#
# This direct address calculation is why array indexing is O(1).
#
# Python's built-in list is more accurately described as a dynamic array of
# references. The references are stored in a contiguous internal array, while
# the actual Python objects may exist elsewhere in memory.
#
# The array module provides a more traditional typed-array representation.

typed_numbers = array("i", [10, 20, 30, 40, 50])

print("Typed array:", typed_numbers)
print("Element at index 3:", typed_numbers[3])
print("Type code:", typed_numbers.typecode)
print("Bytes per item:", typed_numbers.itemsize)
print("Number of elements:", len(typed_numbers))
print("Raw byte size:", typed_numbers.buffer_info()[1] * typed_numbers.itemsize)

# sys.getsizeof() measures the Python object's memory footprint, which is not
# necessarily identical to the total memory occupied by referenced objects.
python_list = [10, 20, 30, 40, 50]
print("Python list object size:", sys.getsizeof(python_list))
print("Typed array object size:", sys.getsizeof(typed_numbers))


# ============================================================================
# 5. TRAVERSAL
# ============================================================================

print("\n" + "=" * 80)
print("5. TRAVERSAL")
print("=" * 80)

numbers = [15, 25, 35, 45, 55]

# Direct traversal is appropriate when only values are required.
print("Values:")
for number in numbers:
    print(number)

# Index-based traversal is useful when the position is required.
print("Index and value:")
for index in range(len(numbers)):
    print(index, numbers[index])

# enumerate() provides both index and value cleanly.
print("Using enumerate():")
for index, number in enumerate(numbers):
    print(index, number)


# ============================================================================
# 6. UPDATE OPERATION
# ============================================================================

print("\n" + "=" * 80)
print("6. UPDATE OPERATION")
print("=" * 80)

scores = [72, 81, 65, 90, 88]

print("Before update:", scores)

# Updating an element by index is O(1).
scores[2] = 75

print("After updating index 2:", scores)


# ============================================================================
# 7. INSERTION
# ============================================================================

print("\n" + "=" * 80)
print("7. INSERTION")
print("=" * 80)

numbers = [10, 20, 30, 40]

# Appending at the end is usually O(1) amortized for a dynamic array.
numbers.append(50)
print("After append:", numbers)

# Inserting at an arbitrary position requires shifting elements.
# This is O(n) in the worst case.
numbers.insert(2, 25)
print("After inserting 25 at index 2:", numbers)

# Insert at the beginning requires shifting all existing elements.
numbers.insert(0, 5)
print("After inserting 5 at beginning:", numbers)


# ============================================================================
# 8. DELETION
# ============================================================================

print("\n" + "=" * 80)
print("8. DELETION")
print("=" * 80)

numbers = [10, 20, 30, 40, 50]

# Removing the final element is O(1) amortized for a dynamic array.
removed = numbers.pop()
print("Removed:", removed)
print("Array:", numbers)

# Removing by index from the middle requires shifting later elements.
removed = numbers.pop(1)
print("Removed index 1:", removed)
print("Array:", numbers)

# remove(value) searches for the value first, then shifts elements.
numbers.remove(40)
print("After remove(40):", numbers)


# ============================================================================
# 9. SEARCHING
# ============================================================================

print("\n" + "=" * 80)
print("9. SEARCHING")
print("=" * 80)

numbers = [12, 24, 36, 48, 60]

# Membership testing on a list performs a linear search.
print("36 exists:", 36 in numbers)
print("99 exists:", 99 in numbers)

# index() returns the first matching position.
print("Index of 48:", numbers.index(48))

try:
    print(numbers.index(99))
except ValueError:
    print("99 is not present.")


# ============================================================================
# 10. LINEAR SEARCH
# ============================================================================

print("\n" + "=" * 80)
print("10. LINEAR SEARCH")
print("=" * 80)


def linear_search(values: list[int], target: int) -> int:
    """
    Return the first index containing target.

    Time complexity:
        Best case: O(1)
        Average case: O(n)
        Worst case: O(n)

    Space complexity:
        O(1)
    """
    for index, value in enumerate(values):
        if value == target:
            return index

    return -1


numbers = [7, 14, 21, 28, 35]

print("Search for 21:", linear_search(numbers, 21))
print("Search for 100:", linear_search(numbers, 100))


# ============================================================================
# 11. LINEAR SEARCH WITH ALL MATCHES
# ============================================================================

print("\n" + "=" * 80)
print("11. FINDING ALL OCCURRENCES")
print("=" * 80)


def find_all_occurrences(values: list[int], target: int) -> list[int]:
    """Return every index at which target occurs."""
    return [
        index
        for index, value in enumerate(values)
        if value == target
    ]


numbers = [5, 2, 5, 8, 5, 10]

print("Array:", numbers)
print("All positions of 5:", find_all_occurrences(numbers, 5))


# ============================================================================
# 12. BINARY SEARCH
# ============================================================================

print("\n" + "=" * 80)
print("12. BINARY SEARCH")
print("=" * 80)

# Binary search requires a sorted array.
#
# Instead of checking every element, binary search repeatedly divides the
# search interval approximately in half.
#
# Time complexity:
#     Best case: O(1)
#     Average/worst case: O(log n)
#
# Space complexity:
#     O(1) for this iterative implementation.


def binary_search(values: list[int], target: int) -> int:
    """Return the index of target in a sorted list, or -1 if absent."""
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


sorted_numbers = [3, 8, 14, 21, 27, 35, 42]

print("Sorted array:", sorted_numbers)
print("Binary search for 27:", binary_search(sorted_numbers, 27))
print("Binary search for 100:", binary_search(sorted_numbers, 100))


# ============================================================================
# 13. BINARY SEARCH: IMPORTANT PRECONDITION
# ============================================================================

print("\n" + "=" * 80)
print("13. BINARY SEARCH PRECONDITION")
print("=" * 80)

# Binary search is not a general replacement for linear search.
# The data must be ordered according to the comparison being used.

unsorted_numbers = [30, 10, 50, 20, 40]

print("Unsorted data:", unsorted_numbers)
print(
    "Binary search on unsorted data is not reliable:",
    binary_search(unsorted_numbers, 20),
)

sorted_numbers = sorted(unsorted_numbers)
print("Sorted data:", sorted_numbers)
print(
    "Binary search after sorting:",
    binary_search(sorted_numbers, 20),
)


# ============================================================================
# 14. ARRAY OPERATION COMPLEXITIES
# ============================================================================

print("\n" + "=" * 80)
print("14. COMMON ARRAY OPERATION COMPLEXITIES")
print("=" * 80)

# Random access by index:
#     O(1)
#
# Update by index:
#     O(1)
#
# Traversal:
#     O(n)
#
# Linear search:
#     O(n)
#
# Binary search on sorted data:
#     O(log n)
#
# Insertion at beginning/middle:
#     O(n)
#
# Deletion at beginning/middle:
#     O(n)
#
# Append:
#     O(1) amortized for a dynamic array.
#
# Sorting:
#     Usually O(n log n) for efficient comparison-based algorithms.

complexities = {
    "Access by index": "O(1)",
    "Update by index": "O(1)",
    "Traversal": "O(n)",
    "Linear search": "O(n)",
    "Binary search": "O(log n), sorted data required",
    "Insert at beginning": "O(n)",
    "Delete from middle": "O(n)",
    "Append": "O(1) amortized",
}

for operation, complexity in complexities.items():
    print(f"{operation}: {complexity}")


# ============================================================================
# 15. FIXED-SIZE ARRAY CONCEPT
# ============================================================================

print("\n" + "=" * 80)
print("15. FIXED-SIZE ARRAY CONCEPT")
print("=" * 80)

# A traditional fixed-size array has a predetermined capacity.
# Once full, inserting another element requires a different allocation.
#
# Python lists are not fixed-size, so we implement a small fixed-size array
# to demonstrate the concept explicitly.


class FixedArray:
    """Simple fixed-capacity array for educational purposes."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")

        self._capacity = capacity
        self._data: list[Optional[int]] = [None] * capacity
        self._size = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size

    def _validate_index(self, index: int) -> None:
        if not 0 <= index < self._size:
            raise IndexError("Index is outside the logical array.")

    def get(self, index: int) -> int:
        self._validate_index(index)
        value = self._data[index]

        if value is None:
            raise RuntimeError("Internal storage inconsistency.")

        return value

    def set(self, index: int, value: int) -> None:
        self._validate_index(index)
        self._data[index] = value

    def append(self, value: int) -> None:
        if self._size >= self._capacity:
            raise OverflowError("Fixed array is full.")

        self._data[self._size] = value
        self._size += 1

    def __repr__(self) -> str:
        return repr(self._data[: self._size])


fixed = FixedArray(3)
fixed.append(10)
fixed.append(20)
fixed.append(30)

print("Fixed array:", fixed)
print("Size:", fixed.size)
print("Capacity:", fixed.capacity)

try:
    fixed.append(40)
except OverflowError as error:
    print("Expected capacity error:", error)


# ============================================================================
# 16. DYNAMIC ARRAYS
# ============================================================================

print("\n" + "=" * 80)
print("16. DYNAMIC ARRAYS")
print("=" * 80)

# A dynamic array maintains a larger storage capacity than its current logical
# size. When the capacity becomes full, it allocates a larger block and copies
# existing elements.
#
# This makes individual resize operations expensive, but repeated appends have
# O(1) amortized complexity when the growth strategy is appropriate.
#
# Typical growth strategies increase capacity by a multiplicative factor,
# such as 1.5x or 2x. A larger growth factor reduces resize frequency but may
# temporarily consume more memory.


T = TypeVar("T")


class DynamicArray(Generic[T]):
    """
    Educational implementation of a dynamic array.

    This implementation stores references in a Python list but explicitly
    manages logical size and capacity so the underlying algorithm is visible.
    """

    def __init__(
        self,
        initial_capacity: int = 4,
        values: Optional[Iterable[T]] = None,
    ):
        if initial_capacity < 1:
            raise ValueError("Initial capacity must be at least 1.")

        self._capacity = initial_capacity
        self._size = 0
        self._data: list[Optional[T]] = [None] * self._capacity

        if values is not None:
            for value in values:
                self.append(value)

    @property
    def size(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    def _validate_index(self, index: int) -> None:
        if not 0 <= index < self._size:
            raise IndexError(
                f"Index {index} is invalid for size {self._size}."
            )

    def _resize(self, new_capacity: int) -> None:
        if new_capacity < self._size:
            raise ValueError("New capacity cannot be smaller than size.")

        new_data: list[Optional[T]] = [None] * new_capacity

        for index in range(self._size):
            new_data[index] = self._data[index]

        self._data = new_data
        self._capacity = new_capacity

    def append(self, value: T) -> None:
        if self._size == self._capacity:
            # Doubling capacity provides amortized O(1) append.
            self._resize(self._capacity * 2)

        self._data[self._size] = value
        self._size += 1

    def get(self, index: int) -> T:
        self._validate_index(index)

        value = self._data[index]

        if value is None:
            raise RuntimeError("Internal storage inconsistency.")

        return value

    def set(self, index: int, value: T) -> None:
        self._validate_index(index)
        self._data[index] = value

    def insert(self, index: int, value: T) -> None:
        if not 0 <= index <= self._size:
            raise IndexError("Insertion index is invalid.")

        if self._size == self._capacity:
            self._resize(self._capacity * 2)

        # Shift elements one position to the right.
        for position in range(self._size, index, -1):
            self._data[position] = self._data[position - 1]

        self._data[index] = value
        self._size += 1

    def pop(self, index: Optional[int] = None) -> T:
        if self._size == 0:
            raise IndexError("Cannot remove from an empty array.")

        if index is None:
            index = self._size - 1

        self._validate_index(index)

        removed = self._data[index]

        # Shift elements left to close the gap.
        for position in range(index, self._size - 1):
            self._data[position] = self._data[position + 1]

        self._data[self._size - 1] = None
        self._size -= 1

        if removed is None:
            raise RuntimeError("Internal storage inconsistency.")

        # Shrink only when the array becomes significantly underutilized.
        # Avoiding aggressive shrinking prevents repeated grow-shrink cycles.
        if self._size > 0 and self._size <= self._capacity // 4:
            new_capacity = max(1, self._capacity // 2)

            if new_capacity >= self._size:
                self._resize(new_capacity)

        return removed

    def linear_search(self, target: T) -> int:
        for index in range(self._size):
            if self._data[index] == target:
                return index

        return -1

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        for index in range(self._size):
            value = self._data[index]

            if value is None:
                raise RuntimeError("Internal storage inconsistency.")

            yield value

    def __repr__(self) -> str:
        return repr(list(self))


dynamic = DynamicArray[int](initial_capacity=2)

for value in [10, 20, 30, 40, 50]:
    dynamic.append(value)
    print(
        f"After append({value}): "
        f"size={dynamic.size}, capacity={dynamic.capacity}, data={dynamic}"
    )

dynamic.insert(2, 25)
print("After insert(2, 25):", dynamic)

dynamic.set(0, 5)
print("After set(0, 5):", dynamic)

print("Value at index 3:", dynamic.get(3))
print("Position of 40:", dynamic.linear_search(40))

removed_value = dynamic.pop(2)
print("Removed:", removed_value)
print("After removal:", dynamic)


# ============================================================================
# 17. WHY AMORTIZED O(1) APPEND?
# ============================================================================

print("\n" + "=" * 80)
print("17. AMORTIZED APPEND")
print("=" * 80)

# Most appends only place the new value into the next free slot.
# Occasionally, a resize occurs and all existing elements are copied.
#
# Example with doubling:
#
# capacity: 1 -> 2 -> 4 -> 8 -> 16
#
# Although one resize may cost O(n), expensive resizes happen increasingly
# rarely. Across n appends, the total copying work is O(n), giving:
#
#     O(n) total work / n operations = O(1) amortized per append.

dynamic = DynamicArray[int](initial_capacity=1)

for value in range(10):
    old_capacity = dynamic.capacity
    dynamic.append(value)

    if dynamic.capacity != old_capacity:
        print(
            f"Resize occurred at size {dynamic.size}: "
            f"{old_capacity} -> {dynamic.capacity}"
        )


# ============================================================================
# 18. INSERTION BY SHIFTING
# ============================================================================

print("\n" + "=" * 80)
print("18. INSERTION BY SHIFTING")
print("=" * 80)

# Suppose:
#
# [10, 20, 30, 40]
#
# Insert 99 at index 1:
#
# [10, 99, 20, 30, 40]
#
# Elements 20, 30 and 40 must move one position to the right.
#
# Therefore insertion in the middle is O(n).

values = [10, 20, 30, 40]

index = 1
value = 99

values.append(None)
for position in range(len(values) - 1, index, -1):
    values[position] = values[position - 1]

values[index] = value

print("After manual insertion:", values)


# ============================================================================
# 19. DELETION BY SHIFTING
# ============================================================================

print("\n" + "=" * 80)
print("19. DELETION BY SHIFTING")
print("=" * 80)

# Suppose:
#
# [10, 20, 30, 40, 50]
#
# Delete index 1:
#
# [10, 30, 40, 50]
#
# Elements after the deleted element move one position to the left.

values = [10, 20, 30, 40, 50]

delete_index = 1

for position in range(delete_index, len(values) - 1):
    values[position] = values[position + 1]

values.pop()

print("After manual deletion:", values)


# ============================================================================
# 20. ACCESS, SEARCH AND INSERT COMPARISON
# ============================================================================

print("\n" + "=" * 80)
print("20. ARRAY OPERATION COMPARISON")
print("=" * 80)

comparison = [
    ("Access by index", "O(1)", "No shifting required"),
    ("Update by index", "O(1)", "Direct location"),
    ("Traversal", "O(n)", "Every element may be visited"),
    ("Linear search", "O(n)", "May inspect every element"),
    ("Binary search", "O(log n)", "Requires sorted data"),
    ("Insert at end", "O(1) amortized", "Resize may occasionally occur"),
    ("Insert at beginning", "O(n)", "Elements must shift right"),
    ("Delete at end", "O(1) amortized", "No shifting required"),
    ("Delete at beginning", "O(n)", "Elements must shift left"),
]

for operation, complexity, reason in comparison:
    print(f"{operation:<25} {complexity:<18} {reason}")


# ============================================================================
# 21. TWO-DIMENSIONAL ARRAYS
# ============================================================================

print("\n" + "=" * 80)
print("21. TWO-DIMENSIONAL ARRAYS")
print("=" * 80)

# A two-dimensional array can be viewed as rows and columns.
#
# Example:
#
#     1 2 3
#     4 5 6
#
# Accessing row 1, column 2 gives 6 when using zero-based indexing.

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

print("Matrix:", matrix)
print("Row 1, column 2:", matrix[1][2])

print("Matrix traversal:")
for row in matrix:
    for value in row:
        print(value, end=" ")
    print()


# ============================================================================
# 22. SAFE 2D ARRAY CREATION
# ============================================================================

print("\n" + "=" * 80)
print("22. SAFE 2D ARRAY CREATION")
print("=" * 80)

# A common Python mistake is:
#
#     matrix = [[0] * columns] * rows
#
# This creates multiple references to the same inner list.
#
# Correct approach:
#     matrix = [[0 for _ in range(columns)] for _ in range(rows)]

rows = 3
columns = 4

correct_matrix = [
    [0 for _ in range(columns)]
    for _ in range(rows)
]

correct_matrix[0][0] = 99

print("Correct independent rows:")
for row in correct_matrix:
    print(row)


# ============================================================================
# 23. JAGGED ARRAYS
# ============================================================================

print("\n" + "=" * 80)
print("23. JAGGED ARRAYS")
print("=" * 80)

# A jagged array contains rows of different lengths.
#
# It is useful when every row does not require the same number of elements.

jagged = [
    [1, 2],
    [3, 4, 5],
    [6],
    [7, 8, 9, 10],
]

for row_index, row in enumerate(jagged):
    print(f"Row {row_index}: {row}")


# ============================================================================
# 24. ARRAY AGGREGATION
# ============================================================================

print("\n" + "=" * 80)
print("24. AGGREGATION")
print("=" * 80)

values = [12, 18, 25, 31, 14]

total = sum(values)
minimum = min(values)
maximum = max(values)
average = total / len(values)

print("Values:", values)
print("Sum:", total)
print("Minimum:", minimum)
print("Maximum:", maximum)
print("Average:", average)


# ============================================================================
# 25. MANUAL MINIMUM AND MAXIMUM
# ============================================================================

print("\n" + "=" * 80)
print("25. MANUAL MINIMUM AND MAXIMUM")
print("=" * 80)


def find_minimum(values: list[int]) -> int:
    if not values:
        raise ValueError("Cannot find minimum of an empty array.")

    current_minimum = values[0]

    for value in values[1:]:
        if value < current_minimum:
            current_minimum = value

    return current_minimum


def find_maximum(values: list[int]) -> int:
    if not values:
        raise ValueError("Cannot find maximum of an empty array.")

    current_maximum = values[0]

    for value in values[1:]:
        if value > current_maximum:
            current_maximum = value

    return current_maximum


values = [45, 12, 89, 34, 7, 56]

print("Manual minimum:", find_minimum(values))
print("Manual maximum:", find_maximum(values))


# ============================================================================
# 26. REVERSE AN ARRAY
# ============================================================================

print("\n" + "=" * 80)
print("26. REVERSING AN ARRAY")
print("=" * 80)


def reverse_in_place(values: list[T]) -> None:
    """
    Reverse the array in place.

    Time complexity: O(n)
    Extra space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left < right:
        values[left], values[right] = values[right], values[left]
        left += 1
        right -= 1


values = [1, 2, 3, 4, 5]

reverse_in_place(values)

print("Reversed in place:", values)


# ============================================================================
# 27. ROTATE AN ARRAY
# ============================================================================

print("\n" + "=" * 80)
print("27. ARRAY ROTATION")
print("=" * 80)


def rotate_right(values: list[T], positions: int) -> None:
    """
    Rotate an array to the right in place.

    Example:
        [1, 2, 3, 4, 5], positions=2
        becomes
        [4, 5, 1, 2, 3]

    The slice implementation is easy to understand but uses O(n) temporary
    storage. The complexity is still O(n).
    """
    if not values:
        return

    positions %= len(values)

    if positions:
        values[:] = values[-positions:] + values[:-positions]


values = [1, 2, 3, 4, 5]
rotate_right(values, 2)

print("Rotated array:", values)


# ============================================================================
# 28. DUPLICATE DETECTION
# ============================================================================

print("\n" + "=" * 80)
print("28. DUPLICATE DETECTION")
print("=" * 80)


def contains_duplicate(values: list[int]) -> bool:
    """
    Detect whether any value occurs more than once.

    Average time: O(n)
    Extra space: O(n)
    """
    seen: set[int] = set()

    for value in values:
        if value in seen:
            return True

        seen.add(value)

    return False


print("Duplicates in [1, 2, 3, 4]:",
      contains_duplicate([1, 2, 3, 4]))

print("Duplicates in [1, 2, 3, 2]:",
      contains_duplicate([1, 2, 3, 2]))


# ============================================================================
# 29. TWO-SUM USING AN ARRAY
# ============================================================================

print("\n" + "=" * 80)
print("29. TWO-SUM")
print("=" * 80)


def two_sum(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Return indexes of two values whose sum equals target.

    Average time: O(n)
    Extra space: O(n)
    """
    seen: dict[int, int] = {}

    for index, value in enumerate(values):
        required = target - value

        if required in seen:
            return seen[required], index

        seen[value] = index

    return None


values = [2, 7, 11, 15]

print("Values:", values)
print("Target 9:", two_sum(values, 9))


# ============================================================================
# 30. PREFIX SUM ARRAY
# ============================================================================

print("\n" + "=" * 80)
print("30. PREFIX SUM ARRAY")
print("=" * 80)

# A prefix sum array stores cumulative sums.
#
# Original:
#     [2, 4, 6, 8]
#
# Prefix:
#     [2, 6, 12, 20]
#
# Once built, a range sum can be answered in O(1).

values = [2, 4, 6, 8, 10]

prefix = [0] * (len(values) + 1)

for index, value in enumerate(values):
    prefix[index + 1] = prefix[index] + value

print("Values:", values)
print("Prefix sums:", prefix)


def range_sum(prefix_sums: list[int], left: int, right: int) -> int:
    """
    Return the inclusive range sum values[left:right+1].

    Requires:
        0 <= left <= right < original array length.
    """
    if left < 0 or right < left or right >= len(prefix_sums) - 1:
        raise IndexError("Invalid range.")

    return prefix_sums[right + 1] - prefix_sums[left]


print("Sum from index 1 to 3:", range_sum(prefix, 1, 3))


# ============================================================================
# 31. SORTING AND SEARCHING
# ============================================================================

print("\n" + "=" * 80)
print("31. SORTING AND SEARCHING")
print("=" * 80)

values = [45, 12, 78, 3, 29, 56]

print("Original:", values)

values.sort()

print("Sorted:", values)
print("Binary search for 29:", binary_search(values, 29))


# ============================================================================
# 32. STABLE SEARCH FOR FIRST OCCURRENCE
# ============================================================================

print("\n" + "=" * 80)
print("32. FIRST OCCURRENCE IN SORTED DATA")
print("=" * 80)


def first_occurrence(values: list[int], target: int) -> int:
    """
    Return the first index of target in sorted data.

    This modified binary search continues toward the left after finding
    the target.
    """
    left = 0
    right = len(values) - 1
    result = -1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            result = middle
            right = middle - 1
        elif values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return result


values = [1, 2, 2, 2, 4, 5, 5, 9]

print("Array:", values)
print("First occurrence of 2:", first_occurrence(values, 2))
print("First occurrence of 5:", first_occurrence(values, 5))


# ============================================================================
# 33. LAST OCCURRENCE
# ============================================================================


def last_occurrence(values: list[int], target: int) -> int:
    """Return the last index of target in sorted data."""
    left = 0
    right = len(values) - 1
    result = -1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            result = middle
            left = middle + 1
        elif values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return result


print("Last occurrence of 2:", last_occurrence(values, 2))
print("Last occurrence of 5:", last_occurrence(values, 5))


# ============================================================================
# 34. EDGE CASES
# ============================================================================

print("\n" + "=" * 80)
print("34. EDGE CASES")
print("=" * 80)

# Important array edge cases include:
#
# 1. Empty array
# 2. Single-element array
# 3. Duplicate values
# 4. Negative values
# 5. Very large values
# 6. Target absent
# 7. Target at first position
# 8. Target at final position
# 9. Invalid indexes
# 10. Insertion into an empty array
# 11. Deletion from an empty array
# 12. Binary search on unsorted data

test_cases = [
    [],
    [10],
    [5, 5, 5],
    [-10, -5, 0, 5, 10],
]

for case in test_cases:
    print("Case:", case)

    if case:
        print("  First:", case[0])
        print("  Last:", case[-1])
        print("  Length:", len(case))
    else:
        print("  Empty array")


# ============================================================================
# 35. SAFE ACCESS FUNCTION
# ============================================================================

print("\n" + "=" * 80)
print("35. SAFE ACCESS")
print("=" * 80)


def safe_get(values: list[T], index: int) -> Optional[T]:
    """
    Return an element if the index is valid; otherwise return None.

    This is useful when an invalid position is an expected condition rather
    than an exceptional programming error.
    """
    if 0 <= index < len(values):
        return values[index]

    return None


values = [10, 20, 30]

print("safe_get index 1:", safe_get(values, 1))
print("safe_get index 10:", safe_get(values, 10))


# ============================================================================
# 36. ARRAY VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("36. INPUT VALIDATION")
print("=" * 80)


def require_non_empty(values: list[T]) -> None:
    """Raise an error when an operation requires at least one element."""
    if not values:
        raise ValueError("The array must contain at least one element.")


def average(values: list[float]) -> float:
    """Calculate an average while rejecting an empty array."""
    require_non_empty(values)
    return sum(values) / len(values)


print("Average:", average([10.0, 20.0, 30.0]))

try:
    average([])
except ValueError as error:
    print("Expected validation error:", error)


# ============================================================================
# 37. ARRAY OF OBJECTS
# ============================================================================

print("\n" + "=" * 80)
print("37. ARRAYS OF OBJECTS")
print("=" * 80)


@dataclass
class Employee:
    name: str
    department: str
    salary: float


employees = [
    Employee("Anita", "Engineering", 85000),
    Employee("Rohan", "Finance", 72000),
    Employee("Priya", "Engineering", 91000),
]

for employee in employees:
    print(employee.name, employee.department, employee.salary)

engineering_employees = [
    employee
    for employee in employees
    if employee.department == "Engineering"
]

print("Engineering employees:")
for employee in engineering_employees:
    print(employee.name)


# ============================================================================
# 38. SEARCHING OBJECT ARRAYS
# ============================================================================

print("\n" + "=" * 80)
print("38. SEARCHING ARRAYS OF OBJECTS")
print("=" * 80)


def find_employee(
    employees: list[Employee],
    name: str,
) -> Optional[Employee]:
    """Linear search through an array of Employee objects."""
    for employee in employees:
        if employee.name == name:
            return employee

    return None


employee = find_employee(employees, "Priya")

if employee is not None:
    print("Found:", employee)
else:
    print("Employee not found.")


# ============================================================================
# 39. ARRAY SLICING
# ============================================================================

print("\n" + "=" * 80)
print("39. ARRAY SLICING")
print("=" * 80)

values = [0, 1, 2, 3, 4, 5, 6, 7]

print("First four:", values[:4])
print("Indexes 2 through 5:", values[2:6])
print("Every second element:", values[::2])
print("Reversed copy:", values[::-1])

# A slice creates a new list, so modifying the slice does not change the
# original list itself.

subset = values[2:5]
subset[0] = 999

print("Modified slice:", subset)
print("Original array:", values)


# ============================================================================
# 40. SHALLOW COPY CONSIDERATION
# ============================================================================

print("\n" + "=" * 80)
print("40. SHALLOW COPY AND REFERENCES")
print("=" * 80)

# Python lists contain references to objects.
# A shallow copy creates a new outer list but does not recursively copy
# contained mutable objects.

nested = [[1, 2], [3, 4]]

shallow_copy = nested.copy()
shallow_copy[0][0] = 999

print("Original nested list:", nested)
print("Shallow copy:", shallow_copy)

# This behavior matters when an array contains mutable objects.


# ============================================================================
# 41. LIST COMPREHENSIONS FOR ARRAY TRANSFORMATION
# ============================================================================

print("\n" + "=" * 80)
print("41. ARRAY TRANSFORMATION")
print("=" * 80)

values = [1, 2, 3, 4, 5, 6]

squares = [value * value for value in values]
even_values = [value for value in values if value % 2 == 0]

print("Original:", values)
print("Squares:", squares)
print("Even values:", even_values)


# ============================================================================
# 42. MEMORY-EFFICIENT TYPED ARRAYS
# ============================================================================

print("\n" + "=" * 80)
print("42. TYPED ARRAYS")
print("=" * 80)

# array.array stores values using a specified C-compatible type code.
#
# Common examples:
#     'i' = signed integer
#     'f' = floating-point value
#     'd' = double-precision floating-point value
#
# Unlike Python lists, typed arrays do not store a separate Python object
# reference for every numeric value.

integer_array = array("i", [1, 2, 3, 4, 5])
floating_array = array("d", [1.5, 2.5, 3.5])

print("Integer typed array:", integer_array)
print("Floating typed array:", floating_array)

integer_array.append(6)
print("After append:", integer_array)


# ============================================================================
# 43. ARRAY VERSUS LIST
# ============================================================================

print("\n" + "=" * 80)
print("43. PYTHON LIST VERSUS TYPED ARRAY")
print("=" * 80)

# Python list:
#     - Flexible
#     - Can contain different object types
#     - Rich built-in operations
#     - Dynamic resizing
#     - Stores references to Python objects
#
# array.array:
#     - Typed
#     - More memory-efficient for many primitive numeric values
#     - More restrictive
#     - Useful when compact typed storage is important
#
# For general Python application development, lists are often the natural
# choice. The appropriate representation depends on data type, memory needs,
# interoperability requirements, and performance characteristics.

mixed_list = [1, 2.5, "three", True]

print("Python list can hold different object types:", mixed_list)

typed = array("i", [1, 2, 3])

try:
    typed.append(2.5)
except OverflowError as error:
    print("Typed array rejected incompatible value:", error)
except TypeError as error:
    print("Typed array rejected incompatible value:", error)


# ============================================================================
# 44. MANUAL CAPACITY VISUALIZATION
# ============================================================================

print("\n" + "=" * 80)
print("44. SIZE VERSUS CAPACITY")
print("=" * 80)

dynamic = DynamicArray[int](initial_capacity=4)

for value in range(10):
    dynamic.append(value)
    print(
        f"Added {value}: "
        f"size={dynamic.size}, capacity={dynamic.capacity}"
    )


# ============================================================================
# 45. SEARCH STRATEGY SELECTION
# ============================================================================

print("\n" + "=" * 80)
print("45. SEARCH STRATEGY SELECTION")
print("=" * 80)

# Linear search:
#     Use when data is unsorted or the array is small.
#
# Binary search:
#     Use when data is sorted and repeated searches justify maintaining
#     sorted order.
#
# Hash-based lookup:
#     Use a set or dictionary when fast average-case membership or key lookup
#     is more important than preserving simple array semantics.

values = [10, 20, 30, 40]

target = 30

print("Linear search:", linear_search(values, target))

sorted_values = sorted(values)

print("Binary search:", binary_search(sorted_values, target))

lookup = {value: index for index, value in enumerate(values)}
print("Hash-based lookup:", lookup.get(target))


# ============================================================================
# 46. TRADE-OFF: SORTING BEFORE SEARCHING
# ============================================================================

print("\n" + "=" * 80)
print("46. SORTING BEFORE SEARCHING")
print("=" * 80)

# If an unsorted array must be searched only once, sorting first is often
# unnecessary:
#
#     Linear search: O(n)
#
# Sorting followed by binary search:
#
#     Sort: O(n log n)
#     Search: O(log n)
#
# For many repeated searches, maintaining sorted data can make binary search
# worthwhile.

unsorted = [44, 12, 78, 3, 19, 51]

print("One-time linear search:", linear_search(unsorted, 19))

sorted_copy = sorted(unsorted)

print(
    "Sorted array for repeated searches:",
    sorted_copy,
)

print(
    "Binary search:",
    binary_search(sorted_copy, 19),
)


# ============================================================================
# 47. REMOVING ALL OCCURRENCES
# ============================================================================

print("\n" + "=" * 80)
print("47. REMOVING ALL OCCURRENCES")
print("=" * 80)


def remove_all(values: list[T], target: T) -> None:
    """
    Remove all occurrences in place.

    This implementation uses a write position rather than repeatedly calling
    remove(), avoiding repeated shifting work.
    """
    write_position = 0

    for value in values:
        if value != target:
            values[write_position] = value
            write_position += 1

    del values[write_position:]


values = [2, 5, 2, 7, 2, 9, 2]

remove_all(values, 2)

print("After removing all 2s:", values)


# ============================================================================
# 48. FILTERING IN PLACE
# ============================================================================

print("\n" + "=" * 80)
print("48. FILTERING")
print("=" * 80)


def retain_even(values: list[int]) -> None:
    """Keep only even values in place."""
    write_position = 0

    for value in values:
        if value % 2 == 0:
            values[write_position] = value
            write_position += 1

    del values[write_position:]


values = [1, 2, 3, 4, 5, 6, 7, 8]

retain_even(values)

print("Even values:", values)


# ============================================================================
# 49. TWO-POINTER ARRAY TECHNIQUE
# ============================================================================

print("\n" + "=" * 80)
print("49. TWO-POINTER TECHNIQUE")
print("=" * 80)

# Two pointers can reduce the need for additional storage.
#
# For a sorted array, two pointers can move from opposite ends to find a pair
# whose sum equals a target.

def two_sum_sorted(
    values: list[int],
    target: int,
) -> Optional[tuple[int, int]]:
    """Find two indexes in a sorted array whose values sum to target."""
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


values = [1, 3, 4, 6, 8, 11]

print("Two-pointer result:", two_sum_sorted(values, 10))


# ============================================================================
# 50. MOVING ZEROES
# ============================================================================

print("\n" + "=" * 80)
print("50. MOVING ZEROES TO THE END")
print("=" * 80)


def move_zeroes(values: list[int]) -> None:
    """
    Move all zeroes to the end while preserving non-zero order.

    Time: O(n)
    Extra space: O(1)
    """
    write_position = 0

    for value in values:
        if value != 0:
            values[write_position] = value
            write_position += 1

    while write_position < len(values):
        values[write_position] = 0
        write_position += 1


values = [0, 1, 0, 3, 12]

move_zeroes(values)

print("Result:", values)


# ============================================================================
# 51. PREFIX MAXIMUMS
# ============================================================================

print("\n" + "=" * 80)
print("51. PREFIX MAXIMUMS")
print("=" * 80)


def prefix_maximums(values: list[int]) -> list[int]:
    """Return the maximum value seen up to every position."""
    if not values:
        return []

    result = [0] * len(values)
    current_maximum = values[0]
    result[0] = current_maximum

    for index in range(1, len(values)):
        current_maximum = max(current_maximum, values[index])
        result[index] = current_maximum

    return result


values = [3, 1, 5, 2, 8, 4]

print("Values:", values)
print("Prefix maximums:", prefix_maximums(values))


# ============================================================================
# 52. SIMPLE ARRAY-BASED STACK
# ============================================================================

print("\n" + "=" * 80)
print("52. ARRAY-BASED STACK")
print("=" * 80)

# A stack follows LIFO: Last In, First Out.
#
# Dynamic arrays provide efficient append/pop-at-end operations, making them
# suitable for stack implementations.

stack: list[int] = []

stack.append(10)
stack.append(20)
stack.append(30)

print("Stack:", stack)
print("Popped:", stack.pop())
print("Stack:", stack)


# ============================================================================
# 53. SIMPLE ARRAY-BASED QUEUE AND ITS TRADE-OFF
# ============================================================================

print("\n" + "=" * 80)
print("53. ARRAY-BASED QUEUE TRADE-OFF")
print("=" * 80)

# A queue follows FIFO: First In, First Out.
#
# Removing from the beginning of a Python list is O(n), because elements must
# shift left. For high-performance queues, collections.deque is usually more
# appropriate.

queue = [10, 20, 30]

first = queue.pop(0)

print("Removed from queue:", first)
print("Remaining queue:", queue)


# ============================================================================
# 54. MEMORY LOCALITY
# ============================================================================

print("\n" + "=" * 80)
print("54. MEMORY LOCALITY")
print("=" * 80)

# Contiguous arrays can provide strong spatial locality.
# When one element is loaded from memory, nearby elements may already be
# available in CPU cache lines.
#
# This can make sequential traversal very efficient.
#
# Python lists complicate this picture because the list contains references,
# and referenced objects may not be contiguous.
#
# The principle remains important in lower-level languages and performance-
# sensitive systems.

values = list(range(10))

print("Sequential traversal:")
total = 0

for value in values:
    total += value

print("Total:", total)


# ============================================================================
# 55. PERFORMANCE MEASUREMENT
# ============================================================================

print("\n" + "=" * 80)
print("55. SIMPLE PERFORMANCE MEASUREMENT")
print("=" * 80)


def measure_linear_search(size: int) -> float:
    """Measure unsuccessful linear search time for an array of given size."""
    values = list(range(size))
    target = -1

    start = time.perf_counter()
    linear_search(values, target)
    end = time.perf_counter()

    return end - start


for size in [1_000, 10_000, 100_000]:
    elapsed = measure_linear_search(size)
    print(f"Size={size:>7}: {elapsed:.8f} seconds")


# ============================================================================
# 56. PERFORMANCE CONSIDERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("56. PERFORMANCE CONSIDERATIONS")
print("=" * 80)

# Performance depends on:
#
# - Number of elements
# - Operation being performed
# - Memory layout
# - Data type
# - CPU cache behavior
# - Allocation and resizing
# - Number of searches
# - Whether data remains sorted
#
# Big-O notation describes how resource requirements grow asymptotically.
# It does not predict exact execution time on every machine.

performance_rules = [
    "Use direct indexing for random access.",
    "Avoid repeated insertion at the beginning of a list.",
    "Use append for efficient dynamic-array growth.",
    "Use binary search only when ordering is guaranteed.",
    "Avoid sorting merely to perform one search.",
    "Use specialized structures when array semantics are inappropriate.",
]

for rule in performance_rules:
    print("-", rule)


# ============================================================================
# 57. SECURITY AND ROBUSTNESS CONSIDERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("57. SECURITY AND ROBUSTNESS")
print("=" * 80)

# Arrays themselves are not inherently a security boundary.
#
# Robust applications should still:
#
# - Validate indexes.
# - Validate input sizes.
# - Reject unexpectedly large allocations.
# - Validate numeric ranges where required.
# - Avoid trusting externally supplied indexes.
# - Handle empty input.
# - Avoid accidental quadratic algorithms on attacker-controlled data.
#
# Excessive input can cause memory exhaustion even when individual operations
# are logically correct.

def bounded_array_input(values: Iterable[int], maximum_size: int) -> list[int]:
    """Create an array while enforcing a maximum number of elements."""
    if maximum_size < 0:
        raise ValueError("Maximum size cannot be negative.")

    result: list[int] = []

    for value in values:
        if len(result) >= maximum_size:
            raise ValueError("Input exceeds the permitted array size.")

        result.append(value)

    return result


print(
    "Bounded input:",
    bounded_array_input([1, 2, 3], maximum_size=5),
)

try:
    bounded_array_input(range(10), maximum_size=3)
except ValueError as error:
    print("Expected size validation error:", error)


# ============================================================================
# 58. DEBUGGING ARRAY OPERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("58. DEBUGGING")
print("=" * 80)

# A useful debugging approach is to inspect:
#
# 1. Current array
# 2. Current index
# 3. Target value
# 4. Loop boundaries
# 5. Array length
# 6. Values before and after mutation
#
# Off-by-one errors are among the most common array bugs.

values = [10, 20, 30, 40]

for index, value in enumerate(values):
    print(
        f"DEBUG index={index}, value={value}, length={len(values)}"
    )


# ============================================================================
# 59. OFF-BY-ONE EXAMPLE
# ============================================================================

print("\n" + "=" * 80)
print("59. OFF-BY-ONE ERRORS")
print("=" * 80)

values = [10, 20, 30, 40]

# Correct:
for index in range(len(values)):
    print("Correct index:", index)

# range(len(values)) produces:
# 0, 1, 2, 3
#
# The last valid index is len(values) - 1.
#
# range(len(values) + 1) would attempt to produce index 4, which is invalid.


# ============================================================================
# 60. MUTATING WHILE ITERATING
# ============================================================================

print("\n" + "=" * 80)
print("60. MUTATING WHILE ITERATING")
print("=" * 80)

# Removing elements directly from a list while iterating over it can cause
# elements to be skipped because indexes shift.

values = [1, 2, 3, 4, 5, 6]

# Safer approach: create a filtered result.
remaining = [value for value in values if value % 2 != 0]

print("Original:", values)
print("Filtered:", remaining)


# ============================================================================
# 61. ARRAY INVARIANTS
# ============================================================================

print("\n" + "=" * 80)
print("61. ARRAY INVARIANTS")
print("=" * 80)

# An invariant is a condition that should remain true throughout an algorithm.
#
# Example for a dynamic array:
#
#     0 <= size <= capacity
#
# Maintaining such invariants helps prevent corrupted internal state.

dynamic = DynamicArray[int](initial_capacity=2)

for value in [10, 20, 30]:
    dynamic.append(value)

    assert 0 <= dynamic.size <= dynamic.capacity

print(
    "Invariant verified:",
    0 <= dynamic.size <= dynamic.capacity,
)


# ============================================================================
# 62. TESTING BASIC ARRAY OPERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("62. TESTING")
print("=" * 80)


def run_basic_tests() -> None:
    """Run assertions covering normal and edge-case behavior."""

    assert linear_search([10, 20, 30], 20) == 1
    assert linear_search([10, 20, 30], 99) == -1

    assert binary_search([10, 20, 30], 20) == 1
    assert binary_search([10, 20, 30], 99) == -1

    assert first_occurrence([1, 2, 2, 2, 5], 2) == 1
    assert last_occurrence([1, 2, 2, 2, 5], 2) == 3

    array_instance = DynamicArray[int](initial_capacity=2)
    array_instance.append(10)
    array_instance.append(20)
    array_instance.append(30)

    assert list(array_instance) == [10, 20, 30]
    assert array_instance.get(1) == 20

    array_instance.insert(1, 15)
    assert list(array_instance) == [10, 15, 20, 30]

    array_instance.set(0, 5)
    assert list(array_instance) == [5, 15, 20, 30]

    removed = array_instance.pop(2)
    assert removed == 20
    assert list(array_instance) == [5, 15, 30]

    test_values = [1, 2, 3, 2, 4]
    remove_all(test_values, 2)
    assert test_values == [1, 3, 4]

    zero_values = [0, 1, 0, 2, 3]
    move_zeroes(zero_values)
    assert zero_values == [1, 2, 3, 0, 0]

    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([1, 2, 3], 100) is None


run_basic_tests()

print("All basic tests passed.")


# ============================================================================
# 63. COMPLETE ARRAY DEMONSTRATION
# ============================================================================

print("\n" + "=" * 80)
print("63. COMPLETE ARRAY WORKFLOW")
print("=" * 80)


def demonstrate_array_workflow() -> None:
    """
    Demonstrate a typical lifecycle:
    creation -> traversal -> update -> insertion -> deletion -> search.
    """
    data = [10, 20, 30, 40]

    print("Initial:", data)

    print("Traversal:")
    for value in data:
        print(value)

    data[1] = 25
    print("After update:", data)

    data.insert(2, 27)
    print("After insertion:", data)

    deleted = data.pop(3)
    print("Deleted:", deleted)
    print("After deletion:", data)

    target = 40
    position = linear_search(data, target)

    print(f"Search for {target}: index={position}")


demonstrate_array_workflow()


# ============================================================================
# 64. ARRAY DESIGN DECISIONS
# ============================================================================

print("\n" + "=" * 80)
print("64. DESIGN DECISIONS")
print("=" * 80)

# When choosing an array-like structure, consider:
#
# 1. Do you need random access?
# 2. Is the data homogeneous?
# 3. How frequently is data inserted or deleted?
# 4. Is ordering important?
# 5. Is memory usage important?
# 6. Are searches frequent?
# 7. Is the collection expected to grow?
# 8. Are indexes meaningful?
#
# Arrays are especially useful when indexed access and sequential storage are
# central requirements.

design_questions = [
    "Need fast random access? Arrays are a strong candidate.",
    "Frequent middle insertion? Consider a different structure.",
    "Need key-based lookup? A dictionary may be more appropriate.",
    "Need fast membership? A set may be appropriate.",
    "Need FIFO behavior? A deque is generally preferable to list.pop(0).",
    "Need compact primitive numeric storage? Consider array.array.",
]

for question in design_questions:
    print("-", question)


# ============================================================================
# 65. REAL-WORLD APPLICATIONS
# ============================================================================

print("\n" + "=" * 80)
print("65. REAL-WORLD APPLICATIONS")
print("=" * 80)

# Arrays appear directly or indirectly in many systems:
#
# - Tables and matrices
# - Image pixels
# - Audio samples
# - Sensor readings
# - Financial time series
# - Scientific measurements
# - Machine-learning feature vectors
# - Buffers
# - Lookup tables
# - Game-board representations
# - Scheduling data
# - Numerical computation
#
# A two-dimensional pixel grid is naturally modeled using rows and columns.

image = [
    [0, 0, 255],
    [255, 128, 0],
    [64, 64, 64],
]

print("Example pixel-like matrix:")
for row in image:
    print(row)


# ============================================================================
# 66. COMPLETE NUMERIC ARRAY ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("66. NUMERIC ARRAY ANALYSIS")
print("=" * 80)


def analyze_array(values: list[float]) -> dict[str, float]:
    """Return basic statistics for a non-empty numeric array."""
    if not values:
        raise ValueError("Cannot analyze an empty array.")

    total = 0.0
    minimum = values[0]
    maximum = values[0]

    for value in values:
        total += value

        if value < minimum:
            minimum = value

        if value > maximum:
            maximum = value

    return {
        "count": float(len(values)),
        "sum": total,
        "minimum": minimum,
        "maximum": maximum,
        "average": total / len(values),
    }


sales = [1250.50, 980.75, 1430.25, 1120.00, 1675.80]

analysis = analyze_array(sales)

for metric, value in analysis.items():
    print(f"{metric}: {value}")


# ============================================================================
# 67. RANDOMIZED TESTING
# ============================================================================

print("\n" + "=" * 80)
print("67. RANDOMIZED TESTING")
print("=" * 80)

# Randomized testing can expose assumptions that a few hand-written examples
# may miss.

random.seed(42)

for _ in range(5):
    values = [random.randint(-10, 10) for _ in range(10)]
    target = random.randint(-10, 10)

    linear_result = linear_search(values, target)

    if linear_result != -1:
        assert values[linear_result] == target

    print(
        f"values={values}, target={target}, "
        f"linear_search_index={linear_result}"
    )


# ============================================================================
# 68. DYNAMIC ARRAY STRESS TEST
# ============================================================================

print("\n" + "=" * 80)
print("68. DYNAMIC ARRAY STRESS TEST")
print("=" * 80)

stress_array = DynamicArray[int](initial_capacity=1)

for value in range(1_000):
    stress_array.append(value)

assert len(stress_array) == 1_000
assert stress_array.get(0) == 0
assert stress_array.get(999) == 999

print("Stress test size:", stress_array.size)
print("Stress test capacity:", stress_array.capacity)
print("First value:", stress_array.get(0))
print("Last value:", stress_array.get(999))


# ============================================================================
# 69. IMPORTANT DISTINCTIONS
# ============================================================================

print("\n" + "=" * 80)
print("69. IMPORTANT DISTINCTIONS")
print("=" * 80)

distinctions = {
    "Size vs capacity":
        "Size is the number of stored elements; capacity is available storage.",
    "Index vs value":
        "An index identifies a position; a value is the data at that position.",
    "Linear vs binary search":
        "Linear search does not require sorting; binary search does.",
    "Fixed vs dynamic array":
        "Fixed arrays have predetermined capacity; dynamic arrays resize.",
    "List vs typed array":
        "Python lists store object references; array.array stores typed values.",
    "Access vs search":
        "Access uses a known index; search determines where a value occurs.",
}

for distinction, explanation in distinctions.items():
    print(f"{distinction}: {explanation}")


# ============================================================================
# 70. COMMON MISTAKES
# ============================================================================

print("\n" + "=" * 80)
print("70. COMMON MISTAKES")
print("=" * 80)

mistakes = [
    "Assuming the first index is 1 instead of 0.",
    "Accessing index equal to len(array).",
    "Using binary search on unsorted data.",
    "Forgetting that middle insertion requires shifting.",
    "Forgetting that beginning deletion requires shifting.",
    "Removing items from a list while directly iterating over it.",
    "Creating 2D lists with repeated references using [[0] * n] * m.",
    "Assuming Python lists store primitive values contiguously like C arrays.",
    "Ignoring memory consumption for very large arrays.",
    "Using a list as a queue when frequent front removals are required.",
]

for number, mistake in enumerate(mistakes, start=1):
    print(f"{number}. {mistake}")


# ============================================================================
# 71. LIMITATIONS OF ARRAYS
# ============================================================================

print("\n" + "=" * 80)
print("71. LIMITATIONS")
print("=" * 80)

limitations = [
    "Insertion and deletion in the middle can require O(n) movement.",
    "A traditional fixed-size array cannot grow beyond its capacity.",
    "Maintaining sorted order can make insertion expensive.",
    "Binary search is only useful when ordering is maintained.",
    "Large contiguous allocations can create memory-management constraints.",
    "Arrays are not ideal for every access pattern.",
]

for limitation in limitations:
    print("-", limitation)


# ============================================================================
# 72. PRODUCTION CONSIDERATIONS
# ============================================================================

print("\n" + "=" * 80)
print("72. PRODUCTION CONSIDERATIONS")
print("=" * 80)

production_considerations = [
    "Choose the data structure based on workload rather than habit.",
    "Validate external indexes and collection sizes.",
    "Use clear invariants for custom data structures.",
    "Prefer tested standard-library structures when they meet requirements.",
    "Measure performance with realistic workloads.",
    "Consider memory consumption as well as execution time.",
    "Avoid accidental O(n^2) behavior in repeated insertion or deletion.",
    "Document whether an operation mutates the original array.",
    "Document whether returned collections are copies or shared references.",
]

for consideration in production_considerations:
    print("-", consideration)


# ============================================================================
# 73. FINAL INTEGRATED EXAMPLE
# ============================================================================

print("\n" + "=" * 80)
print("73. INTEGRATED ARRAY EXAMPLE")
print("=" * 80)


class Inventory:
    """
    Simple inventory backed by an array of records.

    This example demonstrates:
    - object storage
    - traversal
    - searching
    - updating
    - aggregation
    """

    def __init__(self) -> None:
        self.items: list[dict[str, object]] = []

    def add_item(self, name: str, quantity: int, price: float) -> None:
        if not name.strip():
            raise ValueError("Item name cannot be empty.")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        if price < 0:
            raise ValueError("Price cannot be negative.")

        self.items.append(
            {
                "name": name,
                "quantity": quantity,
                "price": price,
            }
        )

    def find_item(self, name: str) -> Optional[dict[str, object]]:
        for item in self.items:
            if item["name"] == name:
                return item

        return None

    def update_quantity(self, name: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        item = self.find_item(name)

        if item is None:
            raise KeyError(f"Item not found: {name}")

        item["quantity"] = quantity

    def total_value(self) -> float:
        total = 0.0

        for item in self.items:
            quantity = int(item["quantity"])
            price = float(item["price"])
            total += quantity * price

        return total


inventory = Inventory()

inventory.add_item("Keyboard", 10, 1500.0)
inventory.add_item("Mouse", 20, 750.0)
inventory.add_item("Monitor", 5, 12000.0)

print("Inventory:")
for item in inventory.items:
    print(item)

print("Monitor:", inventory.find_item("Monitor"))

inventory.update_quantity("Mouse", 25)

print("Updated Mouse:", inventory.find_item("Mouse"))
print("Total inventory value:", inventory.total_value())


# ============================================================================
# 74. STUDY CHECKLIST
# ============================================================================

print("\n" + "=" * 80)
print("74. ARRAY CONCEPT CHECK")
print("=" * 80)

checklist = [
    "An array stores multiple values using indexed positions.",
    "Traditional arrays generally use contiguous memory.",
    "Zero-based indexing makes the first position index 0.",
    "Direct index access is O(1).",
    "Traversal is O(n).",
    "Linear search is O(n).",
    "Binary search is O(log n) on sorted data.",
    "Middle insertion and deletion are generally O(n).",
    "Dynamic arrays resize when capacity is exhausted.",
    "Appending to a dynamic array is O(1) amortized.",
    "Python lists are dynamic arrays of references.",
    "array.array provides typed compact storage.",
    "2D arrays can represent tables and matrices.",
    "Array algorithms must handle empty and boundary cases.",
]

for item in checklist:
    print("[x]", item)


# ============================================================================
# 75. EXECUTION COMPLETE
# ============================================================================

print("\n" + "=" * 80)
print("ARRAY STUDY SCRIPT EXECUTION COMPLETE")
print("=" * 80)

print(
    "\nThis script demonstrated array creation, indexing, traversal, "
    "updating, insertion, deletion, searching, memory representation, "
    "dynamic resizing, multidimensional structures, algorithms, "
    "performance, validation, testing, and production considerations."
)
