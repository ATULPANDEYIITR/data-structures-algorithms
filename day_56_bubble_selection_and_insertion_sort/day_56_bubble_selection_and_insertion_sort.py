#!/usr/bin/env python3

"""
Elementary sorting algorithms:
- Bubble Sort
- Selection Sort
- Insertion Sort

The program compares the algorithms on correctness, stability, operation
counts, already-sorted data, reverse-sorted data, duplicate-heavy data,
and nearly sorted data.

No external dependencies are required.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import Random
from time import perf_counter
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")


class Algorithm(str, Enum):
    BUBBLE = "Bubble Sort"
    SELECTION = "Selection Sort"
    INSERTION = "Insertion Sort"


@dataclass
class SortStats:
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0
    elapsed_seconds: float = 0.0

    @property
    def operations(self) -> int:
        return self.comparisons + self.swaps + self.writes


@dataclass
class SortResult:
    values: list[T]
    stats: SortStats


class SortError(ValueError):
    """Raised when sorting input or configuration is invalid."""


def validate_values(values: Iterable[T]) -> list[T]:
    if values is None:
        raise SortError("Input cannot be None.")

    result = list(values)

    try:
        for index in range(1, len(result)):
            _ = result[index - 1] <= result[index]
    except TypeError as exc:
        raise SortError("All elements must be mutually orderable.") from exc

    return result


def bubble_sort(values: Iterable[T]) -> SortResult:
    data = validate_values(values)
    stats = SortStats()
    start = perf_counter()

    # Bubble Sort repeatedly moves the largest remaining element to the end.
    for end in range(len(data) - 1, 0, -1):
        swapped = False

        for i in range(end):
            stats.comparisons += 1

            if data[i] > data[i + 1]:
                data[i], data[i + 1] = data[i + 1], data[i]
                stats.swaps += 1
                stats.writes += 2
                swapped = True

        # This early exit gives Bubble Sort O(n) behavior on sorted input.
        if not swapped:
            break

    stats.elapsed_seconds = perf_counter() - start
    return SortResult(data, stats)


def selection_sort(values: Iterable[T]) -> SortResult:
    data = validate_values(values)
    stats = SortStats()
    start = perf_counter()

    # Selection Sort selects the smallest remaining value for each position.
    for i in range(len(data) - 1):
        minimum = i

        for j in range(i + 1, len(data)):
            stats.comparisons += 1
            if data[j] < data[minimum]:
                minimum = j

        if minimum != i:
            data[i], data[minimum] = data[minimum], data[i]
            stats.swaps += 1
            stats.writes += 2

    stats.elapsed_seconds = perf_counter() - start
    return SortResult(data, stats)


def insertion_sort(values: Iterable[T]) -> SortResult:
    data = validate_values(values)
    stats = SortStats()
    start = perf_counter()

    # Insertion Sort maintains a sorted prefix and inserts each next item
    # into its correct location.
    for i in range(1, len(data)):
        key = data[i]
        stats.writes += 1
        j = i - 1

        while j >= 0:
            stats.comparisons += 1

            if data[j] <= key:
                break

            data[j + 1] = data[j]
            stats.writes += 1
            j -= 1

        data[j + 1] = key
        stats.writes += 1

    stats.elapsed_seconds = perf_counter() - start
    return SortResult(data, stats)


SORTERS: dict[Algorithm, Callable[[Iterable[T]], SortResult]] = {
    Algorithm.BUBBLE: bubble_sort,
    Algorithm.SELECTION: selection_sort,
    Algorithm.INSERTION: insertion_sort,
}


def verify_sorted(values: list[T]) -> bool:
    return all(values[i - 1] <= values[i] for i in range(1, len(values)))


def verify_permutation(original: list[T], result: list[T]) -> bool:
    try:
        return sorted(original) == result
    except TypeError:
        return False


def run_correctness_suite() -> None:
    cases = [
        [],
        [1],
        [2, 1],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [3, 1, 3, 2, 1, 2],
        [-4, 7, 0, -1, 5],
        [9, 9, 9, 9],
    ]

    for algorithm, sorter in SORTERS.items():
        for case in cases:
            result = sorter(case)

            assert verify_sorted(result.values), (
                f"{algorithm.value} produced unsorted data: {result.values}"
            )
            assert verify_permutation(case, result.values), (
                f"{algorithm.value} changed input values."
            )

    print("Correctness suite: PASS")


def make_datasets(size: int = 250, seed: int = 42) -> dict[str, list[int]]:
    rng = Random(seed)

    random_data = [rng.randint(0, size * 4) for _ in range(size)]
    sorted_data = list(range(size))
    reverse_data = list(range(size, 0, -1))
    duplicate_data = [rng.randint(0, 9) for _ in range(size)]

    nearly_sorted = list(range(size))
    for i in range(0, size - 1, max(1, size // 20)):
        nearly_sorted[i], nearly_sorted[i + 1] = (
            nearly_sorted[i + 1],
            nearly_sorted[i],
        )

    return {
        "random": random_data,
        "sorted": sorted_data,
        "reverse": reverse_data,
        "duplicates": duplicate_data,
        "nearly sorted": nearly_sorted,
    }


def print_comparison(datasets: dict[str, list[int]]) -> None:
    header = (
        f"{'Dataset':<16}"
        f"{'Algorithm':<17}"
        f"{'Comparisons':>14}"
        f"{'Swaps':>10}"
        f"{'Writes':>10}"
        f"{'Time (ms)':>12}"
    )
    print("\n" + header)
    print("-" * len(header))

    for dataset_name, values in datasets.items():
        for algorithm, sorter in SORTERS.items():
            result = sorter(values)

            print(
                f"{dataset_name:<16}"
                f"{algorithm.value:<17}"
                f"{result.stats.comparisons:>14}"
                f"{result.stats.swaps:>10}"
                f"{result.stats.writes:>10}"
                f"{result.stats.elapsed_seconds * 1000:>12.3f}"
            )


def demonstrate_manual_trace() -> None:
    values = [5, 2, 4, 1, 3]

    print("\nManual examples")
    print(f"Input:       {values}")
    print(f"Bubble:      {bubble_sort(values).values}")
    print(f"Selection:   {selection_sort(values).values}")
    print(f"Insertion:   {insertion_sort(values).values}")


def demonstrate_edge_conditions() -> None:
    print("\nEdge-condition checks")

    for invalid in ([1, "two"],):
        for algorithm, sorter in SORTERS.items():
            try:
                sorter(invalid)
            except SortError:
                print(f"{algorithm.value}: invalid heterogeneous input rejected")
            else:
                raise AssertionError(
                    f"{algorithm.value} accepted invalid heterogeneous input."
                )

    print("All edge-condition checks: PASS")


def complexity_report() -> None:
    print("\nComplexity")
    print("Bubble Sort:    best O(n), average O(n^2), worst O(n^2), O(1) extra space")
    print("Selection Sort: best/average/worst O(n^2), O(1) extra space")
    print("Insertion Sort: best O(n), average O(n^2), worst O(n^2), O(1) extra space")
    print("Bubble and Insertion Sort are stable with the comparisons used here.")
    print("Selection Sort is not generally stable.")


def main() -> None:
    run_correctness_suite()

    datasets = make_datasets()
    print_comparison(datasets)
    demonstrate_manual_trace()
    demonstrate_edge_conditions()
    complexity_report()

    # Sorting a copy prevents callers' data from being mutated.
    original = [4, 1, 3, 2]
    result = insertion_sort(original)
    assert original == [4, 1, 3, 2]
    assert result.values == [1, 2, 3, 4]

    print("\nInput-preservation check: PASS")
    print("Elementary sorting study completed successfully.")


if __name__ == "__main__":
    main()
