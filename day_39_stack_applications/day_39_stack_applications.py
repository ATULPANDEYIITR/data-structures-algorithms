"""
Stack Applications
Demonstrates:
- Balanced-parentheses validation
- Infix expression evaluation
- Function-call simulation
- Undo/redo using stacks
- Error handling, validation, and complexity considerations
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional
import operator
import re


# ---------------------------------------------------------------------------
# Balanced Parentheses
# ---------------------------------------------------------------------------

OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}
CLOSE_TO_OPEN = {value: key for key, value in OPEN_TO_CLOSE.items()}


def validate_balanced_parentheses(expression: str) -> tuple[bool, str]:
    """Validate nested parentheses while ignoring brackets inside quoted strings."""
    stack: list[tuple[str, int]] = []
    quote: Optional[str] = None
    escaped = False

    for position, character in enumerate(expression):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue

        if character in {"'", '"'}:
            quote = character
        elif character in OPEN_TO_CLOSE:
            stack.append((character, position))
        elif character in CLOSE_TO_OPEN:
            if not stack:
                return False, f"Unexpected closing bracket {character!r} at index {position}."

            opening, opening_position = stack.pop()
            if opening != CLOSE_TO_OPEN[character]:
                return (
                    False,
                    f"Mismatched {opening!r} at index {opening_position} "
                    f"with {character!r} at index {position}.",
                )

    if quote is not None:
        return False, "Unterminated quoted string."

    if stack:
        opening, position = stack[-1]
        return False, f"Unclosed opening bracket {opening!r} at index {position}."

    return True, "All brackets are balanced."


def demonstrate_parentheses() -> None:
    examples = [
        "function(a[2], {value: (x + y)})",
        "([{}])",
        "([)]",
        "return items[(index + 1]",
        'print("text with [brackets]")',
        'print("unterminated [text)',
    ]

    print("\n=== Balanced Parentheses ===")
    for expression in examples:
        valid, message = validate_balanced_parentheses(expression)
        print(f"{'VALID' if valid else 'INVALID'}: {expression}")
        print(f"  {message}")


# ---------------------------------------------------------------------------
# Infix Expression Evaluation
# ---------------------------------------------------------------------------

TOKEN_PATTERN = re.compile(
    r"""
    (?P<number>(?:\d+(?:\.\d*)?|\.\d+))
    |(?P<operator>[+\-*/%^()])
    |(?P<whitespace>\s+)
    |(?P<identifier>[A-Za-z_][A-Za-z0-9_]*)
    |(?P<other>.)
    """,
    re.VERBOSE,
)

PRECEDENCE = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "%": 2,
    "^": 3,
}

RIGHT_ASSOCIATIVE = {"^"}


def tokenize(expression: str) -> list[str]:
    tokens: list[str] = []

    for match in TOKEN_PATTERN.finditer(expression):
        kind = match.lastgroup
        value = match.group()

        if kind == "whitespace":
            continue
        if kind == "number" or kind == "operator":
            tokens.append(value)
        elif kind == "identifier":
            raise ValueError(f"Unexpected identifier {value!r}.")
        else:
            raise ValueError(f"Invalid character {value!r}.")

    if not tokens:
        raise ValueError("Expression is empty.")

    return tokens


def infix_to_postfix(expression: str) -> list[str]:
    """Convert an infix expression to postfix notation using an operator stack."""
    tokens = tokenize(expression)
    output: list[str] = []
    operators: list[str] = []
    previous: Optional[str] = None

    for token in tokens:
        if re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", token):
            output.append(token)
            previous = "number"
            continue

        if token == "(":
            operators.append(token)
            previous = "("
            continue

        if token == ")":
            found_opening = False
            while operators:
                operator = operators.pop()
                if operator == "(":
                    found_opening = True
                    break
                output.append(operator)

            if not found_opening:
                raise ValueError("Unmatched closing parenthesis.")

            previous = ")"
            continue

        if token in PRECEDENCE:
            # Unary minus is represented as zero minus the following value.
            if token == "-" and (previous is None or previous == "(" or previous == "operator"):
                output.append("0")

            while operators and operators[-1] != "(":
                top = operators[-1]
                higher_precedence = PRECEDENCE[top] > PRECEDENCE[token]
                equal_and_left_associative = (
                    PRECEDENCE[top] == PRECEDENCE[token]
                    and token not in RIGHT_ASSOCIATIVE
                )

                if higher_precedence or equal_and_left_associative:
                    output.append(operators.pop())
                else:
                    break

            operators.append(token)
            previous = "operator"
            continue

        raise ValueError(f"Unsupported token {token!r}.")

    while operators:
        operator = operators.pop()
        if operator == "(":
            raise ValueError("Unmatched opening parenthesis.")
        output.append(operator)

    return output


def evaluate_postfix(postfix: list[str]) -> float:
    values: list[float] = []

    operations: dict[str, Callable[[float, float], float]] = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "%": operator.mod,
        "^": operator.pow,
    }

    for token in postfix:
        if re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", token):
            values.append(float(token))
            continue

        if token not in operations:
            raise ValueError(f"Unknown postfix operator {token!r}.")

        if len(values) < 2:
            raise ValueError("Malformed expression: insufficient operands.")

        right = values.pop()
        left = values.pop()

        if token in {"/", "%"} and right == 0:
            raise ZeroDivisionError("Division or remainder by zero.")

        result = operations[token](left, right)

        if abs(result) == float("inf"):
            raise OverflowError("Expression produced an infinite result.")

        values.append(result)

    if len(values) != 1:
        raise ValueError("Malformed expression: extra operands remain.")

    return values[0]


def evaluate_expression(expression: str) -> float:
    postfix = infix_to_postfix(expression)
    return evaluate_postfix(postfix)


def demonstrate_expression_evaluation() -> None:
    print("\n=== Expression Evaluation ===")

    examples = [
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "20 / (2 + 3)",
        "2 ^ 3 ^ 2",
        "-5 + 3 * 4",
    ]

    for expression in examples:
        postfix = infix_to_postfix(expression)
        result = evaluate_postfix(postfix)
        print(f"{expression:20} -> {' '.join(postfix):20} = {result:g}")

    invalid_examples = [
        "10 / 0",
        "(2 + 3",
        "2 + * 4",
    ]

    for expression in invalid_examples:
        try:
            evaluate_expression(expression)
        except (ValueError, ZeroDivisionError, OverflowError) as error:
            print(f"Rejected {expression!r}: {error}")


# ---------------------------------------------------------------------------
# Function Call Simulation
# ---------------------------------------------------------------------------

@dataclass
class CallFrame:
    function_name: str
    arguments: tuple[object, ...]
    local_variables: dict[str, object]
    return_value: object = None


class CallStack:
    """A LIFO stack representing active function calls."""

    def __init__(self) -> None:
        self._frames: list[CallFrame] = []

    def call(self, function_name: str, *arguments: object) -> CallFrame:
        frame = CallFrame(
            function_name=function_name,
            arguments=arguments,
            local_variables={},
        )
        self._frames.append(frame)
        return frame

    def return_from_call(self, return_value: object = None) -> CallFrame:
        if not self._frames:
            raise RuntimeError("Cannot return because the call stack is empty.")

        frame = self._frames.pop()
        frame.return_value = return_value
        return frame

    def trace(self) -> list[str]:
        return [
            f"{index}: {frame.function_name}{frame.arguments}"
            for index, frame in enumerate(self._frames)
        ]

    @property
    def depth(self) -> int:
        return len(self._frames)


def factorial_with_call_stack(number: int) -> int:
    """Iterative simulation of recursive factorial activation records."""
    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    stack = CallStack()

    for value in range(number, 0, -1):
        frame = stack.call("factorial", value)
        frame.local_variables["n"] = value

    result = 1

    while stack.depth:
        frame = stack.return_from_call(result)
        result *= frame.local_variables["n"]

    return result


def demonstrate_call_stack() -> None:
    print("\n=== Function Call Simulation ===")

    stack = CallStack()

    main = stack.call("main")
    main.local_variables["request_id"] = "REQ-2048"

    authenticate = stack.call("authenticate", "atul")
    authenticate.local_variables["role"] = "developer"

    load_profile = stack.call("load_profile", 42)

    print("Active frames:")
    for frame in stack.trace():
        print(f"  {frame}")

    completed = stack.return_from_call({"name": "Atul"})
    print(f"Returned from {completed.function_name}: {completed.return_value}")

    completed = stack.return_from_call(True)
    print(f"Returned from {completed.function_name}: {completed.return_value}")

    completed = stack.return_from_call("dashboard")
    print(f"Returned from {completed.function_name}: {completed.return_value}")

    print(f"Stack depth after returns: {stack.depth}")
    print(f"Simulated factorial(6): {factorial_with_call_stack(6)}")


# ---------------------------------------------------------------------------
# Undo / Redo
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TextState:
    content: str


class UndoRedoEditor:
    """
    Two stacks model history:
    - undo_stack contains states that can be restored by undo.
    - redo_stack contains states discarded by undo and available for redo.
    """

    def __init__(self, initial_text: str = "") -> None:
        self._current = TextState(initial_text)
        self._undo_stack: list[TextState] = []
        self._redo_stack: list[TextState] = []

    @property
    def text(self) -> str:
        return self._current.content

    def edit(self, new_text: str) -> None:
        if new_text == self._current.content:
            return

        self._undo_stack.append(self._current)
        self._current = TextState(new_text)

        # A new edit creates a new branch of history, so old redo states
        # can no longer be replayed safely.
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack:
            return False

        self._redo_stack.append(self._current)
        self._current = self._undo_stack.pop()
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False

        self._undo_stack.append(self._current)
        self._current = self._redo_stack.pop()
        return True

    def history(self) -> dict[str, list[str]]:
        return {
            "undo": [state.content for state in self._undo_stack],
            "redo": [state.content for state in self._redo_stack],
            "current": [self._current.content],
        }


def demonstrate_undo_redo() -> None:
    print("\n=== Undo / Redo ===")

    editor = UndoRedoEditor()
    editor.edit("Balanced")
    editor.edit("Balanced parentheses")
    editor.edit("Balanced parentheses validated")

    print(f"Current: {editor.text}")

    editor.undo()
    print(f"After undo: {editor.text}")

    editor.undo()
    print(f"After second undo: {editor.text}")

    editor.redo()
    print(f"After redo: {editor.text}")

    editor.edit("Stack applications")
    print(f"After new edit: {editor.text}")
    print(f"Redo available after new edit: {editor.redo()}")


# ---------------------------------------------------------------------------
# Integration and Edge Cases
# ---------------------------------------------------------------------------

def run_edge_case_checks() -> None:
    print("\n=== Edge Cases ===")

    for value in ["", "()", "(((())))", "([{}])", "([{})"]:
        valid, _ = validate_balanced_parentheses(value)
        print(f"Bracket input {value!r}: {'balanced' if valid else 'not balanced'}")

    try:
        factorial_with_call_stack(-1)
    except ValueError as error:
        print(f"Invalid factorial rejected: {error}")

    try:
        CallStack().return_from_call()
    except RuntimeError as error:
        print(f"Empty call stack rejected: {error}")

    try:
        evaluate_expression("8 / 0")
    except ZeroDivisionError as error:
        print(f"Invalid expression rejected: {error}")


def main() -> None:
    demonstrate_parentheses()
    demonstrate_expression_evaluation()
    demonstrate_call_stack()
    demonstrate_undo_redo()
    run_edge_case_checks()


if __name__ == "__main__":
    main()
