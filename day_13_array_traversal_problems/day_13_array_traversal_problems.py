"""
Array Traversal Problems
========================

A comprehensive, executable study file covering array/list traversal in Python
from absolute beginner concepts through advanced traversal techniques.

Topics covered:
- What arrays/lists are
- Indexing and iteration
- Forward, reverse, and indexed traversal
- Maximum and minimum
- Sum and average
- Frequency counting
- Conditional elements
- Counting and filtering
- First/last matching element
- Multiple conditions
- Manual implementations vs built-ins
- Empty-array handling
- Negative numbers, duplicates, and mixed edge cases
- Nested arrays and matrix traversal
- Two-pointer traversal
- Sliding-window traversal
- Prefix sums
- Running statistics
- Simultaneous traversal
- Enumeration
- Complexity analysis
- Validation
- Testing
- Debugging
- Performance considerations
- Practical applications
"""

from collections import Counter
from math import isclose
from typing import Callable, Iterable, Optional, Sequence, TypeVar


T = TypeVar("T")


# ============================================================================
# SECTION 1: FUNDAMENTALS
# ============================================================================

def demonstrate_basic_array():
    """
    Demonstrate the fundamental structure of a Python list.

    Python's list is a dynamic sequence. In introductory array problems,
    Python lists are commonly used to represent arrays.
    """

    numbers = [10, 20, 30, 40, 50]

    print("\n--- Basic Array/List ---")
    print("Array:", numbers)
    print("First element:", numbers[0])
    print("Third element:", numbers[2])
    print("Last element:", numbers[-1])
    print("Number of elements:", len(numbers))

    print("\nForward traversal:")
    for value in numbers:
        print(value)

    print("\nIndex-based traversal:")
    for index in range(len(numbers)):
        print("Index:", index, "Value:", numbers[index])

    print("\nReverse traversal:")
    for value in reversed(numbers):
        print(value)


# ============================================================================
# SECTION 2: VALIDATION
# ============================================================================

def validate_numeric_array(values: Sequence[float]) -> None:
    """
    Validate that every item is numeric.

    bool is intentionally rejected even though bool is a subclass of int in
    Python. Treating True as 1 and False as 0 can silently produce incorrect
    results in educational data-processing programs.
    """

    if values is None:
        raise ValueError("Array cannot be None.")

    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(
                f"Element at index {index} must be an int or float, "
                f"got {type(value).__name__}."
            )


# ============================================================================
# SECTION 3: MAXIMUM AND MINIMUM
# ============================================================================

def find_maximum_manual(values: Sequence[float]) -> float:
    """
    Find the maximum element using explicit traversal.

    Time complexity: O(n)
    Space complexity: O(1)
    """

    validate_numeric_array(values)

    if not values:
        raise ValueError("Cannot find a maximum in an empty array.")

    maximum = values[0]

    for value in values[1:]:
        if value > maximum:
            maximum = value

    return maximum


def find_minimum_manual(values: Sequence[float]) -> float:
    """
    Find the minimum element using explicit traversal.

    Time complexity: O(n)
    Space complexity: O(1)
    """

    validate_numeric_array(values)

    if not values:
        raise ValueError("Cannot find a minimum in an empty array.")

    minimum = values[0]

    for value in values[1:]:
        if value < minimum:
            minimum = value

    return minimum


def demonstrate_maximum_minimum():
    print("\n--- Maximum and Minimum ---")

    values = [42, 17, 93, 8, 51, 93, -10]

    print("Array:", values)
    print("Manual maximum:", find_maximum_manual(values))
    print("Built-in maximum:", max(values))
    print("Manual minimum:", find_minimum_manual(values))
    print("Built-in minimum:", min(values))

    # Important edge case: all elements can be equal.
    equal_values = [7, 7, 7, 7]
    print("All equal:", equal_values)
    print("Maximum:", find_maximum_manual(equal_values))
    print("Minimum:", find_minimum_manual(equal_values))


# ============================================================================
# SECTION 4: SUM AND AVERAGE
# ============================================================================

def calculate_sum_manual(values: Sequence[float]) -> float:
    """
    Calculate the sum by traversing every element.

    Time complexity: O(n)
    Space complexity: O(1)
    """

    validate_numeric_array(values)

    total = 0

    for value in values:
        total += value

    return total


def calculate_average_manual(values: Sequence[float]) -> float:
    """
    Calculate the arithmetic mean.

    The average is:
        sum of all elements / number of elements

    An empty array has no defined arithmetic mean, so ValueError is raised.
    """

    validate_numeric_array(values)

    if not values:
        raise ValueError("Cannot calculate an average of an empty array.")

    return calculate_sum_manual(values) / len(values)


def demonstrate_sum_average():
    print("\n--- Sum and Average ---")

    values = [10, 20, 30, 40, 50]

    total = calculate_sum_manual(values)
    average = calculate_average_manual(values)

    print("Array:", values)
    print("Sum:", total)
    print("Average:", average)
    print("Built-in sum:", sum(values))
    print("Built-in average equivalent:", sum(values) / len(values))


# ============================================================================
# SECTION 5: FREQUENCY
# ============================================================================

