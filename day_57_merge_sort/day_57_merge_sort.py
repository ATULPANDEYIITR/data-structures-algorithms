from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Sequence, TypeVar
import random
import time


T = TypeVar("T")


class SortOrder(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


@dataclass(frozen=True)
class SortResult:
    values: list
    comparisons: int
    merges: int
    elapsed_seconds: float


class MergeSortError(ValueError):
    """Raised when merge-sort input or configuration is invalid."""


class MergeSort:
    """
    Stable top-down merge sort.

    The implementation keeps the original input untouched and uses a single
    auxiliary buffer for merging. Its worst-case time complexity is O(n log n)
    and its auxiliary space complexity is O(n).
    """

    def __init__(
        self,
        *,
        key: Callable[[T], object] | None = None,
        reverse: bool = False,
    ) -> None:
        self.key = key or (lambda value: value)
        self.reverse = reverse
        self.comparisons = 0
        self.merges = 0

    def sort(self, values: Sequence[T]) -> SortResult:
        if values is None:
            raise MergeSortError("Input cannot be None.")

        data = list(values)

        # Validate that the comparator can actually compare the keys before
        # modifying the working array.
        for value in data:
            try:
                self.key(value)
            except Exception as exc:
                raise MergeSortError(
                    f"Key function failed for value {value!r}: {exc}"
                ) from exc

        self.comparisons = 0
        self.merges = 0

        start = time.perf_counter()

        if len(data) > 1:
            buffer = [None] * len(data)
            self._merge_sort(data, buffer, 0, len(data) - 1)

        elapsed = time.perf_counter() - start

        return SortResult(
            values=data,
            comparisons=self.comparisons,
            merges=self.merges,
            elapsed_seconds=elapsed,
        )

    def _merge_sort(
        self,
        data: list[T],
        buffer: list[T | None],
        left: int,
        right: int,
    ) -> None:
        if left >= right:
            return

        middle = left + (right - left) // 2

        self._merge_sort(data, buffer, left, middle)
        self._merge_sort(data, buffer, middle + 1, right)

        # If the two already-sorted halves are ordered, no merge is needed.
        if not self._comes_before(data[middle + 1], data[middle]):
            return

        self._merge(data, buffer, left, middle, right)

    def _comes_before(self, first: T, second: T) -> bool:
        self.comparisons += 1

        first_key = self.key(first)
        second_key = self.key(second)

        if self.reverse:
            return first_key > second_key

        return first_key < second_key

    def _merge(
        self,
        data: list[T],
        buffer: list[T | None],
        left: int,
        middle: int,
        right: int,
    ) -> None:
        self.merges += 1

        i = left
        j = middle + 1
        k = left

        while i <= middle and j <= right:
            # Taking the left element when keys are equal preserves stability.
            if self._comes_before(data[j], data[i]):
                buffer[k] = data[j]
                j += 1
            else:
                buffer[k] = data[i]
                i += 1
            k += 1

        while i <= middle:
            buffer[k] = data[i]
            i += 1
            k += 1

        while j <= right:
            buffer[k] = data[j]
            j += 1
            k += 1

        for index in range(left, right + 1):
            data[index] = buffer[index]  # type: ignore[assignment]


@dataclass(frozen=True)
class Student:
    name: str
    score: int


def verify_sorted(values: Sequence[T], key: Callable[[T], object] | None = None) -> None:
    key = key or (lambda value: value)

    for index in range(1, len(values)):
        if key(values[index - 1]) > key(values[index]):
            raise AssertionError(f"Array is not sorted at index {index}.")


def demonstrate_basic_sorting() -> None:
    examples = [
        [],
        [7],
        [5, 2, 9, 1, 5, 6],
        [4, 3, 2, 1],
        [1, 2, 3, 4],
        [3, 3, 3, 3],
        [-10, 4, -2, 7, 0],
    ]

    print("Basic merge-sort examples")

    for values in examples:
        result = MergeSort().sort(values)
        verify_sorted(result.values)
        print(
            f"input={values!r:28} "
            f"sorted={result.values!r:28} "
            f"comparisons={result.comparisons}"
        )


def demonstrate_stability() -> None:
    students = [
        Student("Asha", 85),
        Student("Ravi", 70),
        Student("Maya", 85),
        Student("Karan", 70),
        Student("Neha", 85),
    ]

    result = MergeSort(key=lambda student: student.score).sort(students)

    print("\nStable sorting by score")

    for student in result.values:
        print(f"{student.name:>5} -> {student.score}")

    score_70_names = [
        student.name for student in result.values if student.score == 70
    ]
    score_85_names = [
        student.name for student in result.values if student.score == 85
    ]

    assert score_70_names == ["Ravi", "Karan"]
    assert score_85_names == ["Asha", "Maya", "Neha"]


def demonstrate_descending() -> None:
    values = [10, 4, 8, 2, 9, 1]
    result = MergeSort(reverse=True).sort(values)

    assert result.values == [10, 9, 8, 4, 2, 1]
    print("\nDescending:", result.values)


def demonstrate_large_input() -> None:
    random.seed(42)
    values = [random.randint(-100_000, 100_000) for _ in range(10_000)]

    result = MergeSort().sort(values)

    verify_sorted(result.values)
    assert sorted(values) == result.values

    print("\nLarge-input validation")
    print(f"items={len(values)}")
    print(f"comparisons={result.comparisons}")
    print(f"merges={result.merges}")
    print(f"elapsed={result.elapsed_seconds:.6f}s")


def demonstrate_failure_handling() -> None:
    sorter = MergeSort()

    try:
        sorter.sort(None)  # type: ignore[arg-type]
    except MergeSortError as exc:
        print("\nValidation error:", exc)

    try:
        MergeSort(key=lambda value: value["missing"]).sort([{"value": 1}])
    except MergeSortError as exc:
        print("Key validation error:", exc)


def run_self_tests() -> None:
    random.seed(7)

    for size in range(0, 100):
        values = [random.randint(-20, 20) for _ in range(size)]
        result = MergeSort().sort(values)

        assert result.values == sorted(values)
        verify_sorted(result.values)

    # Stability test.
    records = [
        ("first", 2),
        ("second", 1),
        ("third", 2),
        ("fourth", 1),
    ]

    sorted_records = MergeSort(key=lambda item: item[1]).sort(records).values

    assert sorted_records == [
        ("second", 1),
        ("fourth", 1),
        ("first", 2),
        ("third", 2),
    ]

    # Reverse-order test.
    values = [1, 8, 3, 4, 2]
    assert MergeSort(reverse=True).sort(values).values == [8, 4, 3, 2, 1]

    print("\nSelf-tests: PASSED")


def main() -> None:
    demonstrate_basic_sorting()
    demonstrate_stability()
    demonstrate_descending()
    demonstrate_large_input()
    demonstrate_failure_handling()
    run_self_tests()

    print("\nComplexity")
    print("Best case:    O(n log n) for the standard recursive structure.")
    print("Average case: O(n log n)")
    print("Worst case:   O(n log n)")
    print("Auxiliary:    O(n)")
    print("Stable:       Yes, when the key function is used as implemented.")


if __name__ == "__main__":
    main()
