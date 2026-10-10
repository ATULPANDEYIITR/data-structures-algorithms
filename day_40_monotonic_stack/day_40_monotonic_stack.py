from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def increasing_stack(values: Iterable[int]) -> list[int]:
    """Return a stack whose values are non-decreasing from bottom to top."""
    stack: list[int] = []
    for value in values:
        while stack and stack[-1] > value:
            stack.pop()
        stack.append(value)
    return stack


def decreasing_stack(values: Iterable[int]) -> list[int]:
    """Return a stack whose values are non-increasing from bottom to top."""
    stack: list[int] = []
    for value in values:
        while stack and stack[-1] < value:
            stack.pop()
        stack.append(value)
    return stack


def next_greater_right(values: list[int]) -> list[int]:
    """
    For every position, find the first strictly greater value to its right.

    The stack stores indices whose next greater value has not been found.
    Values at those indices decrease from bottom to top.
    """
    answer = [-1] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            answer[stack.pop()] = value
        stack.append(i)

    return answer


def next_greater_right_indices(values: list[int]) -> list[int]:
    """Return the index of the next strictly greater element."""
    answer = [-1] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            answer[stack.pop()] = i
        stack.append(i)

    return answer


def next_greater_left(values: list[int]) -> list[int]:
    """Find the first strictly greater value on the left of every element."""
    answer = [-1] * len(values)
    stack: list[int] = []

    for i in range(len(values) - 1, -1, -1):
        while stack and values[stack[-1]] < values[i]:
            answer[stack.pop()] = values[i]
        stack.append(i)

    return answer


def next_smaller_right(values: list[int]) -> list[int]:
    """Find the first strictly smaller value on the right."""
    answer = [-1] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] > value:
            answer[stack.pop()] = value
        stack.append(i)

    return answer


def next_smaller_left(values: list[int]) -> list[int]:
    """Find the first strictly smaller value on the left."""
    answer = [-1] * len(values)
    stack: list[int] = []

    for i in range(len(values) - 1, -1, -1):
        while stack and values[stack[-1]] > values[i]:
            answer[stack.pop()] = values[i]
        stack.append(i)

    return answer


def previous_greater_indices(values: list[int]) -> list[int]:
    """Return the nearest index on the left containing a greater value."""
    answer = [-1] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] <= value:
            stack.pop()
        if stack:
            answer[i] = stack[-1]
        stack.append(i)

    return answer


def previous_smaller_indices(values: list[int]) -> list[int]:
    """Return the nearest index on the left containing a smaller value."""
    answer = [-1] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] >= value:
            stack.pop()
        if stack:
            answer[i] = stack[-1]
        stack.append(i)

    return answer


def daily_temperatures(temperatures: list[int]) -> list[int]:
    """
    For each day, return how many days must pass before a warmer temperature.

    Equal temperatures do not satisfy the 'warmer' condition.
    """
    result = [0] * len(temperatures)
    stack: list[int] = []

    for day, temperature in enumerate(temperatures):
        while stack and temperature > temperatures[stack[-1]]:
            previous_day = stack.pop()
            result[previous_day] = day - previous_day
        stack.append(day)

    return result


def stock_span(prices: list[int]) -> list[int]:
    """
    Compute the number of consecutive previous days whose price is
    less than or equal to today's price.
    """
    spans = [0] * len(prices)
    stack: list[int] = []

    for i, price in enumerate(prices):
        while stack and prices[stack[-1]] <= price:
            stack.pop()

        spans[i] = i + 1 if not stack else i - stack[-1]
        stack.append(i)

    return spans


def largest_rectangle_histogram(heights: list[int]) -> tuple[int, tuple[int, int]]:
    """
    Find the maximum rectangle in a histogram.

    Returns:
        (maximum_area, (left_index, right_index))

    A sentinel zero height flushes all remaining bars at the end.
    """
    if any(height < 0 for height in heights):
        raise ValueError("Histogram heights cannot be negative.")

    stack: list[int] = []
    best_area = 0
    best_range = (-1, -1)

    extended = heights + [0]

    for i, height in enumerate(extended):
        while stack and extended[stack[-1]] > height:
            top = stack.pop()
            rectangle_height = extended[top]
            left = stack[-1] + 1 if stack else 0
            right = i - 1
            width = right - left + 1
            area = rectangle_height * width

            if area > best_area:
                best_area = area
                best_range = (left, right)

        stack.append(i)

    return best_area, best_range


