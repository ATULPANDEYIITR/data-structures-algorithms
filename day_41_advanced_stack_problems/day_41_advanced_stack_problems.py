from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


def largest_rectangle_histogram(heights: list[int]) -> int:
    """Return the maximum rectangle area in a histogram in O(n) time."""
    if any(h < 0 for h in heights):
        raise ValueError("Histogram heights cannot be negative.")

    stack: list[int] = []
    best = 0
    extended = heights + [0]

    for i, height in enumerate(extended):
        while stack and extended[stack[-1]] > height:
            top = stack.pop()
            left_boundary = stack[-1] if stack else -1
            width = i - left_boundary - 1
            best = max(best, extended[top] * width)
        stack.append(i)

    return best


def largest_rectangle_with_coordinates(
    heights: list[int],
) -> tuple[int, int, int, int]:
    """Return (area, left, right, height) for the best histogram rectangle."""
    if any(h < 0 for h in heights):
        raise ValueError("Histogram heights cannot be negative.")
    if not heights:
        return 0, -1, -1, 0

    stack: list[int] = []
    best = (0, -1, -1, 0)

    for i, height in enumerate(heights + [0]):
        while stack and heights[stack[-1]] > height:
            top = stack.pop()
            left = stack[-1] + 1 if stack else 0
            right = i - 1
            candidate = (
                heights[top] * (right - left + 1),
                left,
                right,
                heights[top],
            )
            if candidate[0] > best[0]:
                best = candidate
        stack.append(i)

    return best


def trap_rainwater_two_pointer(heights: list[int]) -> int:
    """Calculate trapped water using O(1) auxiliary space."""
    if any(h < 0 for h in heights):
        raise ValueError("Elevation values cannot be negative.")

    left = 0
    right = len(heights) - 1
    left_max = 0
    right_max = 0
    water = 0

    while left < right:
        if heights[left] <= heights[right]:
            if heights[left] >= left_max:
                left_max = heights[left]
            else:
                water += left_max - heights[left]
            left += 1
        else:
            if heights[right] >= right_max:
                right_max = heights[right]
            else:
                water += right_max - heights[right]
            right -= 1

    return water


def trap_rainwater_stack(heights: list[int]) -> int:
    """Calculate trapped water with a monotonic decreasing stack."""
    if any(h < 0 for h in heights):
        raise ValueError("Elevation values cannot be negative.")

    stack: list[int] = []
    water = 0

    for current, height in enumerate(heights):
        while stack and height > heights[stack[-1]]:
            bottom = stack.pop()

            if not stack:
                break

            left = stack[-1]
            width = current - left - 1
            bounded_height = min(heights[left], height) - heights[bottom]
            water += width * bounded_height

        stack.append(current)

    return water


def stock_span(prices: list[float]) -> list[int]:
    """Return the stock span for each trading day in O(n)."""
    if any(price < 0 for price in prices):
        raise ValueError("Stock prices cannot be negative.")

    stack: list[int] = []
    spans = [0] * len(prices)

    for day, price in enumerate(prices):
        while stack and prices[stack[-1]] <= price:
            stack.pop()

        spans[day] = day + 1 if not stack else day - stack[-1]
        stack.append(day)

    return spans


def next_greater_elements(values: list[int], circular: bool = False) -> list[int]:
    """Find the next strictly greater value, optionally in a circular array."""
    result = [-1] * len(values)
    stack: list[int] = []

    iterations = len(values) * 2 if circular else len(values)

    for i in range(iterations):
        index = i % len(values)
        value = values[index]

        while stack and values[stack[-1]] < value:
            result[stack.pop()] = value

        if i < len(values):
            stack.append(index)

    return result


def previous_smaller_elements(values: list[int]) -> list[int | None]:
    """Find the nearest strictly smaller value to the left."""
    result: list[int | None] = [None] * len(values)
    stack: list[int] = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] >= value:
            stack.pop()

        if stack:
            result[i] = values[stack[-1]]

        stack.append(i)

    return result


