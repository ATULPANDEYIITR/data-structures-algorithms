#!/usr/bin/env python3
"""Sorting fundamentals: stability, in-place behavior, comparison sorting, and complexity."""

from dataclasses import dataclass
from random import Random
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SortResult:
    algorithm: str
    values: list
    stable: bool
    in_place: bool
    comparisons: int
    writes: int


@dataclass(frozen=True)
class Student:
    name: str
    score: int
    registration_order: int


def insertion_sort(items: list[T], key: Callable[[T], object] = lambda x: x) -> SortResult:
    """Stable, in-place insertion sort with O(n²) worst-case time."""
    comparisons = 0
    writes = 0

    for i in range(1, len(items)):
        current = items[i]
        current_key = key(current)
        j = i - 1

        while j >= 0:
            comparisons += 1
            if key(items[j]) <= current_key:
                break
            items[j + 1] = items[j]
            writes += 1
            j -= 1

        items[j + 1] = current
        writes += 1

    return SortResult("insertion_sort", items, True, True, comparisons, writes)


def merge_sort(items: Iterable[T], key: Callable[[T], object] = lambda x: x) -> SortResult:
    """Stable merge sort. Uses O(n) auxiliary space and O(n log n) time."""
    values = list(items)
    comparisons = 0
    writes = 0

    def merge(left: list[T], right: list[T]) -> list[T]:
        nonlocal comparisons, writes
        result: list[T] = []
        i = j = 0

        while i < len(left) and j < len(right):
            comparisons += 1
            # Choosing the left element on equality preserves stability.
            if key(left[i]) <= key(right[j]):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
            writes += 1

        result.extend(left[i:])
        result.extend(right[j:])
        writes += len(left) - i + len(right) - j
        return result

    def sort(sequence: list[T]) -> list[T]:
        if len(sequence) < 2:
            return sequence
        middle = len(sequence) // 2
        return merge(sort(sequence[:middle]), sort(sequence[middle:]))

    sorted_values = sort(values)
    return SortResult("merge_sort", sorted_values, True, False, comparisons, writes)


def quick_sort(items: list[T], key: Callable[[T], object] = lambda x: x) -> SortResult:
    """In-place three-way quicksort; average O(n log n), worst O(n²)."""
    comparisons = 0
    writes = 0

    def sort(low: int, high: int) -> None:
        nonlocal comparisons, writes

        while low < high:
            pivot = key(items[(low + high) // 2])
            less, current, greater = low, low, high

            while current <= greater:
                current_key = key(items[current])
                comparisons += 1

                if current_key < pivot:
                    items[less], items[current] = items[current], items[less]
                    writes += 2
                    less += 1
                    current += 1
                else:
                    comparisons += 1
                    if current_key > pivot:
                        items[current], items[greater] = items[greater], items[current]
                        writes += 2
                        greater -= 1
                    else:
                        current += 1

            # Recurse into the smaller partition to limit stack depth.
            if less - low < high - greater:
                sort(low, less - 1)
                low = greater + 1
            else:
                sort(greater + 1, high)
                high = less - 1

    sort(0, len(items) - 1)
    return SortResult("quick_sort", items, False, True, comparisons, writes)


def is_sorted(items: list[T], key: Callable[[T], object] = lambda x: x) -> bool:
    return all(key(items[i - 1]) <= key(items[i]) for i in range(1, len(items)))


def is_stable(original: list[T], sorted_items: list[T],
              key: Callable[[T], object]) -> bool:
    """Check whether equal-key records retain their original relative order."""
    original_positions = {id(item): i for i, item in enumerate(original)}
    for i in range(1, len(sorted_items)):
        if key(sorted_items[i - 1]) == key(sorted_items[i]):
            if original_positions[id(sorted_items[i - 1])] > original_positions[id(sorted_items[i])]:
                return False
    return True


def main() -> None:
    examples = [
        [],
        [1],
        [5, 2, 4, 1, 3],
        [4, 4, 4, 4],
        [9, -2, 0, 7, -2],
    ]

    print("Integer sorting")
    for sample in examples:
        expected = sorted(sample)
        insertion_input = sample.copy()
        merge_input = sample.copy()
        quick_input = sample.copy()

        insertion = insertion_sort(insertion_input)
        merged = merge_sort(merge_input)
        quick = quick_sort(quick_input)

        assert insertion.values == expected
        assert merged.values == expected
        assert quick.values == expected
        assert is_sorted(insertion.values)
        assert is_sorted(merged.values)
        assert is_sorted(quick.values)

        print(
            f"{sample!r} -> {expected!r} | "
            f"insertion comparisons={insertion.comparisons}, "
            f"merge comparisons={merged.comparisons}, "
            f"quick comparisons={quick.comparisons}"
        )

    students = [
        Student("Asha", 90, 1),
        Student("Ravi", 75, 2),
        Student("Meera", 90, 3),
        Student("Kabir", 75, 4),
        Student("Isha", 90, 5),
    ]

    insertion_records = students.copy()
    insertion_sort(insertion_records, key=lambda student: student.score)
    assert is_stable(students, insertion_records, lambda student: student.score)

    merged_records = merge_sort(students, key=lambda student: student.score)
    assert is_stable(students, merged_records.values, lambda student: student.score)

    quick_records = students.copy()
    quick_sort(quick_records, key=lambda student: student.score)

    print("\nStudent records sorted by score")
    print("Stable insertion sort:")
    for student in insertion_records:
        print(student)

    print("Stable merge sort:")
    for student in merged_records.values:
        print(student)

    print("Unstable quicksort (equal-score order is not guaranteed):")
    for student in quick_records:
        print(student)

    rng = Random(42)
    for size in (0, 1, 2, 10, 100):
        data = [rng.randint(-100, 100) for _ in range(size)]
        expected = sorted(data)
        for algorithm in (
            lambda values: insertion_sort(values),
            lambda values: merge_sort(values),
            lambda values: quick_sort(values),
        ):
            result = algorithm(data.copy())
            assert result.values == expected

    print("\nAll assertions passed.")


if __name__ == "__main__":
    main()