def largest_rectangle_histogram_explicit_boundaries(
    heights: list[int],
) -> tuple[int, tuple[int, int]]:
    """
    Solve the histogram problem by separately computing nearest smaller
    boundaries. This makes the role of increasing monotonic stacks explicit.
    """
    n = len(heights)
    if n == 0:
        return 0, (-1, -1)
    if any(height < 0 for height in heights):
        raise ValueError("Histogram heights cannot be negative.")

    left = [-1] * n
    right = [n] * n
    stack: list[int] = []

    for i, height in enumerate(heights):
        while stack and heights[stack[-1]] >= height:
            stack.pop()
        if stack:
            left[i] = stack[-1]
        stack.append(i)

    stack.clear()

    for i in range(n - 1, -1, -1):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        if stack:
            right[i] = stack[-1]
        stack.append(i)

    best_area = 0
    best_range = (-1, -1)

    for i, height in enumerate(heights):
        width = right[i] - left[i] - 1
        area = height * width
        if area > best_area:
            best_area = area
            best_range = (left[i] + 1, right[i] - 1)

    return best_area, best_range


def maximal_rectangle(matrix: list[list[str]]) -> int:
    """
    Find the largest all-'1' rectangle in a binary matrix.

    Each row becomes a histogram of consecutive ones, so the histogram
    monotonic-stack algorithm solves the two-dimensional problem.
    """
    if not matrix:
        return 0

    width = len(matrix[0])
    if width == 0:
        return 0

    if any(len(row) != width for row in matrix):
        raise ValueError("Every matrix row must have the same width.")

    heights = [0] * width
    maximum = 0

    for row in matrix:
        for column, cell in enumerate(row):
            if cell not in {"0", "1"}:
                raise ValueError("Matrix cells must contain only '0' or '1'.")
            heights[column] = heights[column] + 1 if cell == "1" else 0

        area, _ = largest_rectangle_histogram(heights)
        maximum = max(maximum, area)

    return maximum


def sum_of_subarray_minimums(values: list[int]) -> int:
    """
    Sum the minimum value of every contiguous subarray.

    For each value, count how many subarrays choose it as their unique
    ownership point. Strictness on one side and non-strictness on the
    other prevents duplicate ownership when equal values occur.
    """
    n = len(values)
    previous_less = [-1] * n
    next_less_or_equal = [n] * n

    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] > value:
            stack.pop()
        if stack:
            previous_less[i] = stack[-1]
        stack.append(i)

    stack.clear()

    for i in range(n - 1, -1, -1):
        while stack and values[stack[-1]] >= values[i]:
            stack.pop()
        if stack:
            next_less_or_equal[i] = stack[-1]
        stack.append(i)

    total = 0
    for i, value in enumerate(values):
        left_choices = i - previous_less[i]
        right_choices = next_less_or_equal[i] - i
        total += value * left_choices * right_choices

    return total


def sum_of_subarray_ranges(values: list[int]) -> int:
    """
    Sum max(subarray) - min(subarray) over every contiguous subarray.

    The implementation reuses monotonic-stack ownership counting for
    maximums and minimums rather than enumerating all subarrays.
    """
    n = len(values)
    if n == 0:
        return 0

    def contribution_for_minimum() -> int:
        previous_less = [-1] * n
        next_less_or_equal = [n] * n
        stack: list[int] = []

        for i, value in enumerate(values):
            while stack and values[stack[-1]] > value:
                stack.pop()
            if stack:
                previous_less[i] = stack[-1]
            stack.append(i)

        stack.clear()

        for i in range(n - 1, -1, -1):
            while stack and values[stack[-1]] >= values[i]:
                stack.pop()
            if stack:
                next_less_or_equal[i] = stack[-1]
            stack.append(i)

        return sum(
            values[i]
            * (i - previous_less[i])
            * (next_less_or_equal[i] - i)
            for i in range(n)
        )

    def contribution_for_maximum() -> int:
        previous_greater = [-1] * n
        next_greater_or_equal = [n] * n
        stack: list[int] = []

        for i, value in enumerate(values):
            while stack and values[stack[-1]] < value:
                stack.pop()
            if stack:
                previous_greater[i] = stack[-1]
            stack.append(i)

        stack.clear()

        for i in range(n - 1, -1, -1):
            while stack and values[stack[-1]] <= values[i]:
                stack.pop()
            if stack:
                next_greater_or_equal[i] = stack[-1]
            stack.append(i)

        return sum(
            values[i]
            * (i - previous_greater[i])
            * (next_greater_or_equal[i] - i)
            for i in range(n)
        )

    return contribution_for_maximum() - contribution_for_minimum()


