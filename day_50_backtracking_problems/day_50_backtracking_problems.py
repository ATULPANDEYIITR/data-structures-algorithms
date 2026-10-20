from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Sequence
import math


def validate_items(items: Sequence[int], *, name: str = "items") -> None:
    if items is None:
        raise ValueError(f"{name} cannot be None")
    if any(item is None for item in items):
        raise ValueError(f"{name} cannot contain None")


def subsets(items: Sequence[int]) -> list[list[int]]:
    """Generate every subset by making an include/exclude decision per item."""
    validate_items(items)
    result: list[list[int]] = []
    current: list[int] = []

    def backtrack(index: int) -> None:
        if index == len(items):
            result.append(current.copy())
            return

        # Exclude the current element.
        backtrack(index + 1)

        # Include the current element.
        current.append(items[index])
        backtrack(index + 1)
        current.pop()

    backtrack(0)
    return result


def unique_subsets(items: Sequence[int]) -> list[list[int]]:
    """Generate unique subsets when the input can contain duplicate values."""
    validate_items(items)
    values = sorted(items)
    result: list[list[int]] = []
    current: list[int] = []

    def backtrack(start: int) -> None:
        result.append(current.copy())

        for index in range(start, len(values)):
            # Equal values at the same recursion depth produce duplicate branches.
            if index > start and values[index] == values[index - 1]:
                continue

            current.append(values[index])
            backtrack(index + 1)
            current.pop()

    backtrack(0)
    return result


def permutations(items: Sequence[int]) -> list[list[int]]:
    """Generate permutations of distinct input values."""
    validate_items(items)
    if len(set(items)) != len(items):
        raise ValueError("permutations() requires distinct values")

    result: list[list[int]] = []
    current: list[int] = []
    used = [False] * len(items)

    def backtrack() -> None:
        if len(current) == len(items):
            result.append(current.copy())
            return

        for index, value in enumerate(items):
            if used[index]:
                continue

            used[index] = True
            current.append(value)
            backtrack()
            current.pop()
            used[index] = False

    backtrack()
    return result


def unique_permutations(items: Sequence[int]) -> list[list[int]]:
    """Generate unique permutations without relying on a set of final results."""
    validate_items(items)
    values = sorted(items)
    result: list[list[int]] = []
    current: list[int] = []
    used = [False] * len(values)

    def backtrack() -> None:
        if len(current) == len(values):
            result.append(current.copy())
            return

        for index in range(len(values)):
            if used[index]:
                continue

            # If an equal value is unused at this recursion level, selecting
            # this later copy would create the same permutation prefix.
            if index > 0 and values[index] == values[index - 1] and not used[index - 1]:
                continue

            used[index] = True
            current.append(values[index])
            backtrack()
            current.pop()
            used[index] = False

    backtrack()
    return result


def combinations(items: Sequence[int], k: int) -> list[list[int]]:
    """Generate all k-element combinations."""
    validate_items(items)
    if k < 0 or k > len(items):
        return []

    result: list[list[int]] = []
    current: list[int] = []

    def backtrack(start: int) -> None:
        if len(current) == k:
            result.append(current.copy())
            return

        needed = k - len(current)
        last_start = len(items) - needed

        for index in range(start, last_start + 1):
            current.append(items[index])
            backtrack(index + 1)
            current.pop()

    if k == 0:
        return [[]]

    backtrack(0)
    return result


def solve_n_queens(n: int) -> list[list[str]]:
    """Return every N-Queens board using column and diagonal constraints."""
    if n < 1:
        raise ValueError("n must be positive")

    solutions: list[list[str]] = []
    board = [["."] * n for _ in range(n)]
    columns: set[int] = set()
    down_diagonals: set[int] = set()  # row - column
    up_diagonals: set[int] = set()    # row + column

    def backtrack(row: int) -> None:
        if row == n:
            solutions.append(["".join(line) for line in board])
            return

        for column in range(n):
            if column in columns:
                continue
            if row - column in down_diagonals:
                continue
            if row + column in up_diagonals:
                continue

            board[row][column] = "Q"
            columns.add(column)
            down_diagonals.add(row - column)
            up_diagonals.add(row + column)

            backtrack(row + 1)

            up_diagonals.remove(row + column)
            down_diagonals.remove(row - column)
            columns.remove(column)
            board[row][column] = "."

    backtrack(0)
    return solutions