def frequency_manual(values: Sequence[T]) -> dict[T, int]:
    """
    Count how many times each value appears.

    A dictionary stores:
        value -> number of occurrences

    Average-case time complexity: O(n)
    Space complexity: O(k), where k is the number of distinct values.
    """

    frequencies: dict[T, int] = {}

    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1

    return frequencies


def demonstrate_frequency():
    print("\n--- Frequency Counting ---")

    values = [2, 4, 2, 7, 4, 2, 9, 7, 4]

    manual_result = frequency_manual(values)
    counter_result = Counter(values)

    print("Array:", values)
    print("Manual frequency:", manual_result)
    print("Counter frequency:", dict(counter_result))

    most_common_value, most_common_count = counter_result.most_common(1)[0]
    print(
        "Most frequent value:",
        most_common_value,
        "with frequency:",
        most_common_count,
    )


def count_occurrences_manual(values: Sequence[T], target: T) -> int:
    """
    Count occurrences of one target value.

    Time complexity: O(n)
    Space complexity: O(1)
    """

    count = 0

    for value in values:
        if value == target:
            count += 1

    return count


# ============================================================================
# SECTION 6: CONDITIONAL ELEMENTS
# ============================================================================

def get_even_numbers(values: Sequence[int]) -> list[int]:
    """Return all even numbers encountered during traversal."""

    result = []

    for value in values:
        if value % 2 == 0:
            result.append(value)

    return result


def get_odd_numbers(values: Sequence[int]) -> list[int]:
    """Return all odd numbers encountered during traversal."""

    result = []

    for value in values:
        if value % 2 != 0:
            result.append(value)

    return result


def get_positive_numbers(values: Sequence[float]) -> list[float]:
    """Return all positive elements."""

    result = []

    for value in values:
        if value > 0:
            result.append(value)

    return result


def get_negative_numbers(values: Sequence[float]) -> list[float]:
    """Return all negative elements."""

    result = []

    for value in values:
        if value < 0:
            result.append(value)

    return result


def get_elements_greater_than(values: Sequence[float], threshold: float) -> list[float]:
    """Return every element strictly greater than the threshold."""

    return [value for value in values if value > threshold]


def get_elements_in_range(
    values: Sequence[float],
    lower: float,
    upper: float,
    inclusive: bool = True,
) -> list[float]:
    """
    Select elements from a numeric range.

    inclusive=True:
        lower <= value <= upper

    inclusive=False:
        lower < value < upper
    """

    if lower > upper:
        raise ValueError("Lower bound cannot be greater than upper bound.")

    result = []

    for value in values:
        if inclusive:
            if lower <= value <= upper:
                result.append(value)
        else:
            if lower < value < upper:
                result.append(value)

    return result


def demonstrate_conditional_traversal():
    print("\n--- Conditional Traversal ---")

    values = [-12, -5, 0, 3, 8, 11, 14, 21]

    print("Array:", values)
    print("Even:", get_even_numbers(values))
    print("Odd:", get_odd_numbers(values))
    print("Positive:", get_positive_numbers(values))
    print("Negative:", get_negative_numbers(values))
    print("Greater than 10:", get_elements_greater_than(values, 10))
    print("Between -5 and 14:", get_elements_in_range(values, -5, 14))


# ============================================================================
# SECTION 7: COUNTING CONDITIONAL ELEMENTS
# ============================================================================

def count_even(values: Sequence[int]) -> int:
    count = 0

    for value in values:
        if value % 2 == 0:
            count += 1

    return count


def count_greater_than(values: Sequence[float], threshold: float) -> int:
    count = 0

    for value in values:
        if value > threshold:
            count += 1

    return count


def count_in_range(
    values: Sequence[float],
    lower: float,
    upper: float,
) -> int:
    count = 0

    for value in values:
        if lower <= value <= upper:
            count += 1

    return count


def demonstrate_conditional_counts():
    print("\n--- Conditional Counts ---")

    values = [4, 7, 12, 3, 18, 25, 30, 11]

    print("Array:", values)
    print("Even count:", count_even(values))
    print("Count greater than 10:", count_greater_than(values, 10))
    print("Count between 5 and 20:", count_in_range(values, 5, 20))


# ============================================================================
# SECTION 8: FIRST, LAST, AND ALL MATCHING ELEMENTS
# ============================================================================

def first_matching(
    values: Sequence[T],
    condition: Callable[[T], bool],
) -> Optional[T]:
    """
    Return the first element satisfying a condition.

    None is returned when no element matches.
    """

    for value in values:
        if condition(value):
            return value

    return None


def last_matching(
    values: Sequence[T],
    condition: Callable[[T], bool],
) -> Optional[T]:
    """Return the last element satisfying a condition."""

    found = None

    for value in values:
        if condition(value):
            found = value

    return found


def matching_indices(
    values: Sequence[T],
    condition: Callable[[T], bool],
) -> list[int]:
    """Return indices of all elements satisfying a condition."""

    indices = []

    for index, value in enumerate(values):
        if condition(value):
            indices.append(index)

    return indices


