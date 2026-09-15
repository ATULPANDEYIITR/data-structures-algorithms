"""
Array Manipulation: Beginner to Advanced Study and Practice
=============================================================

This standalone Python program demonstrates practical array/list manipulation
from fundamental operations through more advanced rearrangement techniques.

Python calls its built-in dynamic array structure a "list". Lists provide
indexed access, insertion, deletion, slicing, iteration, and many useful
methods. The algorithms below also demonstrate operations manually so that
their underlying mechanics are visible.

Topics covered:
- Indexing and traversal
- Updating elements
- Insertion and deletion
- Searching
- Swapping
- Reversing
- Left and right shifting
- Left and right rotation
- Removing duplicates
- Moving zeroes
- Partitioning
- Rearrangement by parity
- Stable and unstable rearrangement
- Sorting-related rearrangement
- Two-pointer techniques
- In-place versus out-of-place algorithms
- Complexity analysis
- Edge cases and validation
- Testing
- A realistic array-processing case study
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional
import random
import time


# ---------------------------------------------------------------------------
# 1. FUNDAMENTALS
# ---------------------------------------------------------------------------

def demonstrate_basics() -> None:
    """Demonstrate indexing, updating, traversal, slicing, and membership."""
    numbers = [10, 20, 30, 40, 50]

    print("\n=== 1. Array/List Fundamentals ===")
    print("Array:", numbers)
    print("First element:", numbers[0])
    print("Last element:", numbers[-1])

    # Updating an element is O(1) because the index directly identifies
    # the element position.
    numbers[2] = 35
    print("After updating index 2:", numbers)

    print("Forward traversal:")
    for index, value in enumerate(numbers):
        print(f"  index={index}, value={value}")

    print("Slice [1:4]:", numbers[1:4])
    print("Reversed copy:", numbers[::-1])
    print("30 in array:", 30 in numbers)


# ---------------------------------------------------------------------------
# 2. INSERTION
# ---------------------------------------------------------------------------

def insert_at(array: list[int], index: int, value: int) -> None:
    """
    Insert value at index using manual shifting.

    Elements at and after index move one position to the right.
    Average complexity: O(n).
    """
    if index < 0 or index > len(array):
        raise IndexError("Insertion index out of range")

    array.append(0)

    # Shift elements from right to left so that values are not overwritten.
    for position in range(len(array) - 1, index, -1):
        array[position] = array[position - 1]

    array[index] = value


def demonstrate_insertion() -> None:
    print("\n=== 2. Insertion ===")

    values = [10, 20, 40, 50]
    print("Before:", values)

    insert_at(values, 2, 30)
    print("After inserting 30 at index 2:", values)

    # Built-in list.insert() performs the same conceptual operation.
    values.insert(0, 5)
    print("After built-in insertion at beginning:", values)

    values.insert(len(values), 60)
    print("After insertion at end:", values)


# ---------------------------------------------------------------------------
# 3. DELETION
# ---------------------------------------------------------------------------

def delete_at(array: list[int], index: int) -> int:
    """
    Delete and return the value at index using manual shifting.

    Complexity: O(n) in the general case.
    """
    if index < 0 or index >= len(array):
        raise IndexError("Deletion index out of range")

    deleted = array[index]

    for position in range(index, len(array) - 1):
        array[position] = array[position + 1]

    array.pop()
    return deleted


def demonstrate_deletion() -> None:
    print("\n=== 3. Deletion ===")

    values = [10, 20, 30, 40, 50]
    deleted = delete_at(values, 2)

    print("Deleted:", deleted)
    print("Remaining:", values)

    values.remove(40)
    print("After removing value 40:", values)

    last = values.pop()
    print("Popped last element:", last)
    print("Remaining:", values)


# ---------------------------------------------------------------------------
# 4. SWAPPING
# ---------------------------------------------------------------------------

def swap(array: list[int], first: int, second: int) -> None:
    """Swap two positions in O(1) time."""
    if not (0 <= first < len(array) and 0 <= second < len(array)):
        raise IndexError("Swap index out of range")

    array[first], array[second] = array[second], array[first]


def demonstrate_swapping() -> None:
    print("\n=== 4. Swapping ===")

    values = [10, 20, 30, 40]
    print("Before:", values)

    swap(values, 0, 3)
    print("After swapping first and last:", values)


# ---------------------------------------------------------------------------
# 5. REVERSING
# ---------------------------------------------------------------------------

def reverse_in_place(array: list[int]) -> None:
    """
    Reverse an array without allocating another array.

    Two-pointer technique:
    - left starts at the beginning.
    - right starts at the end.
    - swap and move both pointers inward.

    Complexity: O(n) time and O(1) auxiliary space.
    """
    left = 0
    right = len(array) - 1

    while left < right:
        array[left], array[right] = array[right], array[left]
        left += 1
        right -= 1


def demonstrate_reversing() -> None:
    print("\n=== 5. Reversing ===")

    values = [1, 2, 3, 4, 5, 6]
    reverse_in_place(values)
    print("In-place reversed:", values)

    values = [1, 2, 3, 4, 5]
    print("Slice reversed copy:", values[::-1])


# ---------------------------------------------------------------------------
# 6. SHIFTING
# ---------------------------------------------------------------------------

def shift_left(array: list[int], positions: int, fill: int = 0) -> None:
    """
    Shift elements left.

    Example:
        [1,2,3,4,5], shift by 2
        -> [3,4,5,0,0]

    Unlike rotation, discarded elements do not return at the other end.
    """
    if positions < 0:
        raise ValueError("Positions must be non-negative")

    if not array:
        return

    positions = min(positions, len(array))

    for index in range(len(array) - positions):
        array[index] = array[index + positions]

    for index in range(len(array) - positions, len(array)):
        array[index] = fill


def shift_right(array: list[int], positions: int, fill: int = 0) -> None:
    """Shift elements right while filling newly opened positions."""
    if positions < 0:
        raise ValueError("Positions must be non-negative")

    if not array:
        return

    positions = min(positions, len(array))

    for index in range(len(array) - 1, positions - 1, -1):
        array[index] = array[index - positions]

    for index in range(positions):
        array[index] = fill


def demonstrate_shifting() -> None:
    print("\n=== 6. Shifting ===")

    left = [1, 2, 3, 4, 5]
    shift_left(left, 2)
    print("Left shift:", left)

    right = [1, 2, 3, 4, 5]
    shift_right(right, 2)
    print("Right shift:", right)

    # A shift loses values. This is different from a rotation.
    print("A shift discards values; rotation preserves all values.")


# ---------------------------------------------------------------------------
# 7. ROTATION
# ---------------------------------------------------------------------------

def rotate_left(array: list[int], positions: int) -> None:
    """
    Rotate left using the reversal algorithm.

    For [1,2,3,4,5] and k=2:
    [1,2,3,4,5]
    -> [2,1,3,4,5]
    -> [2,1,5,4,3]
    -> [3,4,5,1,2]

    Complexity: O(n) time and O(1) auxiliary space.
    """
    n = len(array)
    if n == 0:
        return

    positions %= n

    def reverse_range(left: int, right: int) -> None:
        while left < right:
            array[left], array[right] = array[right], array[left]
            left += 1
            right -= 1

    reverse_range(0, positions - 1)
    reverse_range(positions, n - 1)
    reverse_range(0, n - 1)


def rotate_right(array: list[int], positions: int) -> None:
    """Rotate right using three reversals."""
    n = len(array)
    if n == 0:
        return

    positions %= n
    if positions == 0:
        return

    rotate_left(array, n - positions)


def demonstrate_rotation() -> None:
    print("\n=== 7. Rotation ===")

    values = [1, 2, 3, 4, 5]
    rotate_left(values, 2)
    print("Left rotation by 2:", values)

    values = [1, 2, 3, 4, 5]
    rotate_right(values, 2)
    print("Right rotation by 2:", values)

    # Modulo handles positions larger than the array length.
    values = [1, 2, 3]
    rotate_left(values, 100)
    print("Rotation by 100:", values)


# ---------------------------------------------------------------------------
# 8. REARRANGEMENT TECHNIQUES
# ---------------------------------------------------------------------------

def move_zeroes_to_end(array: list[int]) -> None:
    """
    Move all zeroes to the end while preserving the order of non-zero values.

    This is a stable two-pointer algorithm.
    Complexity: O(n) time, O(1) auxiliary space.
    """
    write_index = 0

    for read_index in range(len(array)):
        if array[read_index] != 0:
            array[write_index] = array[read_index]
            write_index += 1

    while write_index < len(array):
        array[write_index] = 0
        write_index += 1


def partition_by_pivot(array: list[int], pivot: int) -> None:
    """
    Rearrange so values less than pivot appear before values greater than
    or equal to pivot. Relative ordering is not guaranteed.
    """
    left = 0
    right = len(array) - 1

    while left <= right:
        while left <= right and array[left] < pivot:
            left += 1

        while left <= right and array[right] >= pivot:
            right -= 1

        if left < right:
            array[left], array[right] = array[right], array[left]
            left += 1
            right -= 1


def rearrange_even_odd(array: list[int]) -> None:
    """Place even values before odd values using two pointers."""
    left = 0
    right = len(array) - 1

    while left < right:
        while left < right and array[left] % 2 == 0:
            left += 1

        while left < right and array[right] % 2 != 0:
            right -= 1

        if left < right:
            array[left], array[right] = array[right], array[left]


def rearrange_alternating_sign(array: list[int]) -> list[int]:
    """
    Return an array alternating positive and negative values when possible.

    The implementation preserves relative order within positive and negative
    groups. Remaining values are appended when one group is exhausted.
    """
    positives = [value for value in array if value >= 0]
    negatives = [value for value in array if value < 0]

    result: list[int] = []
    positive_index = 0
    negative_index = 0

    # Start with a positive value when one exists.
    use_positive = bool(positives)

    while positive_index < len(positives) or negative_index < len(negatives):
        if use_positive and positive_index < len(positives):
            result.append(positives[positive_index])
            positive_index += 1
        elif not use_positive and negative_index < len(negatives):
            result.append(negatives[negative_index])
            negative_index += 1
        elif positive_index < len(positives):
            result.append(positives[positive_index])
            positive_index += 1
        else:
            result.append(negatives[negative_index])
            negative_index += 1

        use_positive = not use_positive

    return result


def demonstrate_rearrangement() -> None:
    print("\n=== 8. Rearrangement ===")

    values = [0, 1, 0, 3, 12, 0, 5]
    move_zeroes_to_end(values)
    print("Zeroes moved to end:", values)

    values = [9, 2, 7, 4, 6, 1, 8, 3]
    partition_by_pivot(values, 5)
    print("Partition around pivot 5:", values)

    values = [1, 2, 3, 4, 5, 6, 7]
    rearrange_even_odd(values)
    print("Even values before odd values:", values)

    values = [1, -2, 3, -4, -5, 6]
    print("Alternating signs:", rearrange_alternating_sign(values))


# ---------------------------------------------------------------------------
# 9. DUPLICATE REMOVAL
# ---------------------------------------------------------------------------

def remove_duplicates_preserve_order(array: Iterable[int]) -> list[int]:
    """Remove duplicates while retaining the first occurrence of each value."""
    seen: set[int] = set()
    result: list[int] = []

    for value in array:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def remove_duplicates_sorted_in_place(array: list[int]) -> int:
    """
    Remove duplicates from a sorted array in-place.

    Returns the length of the unique prefix.

    Complexity: O(n) time and O(1) auxiliary space.
    """
    if not array:
        return 0

    write_index = 1

    for read_index in range(1, len(array)):
        if array[read_index] != array[write_index - 1]:
            array[write_index] = array[read_index]
            write_index += 1

    return write_index


def demonstrate_duplicates() -> None:
    print("\n=== 9. Duplicate Handling ===")

    values = [3, 1, 3, 2, 1, 4, 2]
    print("Original:", values)
    print("Unique while preserving order:",
          remove_duplicates_preserve_order(values))

    values = [1, 1, 2, 2, 2, 3, 4, 4]
    unique_length = remove_duplicates_sorted_in_place(values)
    print("Unique sorted prefix:", values[:unique_length])


# ---------------------------------------------------------------------------
# 10. SEARCHING AND MANIPULATION TOGETHER
# ---------------------------------------------------------------------------

def linear_search(array: list[int], target: int) -> int:
    """Return the first matching index, or -1 when target is absent."""
    for index, value in enumerate(array):
        if value == target:
            return index
    return -1


def binary_search(array: list[int], target: int) -> int:
    """
    Binary search requires sorted input.

    Complexity: O(log n) time.
    """
    left = 0
    right = len(array) - 1

    while left <= right:
        middle = (left + right) // 2

        if array[middle] == target:
            return middle
        if array[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def demonstrate_searching() -> None:
    print("\n=== 10. Searching ===")

    values = [7, 2, 9, 4, 2]
    print("Linear search for 4:", linear_search(values, 4))

    sorted_values = [1, 2, 4, 7, 9, 12]
    print("Binary search for 7:", binary_search(sorted_values, 7))
    print("Binary search for 8:", binary_search(sorted_values, 8))


# ---------------------------------------------------------------------------
# 11. ADVANCED REARRANGEMENT
# ---------------------------------------------------------------------------

def dutch_national_flag(array: list[int]) -> None:
    """
    Sort an array containing only 0, 1, and 2 in O(n) time and O(1) space.

    low     = next position for 0
    current = element currently examined
    high    = next position for 2

    This demonstrates a three-way partition.
    """
    low = 0
    current = 0
    high = len(array) - 1

    while current <= high:
        if array[current] == 0:
            array[low], array[current] = array[current], array[low]
            low += 1
            current += 1
        elif array[current] == 1:
            current += 1
        elif array[current] == 2:
            array[current], array[high] = array[high], array[current]
            high -= 1
        else:
            raise ValueError("Array may contain only 0, 1, and 2")


def wiggle_rearrange(array: list[int]) -> None:
    """
    Rearrange into a1 <= a2 >= a3 <= a4 >= ...

    A local greedy swap is sufficient after scanning adjacent positions.
    """
    for index in range(len(array) - 1):
        if index % 2 == 0:
            if array[index] > array[index + 1]:
                array[index], array[index + 1] = (
                    array[index + 1],
                    array[index],
                )
        else:
            if array[index] < array[index + 1]:
                array[index], array[index + 1] = (
                    array[index + 1],
                    array[index],
                )


def rearrange_by_index_mapping(array: list[int]) -> None:
    """
    Apply a permutation in-place using cycle decomposition.

    The array must contain a permutation of indexes 0..n-1.
    Afterward, the value originally at i moves to permutation[i].

    This function is included to demonstrate the concept of rearrangement
    through index mapping rather than value comparisons.
    """
    n = len(array)

    if sorted(array) != list(range(n)):
        raise ValueError("Input must be a permutation of 0..n-1")

    visited = [False] * n
    result = [0] * n

    for start in range(n):
        if visited[start]:
            continue

        current = start
        cycle_values = []

        while not visited[current]:
            visited[current] = True
            cycle_values.append((current, array[current]))
            current = array[current]

        for source_index, value in cycle_values:
            result[value] = source_index

    array[:] = result


def demonstrate_advanced_rearrangement() -> None:
    print("\n=== 11. Advanced Rearrangement ===")

    colors = [2, 0, 2, 1, 1, 0, 2, 1]
    dutch_national_flag(colors)
    print("Three-way partition:", colors)

    values = [3, 5, 2, 1, 6, 4]
    wiggle_rearrange(values)
    print("Wiggle arrangement:", values)

    permutation = [2, 0, 3, 1]
    rearrange_by_index_mapping(permutation)
    print("Index permutation rearrangement:", permutation)


# ---------------------------------------------------------------------------
# 12. ARRAY ROTATION WITH A COPY
# ---------------------------------------------------------------------------

def rotate_with_slice(array: list[int], positions: int) -> list[int]:
    """
    Simpler but out-of-place rotation.

    This is easier to read than the reversal algorithm, but it allocates
    another list.
    """
    if not array:
        return []

    positions %= len(array)
    return array[positions:] + array[:positions]


# ---------------------------------------------------------------------------
# 13. BATCH OPERATIONS
# ---------------------------------------------------------------------------

def apply_operations(
    array: list[int],
    operations: list[tuple[str, int, Optional[int]]],
) -> list[int]:
    """
    Apply a sequence of array operations.

    Supported operations:
        ("insert", index, value)
        ("delete", index, None)
        ("rotate_left", count, None)
        ("rotate_right", count, None)
        ("swap", index1, index2)
        ("reverse", 0, None)

    This resembles a small command processor and demonstrates how primitive
    array operations can be composed into a higher-level workflow.
    """
    result = array.copy()

    for operation in operations:
        name, first, second = operation

        if name == "insert":
            if second is None:
                raise ValueError("Insert requires a value")
            insert_at(result, first, second)

        elif name == "delete":
            delete_at(result, first)

        elif name == "rotate_left":
            rotate_left(result, first)

        elif name == "rotate_right":
            rotate_right(result, first)

        elif name == "swap":
            if second is None:
                raise ValueError("Swap requires two indexes")
            swap(result, first, second)

        elif name == "reverse":
            reverse_in_place(result)

        else:
            raise ValueError(f"Unsupported operation: {name}")

    return result


# ---------------------------------------------------------------------------
# 14. EDGE CASES
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print("\n=== 12. Edge Cases ===")

    empty: list[int] = []
    rotate_left(empty, 10)
    reverse_in_place(empty)
    print("Empty array after safe operations:", empty)

    one = [42]
    rotate_right(one, 100)
    reverse_in_place(one)
    print("Single-element array:", one)

    values = [1, 2, 3]
    rotate_left(values, -1 % len(values))
    print("Explicit normalized rotation:", values)

    values = [1, 2, 3]
    print("Rotation by length:", rotate_with_slice(values, len(values)))

    try:
        insert_at(values, 10, 99)
    except IndexError as error:
        print("Caught invalid insertion:", error)

    try:
        delete_at(values, 10)
    except IndexError as error:
        print("Caught invalid deletion:", error)

    try:
        dutch_national_flag([0, 1, 3])
    except ValueError as error:
        print("Caught invalid three-way input:", error)


# ---------------------------------------------------------------------------
# 15. PERFORMANCE COMPARISON
# ---------------------------------------------------------------------------

def benchmark_rotation() -> None:
    """
    Compare an in-place rotation with a slicing-based rotation.

    Benchmark numbers depend on hardware, interpreter, and system load.
    The important lesson is the allocation difference, not a fixed time.
    """
    print("\n=== 13. Performance Considerations ===")

    size = 100_000
    original = list(range(size))

    start = time.perf_counter()
    in_place = original.copy()
    rotate_left(in_place, 12_345)
    in_place_time = time.perf_counter() - start

    start = time.perf_counter()
    copied = rotate_with_slice(original, 12_345)
    copy_time = time.perf_counter() - start

    print(f"In-place rotation: {in_place_time:.6f} seconds")
    print(f"Slicing rotation:  {copy_time:.6f} seconds")
    print("Both are O(n) time; slicing creates an additional list.")


# ---------------------------------------------------------------------------
# 16. REALISTIC CASE STUDY: PROCESSING SENSOR READINGS
# ---------------------------------------------------------------------------

@dataclass
class SensorBatch:
    """Represent a batch of integer sensor measurements."""

    readings: list[int]

    def clean(self) -> None:
        """Remove invalid negative readings."""
        self.readings = [value for value in self.readings if value >= 0]

    def remove_outliers_above(self, maximum: int) -> None:
        """Remove readings above an application-defined safe threshold."""
        self.readings = [
            value for value in self.readings
            if value <= maximum
        ]

    def rotate_for_alignment(self, offset: int) -> None:
        """Rotate readings when sensor channel alignment is shifted."""
        rotate_left(self.readings, offset)

    def normalize_order(self) -> None:
        """Move zero measurements to the end for downstream processing."""
        move_zeroes_to_end(self.readings)

    def statistics(self) -> dict[str, float]:
        """Calculate basic statistics after preprocessing."""
        if not self.readings:
            return {
                "count": 0,
                "minimum": 0,
                "maximum": 0,
                "mean": 0.0,
            }

        return {
            "count": len(self.readings),
            "minimum": min(self.readings),
            "maximum": max(self.readings),
            "mean": sum(self.readings) / len(self.readings),
        }


def demonstrate_case_study() -> None:
    print("\n=== 14. Sensor Batch Case Study ===")

    batch = SensorBatch(
        readings=[18, 21, -1, 25, 0, 27, 105, 30, 0, 32]
    )

    print("Raw readings:", batch.readings)

    batch.clean()
    batch.remove_outliers_above(100)
    batch.rotate_for_alignment(2)
    batch.normalize_order()

    print("Processed readings:", batch.readings)
    print("Statistics:", batch.statistics())


# ---------------------------------------------------------------------------
# 17. VALIDATION AND TESTING
# ---------------------------------------------------------------------------

def is_rotation(original: list[int], candidate: list[int]) -> bool:
    """
    Determine whether candidate is a rotation of original.

    For non-empty arrays, a rotation appears as a contiguous sequence in
    original + original.
    """
    if len(original) != len(candidate):
        return False

    if not original:
        return True

    doubled = original + original
    n = len(original)

    return any(doubled[index:index + n] == candidate
               for index in range(n))


def run_tests() -> None:
    """Run deterministic correctness checks."""
    print("\n=== 15. Automated Tests ===")

    values = [1, 2, 3, 4, 5]
    rotate_left(values, 2)
    assert values == [3, 4, 5, 1, 2]

    values = [1, 2, 3, 4, 5]
    rotate_right(values, 2)
    assert values == [4, 5, 1, 2, 3]

    values = [1, 2, 3, 4]
    reverse_in_place(values)
    assert values == [4, 3, 2, 1]

    values = [0, 1, 0, 3, 12]
    move_zeroes_to_end(values)
    assert values == [1, 3, 12, 0, 0]

    values = [1, 1, 2, 2, 3]
    length = remove_duplicates_sorted_in_place(values)
    assert values[:length] == [1, 2, 3]

    assert linear_search([4, 7, 9], 7) == 1
    assert linear_search([4, 7, 9], 8) == -1

    assert binary_search([1, 3, 5, 7], 5) == 2
    assert binary_search([1, 3, 5, 7], 6) == -1

    assert is_rotation([1, 2, 3, 4], [3, 4, 1, 2])
    assert not is_rotation([1, 2, 3, 4], [3, 4, 2, 1])

    colors = [2, 0, 1, 2, 1, 0]
    dutch_national_flag(colors)
    assert colors == [0, 0, 1, 1, 2, 2]

    print("All tests passed.")


# ---------------------------------------------------------------------------
# 18. RANDOMIZED PROPERTY CHECKS
# ---------------------------------------------------------------------------

def randomized_rotation_tests(number_of_tests: int = 100) -> None:
    """
    Verify rotation behavior against Python's straightforward slicing model.

    Randomized tests are useful for finding boundary conditions that fixed
    examples may miss.
    """
    print("\n=== 16. Randomized Rotation Tests ===")

    for _ in range(number_of_tests):
        size = random.randint(0, 30)
        values = [random.randint(-50, 50) for _ in range(size)]
        positions = random.randint(0, 100)

        expected = rotate_with_slice(values, positions)
        actual = values.copy()

        rotate_left(actual, positions)

        assert actual == expected

    print(f"{number_of_tests} randomized tests passed.")


# ---------------------------------------------------------------------------
# 19. COMPLEXITY REFERENCE
# ---------------------------------------------------------------------------

def print_complexity_reference() -> None:
    print("\n=== 17. Complexity Reference ===")

    rows = [
        ("Indexed access", "O(1)", "O(1)", "Direct position access"),
        ("Update by index", "O(1)", "O(1)", "Replace an existing value"),
        ("Insert at end", "O(1) amortized", "O(1)", "Dynamic-array append"),
        ("Insert at beginning", "O(n)", "O(1)", "Elements shift right"),
        ("Delete at beginning", "O(n)", "O(1)", "Elements shift left"),
        ("Linear search", "O(n)", "O(1)", "Works without sorting"),
        ("Binary search", "O(log n)", "O(1)", "Requires sorted input"),
        ("Reverse", "O(n)", "O(1)", "Two-pointer swapping"),
        ("Rotation", "O(n)", "O(1)", "Reversal algorithm"),
        ("Move zeroes", "O(n)", "O(1)", "Stable two-pointer method"),
        ("Remove duplicates with set", "O(n) average", "O(n)", "Preserves order"),
    ]

    for operation, time_complexity, space, explanation in rows:
        print(
            f"{operation:30} "
            f"time={time_complexity:16} "
            f"space={space:8} "
            f"{explanation}"
        )


# ---------------------------------------------------------------------------
# 20. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the complete educational demonstration."""
    print("=" * 72)
    print("ARRAY MANIPULATION: COMPLETE PYTHON STUDY PROGRAM")
    print("=" * 72)

    demonstrate_basics()
    demonstrate_insertion()
    demonstrate_deletion()
    demonstrate_swapping()
    demonstrate_reversing()
    demonstrate_shifting()
    demonstrate_rotation()
    demonstrate_rearrangement()
    demonstrate_duplicates()
    demonstrate_searching()
    demonstrate_advanced_rearrangement()
    demonstrate_edge_cases()
    benchmark_rotation()
    demonstrate_case_study()
    run_tests()
    randomized_rotation_tests()
    print_complexity_reference()

    print("\n=== Key Distinctions ===")
    print("Insertion changes array length; updating does not.")
    print("Deletion changes array length; shifting usually preserves length.")
    print("Shifting discards values that leave the boundary.")
    print("Rotation preserves every value and wraps elements around.")
    print("Reversal changes ordering by mirroring positions.")
    print("Stable rearrangement preserves relative order within groups.")
    print("In-place algorithms reduce extra memory but may be harder to reason about.")
    print("Python lists are dynamic arrays, not fixed-size C-style arrays.")


if __name__ == "__main__":
    main()
