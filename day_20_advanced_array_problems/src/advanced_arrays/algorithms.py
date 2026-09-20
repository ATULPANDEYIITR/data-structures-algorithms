"""Advanced array algorithms.

The functions in this module use only the Python standard library.
Each implementation is written to expose the algorithmic idea directly.
"""

from __future__ import annotations

from collections.abc import Sequence


def _require_integer_sequence(values: Sequence[int], name: str = "values") -> None:
    """Validate that a sequence contains integers.

    bool is rejected because it is a subclass of int but normally represents
    a logical value rather than an array number.
    """
    if not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence")

    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise TypeError(f"{name} must contain only integers")


def max_subarray_sum(values: Sequence[int]) -> int:
    """Return the largest sum obtainable from a contiguous non-empty subarray.

    Uses Kadane's algorithm.

    Time: O(n)
    Space: O(1)
    """
    _require_integer_sequence(values)

    if not values:
        raise ValueError("values must not be empty")

    best_ending_here = best_total = values[0]

    for value in values[1:]:
        best_ending_here = max(value, best_ending_here + value)
        best_total = max(best_total, best_ending_here)

    return best_total


def find_majority_element(values: Sequence[int]) -> int | None:
    """Return an element occurring more than n/2 times, otherwise None.

    Uses the Boyer-Moore majority vote algorithm followed by verification.

    Time: O(n)
    Space: O(1)
    """
    _require_integer_sequence(values)

    if not values:
        return None

    candidate = None
    count = 0

    for value in values:
        if count == 0:
            candidate = value
            count = 1
        elif value == candidate:
            count += 1
        else:
            count -= 1

    if values.count(candidate) > len(values) // 2:
        return candidate

    return None


def find_missing_number(values: Sequence[int]) -> int:
    """Find the missing value from an array containing 0..n exactly once.

    Uses XOR so that no auxiliary set is required.

    Time: O(n)
    Space: O(1)
    """
    _require_integer_sequence(values)

    n = len(values)
    result = n

    for index, value in enumerate(values):
        if value < 0 or value > n:
            raise ValueError("values must contain integers in the range 0..n")
        result ^= index ^ value

    if len(set(values)) != len(values):
        raise ValueError("values must contain unique numbers")

    return result


def find_duplicate(values: Sequence[int]) -> int:
    """Find a duplicate in an array containing values 1..n with one duplicate.

    Floyd's cycle detection treats each value as a pointer to another index.

    Time: O(n)
    Space: O(1)
    """
    _require_integer_sequence(values)

    if len(values) < 2:
        raise ValueError("at least two values are required")

    n = len(values) - 1
    if any(value < 1 or value > n for value in values):
        raise ValueError("values must be in the range 1..n")

    slow = values[0]
    fast = values[values[0]]

    while slow != fast:
        slow = values[slow]
        fast = values[values[fast]]

    slow = 0

    while slow != fast:
        slow = values[slow]
        fast = values[fast]

    return slow


def rotate_array(values: Sequence[int], k: int) -> list[int]:
    """Rotate an array to the right by k positions.

    Uses the three-reversal technique.

    Time: O(n)
    Space: O(n) because the function returns a new list.
    """
    _require_integer_sequence(values)

    result = list(values)
    if not result:
        return result

    k %= len(result)

    def reverse(left: int, right: int) -> None:
        while left < right:
            result[left], result[right] = result[right], result[left]
            left += 1
            right -= 1

    reverse(0, len(result) - 1)
    reverse(0, k - 1)
    reverse(k, len(result) - 1)

    return result


def product_except_self(values: Sequence[int]) -> list[int]:
    """Return products of all values except the value at each position.

    Does not use division and correctly handles zeros.

    Time: O(n)
    Space: O(n) for the returned output.
    """
    _require_integer_sequence(values)

    result = [1] * len(values)

    prefix = 1
    for index, value in enumerate(values):
        result[index] = prefix
        prefix *= value

    suffix = 1
    for index in range(len(values) - 1, -1, -1):
        result[index] *= suffix
        suffix *= values[index]

    return result