def infix_to_postfix(expression: str) -> str:
    """
    Convert an infix arithmetic expression to postfix notation.

    Supported operators:
        + - * / % ^
    Supported parentheses:
        ( )
    Operands may be identifiers or numeric tokens.
    """
    tokens = expression.replace("(", " ( ").replace(")", " ) ").split()

    precedence = {
        "+": 1,
        "-": 1,
        "*": 2,
        "/": 2,
        "%": 2,
        "^": 3,
    }

    right_associative = {"^"}
    output: list[str] = []
    operators: list[str] = []

    for token in tokens:
        if token.isidentifier() or token.replace(".", "", 1).isdigit():
            output.append(token)
            continue

        if token == "(":
            operators.append(token)
            continue

        if token == ")":
            while operators and operators[-1] != "(":
                output.append(operators.pop())

            if not operators:
                raise ValueError("Mismatched parentheses.")

            operators.pop()
            continue

        if token not in precedence:
            raise ValueError(f"Unsupported token: {token}")

        while operators and operators[-1] != "(":
            top = operators[-1]
            should_pop = (
                precedence[top] > precedence[token]
                or (
                    precedence[top] == precedence[token]
                    and token not in right_associative
                )
            )

            if not should_pop:
                break

            output.append(operators.pop())

        operators.append(token)

    while operators:
        if operators[-1] == "(":
            raise ValueError("Mismatched parentheses.")
        output.append(operators.pop())

    return " ".join(output)