def demonstrate_matching():
    print("\n--- First, Last, and Matching Indices ---")

    values = [3, 8, 11, 16, 21, 24, 31]

    is_even = lambda value: value % 2 == 0

    print("Array:", values)
    print("First even:", first_matching(values, is_even))
    print("Last even:", last_matching(values, is_even))
    print("Indices of even elements:", matching_indices(values, is_even))


# ============================================================================
# SECTION 9: ENUMERATE AND INDEX-AWARE TRAVERSAL
# ============================================================================

def demonstrate_enumerate():
    print("\n--- Index-Aware Traversal ---")

    names = ["Asha", "Ravi", "Neha", "Kabir"]

    for index, name in enumerate(names):
        print(f"Index {index}: {name}")

    print("\nStarting enumeration at 1:")
    for position, name in enumerate(names, start=1):
        print(f"Position {position}: {name}")


# ============================================================================
# SECTION 10: SEARCHING DURING TRAVERSAL
# ============================================================================

def linear_search(values: Sequence[T], target: T) -> int:
    """
    Return the first index containing target.

    Return -1 if target does not exist.

    Time complexity: O(n)
    Space complexity: O(1)
    """

    for index, value in enumerate(values):
        if value == target:
            return index

    return -1


def contains_value(values: Sequence[T], target: T) -> bool:
    """Determine whether a target exists."""

    for value in values:
        if value == target:
            return True

    return False


def demonstrate_linear_search():
    print("\n--- Linear Search ---")

    values = [15, 8, 23, 42, 9, 17]

    print("Array:", values)
    print("Index of 42:", linear_search(values, 42))
    print("Index of 100:", linear_search(values, 100))
    print("Contains 23:", contains_value(values, 23))
    print("Contains 100:", contains_value(values, 100))


# ============================================================================
# SECTION 11: SINGLE-PASS MULTIPLE STATISTICS
# ============================================================================

def calculate_statistics_single_pass(
    values: Sequence[float],
) -> dict[str, float]:
    """
    Calculate minimum, maximum, sum, and average in one traversal.

    A naive implementation might separately call min(), max(), and sum(),
    causing several passes. A single-pass approach demonstrates how multiple
    statistics can be collected together.

    Time complexity: O(n)
    Space complexity: O(1), excluding the returned dictionary.
    """

    validate_numeric_array(values)

    if not values:
        raise ValueError("Statistics require at least one element.")

    minimum = values[0]
    maximum = values[0]
    total = 0

    for value in values:
        if value < minimum:
            minimum = value

        if value > maximum:
            maximum = value

        total += value

    average = total / len(values)

    return {
        "minimum": minimum,
        "maximum": maximum,
        "sum": total,
        "average": average,
    }


def demonstrate_single_pass_statistics():
    print("\n--- Single-Pass Statistics ---")

    values = [14, -3, 27, 8, 19, 4]

    statistics = calculate_statistics_single_pass(values)

    print("Array:", values)

    for name, result in statistics.items():
        print(f"{name.title()}: {result}")


# ============================================================================
# SECTION 12: RUNNING / PREFIX RESULTS
# ============================================================================

def running_sum(values: Sequence[float]) -> list[float]:
    """
    Produce cumulative sums.

    Example:
        [2, 5, 3] -> [2, 7, 10]
    """

    result = []
    total = 0

    for value in values:
        total += value
        result.append(total)

    return result


def running_maximum(values: Sequence[float]) -> list[float]:
    """
    Produce the maximum seen up to every position.

    Example:
        [4, 2, 7, 3] -> [4, 4, 7, 7]
    """

    if not values:
        return []

    result = []
    current_maximum = values[0]

    for value in values:
        if value > current_maximum:
            current_maximum = value

        result.append(current_maximum)

    return result


def running_minimum(values: Sequence[float]) -> list[float]:
    """Produce the minimum seen up to every position."""

    if not values:
        return []

    result = []
    current_minimum = values[0]

    for value in values:
        if value < current_minimum:
            current_minimum = value

        result.append(current_minimum)

    return result


def demonstrate_running_results():
    print("\n--- Running Results ---")

    values = [5, 2, 8, 3, 10, 1]

    print("Array:", values)
    print("Running sum:", running_sum(values))
    print("Running maximum:", running_maximum(values))
    print("Running minimum:", running_minimum(values))


# ============================================================================
# SECTION 13: PREFIX SUMS AND RANGE QUERIES
# ============================================================================

def build_prefix_sum(values: Sequence[float]) -> list[float]:
    """
    Build a prefix-sum array with a leading zero.

    For values:
        [10, 20, 30]

    Prefix:
        [0, 10, 30, 60]

    The sum from index left through right is:

        prefix[right + 1] - prefix[left]

    Construction: O(n)
    Range query: O(1)
    """

    prefix = [0]

    for value in values:
        prefix.append(prefix[-1] + value)

    return prefix


def range_sum(
    prefix: Sequence[float],
    left: int,
    right: int,
) -> float:
    """Return the inclusive range sum using a prefix-sum array."""

    if left < 0 or right < 0:
        raise IndexError("Range indices cannot be negative.")

    if left > right:
        raise ValueError("Left index cannot exceed right index.")

    if right + 1 >= len(prefix):
        raise IndexError("Range exceeds prefix-sum boundaries.")

    return prefix[right + 1] - prefix[left]