def rearrange_alternating(values: Sequence[int]) -> list[int]:
    """Rearrange values so positive and negative values alternate when possible.

    The relative order within the positive and negative groups is preserved.
    Zeros are treated as non-negative values.

    When one sign has more elements, remaining values are appended.

    Time: O(n)
    Space: O(n)
    """
    _require_integer_sequence(values)

    positive = [value for value in values if value >= 0]
    negative = [value for value in values if value < 0]

    result: list[int] = []
    positive_turn = len(positive) >= len(negative)
    positive_index = negative_index = 0

    while positive_index < len(positive) or negative_index < len(negative):
        if positive_turn and positive_index < len(positive):
            result.append(positive[positive_index])
            positive_index += 1
        elif not positive_turn and negative_index < len(negative):
            result.append(negative[negative_index])
            negative_index += 1
        elif positive_index < len(positive):
            result.append(positive[positive_index])
            positive_index += 1
        else:
            result.append(negative[negative_index])
            negative_index += 1

        positive_turn = not positive_turn

    return result


def longest_consecutive_sequence(values: Sequence[int]) -> int:
    """Return the length of the longest consecutive integer sequence.

    A hash set allows every sequence to be discovered from its smallest value.

    Time: O(n) expected
    Space: O(n)
    """
    _require_integer_sequence(values)

    numbers = set(values)
    longest = 0

    for value in numbers:
        if value - 1 not in numbers:
            length = 1
            current = value

            while current + 1 in numbers:
                current += 1
                length += 1

            longest = max(longest, length)

    return longest


def three_sum(values: Sequence[int], target: int = 0) -> list[tuple[int, int, int]]:
    """Return unique triples whose sum equals target.

    Sorting enables a two-pointer search and duplicate elimination.

    Time: O(n²)
    Space: O(n) for the sorted copy and result.
    """
    _require_integer_sequence(values)

    numbers = sorted(values)
    result: list[tuple[int, int, int]] = []

    for index in range(len(numbers) - 2):
        if index > 0 and numbers[index] == numbers[index - 1]:
            continue

        left = index + 1
        right = len(numbers) - 1

        while left < right:
            total = numbers[index] + numbers[left] + numbers[right]

            if total == target:
                result.append((numbers[index], numbers[left], numbers[right]))
                left += 1
                right -= 1

                while left < right and numbers[left] == numbers[left - 1]:
                    left += 1
                while left < right and numbers[right] == numbers[right + 1]:
                    right -= 1
            elif total < target:
                left += 1
            else:
                right -= 1

    return result


def merge_intervals(intervals: Sequence[Sequence[int]]) -> list[list[int]]:
    """Merge overlapping closed intervals.

    Each interval must contain exactly two integer endpoints.

    Time: O(n log n)
    Space: O(n)
    """
    normalized: list[list[int]] = []

    for interval in intervals:
        if len(interval) != 2:
            raise ValueError("each interval must contain exactly two values")

        start, end = interval
        if isinstance(start, bool) or isinstance(end, bool):
            raise TypeError("interval endpoints must be integers")
        if not isinstance(start, int) or not isinstance(end, int):
            raise TypeError("interval endpoints must be integers")
        if start > end:
            raise ValueError("interval start cannot exceed interval end")

        normalized.append([start, end])

    normalized.sort(key=lambda interval: interval[0])
    merged: list[list[int]] = []

    for start, end in normalized:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    return merged


def apply_permutation(values: Sequence[int], permutation: Sequence[int]) -> list[int]:
    """Return values reordered according to a permutation array.

    permutation[i] is the destination index for values[i].

    The permutation must contain each index exactly once.

    Time: O(n)
    Space: O(n)
    """
    _require_integer_sequence(values, "values")
    _require_integer_sequence(permutation, "permutation")

    if len(values) != len(permutation):
        raise ValueError("values and permutation must have equal lengths")

    n = len(values)
    if sorted(permutation) != list(range(n)):
        raise ValueError("permutation must contain each index exactly once")

    result = [0] * n

    for source, destination in enumerate(permutation):
        result[destination] = values[source]

    return result