def evaluate_postfix(expression: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate whitespace-separated postfix notation."""
    variables = variables or {}
    stack: list[float] = []

    operators: dict[str, Callable[[float, float], float]] = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
        "%": lambda a, b: a % b,
        "^": lambda a, b: a**b,
    }

    for token in expression.split():
        if token in operators:
            if len(stack) < 2:
                raise ValueError("Invalid postfix expression.")

            right = stack.pop()
            left = stack.pop()

            if token == "/" and right == 0:
                raise ZeroDivisionError("Division by zero.")

            stack.append(operators[token](left, right))
        else:
            try:
                value = float(token)
            except ValueError:
                if token not in variables:
                    raise ValueError(f"Unknown operand: {token}")
                value = float(variables[token])

            stack.append(value)

    if len(stack) != 1:
        raise ValueError("Invalid postfix expression.")

    return stack[0]


def infix_to_prefix(expression: str) -> str:
    """Convert infix notation to prefix notation using an operator stack."""
    tokens = expression.replace("(", " ( ").replace(")", " ) ").split()

    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "^": 3}
    output: list[str] = []
    operators: list[str] = []

    reversed_tokens = []
    for token in reversed(tokens):
        if token == "(":
            reversed_tokens.append(")")
        elif token == ")":
            reversed_tokens.append("(")
        else:
            reversed_tokens.append(token)

    for token in reversed_tokens:
        if token.isidentifier() or token.replace(".", "", 1).isdigit():
            output.append(token)
        elif token == "(":
            operators.append(token)
        elif token == ")":
            while operators and operators[-1] != "(":
                output.append(operators.pop())
            if not operators:
                raise ValueError("Mismatched parentheses.")
            operators.pop()
        else:
            while (
                operators
                and operators[-1] != "("
                and precedence[operators[-1]] > precedence[token]
            ):
                output.append(operators.pop())
            operators.append(token)

    while operators:
        if operators[-1] == "(":
            raise ValueError("Mismatched parentheses.")
        output.append(operators.pop())

    return " ".join(reversed(output))


def daily_temperature_waits(temperatures: list[int]) -> list[int]:
    """Return how many days each temperature must wait for a warmer day."""
    stack: list[int] = []
    answer = [0] * len(temperatures)

    for day, temperature in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temperature:
            previous = stack.pop()
            answer[previous] = day - previous
        stack.append(day)

    return answer


def sum_of_subarray_ranges(values: list[int]) -> int:
    """
    Sum max(subarray) - min(subarray) over every subarray.

    Monotonic stacks count how often each value contributes as a maximum
    and as a minimum instead of enumerating all subarrays.
    """
    n = len(values)

    def contribution_for_max() -> int:
        left = [0] * n
        right = [0] * n
        stack: list[int] = []

        for i in range(n):
            while stack and values[stack[-1]] < values[i]:
                stack.pop()
            left[i] = i - stack[-1] if stack else i + 1
            stack.append(i)

        stack.clear()

        for i in range(n - 1, -1, -1):
            while stack and values[stack[-1]] <= values[i]:
                stack.pop()
            right[i] = stack[-1] - i if stack else n - i
            stack.append(i)

        return sum(values[i] * left[i] * right[i] for i in range(n))

    def contribution_for_min() -> int:
        left = [0] * n
        right = [0] * n
        stack: list[int] = []

        for i in range(n):
            while stack and values[stack[-1]] > values[i]:
                stack.pop()
            left[i] = i - stack[-1] if stack else i + 1
            stack.append(i)

        stack.clear()

        for i in range(n - 1, -1, -1):
            while stack and values[stack[-1]] >= values[i]:
                stack.pop()
            right[i] = stack[-1] - i if stack else n - i
            stack.append(i)

        return sum(values[i] * left[i] * right[i] for i in range(n))

    return contribution_for_max() - contribution_for_min()


def maximal_rectangle(matrix: list[list[int]]) -> int:
    """Find the largest all-1 rectangle in a binary matrix."""
    if not matrix:
        return 0

    width = len(matrix[0])
    if width == 0:
        return 0

    if any(len(row) != width for row in matrix):
        raise ValueError("Matrix must be rectangular.")

    heights = [0] * width
    best = 0

    for row in matrix:
        for column, value in enumerate(row):
            if value not in (0, 1):
                raise ValueError("Binary matrix values must be 0 or 1.")
            heights[column] = heights[column] + 1 if value else 0

        best = max(best, largest_rectangle_histogram(heights))

    return best


@dataclass
class StackFrame:
    name: str
    local_state: dict[str, str]


class MonotonicStackAnalyzer:
    """Small diagnostic utility for visualizing stack decisions."""

    def __init__(self, values: Iterable[int]) -> None:
        self.values = list(values)

    def increasing_stack_events(self) -> list[str]:
        stack: list[int] = []
        events: list[str] = []

        for index, value in enumerate(self.values):
            while stack and self.values[stack[-1]] >= value:
                removed = stack.pop()
                events.append(
                    f"index={index}: pop index={removed}, "
                    f"value={self.values[removed]} because {value} is smaller/equal"
                )

            stack.append(index)
            events.append(f"index={index}: push value={value}")

        return events


def run_examples() -> None:
    print("=== Largest Rectangle in Histogram ===")
    histogram = [2, 1, 5, 6, 2, 3]
    print("Heights:", histogram)
    print("Maximum area:", largest_rectangle_histogram(histogram))
    print("Rectangle:", largest_rectangle_with_coordinates(histogram))

    print("\n=== Trapping Rainwater ===")
    elevation = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
    print("Elevation:", elevation)
    print("Two-pointer result:", trap_rainwater_two_pointer(elevation))
    print("Stack result:", trap_rainwater_stack(elevation))

    print("\n=== Stock Span ===")
    prices = [100, 80, 60, 70, 60, 75, 85]
    print("Prices:", prices)
    print("Spans:", stock_span(prices))

    print("\n=== Expression Conversion ===")
    expression = "a + b * ( c ^ d - e ) ^ ( f + g * h ) - i"
    postfix = infix_to_postfix(expression)
    prefix = infix_to_prefix(expression)
    print("Infix:", expression)
    print("Postfix:", postfix)
    print("Prefix:", prefix)

    arithmetic = "3 + 4 * 2 / ( 1 - 5 ) ^ 2"
    arithmetic_postfix = infix_to_postfix(arithmetic)
    print("Arithmetic:", arithmetic)
    print("Postfix:", arithmetic_postfix)
    print("Value:", evaluate_postfix(arithmetic_postfix))

    print("\n=== Next Greater Element ===")
    values = [1, 2, 1, 3]
    print("Values:", values)
    print("Linear:", next_greater_elements(values))
    print("Circular:", next_greater_elements(values, circular=True))

    print("\n=== Previous Smaller Element ===")
    print(previous_smaller_elements([4, 5, 2, 10, 8]))

    print("\n=== Daily Temperatures ===")
    temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
    print(daily_temperature_waits(temperatures))

    print("\n=== Sum of Subarray Ranges ===")
    print("Values:", [1, 2, 3])
    print("Range sum:", sum_of_subarray_ranges([1, 2, 3]))

    print("\n=== Maximal Rectangle in Binary Matrix ===")
    matrix = [
        [1, 0, 1, 0, 0],
        [1, 0, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 1, 0],
    ]
    print("Maximum area:", maximal_rectangle(matrix))

    print("\n=== Monotonic Stack Diagnostics ===")
    analyzer = MonotonicStackAnalyzer([5, 3, 4, 2])
    for event in analyzer.increasing_stack_events():
        print(event)


def run_edge_case_checks() -> None:
    print("\n=== Edge Cases ===")

    cases = [
        ("empty histogram", lambda: largest_rectangle_histogram([]), 0),
        ("single histogram bar", lambda: largest_rectangle_histogram([7]), 7),
        ("flat histogram", lambda: largest_rectangle_histogram([4, 4, 4]), 12),
        ("empty water", lambda: trap_rainwater_two_pointer([]), 0),
        ("short water", lambda: trap_rainwater_two_pointer([3, 2]), 0),
        ("single stock day", lambda: stock_span([100]), [1]),
        ("empty matrix", lambda: maximal_rectangle([]), 0),
    ]

    for name, operation, expected in cases:
        actual = operation()
        status = "PASS" if actual == expected else "FAIL"
        print(f"{status}: {name}: {actual}")

    try:
        largest_rectangle_histogram([2, -1, 3])
    except ValueError as error:
        print("PASS: invalid histogram rejected:", error)

    try:
        maximal_rectangle([[1, 0], [1]])
    except ValueError as error:
        print("PASS: ragged matrix rejected:", error)

    try:
        infix_to_postfix("( 2 + 3")
    except ValueError as error:
        print("PASS: mismatched expression rejected:", error)


def run_assertions() -> None:
    assert largest_rectangle_histogram([2, 1, 5, 6, 2, 3]) == 10
    assert largest_rectangle_histogram([2, 4]) == 4
    assert trap_rainwater_two_pointer([4, 2, 0, 3, 2, 5]) == 9
    assert trap_rainwater_stack([4, 2, 0, 3, 2, 5]) == 9
    assert stock_span([100, 80, 60, 70, 60, 75, 85]) == [1, 1, 1, 2, 1, 4, 6]
    assert next_greater_elements([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
    assert daily_temperature_waits([73, 74, 75, 71, 69, 72, 76, 73]) == [
        1,
        1,
        4,
        2,
        1,
        1,
        0,
        0,
    ]
    assert maximal_rectangle(
        [
            [1, 0, 1, 0, 0],
            [1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 0, 0, 1, 0],
        ]
    ) == 6

    expression = infix_to_postfix("3 + 4 * 2 / ( 1 - 5 ) ^ 2")
    assert abs(evaluate_postfix(expression) - 3.5) < 1e-9
    assert sum_of_subarray_ranges([1, 2, 3]) == 4


if __name__ == "__main__":
    run_examples()
    run_edge_case_checks()
    run_assertions()
    print("\nAll algorithm assertions passed.")