def demonstrate_prefix_sum():
    print("\n--- Prefix Sums ---")

    values = [5, 10, 15, 20, 25]
    prefix = build_prefix_sum(values)

    print("Array:", values)
    print("Prefix sums:", prefix)
    print("Sum from index 1 to 3:", range_sum(prefix, 1, 3))


# ============================================================================
# SECTION 14: TWO-ARRAY TRAVERSAL
# ============================================================================

def elementwise_sum(
    first: Sequence[float],
    second: Sequence[float],
) -> list[float]:
    """
    Add corresponding elements of two arrays.

    Equal lengths are required to avoid silently losing data.
    """

    if len(first) != len(second):
        raise ValueError("Arrays must have the same length.")

    result = []

    for index in range(len(first)):
        result.append(first[index] + second[index])

    return result


def dot_product(
    first: Sequence[float],
    second: Sequence[float],
) -> float:
    """
    Calculate a dot product using simultaneous traversal.

    Example:
        [1, 2, 3] · [4, 5, 6]
        = 1*4 + 2*5 + 3*6
        = 32
    """

    if len(first) != len(second):
        raise ValueError("Arrays must have the same length.")

    result = 0

    for first_value, second_value in zip(first, second):
        result += first_value * second_value

    return result


def demonstrate_two_array_traversal():
    print("\n--- Two-Array Traversal ---")

    first = [1, 2, 3, 4]
    second = [10, 20, 30, 40]

    print("First:", first)
    print("Second:", second)
    print("Elementwise sum:", elementwise_sum(first, second))
    print("Dot product:", dot_product(first, second))


# ============================================================================
# SECTION 15: REVERSE TRAVERSAL
# ============================================================================

def reverse_copy_manual(values: Sequence[T]) -> list[T]:
    """Create a reversed copy using explicit index traversal."""

    result = []

    for index in range(len(values) - 1, -1, -1):
        result.append(values[index])

    return result


def demonstrate_reverse_traversal():
    print("\n--- Reverse Traversal ---")

    values = [10, 20, 30, 40, 50]

    print("Original:", values)
    print("Manual reversed copy:", reverse_copy_manual(values))
    print("Built-in reversed:", list(reversed(values)))


# ============================================================================
# SECTION 16: ADJACENT-ELEMENT TRAVERSAL
# ============================================================================

def find_increasing_adjacent_pairs(
    values: Sequence[float],
) -> list[tuple[float, float]]:
    """
    Find pairs where the second element is greater than the first.

    Each pair consists of adjacent elements:
        (values[i], values[i + 1])
    """

    result = []

    for index in range(len(values) - 1):
        current = values[index]
        next_value = values[index + 1]

        if next_value > current:
            result.append((current, next_value))

    return result


def count_adjacent_changes(values: Sequence[T]) -> int:
    """Count how many times consecutive values differ."""

    if len(values) < 2:
        return 0

    count = 0

    for index in range(1, len(values)):
        if values[index] != values[index - 1]:
            count += 1

    return count


def demonstrate_adjacent_traversal():
    print("\n--- Adjacent-Element Traversal ---")

    values = [3, 5, 5, 2, 9, 11, 11]

    print("Array:", values)
    print(
        "Increasing adjacent pairs:",
        find_increasing_adjacent_pairs(values),
    )
    print("Adjacent changes:", count_adjacent_changes(values))


# ============================================================================
# SECTION 17: SLIDING WINDOW
# ============================================================================

def maximum_window_sum(
    values: Sequence[float],
    window_size: int,
) -> float:
    """
    Find the maximum sum of any contiguous window of fixed size.

    Instead of calculating every window from scratch, remove the outgoing
    element and add the incoming element.

    Time complexity: O(n)
    Space complexity: O(1)
    """

    if window_size <= 0:
        raise ValueError("Window size must be positive.")

    if window_size > len(values):
        raise ValueError("Window size cannot exceed array length.")

    current_sum = sum(values[:window_size])
    maximum_sum = current_sum

    for right in range(window_size, len(values)):
        left = right - window_size

        current_sum -= values[left]
        current_sum += values[right]

        if current_sum > maximum_sum:
            maximum_sum = current_sum

    return maximum_sum


def all_window_averages(
    values: Sequence[float],
    window_size: int,
) -> list[float]:
    """Return the average of every fixed-size contiguous window."""

    if window_size <= 0:
        raise ValueError("Window size must be positive.")

    if window_size > len(values):
        return []

    window_sum = sum(values[:window_size])
    result = [window_sum / window_size]

    for right in range(window_size, len(values)):
        left = right - window_size
        window_sum += values[right] - values[left]
        result.append(window_sum / window_size)

    return result


def demonstrate_sliding_window():
    print("\n--- Sliding-Window Traversal ---")

    values = [2, 1, 5, 1, 3, 2]
    window_size = 3

    print("Array:", values)
    print("Window size:", window_size)
    print("Maximum window sum:", maximum_window_sum(values, window_size))
    print("Window averages:", all_window_averages(values, window_size))


