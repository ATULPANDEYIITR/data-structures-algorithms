#!/usr/bin/env python3
"""
Non-comparison sorting laboratory.

Implements counting sort, radix sort, and bucket sort, with an algorithm
selection policy, validation, correctness checks, and benchmark reporting.
Compatible with Python 3.10+ and the standard library only.
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, localcontext
from enum import Enum
from typing import Sequence


class SortingError(ValueError):
    """Raised when an input or sorting configuration is invalid."""


class Algorithm(str, Enum):
    COUNTING = "counting"
    RADIX = "radix"
    BUCKET = "bucket"
    COMPARISON = "comparison"


@dataclass(frozen=True)
class SortReport:
    algorithm: Algorithm
    values: tuple[int | float, ...]
    elapsed_ns: int
    input_size: int

    @property
    def elapsed_ms(self) -> float:
        return self.elapsed_ns / 1_000_000


MAX_INPUT_SIZE = 1_000_000
DEFAULT_MAX_COUNTING_RANGE = 1_000_000
MAX_BUCKET_COUNT = 10_000


def validate_sequence(values: Sequence[object]) -> list[object]:
    if isinstance(values, (str, bytes, bytearray)):
        raise SortingError("Input must be a sequence of numeric values.")

    try:
        result = list(values)
    except TypeError as exc:
        raise SortingError("Input must be iterable.") from exc

    if len(result) > MAX_INPUT_SIZE:
        raise SortingError(
            f"Input exceeds the maximum size of {MAX_INPUT_SIZE}."
        )

    return result


def validate_integers(values: Sequence[object]) -> list[int]:
    result = validate_sequence(values)

    if any(type(value) is not int for value in result):
        raise SortingError("Integer sorting accepts integers only.")

    return result  # type: ignore[return-value]


def validate_numbers(values: Sequence[object]) -> list[int | float]:
    result = validate_sequence(values)

    for value in result:
        if type(value) not in (int, float):
            raise SortingError("Bucket sorting accepts integers and floats.")

        if isinstance(value, float) and not math.isfinite(value):
            raise SortingError("NaN and infinite values are not supported.")

    return result  # type: ignore[return-value]


def counting_sort(
    values: Sequence[int],
    max_range: int = DEFAULT_MAX_COUNTING_RANGE,
) -> list[int]:
    """
    Stable counting sort supporting negative integers.

    Time: O(n + k), where k is max(value) - min(value) + 1.
    Space: O(n + k).
    """
    data = validate_integers(values)

    if type(max_range) is not int or max_range < 1:
        raise SortingError("max_range must be a positive integer.")

    if not data:
        return []

    minimum = min(data)
    maximum = max(data)
    span = maximum - minimum + 1

    # Bound memory allocation before creating the frequency array.
    if span > max_range:
        raise SortingError(
            f"Counting sort range {span} exceeds configured limit "
            f"{max_range}; use radix sort for this workload."
        )

    counts = [0] * span

    for value in data:
        counts[value - minimum] += 1

    result: list[int] = []

    for offset, frequency in enumerate(counts):
        if frequency:
            result.extend([minimum + offset] * frequency)

    return result


def radix_sort(values: Sequence[int]) -> list[int]:
    """
    Stable LSD radix sort for signed Python integers.

    Values are shifted by the minimum so every sorting key is non-negative.
    Base 256 processes one byte per pass. Python integers have arbitrary
    precision, so the number of passes depends on the input range.

    Time: O(d * (n + 256)), where d is the number of byte passes.
    Space: O(n + 256).
    """
    data = validate_integers(values)

    if len(data) < 2:
        return data.copy()

    minimum = min(data)
    keys = [value - minimum for value in data]
    maximum_key = max(keys)

    if maximum_key == 0:
        return data.copy()

    base = 256
    shift = 0
    result = data.copy()

    while (maximum_key >> shift) > 0:
        counts = [0] * base

        for key in keys:
            digit = (key >> shift) & 0xFF
            counts[digit] += 1

        # Convert frequencies into ending positions.
        total = 0
        for index in range(base):
            total += counts[index]
            counts[index] = total

        output = [0] * len(data)
        output_keys = [0] * len(data)

        # Reverse traversal preserves the relative order of equal keys.
        for index in range(len(data) - 1, -1, -1):
            digit = (keys[index] >> shift) & 0xFF
            destination = counts[digit] - 1
            output[destination] = result[index]
            output_keys[destination] = keys[index]
            counts[digit] -= 1

        result = output
        keys = output_keys
        shift += 8

    return result


def _to_decimal(value: int | float) -> Decimal:
    # Decimal(str(float)) avoids importing the float's binary approximation.
    return Decimal(value) if type(value) is int else Decimal(str(value))


def _insertion_sort(values: list[int | float]) -> None:
    """In-place stable insertion sort for one bucket."""
    for index in range(1, len(values)):
        current = values[index]
        position = index - 1

        while position >= 0 and values[position] > current:
            values[position + 1] = values[position]
            position -= 1

        values[position + 1] = current


def bucket_sort(
    values: Sequence[int | float],
    bucket_count: int | None = None,
) -> list[int | float]:
    """
    Bucket sort for finite numeric values.

    Values are distributed across an interval derived from the observed
    minimum and maximum. Each bucket is sorted with insertion sort.

    Expected time for reasonably distributed data: O(n + k).
    Worst-case time: O(n^2) when most values occupy one bucket.
    """
    data = validate_numbers(values)

    if len(data) < 2:
        return data.copy()

    if bucket_count is None:
        bucket_count = max(1, math.ceil(math.sqrt(len(data))))

    if type(bucket_count) is not int or not 1 <= bucket_count <= MAX_BUCKET_COUNT:
        raise SortingError(
            f"bucket_count must be between 1 and {MAX_BUCKET_COUNT}."
        )

    minimum = min(data)
    maximum = max(data)

    if minimum == maximum:
        return data.copy()

    # Precision is based on input size rather than a fixed decimal context.
    precision = max(
        50,
        max(len(str(abs(value))) for value in data) + 25,
    )

    decimal_min = _to_decimal(minimum)
    decimal_max = _to_decimal(maximum)
    decimal_span = decimal_max - decimal_min

    buckets: list[list[int | float]] = [
        [] for _ in range(bucket_count)
    ]

    with localcontext() as context:
        context.prec = precision

        for value in data:
            decimal_value = _to_decimal(value)
            scaled = (
                (decimal_value - decimal_min)
                * Decimal(bucket_count)
                / decimal_span
            )

            index = int(scaled)

            # The maximum value maps to the final bucket.
            index = max(0, min(bucket_count - 1, index))
            buckets[index].append(value)

    result: list[int | float] = []

    for bucket in buckets:
        if len(bucket) > 1:
            _insertion_sort(bucket)
        result.extend(bucket)

    return result


def comparison_sort(
    values: Sequence[int | float],
) -> list[int | float]:
    """Comparison-based reference implementation."""
    return sorted(validate_numbers(values))


def select_algorithm(
    values: Sequence[object],
    max_counting_range: int = DEFAULT_MAX_COUNTING_RANGE,
    counting_range_ratio: int = 16,
) -> Algorithm:
    """
    Choose an algorithm using type, range, and input-size information.

    Counting sort is selected only when its frequency array is reasonably
    bounded relative to the input. Wide integer ranges use radix sort.
    Decimal or mixed numeric data use bucket sort.
    """
    data = validate_numbers(values)

    if not data:
        return Algorithm.COUNTING

    if any(type(value) is float for value in data):
        return Algorithm.BUCKET

    integers = validate_integers(data)
    span = max(integers) - min(integers) + 1

    if (
        span <= max_counting_range
        and span <= max(256, len(integers) * counting_range_ratio)
    ):
        return Algorithm.COUNTING

    return Algorithm.RADIX


def sort_values(
    values: Sequence[object],
    algorithm: Algorithm | str = "auto",
    max_counting_range: int = DEFAULT_MAX_COUNTING_RANGE,
) -> list[int | float]:
    data = validate_numbers(values)

    if algorithm == "auto":
        selected = select_algorithm(data, max_counting_range)
    else:
        try:
            selected = Algorithm(algorithm)
        except ValueError as exc:
            raise SortingError(f"Unsupported algorithm: {algorithm}") from exc

    if selected == Algorithm.COUNTING:
        return counting_sort(data, max_counting_range)

    if selected == Algorithm.RADIX:
        return radix_sort(data)

    if selected == Algorithm.BUCKET:
        return bucket_sort(data)

    if selected == Algorithm.COMPARISON:
        return comparison_sort(data)

    raise SortingError(f"Unsupported algorithm: {selected}")


def benchmark(
    values: Sequence[object],
    algorithms: Sequence[Algorithm] | None = None,
) -> list[SortReport]:
    """
    Run compatible algorithms and verify each result against a reference.

    Counter-based validation checks multiplicity as well as sorted order.
    """
    data = validate_numbers(values)
    reference = sorted(data)

    if algorithms is None:
        selected = select_algorithm(data)
        candidates = [
            selected,
            Algorithm.COMPARISON,
        ]

        if all(type(value) is int for value in data):
            candidates.extend(
                [Algorithm.COUNTING, Algorithm.RADIX]
            )
        else:
            candidates.append(Algorithm.BUCKET)

        algorithms = list(dict.fromkeys(candidates))

    reports: list[SortReport] = []

    for algorithm in algorithms:
        start = time.perf_counter_ns()
        result = sort_values(data, algorithm)
        elapsed = time.perf_counter_ns() - start

        if result != reference:
            raise AssertionError(f"{algorithm.value} produced an incorrect result.")

        if Counter(result) != Counter(data):
            raise AssertionError(
                f"{algorithm.value} changed the input value frequencies."
            )

        reports.append(
            SortReport(
                algorithm=algorithm,
                values=tuple(result),
                elapsed_ns=elapsed,
                input_size=len(data),
            )
        )

    return reports


def demonstrate_integer_sorting() -> None:
    print("\nINTEGER SORTING")

    examples = {
        "small signed range": [4, -2, 7, 4, 0, -2, 3, 1],
        "wide signed range": [
            9_000_000_000,
            -8_000_000_000,
            0,
            9_000_000_000,
            -1,
            42,
        ],
        "duplicates": [5, 5, 5, 5, 5],
        "empty input": [],
        "single value": [-17],
    }

    for name, values in examples.items():
        selected = select_algorithm(values)
        result = sort_values(values, "auto")

        print(f"{name}:")
        print(f"  input:     {values}")
        print(f"  algorithm: {selected.value}")
        print(f"  output:    {result}")

        assert result == sorted(values)


def demonstrate_bucket_sorting() -> None:
    print("\nBUCKET SORTING")

    examples = [
        [0.42, 0.32, 0.23, 0.52, 0.25, 0.47, 0.51],
        [-100.5, -0.25, 0.0, 18.75, 100.5],
        [3.14, 3.14, 3.14],
        [float("-0.0"), 0.0, -1.5, 1.5],
    ]

    for values in examples:
        result = bucket_sort(values)
        print(f"  input:  {values}")
        print(f"  output: {result}")
        assert result == sorted(values)


def demonstrate_benchmarks() -> None:
    print("\nBENCHMARKS")

    random_generator = random.Random(20261030)

    workloads = {
        "narrow integer range": [
            random_generator.randint(-500, 500)
            for _ in range(20_000)
        ],
        "wide integer range": [
            random_generator.randint(-(10**15), 10**15)
            for _ in range(20_000)
        ],
        "uniform decimal interval": [
            random_generator.uniform(-1.0, 1.0)
            for _ in range(20_000)
        ],
    }

    for name, values in workloads.items():
        print(f"\n{name}")

        for report in benchmark(values):
            print(
                f"  {report.algorithm.value:12s} "
                f"{report.elapsed_ms:10.3f} ms "
                f"({report.input_size} values)"
            )


def demonstrate_validation() -> None:
    print("\nVALIDATION")

    invalid_cases = [
        ("counting with floats", lambda: counting_sort([1, 2.5, 3])),
        ("radix with booleans", lambda: radix_sort([1, True, 3])),
        ("bucket with NaN", lambda: bucket_sort([1.0, float("nan")])),
        (
            "counting range limit",
            lambda: counting_sort([0, 10_000], max_range=100),
        ),
        (
            "invalid bucket count",
            lambda: bucket_sort([1.0, 2.0], bucket_count=0),
        ),
    ]

    for description, operation in invalid_cases:
        try:
            operation()
        except SortingError as exc:
            print(f"  Rejected {description}: {exc}")
        else:
            raise AssertionError(f"Expected validation failure: {description}")


def main() -> None:
    demonstrate_integer_sorting()
    demonstrate_bucket_sorting()
    demonstrate_validation()
    demonstrate_benchmarks()

    print("\nALL SORTING CHECKS PASSED")


if __name__ == "__main__":
    main()
