from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random
import sys
import time
from typing import Callable, Iterable


class PivotStrategy(Enum):
    FIRST = "first"
    LAST = "last"
    MIDDLE = "middle"
    MEDIAN_OF_THREE = "median_of_three"
    RANDOM = "random"


class PartitionStrategy(Enum):
    LOMUTO = "lomuto"
    HOARE = "hoare"


@dataclass
class SortStats:
    comparisons: int = 0
    swaps: int = 0
    partitions: int = 0
    max_recursion_depth: int = 0


class QuickSorter:
    """
    Quick sort implementation supporting multiple pivot and partition strategies.

    Average time: O(n log n)
    Worst-case time: O(n^2)
    Auxiliary stack space: O(log n) on balanced partitions, O(n) in the
    worst recursive case. The implementation below reduces stack risk by
    processing the smaller partition first and iterating over the larger one.
    """

    def __init__(
        self,
        pivot_strategy: PivotStrategy = PivotStrategy.MEDIAN_OF_THREE,
        partition_strategy: PartitionStrategy = PartitionStrategy.HOARE,
        seed: int = 42,
    ) -> None:
        self.pivot_strategy = pivot_strategy
        self.partition_strategy = partition_strategy
        self.random = random.Random(seed)

    def sort(self, values: Iterable[int]) -> tuple[list[int], SortStats]:
        data = list(values)
        stats = SortStats()

        if len(data) < 2:
            return data, stats

        self._quick_sort(data, 0, len(data) - 1, stats, 1)
        return data, stats

    def _quick_sort(
        self,
        data: list[int],
        low: int,
        high: int,
        stats: SortStats,
        depth: int,
    ) -> None:
        while low < high:
            stats.max_recursion_depth = max(stats.max_recursion_depth, depth)
            stats.partitions += 1

            if self.partition_strategy == PartitionStrategy.LOMUTO:
                pivot_index = self._choose_pivot(data, low, high, stats)
                split = self._lomuto_partition(
                    data, low, high, pivot_index, stats
                )

                left_size = split - low
                right_size = high - split

                # Recurse into the smaller side and iterate over the larger
                # side to keep stack usage bounded.
                if left_size < right_size:
                    self._quick_sort(data, low, split - 1, stats, depth + 1)
                    low = split + 1
                else:
                    self._quick_sort(data, split + 1, high, stats, depth + 1)
                    high = split - 1

            else:
                pivot_index = self._choose_pivot(data, low, high, stats)
                pivot_value = data[pivot_index]
                split = self._hoare_partition(
                    data, low, high, pivot_value, stats
                )

                left_size = split - low + 1
                right_size = high - split

                if left_size < right_size:
                    self._quick_sort(data, low, split, stats, depth + 1)
                    low = split + 1
                else:
                    self._quick_sort(data, split + 1, high, stats, depth + 1)
                    high = split

    def _choose_pivot(
        self,
        data: list[int],
        low: int,
        high: int,
        stats: SortStats,
    ) -> int:
        if self.pivot_strategy == PivotStrategy.FIRST:
            return low

        if self.pivot_strategy == PivotStrategy.LAST:
            return high

        if self.pivot_strategy == PivotStrategy.MIDDLE:
            return low + (high - low) // 2

        if self.pivot_strategy == PivotStrategy.RANDOM:
            return self.random.randint(low, high)

        # Median-of-three reduces the likelihood of highly unbalanced
        # partitions on already sorted or reverse-sorted data.
        middle = low + (high - low) // 2
        a, b, c = data[low], data[middle], data[high]

        stats.comparisons += 3

        if (a <= b <= c) or (c <= b <= a):
            return middle
        if (b <= a <= c) or (c <= a <= b):
            return low
        return high

    @staticmethod
    def _swap(
        data: list[int],
        i: int,
        j: int,
        stats: SortStats,
    ) -> None:
        if i != j:
            data[i], data[j] = data[j], data[i]
            stats.swaps += 1

    def _lomuto_partition(
        self,
        data: list[int],
        low: int,
        high: int,
        pivot_index: int,
        stats: SortStats,
    ) -> int:
        self._swap(data, pivot_index, high, stats)
        pivot = data[high]

        store = low
        for i in range(low, high):
            stats.comparisons += 1
            if data[i] <= pivot:
                self._swap(data, i, store, stats)
                store += 1

        self._swap(data, store, high, stats)
        return store

    def _hoare_partition(
        self,
        data: list[int],
        low: int,
        high: int,
        pivot: int,
        stats: SortStats,
    ) -> int:
        i = low - 1
        j = high + 1

        while True:
            i += 1
            while True:
                stats.comparisons += 1
                if data[i] >= pivot:
                    break
                i += 1

            j -= 1
            while True:
                stats.comparisons += 1
                if data[j] <= pivot:
                    break
                j -= 1

            if i >= j:
                return j

            self._swap(data, i, j, stats)


def benchmark(
    name: str,
    values: list[int],
    sorter: QuickSorter,
) -> None:
    start = time.perf_counter()
    result, stats = sorter.sort(values)
    elapsed = time.perf_counter() - start

    assert result == sorted(values), f"{name} produced an invalid ordering"

    print(f"\n{name}")
    print(f"size={len(values):,}")
    print(f"time={elapsed:.6f}s")
    print(f"comparisons={stats.comparisons:,}")
    print(f"swaps={stats.swaps:,}")
    print(f"partitions={stats.partitions:,}")
    print(f"max_recursion_depth={stats.max_recursion_depth}")


def main() -> None:
    examples = [
        [],
        [5],
        [3, 1, 4, 1, 5, 9, 2, 6],
        [7, 7, 7, 7],
        [5, 4, 3, 2, 1],
        [-4, 9, 0, -7, 3, 3, 1],
    ]

    sorter = QuickSorter(
        pivot_strategy=PivotStrategy.MEDIAN_OF_THREE,
        partition_strategy=PartitionStrategy.HOARE,
    )

    print("Quick Sort examples")
    for values in examples:
        result, stats = sorter.sort(values)
        print(
            f"{values} -> {result} "
            f"(comparisons={stats.comparisons}, swaps={stats.swaps})"
        )

    random_values = [random.Random(10).randint(-100_000, 100_000) for _ in range(10_000)]
    benchmark("Random input", random_values, sorter)

    sorted_values = list(range(10_000))
    benchmark("Already sorted input", sorted_values, sorter)

    reverse_values = list(range(9_999, -1, -1))
    benchmark("Reverse sorted input", reverse_values, sorter)

    duplicate_values = [7] * 10_000
    benchmark("Duplicate-heavy input", duplicate_values, sorter)

    print("\nStrategy comparison on sorted input")
    for strategy in (
        PivotStrategy.FIRST,
        PivotStrategy.MIDDLE,
        PivotStrategy.MEDIAN_OF_THREE,
        PivotStrategy.RANDOM,
    ):
        comparison_sorter = QuickSorter(
            pivot_strategy=strategy,
            partition_strategy=PartitionStrategy.HOARE,
            seed=42,
        )
        _, stats = comparison_sorter.sort(sorted_values)
        print(
            f"{strategy.value:16} "
            f"comparisons={stats.comparisons:,} "
            f"max_depth={stats.max_recursion_depth}"
        )

    # Demonstrate an invalid configuration explicitly.
    try:
        invalid = QuickSorter()
        result, _ = invalid.sort([3, 2, 1])
        if result != [1, 2, 3]:
            raise ValueError("Sorting invariant failed")
    except (TypeError, ValueError) as exc:
        print(f"Validation failure: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