# ============================================================================
# SECTION 18: MATRIX / NESTED ARRAY TRAVERSAL
# ============================================================================

def matrix_row_sum(matrix: Sequence[Sequence[float]]) -> list[float]:
    """Calculate the sum of each row."""

    return [sum(row) for row in matrix]


def matrix_column_sum(matrix: Sequence[Sequence[float]]) -> list[float]:
    """
    Calculate column sums for a rectangular matrix.

    Ragged rows are rejected because they do not have a consistent set of
    columns.
    """

    if not matrix:
        return []

    column_count = len(matrix[0])

    for row in matrix:
        if len(row) != column_count:
            raise ValueError("Matrix must be rectangular.")

    result = [0] * column_count

    for row in matrix:
        for column_index, value in enumerate(row):
            result[column_index] += value

    return result


def traverse_matrix(matrix: Sequence[Sequence[T]]) -> list[T]:
    """Flatten a matrix using row-major traversal."""

    result = []

    for row in matrix:
        for value in row:
            result.append(value)

    return result


def demonstrate_matrix_traversal():
    print("\n--- Nested Array / Matrix Traversal ---")

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    print("Matrix:")
    for row in matrix:
        print(row)

    print("Row sums:", matrix_row_sum(matrix))
    print("Column sums:", matrix_column_sum(matrix))
    print("Row-major traversal:", traverse_matrix(matrix))


# ============================================================================
# SECTION 19: CONDITIONAL STATISTICS
# ============================================================================

def conditional_statistics(
    values: Sequence[float],
    condition: Callable[[float], bool],
) -> dict[str, Optional[float]]:
    """
    Calculate count, sum, minimum, maximum, and average only for matching
    elements.

    This demonstrates how a single traversal can perform several conditional
    operations simultaneously.
    """

    count = 0
    total = 0
    minimum = None
    maximum = None

    for value in values:
        if condition(value):
            count += 1
            total += value

            if minimum is None or value < minimum:
                minimum = value

            if maximum is None or value > maximum:
                maximum = value

    average = total / count if count else None

    return {
        "count": count,
        "sum": total,
        "minimum": minimum,
        "maximum": maximum,
        "average": average,
    }


def demonstrate_conditional_statistics():
    print("\n--- Conditional Statistics ---")

    values = [5, 12, 17, 22, 3, 30, 41]

    result = conditional_statistics(values, lambda value: value % 2 == 0)

    print("Array:", values)
    print("Statistics for even values:", result)


# ============================================================================
# SECTION 20: DUPLICATE DETECTION
# ============================================================================

def find_duplicates(values: Sequence[T]) -> list[T]:
    """
    Find unique values that occur more than once.

    The order of first duplicate detection is preserved.
    """

    seen: set[T] = set()
    duplicates: set[T] = set()
    result = []

    for value in values:
        if value in seen and value not in duplicates:
            duplicates.add(value)
            result.append(value)
        else:
            seen.add(value)

    return result


def demonstrate_duplicate_detection():
    print("\n--- Duplicate Detection ---")

    values = [4, 2, 7, 4, 9, 2, 2, 11, 7]

    print("Array:", values)
    print("Duplicates:", find_duplicates(values))


# ============================================================================
# SECTION 21: SECOND LARGEST DISTINCT ELEMENT
# ============================================================================

def second_largest_distinct(values: Sequence[float]) -> float:
    """
    Find the second-largest distinct value using one traversal.

    At least two distinct values are required.

    This is different from sorting the array because sorting takes O(n log n)
    time while this traversal uses O(n) time and O(1) auxiliary space.
    """

    validate_numeric_array(values)

    largest = None
    second_largest = None

    for value in values:
        if largest is None or value > largest:
            second_largest = largest
            largest = value
        elif value != largest and (
            second_largest is None or value > second_largest
        ):
            second_largest = value

    if second_largest is None:
        raise ValueError("At least two distinct values are required.")

    return second_largest


def demonstrate_second_largest():
    print("\n--- Second-Largest Distinct Element ---")

    values = [12, 5, 19, 19, 8, 15, 12]

    print("Array:", values)
    print("Second-largest distinct value:", second_largest_distinct(values))


# ============================================================================
# SECTION 22: BEST BUY/SELL STYLE TRAVERSAL
# ============================================================================

def maximum_single_transaction_profit(prices: Sequence[float]) -> float:
    """
    Find the maximum profit from buying once and selling once later.

    The selling day must occur after the buying day.

    Example:
        [7, 1, 5, 3, 6, 4] -> 5

    The algorithm tracks the cheapest price seen so far and evaluates the
    profit obtainable by selling at each later price.

    Time complexity: O(n)
    Space complexity: O(1)
    """

    if len(prices) < 2:
        return 0

    minimum_price = prices[0]
    maximum_profit = 0

    for price in prices[1:]:
        potential_profit = price - minimum_price

        if potential_profit > maximum_profit:
            maximum_profit = potential_profit

        if price < minimum_price:
            minimum_price = price

    return maximum_profit