def remove_k_digits(number: str, k: int) -> str:
    """
    Remove exactly k digits to obtain the smallest possible non-negative
    decimal number. The stack remains increasing whenever possible.
    """
    if not number or not number.isdigit():
        raise ValueError("number must be a non-empty decimal string.")
    if not 0 <= k <= len(number):
        raise ValueError("k must be between zero and the number of digits.")

    stack: list[str] = []

    for digit in number:
        while k and stack and stack[-1] > digit:
            stack.pop()
            k -= 1
        stack.append(digit)

    if k:
        stack = stack[:-k]

    result = "".join(stack).lstrip("0")
    return result or "0"


def validate_monotonic_invariant(stack: list[int], increasing: bool) -> bool:
    """Check an invariant directly, useful when debugging an algorithm."""
    pairs = zip(stack, stack[1:])
    return all(
        left <= right if increasing else left >= right
        for left, right in pairs
    )


@dataclass
class HistogramAnalyzer:
    heights: list[int]

    def analyze(self) -> dict[str, object]:
        if not self.heights:
            return {"area": 0, "range": (-1, -1), "height": 0}

        area, (left, right) = largest_rectangle_histogram(self.heights)
        height = self.heights[left] if left >= 0 else 0

        return {
            "area": area,
            "range": (left, right),
            "height": height,
        }


def run_examples() -> None:
    print("Monotonic Stack Demonstration")
    print("=" * 32)

    values = [2, 1, 2, 4, 3]
    print("\nInput:", values)
    print("Increasing stack:", increasing_stack(values))
    print("Decreasing stack:", decreasing_stack(values))

    print("\nNext greater element")
    print(next_greater_right(values))
    print(next_greater_right_indices(values))

    print("\nNext smaller element")
    print(next_smaller_right(values))
    print("Previous smaller indices:", previous_smaller_indices(values))
    print("Previous greater indices:", previous_greater_indices(values))

    temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
    print("\nDaily temperatures:", temperatures)
    print("Wait times:", daily_temperatures(temperatures))

    prices = [100, 80, 60, 70, 60, 75, 85]
    print("\nStock prices:", prices)
    print("Stock spans:", stock_span(prices))

    histogram = [2, 1, 5, 6, 2, 3]
    analyzer = HistogramAnalyzer(histogram)
    print("\nHistogram:", histogram)
    print("Best rectangle:", analyzer.analyze())
    print(
        "Boundary-based result:",
        largest_rectangle_histogram_explicit_boundaries(histogram),
    )

    matrix = [
        list("10100"),
        list("10111"),
        list("11111"),
        list("10010"),
    ]
    print("\nLargest rectangle in binary matrix:", maximal_rectangle(matrix))

    print("\nSubarray minimums")
    print(sum_of_subarray_minimums([3, 1, 2, 4]))

    print("\nSubarray ranges")
    print(sum_of_subarray_ranges([1, 3, 3]))

    print("\nGreedy monotonic-stack reduction")
    print(remove_k_digits("1432219", 3))
    print(remove_k_digits("10200", 1))

    print("\nInvariant checks")
    inc = increasing_stack([5, 1, 4, 2, 3])
    dec = decreasing_stack([5, 1, 4, 2, 3])
    print("Increasing invariant:", validate_monotonic_invariant(inc, True))
    print("Decreasing invariant:", validate_monotonic_invariant(dec, False))

    print("\nEdge cases")
    for sample in ([], [5], [2, 2, 2], [5, 4, 3, 2, 1]):
        print(
            sample,
            "=> next greater:",
            next_greater_right(sample),
            "histogram:",
            largest_rectangle_histogram(sample),
        )

    try:
        largest_rectangle_histogram([2, -1, 3])
    except ValueError as exc:
        print("\nValidation failure:", exc)

    try:
        maximal_rectangle([["1", "0"], ["1"]])
    except ValueError as exc:
        print("Matrix validation failure:", exc)


if __name__ == "__main__":
    run_examples()
