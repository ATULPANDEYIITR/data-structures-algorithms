from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple


class SearchError(ValueError):
    """Raised when search input violates an algorithm's preconditions."""


@dataclass(frozen=True)
class SearchResult:
    algorithm: str
    index: Optional[int]
    value: Optional[int]
    comparisons: int


def binary_search(
    values: Sequence[int], target: int
) -> SearchResult:
    """Search a sorted sequence in O(log n) time."""
    left, right = 0, len(values) - 1
    comparisons = 0

    while left <= right:
        mid = left + (right - left) // 2
        comparisons += 1

        if values[mid] == target:
            return SearchResult("binary_search", mid, values[mid], comparisons)
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return SearchResult("binary_search", None, None, comparisons)


def rotated_binary_search(
    values: Sequence[int], target: int
) -> SearchResult:
    """
    Search a rotated strictly increasing array.

    Example:
        [13, 18, 25, 2, 8, 10] is a rotation of
        [2, 8, 10, 13, 18, 25].
    """
    left, right = 0, len(values) - 1
    comparisons = 0

    while left <= right:
        mid = left + (right - left) // 2
        comparisons += 1

        if values[mid] == target:
            return SearchResult(
                "rotated_binary_search", mid, values[mid], comparisons
            )

        # The left half is sorted.
        if values[left] <= values[mid]:
            if values[left] <= target < values[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # The right half is sorted.
        else:
            if values[mid] < target <= values[right]:
                left = mid + 1
            else:
                right = mid - 1

    return SearchResult(
        "rotated_binary_search", None, None, comparisons
    )


def rotated_binary_search_with_duplicates(
    values: Sequence[int], target: int
) -> SearchResult:
    """
    Search a rotated sorted array that may contain duplicates.

    Duplicate boundary values can make it impossible to identify a
    sorted half, so equal boundaries are discarded. Worst case is O(n).
    """
    left, right = 0, len(values) - 1
    comparisons = 0

    while left <= right:
        mid = left + (right - left) // 2
        comparisons += 1

        if values[mid] == target:
            return SearchResult(
                "rotated_search_with_duplicates",
                mid,
                values[mid],
                comparisons,
            )

        if values[left] == values[mid] == values[right]:
            left += 1
            right -= 1
            continue

        if values[left] <= values[mid]:
            if values[left] <= target < values[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if values[mid] < target <= values[right]:
                left = mid + 1
            else:
                right = mid - 1

    return SearchResult(
        "rotated_search_with_duplicates", None, None, comparisons
    )


def find_peak_bitonic(values: Sequence[int]) -> SearchResult:
    """
    Find the peak index in a strictly bitonic sequence.

    A bitonic sequence increases up to one peak and then decreases.
    The peak is found in O(log n).
    """
    if not values:
        raise SearchError("A bitonic sequence cannot be empty.")

    left, right = 0, len(values) - 1
    comparisons = 0

    while left < right:
        mid = left + (right - left) // 2
        comparisons += 1

        if values[mid] < values[mid + 1]:
            left = mid + 1
        else:
            right = mid

    return SearchResult(
        "bitonic_peak", left, values[left], comparisons
    )


def search_bitonic(values: Sequence[int], target: int) -> SearchResult:
    """Search a strictly bitonic sequence in O(log n)."""
    if not values:
        return SearchResult("bitonic_search", None, None, 0)

    peak = find_peak_bitonic(values)
    comparisons = peak.comparisons

    # Search increasing portion.
    left, right = 0, peak.index
    while left <= right:
        mid = left + (right - left) // 2
        comparisons += 1

        if values[mid] == target:
            return SearchResult(
                "bitonic_search", mid, values[mid], comparisons
            )
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    # Search decreasing portion.
    left, right = peak.index + 1, len(values) - 1
    while left <= right:
        mid = left + (right - left) // 2
        comparisons += 1

        if values[mid] == target:
            return SearchResult(
                "bitonic_search", mid, values[mid], comparisons
            )
        if values[mid] > target:
            left = mid + 1
        else:
            right = mid - 1

    return SearchResult("bitonic_search", None, None, comparisons)


def search_matrix(
    matrix: Sequence[Sequence[int]], target: int
) -> SearchResult:
    """
    Search a matrix where every row is sorted and the first value
    of each row is greater than the last value of the previous row.

    Treating the matrix as a virtual one-dimensional sorted array
    gives O(log(rows * columns)) time without flattening it.
    """
    if not matrix:
        return SearchResult("matrix_binary_search", None, None, 0)

    columns = len(matrix[0])
    if columns == 0:
        return SearchResult("matrix_binary_search", None, None, 0)

    if any(len(row) != columns for row in matrix):
        raise SearchError("Matrix must be rectangular.")

    rows = len(matrix)
    left, right = 0, rows * columns - 1
    comparisons = 0

    while left <= right:
        mid = left + (right - left) // 2
        row, column = divmod(mid, columns)
        value = matrix[row][column]
        comparisons += 1

        if value == target:
            return SearchResult(
                "matrix_binary_search",
                mid,
                value,
                comparisons,
            )
        if value < target:
            left = mid + 1
        else:
            right = mid - 1

    return SearchResult(
        "matrix_binary_search", None, None, comparisons
    )


def search_row_column_matrix(
    matrix: Sequence[Sequence[int]], target: int
) -> SearchResult:
    """
    Search a matrix sorted left-to-right in rows and top-to-bottom
    in columns. The staircase algorithm runs in O(rows + columns).
    """
    if not matrix:
        return SearchResult("staircase_matrix_search", None, None, 0)

    columns = len(matrix[0])
    if columns == 0:
        return SearchResult("staircase_matrix_search", None, None, 0)

    if any(len(row) != columns for row in matrix):
        raise SearchError("Matrix must be rectangular.")

    row, column = 0, columns - 1
    comparisons = 0

    while row < len(matrix) and column >= 0:
        value = matrix[row][column]
        comparisons += 1

        if value == target:
            index = row * columns + column
            return SearchResult(
                "staircase_matrix_search",
                index,
                value,
                comparisons,
            )

        if value > target:
            column -= 1
        else:
            row += 1

    return SearchResult(
        "staircase_matrix_search", None, None, comparisons
    )


def lower_bound(values: Sequence[int], target: int) -> int:
    """Return the first index whose value is >= target."""
    left, right = 0, len(values)

    while left < right:
        mid = left + (right - left) // 2
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid

    return left


def upper_bound(values: Sequence[int], target: int) -> int:
    """Return the first index whose value is > target."""
    left, right = 0, len(values)

    while left < right:
        mid = left + (right - left) // 2
        if values[mid] <= target:
            left = mid + 1
        else:
            right = mid

    return left


def first_and_last(
    values: Sequence[int], target: int
) -> Tuple[int, int]:
    first = lower_bound(values, target)
    last_exclusive = upper_bound(values, target)

    if first == last_exclusive:
        return -1, -1

    return first, last_exclusive - 1


def assert_sorted(values: Sequence[int]) -> None:
    if any(values[i] > values[i + 1] for i in range(len(values) - 1)):
        raise SearchError("Input must be sorted in non-decreasing order.")


def run_examples() -> None:
    sorted_values = [2, 5, 8, 12, 17, 21, 29]
    assert_sorted(sorted_values)

    result = binary_search(sorted_values, 17)
    assert result.index == 4

    rotated = [13, 18, 25, 2, 8, 10]
    result = rotated_binary_search(rotated, 8)
    assert result.index == 4

    duplicate_rotated = [2, 5, 6, 0, 0, 1, 2]
    result = rotated_binary_search_with_duplicates(
        duplicate_rotated, 0
    )
    assert result.index in {3, 4}

    bitonic = [2, 5, 9, 14, 19, 16, 11, 4]
    peak = find_peak_bitonic(bitonic)
    assert peak.index == 4

    result = search_bitonic(bitonic, 11)
    assert result.index == 6

    matrix = [
        [1, 3, 5, 7],
        [10, 12, 14, 16],
        [20, 22, 24, 26],
    ]
    result = search_matrix(matrix, 22)
    assert result.index == 9

    sorted_rows_columns = [
        [1, 4, 7, 11],
        [2, 5, 8, 13],
        [3, 6, 9, 15],
        [10, 12, 14, 18],
    ]
    result = search_row_column_matrix(sorted_rows_columns, 9)
    assert result.index == 10

    duplicates = [1, 2, 2, 2, 4, 7]
    assert first_and_last(duplicates, 2) == (1, 3)

    assert binary_search(sorted_values, 100).index is None
    assert search_matrix(matrix, 99).index is None

    print("Advanced binary-search examples passed.")
    print("Rotated:", rotated_binary_search(rotated, 8))
    print("Bitonic peak:", peak)
    print("Matrix:", search_matrix(matrix, 22))
    print("Range:", first_and_last(duplicates, 2))


if __name__ == "__main__":
    run_examples()