def solve_sudoku(board: list[list[int]]) -> bool:
    """
    Solve a 9x9 Sudoku in-place.

    Empty cells contain 0. Returns False when the puzzle has no solution.
    """
    if len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("Sudoku board must be 9x9")

    for row in board:
        for value in row:
            if not isinstance(value, int) or not 0 <= value <= 9:
                raise ValueError("Sudoku cells must contain integers from 0 to 9")

    rows = [set() for _ in range(9)]
    columns = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empty: list[tuple[int, int]] = []

    for row in range(9):
        for column in range(9):
            value = board[row][column]
            if value == 0:
                empty.append((row, column))
                continue

            box = (row // 3) * 3 + column // 3
            if value in rows[row] or value in columns[column] or value in boxes[box]:
                return False

            rows[row].add(value)
            columns[column].add(value)
            boxes[box].add(value)

    def backtrack() -> bool:
        if not empty:
            return True

        # Minimum Remaining Values reduces branching substantially.
        best_index = -1
        best_candidates: set[int] | None = None

        for index, (row, column) in enumerate(empty):
            if index < 0:
                continue

            box = (row // 3) * 3 + column // 3
            candidates = (
                set(range(1, 10))
                - rows[row]
                - columns[column]
                - boxes[box]
            )

            if not candidates:
                return False

            if best_candidates is None or len(candidates) < len(best_candidates):
                best_index = index
                best_candidates = candidates

                if len(candidates) == 1:
                    break

        row, column = empty.pop(best_index)
        box = (row // 3) * 3 + column // 3

        for value in sorted(best_candidates):
            board[row][column] = value
            rows[row].add(value)
            columns[column].add(value)
            boxes[box].add(value)

            if backtrack():
                return True

            boxes[box].remove(value)
            columns[column].remove(value)
            rows[row].remove(value)
            board[row][column] = 0

        empty.insert(best_index, (row, column))
        return False

    return backtrack()


@dataclass(frozen=True)
class GridPosition:
    row: int
    column: int


def find_paths(
    grid: Sequence[Sequence[int]],
    start: GridPosition,
    target: GridPosition,
    *,
    blocked_value: int = 1,
    max_paths: int = 1000,
) -> list[list[GridPosition]]:
    """
    Find simple four-direction paths through a binary grid.

    0 means traversable and blocked_value means unavailable.
    The search stops after max_paths results to avoid unbounded output.
    """
    if not grid or not grid[0]:
        return []

    rows = len(grid)
    columns = len(grid[0])

    if any(len(row) != columns for row in grid):
        raise ValueError("Grid must be rectangular")

    for position in (start, target):
        if not (0 <= position.row < rows and 0 <= position.column < columns):
            raise ValueError("Start and target must be inside the grid")

    if grid[start.row][start.column] == blocked_value:
        return []
    if grid[target.row][target.column] == blocked_value:
        return []
    if max_paths <= 0:
        return []

    result: list[list[GridPosition]] = []
    path: list[GridPosition] = [start]
    visited = {start}

    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def backtrack(position: GridPosition) -> None:
        if len(result) >= max_paths:
            return

        if position == target:
            result.append(path.copy())
            return

        for row_delta, column_delta in directions:
            next_position = GridPosition(
                position.row + row_delta,
                position.column + column_delta,
            )

            if not (0 <= next_position.row < rows and 0 <= next_position.column < columns):
                continue
            if grid[next_position.row][next_position.column] == blocked_value:
                continue
            if next_position in visited:
                continue

            visited.add(next_position)
            path.append(next_position)
            backtrack(next_position)
            path.pop()
            visited.remove(next_position)

    backtrack(start)
    return result


def solve_maze(grid: Sequence[Sequence[int]]) -> list[GridPosition] | None:
    """
    Find one path from the upper-left cell to the lower-right cell.

    Uses backtracking and returns None when no path exists.
    """
    if not grid or not grid[0]:
        return None

    rows = len(grid)
    columns = len(grid[0])

    if any(len(row) != columns for row in grid):
        raise ValueError("Maze must be rectangular")

    start = GridPosition(0, 0)
    target = GridPosition(rows - 1, columns - 1)

    paths = find_paths(grid, start, target, max_paths=1)
    return paths[0] if paths else None


def run_demo() -> None:
    print("Subsets:", subsets([1, 2, 3]))
    print("Unique subsets:", unique_subsets([1, 2, 2]))

    print("Permutations:", permutations([1, 2, 3]))
    print("Unique permutations:", unique_permutations([1, 1, 2]))

    print("Combinations of 4 choose 2:", combinations([1, 2, 3, 4], 2))

    queens = solve_n_queens(4)
    print("4-Queens solutions:", len(queens))
    for board in queens:
        print("\n".join(board))
        print()

    sudoku = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    print("Sudoku solved:", solve_sudoku(sudoku))
    for row in sudoku:
        print(row)

    maze = [
        [0, 0, 1, 0, 0],
        [1, 0, 1, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 1, 0],
    ]

    path = solve_maze(maze)
    print("Maze path:", path)

    all_paths = find_paths(
        maze,
        GridPosition(0, 0),
        GridPosition(4, 4),
        max_paths=10,
    )
    print("Number of paths returned:", len(all_paths))


if __name__ == "__main__":
    run_demo()
