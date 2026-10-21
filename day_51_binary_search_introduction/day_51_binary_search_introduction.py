"""Binary Search Introduction: iterative and recursive search on sorted data.

Run with:
    python binary_search.py
"""

from dataclasses import dataclass
from typing import Optional


class BinarySearchError(ValueError):
    """Raised when input violates binary-search preconditions."""


def validate_sorted(values: list[int]) -> None:
    """Binary search requires non-decreasing sorted input."""
    if any(values[index] > values[index + 1] for index in range(len(values) - 1)):
        raise BinarySearchError("Binary search requires a sorted list.")


def binary_search_iterative(values: list[int], target: int) -> Optional[int]:
    """Return any matching index, or None when target is absent.

    The interval [left, right] is closed. Each comparison removes
    roughly half of the remaining candidates.
    """
    validate_sorted(values)

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

    return None


def binary_search_recursive(
    values: list[int], target: int, left: int = 0, right: Optional[int] = None
) -> Optional[int]:
    """Recursive binary search using a closed search interval."""
    if right is None:
        validate_sorted(values)
        right = len(values) - 1

    if left > right:
        return None

    middle = left + (right - left) // 2

    if values[middle] == target:
        return middle
    if values[middle] < target:
        return binary_search_recursive(values, target, middle + 1, right)

    return binary_search_recursive(values, target, left, middle - 1)


def lower_bound(values: list[int], target: int) -> int:
    """Return the first index whose value is >= target.

    If no such value exists, returns len(values).
    """
    validate_sorted(values)

    left = 0
    right = len(values)

    while left < right:
        middle = left + (right - left) // 2

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle

    return left


def upper_bound(values: list[int], target: int) -> int:
    """Return the first index whose value is > target."""
    validate_sorted(values)

    left = 0
    right = len(values)

    while left < right:
        middle = left + (right - left) // 2

        if values[middle] <= target:
            left = middle + 1
        else:
            right = middle

    return left


@dataclass(frozen=True)
class SearchResult:
    target: int
    index: Optional[int]
    method: str


def demonstrate(values: list[int], targets: list[int]) -> None:
    print(f"Sorted data: {values}")

    for target in targets:
        iterative = binary_search_iterative(values, target)
        recursive = binary_search_recursive(values, target)

        print(
            f"target={target:>3} | "
            f"iterative={iterative!s:>4} | "
            f"recursive={recursive!s:>4}"
        )

        if iterative is not None:
            assert values[iterative] == target
        if recursive is not None:
            assert values[recursive] == target

        first = lower_bound(values, target)
        after = upper_bound(values, target)

        if first < len(values) and values[first] == target:
            print(f"  matching range: [{first}, {after - 1}]")
        else:
            print(f"  insertion position: {first}")


def run_edge_cases() -> None:
    cases = [
        ([], 10),
        ([10], 10),
        ([10], 5),
        ([1, 2, 2, 2, 7], 2),
        ([-20, -10, -1, 0, 4, 9], -20),
        ([-20, -10, -1, 0, 4, 9], 100),
    ]

    print("\nEdge cases:")
    for values, target in cases:
        print(
            f"{values!r}, target={target}: "
            f"{binary_search_iterative(values, target)!r}"
        )

    try:
        binary_search_iterative([1, 5, 3, 9], 5)
    except BinarySearchError as exc:
        print(f"Validation failure handled: {exc}")


def main() -> None:
    values = [-20, -10, -1, 0, 4, 4, 4, 9, 15, 21, 42]
    demonstrate(values, [-20, 4, 5, 42, 100])
    run_edge_cases()

    print("\nComplexity:")
    print("  Time: O(log n) for iterative and recursive search")
    print("  Extra space: O(1) iterative, O(log n) recursive call stack")


if __name__ == "__main__":
    main()
