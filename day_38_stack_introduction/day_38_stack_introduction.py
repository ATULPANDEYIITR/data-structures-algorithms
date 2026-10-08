"""
Stack Introduction
===================
Demonstrates LIFO behavior, stack operations, array-based stacks,
linked-list stacks, and practical applications.

The program is self-contained and uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar


T = TypeVar("T")


class StackEmptyError(IndexError):
    """Raised when a stack operation requires an element but the stack is empty."""


class StackOverflowError(OverflowError):
    """Raised when a fixed-capacity stack cannot accept another element."""


class ArrayStack(Generic[T]):
    """
    Stack implemented with Python's dynamic list.

    The end of the list represents the top of the stack. Appending and
    removing from that end are amortized O(1).
    """

    def __init__(self, capacity: Optional[int] = None) -> None:
        if capacity is not None and capacity <= 0:
            raise ValueError("capacity must be positive")
        self._items: list[T] = []
        self._capacity = capacity

    def push(self, item: T) -> None:
        if self._capacity is not None and len(self._items) >= self._capacity:
            raise StackOverflowError("stack capacity has been reached")
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise StackEmptyError("cannot pop from an empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise StackEmptyError("cannot peek at an empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        return not self._items

    def is_full(self) -> bool:
        return self._capacity is not None and len(self._items) == self._capacity

    def size(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()

    def __iter__(self) -> Iterator[T]:
        # Iteration starts at the top because that is the natural inspection
        # order for a LIFO structure.
        return reversed(self._items)

    def __repr__(self) -> str:
        return f"ArrayStack({self._items!r})"


@dataclass
class _Node(Generic[T]):
    value: T
    next: Optional["_Node[T]"] = None


class LinkedStack(Generic[T]):
    """
    Stack implemented as a singly linked list.

    The head node is the top of the stack, so push and pop both operate in O(1)
    time without shifting existing elements.
    """

    def __init__(self, values: Iterable[T] = ()) -> None:
        self._top: Optional[_Node[T]] = None
        self._size = 0

        for value in values:
            self.push(value)

    def push(self, value: T) -> None:
        self._top = _Node(value, self._top)
        self._size += 1

    def pop(self) -> T:
        if self._top is None:
            raise StackEmptyError("cannot pop from an empty linked stack")

        value = self._top.value
        self._top = self._top.next
        self._size -= 1
        return value

    def peek(self) -> T:
        if self._top is None:
            raise StackEmptyError("cannot peek at an empty linked stack")
        return self._top.value

    def is_empty(self) -> bool:
        return self._top is None

    def size(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        current = self._top
        while current is not None:
            yield current.value
            current = current.next


class MinStack(Generic[T]):
    """
    Stack that supports retrieving the minimum value in O(1).

    A second stack stores the minimum value visible at every depth. This is
    useful when an application needs ordinary LIFO operations plus a fast
    aggregate query.
    """

    def __init__(self) -> None:
        self._values: list[T] = []
        self._minimums: list[T] = []

    def push(self, value: T) -> None:
        self._values.append(value)
        if not self._minimums or value <= self._minimums[-1]:
            self._minimums.append(value)

    def pop(self) -> T:
        if not self._values:
            raise StackEmptyError("cannot pop from an empty min stack")

        value = self._values.pop()
        if value == self._minimums[-1]:
            self._minimums.pop()
        return value

    def min_value(self) -> T:
        if not self._minimums:
            raise StackEmptyError("minimum is undefined for an empty stack")
        return self._minimums[-1]


def demonstrate_lifo() -> None:
    print("\n=== LIFO behavior ===")

    stack = ArrayStack[str]()
    for page in ("Home", "Products", "Cart", "Checkout"):
        stack.push(page)

    print("Top:", stack.peek())

    while not stack.is_empty():
        print("Visit/remove:", stack.pop())

    print("The last inserted item was removed first.")


def demonstrate_array_stack() -> None:
    print("\n=== Array-based stack ===")

    stack = ArrayStack[int](capacity=3)

    for value in (10, 20, 30):
        stack.push(value)

    print("Stack from top to bottom:", list(stack))
    print("Full:", stack.is_full())

    try:
        stack.push(40)
    except StackOverflowError as error:
        print("Overflow:", error)

    print("Pop:", stack.pop())
    print("Peek:", stack.peek())
    print("Size:", stack.size())


def demonstrate_linked_stack() -> None:
    print("\n=== Linked-list stack ===")

    stack = LinkedStack[str]()
    for item in ("compile", "test", "package"):
        stack.push(item)

    print("Top:", stack.peek())
    print("Top-to-bottom:", list(stack))

    print("Removing:", stack.pop())
    print("Remaining:", list(stack))


def validate_parentheses(expression: str) -> bool:
    """
    Check balanced (), [], and {} delimiters.

    A closing delimiter must match the most recently opened delimiter.
    That matching requirement is precisely a LIFO operation.
    """

    matching = {")": "(", "]": "[", "}": "{"}
    opening = set(matching.values())
    stack: ArrayStack[str] = ArrayStack()

    for character in expression:
        if character in opening:
            stack.push(character)
        elif character in matching:
            if stack.is_empty() or stack.pop() != matching[character]:
                return False

    return stack.is_empty()


def demonstrate_expression_validation() -> None:
    print("\n=== Balanced delimiter application ===")

    expressions = [
        "(total + price) * [count - 1]",
        "{[()]}",
        "([)]",
        "((value)",
        "items[0] + data[1]",
    ]

    for expression in expressions:
        print(f"{expression!r}: {validate_parentheses(expression)}")


def evaluate_postfix(expression: str) -> float:
    """
    Evaluate a space-separated postfix expression.

    Example: "5 2 + 3 *" means (5 + 2) * 3.
    Operands are pushed, while an operator pops its operands and pushes
    the resulting value back onto the stack.
    """

    stack: ArrayStack[float] = ArrayStack()

    for token in expression.split():
        try:
            stack.push(float(token))
            continue
        except ValueError:
            pass

        if token not in {"+", "-", "*", "/"}:
            raise ValueError(f"unsupported token: {token}")

        if stack.size() < 2:
            raise ValueError(f"operator {token!r} lacks two operands")

        right = stack.pop()
        left = stack.pop()

        if token == "+":
            result = left + right
        elif token == "-":
            result = left - right
        elif token == "*":
            result = left * right
        else:
            if right == 0:
                raise ZeroDivisionError("postfix expression divides by zero")
            result = left / right

        stack.push(result)

    if stack.size() != 1:
        raise ValueError("invalid postfix expression")

    return stack.pop()


def demonstrate_postfix() -> None:
    print("\n=== Postfix evaluation ===")

    expressions = {
        "5 2 + 3 *": 21.0,
        "10 2 / 4 +": 9.0,
        "8 3 - 2 *": 10.0,
    }

    for expression, expected in expressions.items():
        result = evaluate_postfix(expression)
        print(f"{expression} = {result} (expected {expected})")


def reverse_text(text: str) -> str:
    """Reverse text by pushing every character and popping in LIFO order."""

    stack: ArrayStack[str] = ArrayStack()
    for character in text:
        stack.push(character)

    return "".join(stack.pop() for _ in range(stack.size()))


def demonstrate_undo_redo() -> None:
    print("\n=== Undo/redo application ===")

    undo: ArrayStack[str] = ArrayStack()
    redo: ArrayStack[str] = ArrayStack()

    def perform(action: str) -> None:
        undo.push(action)
        redo.clear()

    def undo_action() -> Optional[str]:
        if undo.is_empty():
            return None
        action = undo.pop()
        redo.push(action)
        return action

    def redo_action() -> Optional[str]:
        if redo.is_empty():
            return None
        action = redo.pop()
        undo.push(action)
        return action

    perform("type: Hello")
    perform("type: World")
    perform("delete: World")

    print("Undo:", undo_action())
    print("Undo:", undo_action())
    print("Redo:", redo_action())

    # A new operation invalidates the old redo history.
    perform("type: Python")
    print("Redo available after a new operation:", not redo.is_empty())


def demonstrate_min_stack() -> None:
    print("\n=== Augmented stack ===")

    stack = MinStack[int]()

    for value in (7, 3, 9, 2, 5):
        stack.push(value)
        print(f"push({value}), minimum={stack.min_value()}")

    print("pop:", stack.pop(), "minimum:", stack.min_value())
    print("pop:", stack.pop(), "minimum:", stack.min_value())


def demonstrate_edge_cases() -> None:
    print("\n=== Edge cases ===")

    empty = ArrayStack[int]()

    for operation in (empty.pop, empty.peek):
        try:
            operation()
        except StackEmptyError as error:
            print("Expected empty-stack error:", error)

    try:
        ArrayStack[int](0)
    except ValueError as error:
        print("Expected invalid-capacity error:", error)

    try:
        evaluate_postfix("8 0 /")
    except ZeroDivisionError as error:
        print("Expected arithmetic error:", error)

    print("Reverse:", reverse_text("LIFO"))


def complexity_notes() -> None:
    print("\n=== Complexity ===")
    print("Array stack push: amortized O(1)")
    print("Array stack pop: O(1)")
    print("Array stack peek: O(1)")
    print("Linked stack push: O(1)")
    print("Linked stack pop: O(1)")
    print("Linked stack peek: O(1)")
    print("Balanced delimiter validation: O(n) time, O(n) space")
    print("Postfix evaluation: O(n) time, O(n) auxiliary space")
    print("A fixed-capacity array stack provides an explicit overflow boundary.")


def main() -> None:
    demonstrate_lifo()
    demonstrate_array_stack()
    demonstrate_linked_stack()
    demonstrate_expression_validation()
    demonstrate_postfix()
    demonstrate_undo_redo()
    demonstrate_min_stack()
    demonstrate_edge_cases()
    complexity_notes()


if __name__ == "__main__":
    main()