def demonstrate_profit_traversal():
    print("\n--- State Tracking During Traversal ---")

    prices = [7, 1, 5, 3, 6, 4]

    print("Prices:", prices)
    print(
        "Maximum single-transaction profit:",
        maximum_single_transaction_profit(prices),
    )


# ============================================================================
# SECTION 23: STABLE PARTITION BY CONDITION
# ============================================================================

def stable_partition_even_first(values: Sequence[int]) -> list[int]:
    """
    Put even elements before odd elements while preserving relative order.

    Example:
        [5, 2, 7, 4, 1, 6]
        -> [2, 4, 6, 5, 7, 1]

    This uses additional O(n) space.
    """

    evens = []
    odds = []

    for value in values:
        if value % 2 == 0:
            evens.append(value)
        else:
            odds.append(value)

    return evens + odds


def demonstrate_partition():
    print("\n--- Conditional Partition ---")

    values = [5, 2, 7, 4, 1, 6, 9, 8]

    print("Array:", values)
    print("Even elements first:", stable_partition_even_first(values))


# ============================================================================
# SECTION 24: IN-PLACE CONDITIONAL MODIFICATION
# ============================================================================

def replace_negative_values(values: list[float], replacement: float = 0) -> None:
    """
    Replace negative values in-place.

    This changes the original list.
    """

    for index, value in enumerate(values):
        if value < 0:
            values[index] = replacement


def demonstrate_in_place_modification():
    print("\n--- In-Place Traversal ---")

    values = [5, -3, 8, -1, 0, -7]

    print("Before:", values)
    replace_negative_values(values)
    print("After replacing negatives:", values)


# ============================================================================
# SECTION 25: CUSTOM TRAVERSAL WITH GENERATORS
# ============================================================================

def values_above_threshold(
    values: Iterable[float],
    threshold: float,
):
    """
    Yield matching values lazily.

    A generator does not construct the entire output list at once. This can
    reduce memory usage when processing large streams of data.
    """

    for value in values:
        if value > threshold:
            yield value


def demonstrate_generator_traversal():
    print("\n--- Lazy Traversal with a Generator ---")

    values = [2, 17, 4, 23, 8, 31]

    generator = values_above_threshold(values, 10)

    print("Values greater than 10:", list(generator))


# ============================================================================
# SECTION 26: TRAVERSAL OF RECORDS / DICTIONARIES
# ============================================================================

def average_salary(employees: Sequence[dict]) -> float:
    """Calculate average salary from employee records."""

    if not employees:
        raise ValueError("At least one employee is required.")

    total = 0

    for employee in employees:
        if "salary" not in employee:
            raise KeyError("Employee record is missing 'salary'.")

        total += employee["salary"]

    return total / len(employees)


def highest_paid_employee(employees: Sequence[dict]) -> dict:
    """Return the employee record with the highest salary."""

    if not employees:
        raise ValueError("Employee list cannot be empty.")

    highest = employees[0]

    for employee in employees[1:]:
        if employee["salary"] > highest["salary"]:
            highest = employee

    return highest


def demonstrate_record_traversal():
    print("\n--- Traversal of Records ---")

    employees = [
        {"name": "Asha", "salary": 65000},
        {"name": "Ravi", "salary": 72000},
        {"name": "Neha", "salary": 68000},
        {"name": "Kabir", "salary": 91000},
    ]

    print("Average salary:", average_salary(employees))
    print("Highest-paid employee:", highest_paid_employee(employees))


# ============================================================================
# SECTION 27: TEXT ARRAY TRAVERSAL
# ============================================================================

def count_long_words(words: Sequence[str], minimum_length: int) -> int:
    """Count strings whose length meets a threshold."""

    if minimum_length < 0:
        raise ValueError("Minimum length cannot be negative.")

    count = 0

    for word in words:
        if len(word) >= minimum_length:
            count += 1

    return count


def longest_word(words: Sequence[str]) -> str:
    """Find the longest string through traversal."""

    if not words:
        raise ValueError("At least one word is required.")

    longest = words[0]

    for word in words[1:]:
        if len(word) > len(longest):
            longest = word

    return longest


def demonstrate_text_traversal():
    print("\n--- Traversal of Text Arrays ---")

    words = [
        "Python",
        "array",
        "algorithm",
        "data",
        "traversal",
        "code",
    ]

    print("Words:", words)
    print("Words with length >= 7:", count_long_words(words, 7))
    print("Longest word:", longest_word(words))


# ============================================================================
# SECTION 28: EDGE CASES
# ============================================================================

def demonstrate_edge_cases():
    print("\n--- Edge Cases ---")

    cases = {
        "empty": [],
        "single": [42],
        "duplicates": [5, 5, 5, 5],
        "negative": [-8, -3, -15, -1],
        "mixed": [-5, 0, 7, -2, 9],
        "already_sorted": [1, 2, 3, 4, 5],
        "reverse_sorted": [5, 4, 3, 2, 1],
    }

    for name, values in cases.items():
        print(f"\n{name}: {values}")

        if values:
            print("Minimum:", find_minimum_manual(values))
            print("Maximum:", find_maximum_manual(values))
            print("Sum:", calculate_sum_manual(values))
            print("Average:", calculate_average_manual(values))
        else:
            print("Minimum/maximum/average: undefined for empty array")
            print("Sum:", calculate_sum_manual(values))


# ============================================================================
# SECTION 29: ERROR HANDLING
# ============================================================================

def demonstrate_error_handling():
    print("\n--- Error Handling ---")

    try:
        find_maximum_manual([])
    except ValueError as error:
        print("Handled empty-array error:", error)

    try:
        calculate_average_manual([])
    except ValueError as error:
        print("Handled average error:", error)

    try:
        get_elements_in_range([1, 2, 3], 10, 5)
    except ValueError as error:
        print("Handled invalid range:", error)

    try:
        validate_numeric_array([1, 2, "three"])
    except TypeError as error:
        print("Handled invalid element:", error)


# ============================================================================
# SECTION 30: PERFORMANCE COMPARISON
# ============================================================================

def repeated_traversal_statistics(values: Sequence[float]) -> dict[str, float]:
    """
    Calculate statistics using separate operations.

    This is clear and idiomatic for normal Python programs, even though it
    logically performs multiple traversals.
    """

    if not values:
        raise ValueError("Array cannot be empty.")

    return {
        "minimum": min(values),
        "maximum": max(values),
        "sum": sum(values),
        "average": sum(values) / len(values),
    }


def demonstrate_performance_concept():
    print("\n--- Performance and Traversal Count ---")

    values = list(range(1, 1001))

    separate = repeated_traversal_statistics(values)
    single = calculate_statistics_single_pass(values)

    print("Separate-operation statistics:", separate)
    print("Single-pass statistics:", single)

    print(
        "\nImportant distinction:"
        "\n- Multiple built-in operations may perform multiple logical passes."
        "\n- A single-pass algorithm can reduce traversal work."
        "\n- Built-ins are implemented efficiently and are often preferable"
        "\n  when the data is normal-sized and readability matters more."
    )


# ============================================================================
# SECTION 31: COMPARISON OF APPROACHES
# ============================================================================

def compare_traversal_approaches():
    print("\n--- Traversal Approach Comparison ---")

    values = [8, 3, 10, 2, 7]

    print("Array:", values)

    print("\nExplicit loop:")
    total = 0
    for value in values:
        total += value
    print(total)

    print("\nBuilt-in sum:")
    print(sum(values))

    print("\nList comprehension for filtering:")
    print([value for value in values if value > 5])

    print("\nGenerator expression:")
    print(sum(value for value in values if value > 5))

    print(
        "\nUse explicit loops when:"
        "\n- learning the traversal mechanism"
        "\n- several conditions or state variables are required"
        "\n- the algorithm is more complex than a simple expression"
    )

    print(
        "\nUse built-ins when:"
        "\n- the operation is standard"
        "\n- clarity improves"
        "\n- no custom traversal logic is necessary"
    )


# ============================================================================
# SECTION 32: DEBUGGING TRAVERSAL
# ============================================================================

def debug_running_sum(values: Sequence[float]) -> float:
    """
    Demonstrate state inspection during traversal.

    Printing every iteration is useful for learning and debugging, but should
    normally be removed or replaced by structured logging in production.
    """

    total = 0

    for index, value in enumerate(values):
        total += value

        print(
            f"DEBUG | index={index}, value={value}, running_total={total}"
        )

    return total


def demonstrate_debugging():
    print("\n--- Debugging a Traversal ---")

    values = [10, -2, 7, 5]

    result = debug_running_sum(values)

    print("Final total:", result)


# ============================================================================
# SECTION 33: TESTS
# ============================================================================

def run_assertion_tests():
    """
    Lightweight tests using Python assertions.

    These tests verify normal cases, edge cases, and important algorithmic
    behavior without requiring an external testing framework.
    """

    assert find_maximum_manual([3, 1, 8, 2]) == 8
    assert find_minimum_manual([3, 1, 8, 2]) == 1

    assert calculate_sum_manual([1, 2, 3, 4]) == 10
    assert calculate_average_manual([1, 2, 3, 4]) == 2.5

    assert frequency_manual([1, 2, 1, 3, 2, 1]) == {
        1: 3,
        2: 2,
        3: 1,
    }

    assert get_even_numbers([1, 2, 3, 4, 6]) == [2, 4, 6]
    assert get_odd_numbers([1, 2, 3, 4, 6]) == [1, 3]
    assert get_positive_numbers([-2, 0, 5, 8]) == [5, 8]
    assert get_negative_numbers([-2, 0, 5, -8]) == [-2, -8]

    assert linear_search([10, 20, 30], 20) == 1
    assert linear_search([10, 20, 30], 99) == -1

    assert running_sum([2, 5, 3]) == [2, 7, 10]
    assert running_maximum([4, 2, 7, 3]) == [4, 4, 7, 7]
    assert running_minimum([4, 2, 7, 1]) == [4, 2, 2, 1]

    assert build_prefix_sum([10, 20, 30]) == [0, 10, 30, 60]
    assert range_sum(build_prefix_sum([10, 20, 30]), 0, 1) == 30

    assert elementwise_sum([1, 2], [3, 4]) == [4, 6]
    assert dot_product([1, 2, 3], [4, 5, 6]) == 32

    assert reverse_copy_manual([1, 2, 3]) == [3, 2, 1]

    assert find_increasing_adjacent_pairs([1, 3, 2, 5]) == [
        (1, 3),
        (2, 5),
    ]

    assert maximum_window_sum([2, 1, 5, 1, 3, 2], 3) == 9
    assert all_window_averages([2, 4, 6, 8], 2) == [3, 5, 7]

    assert matrix_row_sum([[1, 2], [3, 4]]) == [3, 7]
    assert matrix_column_sum([[1, 2], [3, 4]]) == [4, 6]

    assert conditional_statistics(
        [1, 2, 3, 4],
        lambda value: value % 2 == 0,
    ) == {
        "count": 2,
        "sum": 6,
        "minimum": 2,
        "maximum": 4,
        "average": 3.0,
    }

    assert find_duplicates([1, 2, 1, 3, 2, 1]) == [1, 2]
    assert second_largest_distinct([5, 1, 9, 9, 7]) == 7

    assert maximum_single_transaction_profit(
        [7, 1, 5, 3, 6, 4]
    ) == 5

    assert stable_partition_even_first(
        [5, 2, 7, 4, 1, 6]
    ) == [2, 4, 6, 5, 7, 1]

    values = [3, -2, 5, -7]
    replace_negative_values(values)
    assert values == [3, 0, 5, 0]

    assert list(values_above_threshold([2, 10, 4, 20], 9)) == [10, 20]

    assert count_long_words(["a", "abcd", "python"], 4) == 2
    assert longest_word(["cat", "elephant", "dog"]) == "elephant"

    assert isclose(
        calculate_average_manual([0.1, 0.2]),
        0.15,
        rel_tol=1e-12,
    )

    print("\nAll assertion tests passed.")


# ============================================================================
# SECTION 34: PRACTICAL COMPLETE EXAMPLE
# ============================================================================

def analyze_sales_data(sales: Sequence[float]) -> dict:
    """
    Perform a practical traversal-based analysis of daily sales.

    The function identifies:
    - total sales
    - average sales
    - highest day
    - lowest day
    - number of days above average
    - number of zero-sales days
    - number of profitable/positive days
    - running sales
    """

    if not sales:
        raise ValueError("Sales data cannot be empty.")

    validate_numeric_array(sales)

    total = 0
    highest = sales[0]
    lowest = sales[0]
    zero_days = 0
    positive_days = 0

    for sale in sales:
        total += sale

        if sale > highest:
            highest = sale

        if sale < lowest:
            lowest = sale

        if sale == 0:
            zero_days += 1

        if sale > 0:
            positive_days += 1

    average = total / len(sales)

    days_above_average = 0

    for sale in sales:
        if sale > average:
            days_above_average += 1

    return {
        "total_sales": total,
        "average_sales": average,
        "highest_day_sales": highest,
        "lowest_day_sales": lowest,
        "days_above_average": days_above_average,
        "zero_sales_days": zero_days,
        "positive_sales_days": positive_days,
        "running_sales": running_sum(sales),
    }


def demonstrate_practical_example():
    print("\n--- Practical Sales Analysis ---")

    sales = [1200, 950, 0, 1750, 2100, 1300, 800]

    result = analyze_sales_data(sales)

    print("Daily sales:", sales)

    for key, value in result.items():
        print(f"{key}: {value}")


# ============================================================================
# SECTION 35: COMPLETE STUDY DEMONSTRATION
# ============================================================================

def main():
    print("=" * 72)
    print("ARRAY TRAVERSAL PROBLEMS")
    print("=" * 72)

    demonstrate_basic_array()
    demonstrate_maximum_minimum()
    demonstrate_sum_average()
    demonstrate_frequency()
    demonstrate_conditional_traversal()
    demonstrate_conditional_counts()
    demonstrate_matching()
    demonstrate_enumerate()
    demonstrate_linear_search()
    demonstrate_single_pass_statistics()
    demonstrate_running_results()
    demonstrate_prefix_sum()
    demonstrate_two_array_traversal()
    demonstrate_reverse_traversal()
    demonstrate_adjacent_traversal()
    demonstrate_sliding_window()
    demonstrate_matrix_traversal()
    demonstrate_conditional_statistics()
    demonstrate_duplicate_detection()
    demonstrate_second_largest()
    demonstrate_profit_traversal()
    demonstrate_partition()
    demonstrate_in_place_modification()
    demonstrate_generator_traversal()
    demonstrate_record_traversal()
    demonstrate_text_traversal()
    demonstrate_edge_cases()
    demonstrate_error_handling()
    demonstrate_performance_concept()
    compare_traversal_approaches()
    demonstrate_debugging()
    demonstrate_practical_example()

    print("\n--- Running Tests ---")
    run_assertion_tests()

    print("\n" + "=" * 72)
    print("ARRAY TRAVERSAL STUDY PROGRAM COMPLETED")
    print("=" * 72)


if __name__ == "__main__":
    main()
