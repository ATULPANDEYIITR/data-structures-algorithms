from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional


def generate_binary_strings(length: int) -> list[str]:
    """Generate every binary string of a fixed length using backtracking."""
    if length < 0:
        raise ValueError("length must be non-negative")

    result: list[str] = []
    path: list[str] = []

    def search() -> None:
        if len(path) == length:
            result.append("".join(path))
            return

        for choice in ("0", "1"):
            path.append(choice)
            search()
            path.pop()  # Undo the choice before exploring the next branch.

    search()
    return result


def generate_subsets(values: list[int]) -> list[list[int]]:
    """Explore include/exclude decisions for every input element."""
    result: list[list[int]] = []
    path: list[int] = []

    def search(index: int) -> None:
        if index == len(values):
            result.append(path.copy())
            return

        # Branch where the current value is excluded.
        search(index + 1)

        # Branch where the current value is included.
        path.append(values[index])
        search(index + 1)
        path.pop()

    search(0)
    return result


def permutations(values: list[int]) -> list[list[int]]:
    """Generate permutations while tracking which values are already used."""
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(values)

    def search() -> None:
        if len(path) == len(values):
            result.append(path.copy())
            return

        for index, value in enumerate(values):
            if used[index]:
                continue

            used[index] = True
            path.append(value)
            search()
            path.pop()
            used[index] = False

    search()
    return result


def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    """Find combinations whose values add to target.

    A candidate may be reused. Sorting enables pruning because once a candidate
    exceeds the remaining target, later candidates cannot produce a solution.
    """
    if target < 0:
        raise ValueError("target must be non-negative")

    candidates = sorted(set(candidates))
    if any(value <= 0 for value in candidates):
        raise ValueError("candidates must contain positive integers")

    result: list[list[int]] = []
    path: list[int] = []

    def search(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path.copy())
            return

        for index in range(start, len(candidates)):
            value = candidates[index]
            if value > remaining:
                break

            path.append(value)
            # Reuse is allowed, so the next search starts at index.
            search(index, remaining - value)
            path.pop()

    search(0, target)
    return result


def solve_n_queens(n: int) -> list[list[str]]:
    """Place n queens so no two share a row, column, or diagonal."""
    if n <= 0:
        raise ValueError("n must be positive")

    solutions: list[list[str]] = []
    board = [["."] * n for _ in range(n)]
    columns: set[int] = set()
    diagonals: set[int] = set()       # row - column
    anti_diagonals: set[int] = set()  # row + column

    def search(row: int) -> None:
        if row == n:
            solutions.append(["".join(line) for line in board])
            return

        for column in range(n):
            diagonal = row - column
            anti_diagonal = row + column

            if (
                column in columns
                or diagonal in diagonals
                or anti_diagonal in anti_diagonals
            ):
                continue

            board[row][column] = "Q"
            columns.add(column)
            diagonals.add(diagonal)
            anti_diagonals.add(anti_diagonal)

            search(row + 1)

            # Restore every mutated state before returning to the parent.
            board[row][column] = "."
            columns.remove(column)
            diagonals.remove(diagonal)
            anti_diagonals.remove(anti_diagonal)

    search(0)
    return solutions


def maze_paths(maze: list[list[int]]) -> list[str]:
    """Find paths through a grid where 0 is open and 1 is blocked.

    Movement is restricted to right, down, left, and up. A cell is marked
    visited during the current path and unmarked when backtracking.
    """
    if not maze or not maze[0]:
        return []

    rows = len(maze)
    columns = len(maze[0])

    if any(len(row) != columns for row in maze):
        raise ValueError("maze must be rectangular")

    if maze[0][0] == 1 or maze[-1][-1] == 1:
        return []

    visited = [[False] * columns for _ in range(rows)]
    paths: list[str] = []
    path: list[str] = []
    moves = (
        ("D", 1, 0),
        ("R", 0, 1),
        ("U", -1, 0),
        ("L", 0, -1),
    )

    def search(row: int, column: int) -> None:
        if row == rows - 1 and column == columns - 1:
            paths.append("".join(path))
            return

        visited[row][column] = True

        for symbol, row_delta, column_delta in moves:
            next_row = row + row_delta
            next_column = column + column_delta

            if not (0 <= next_row < rows and 0 <= next_column < columns):
                continue
            if maze[next_row][next_column] == 1:
                continue
            if visited[next_row][next_column]:
                continue

            path.append(symbol)
            search(next_row, next_column)
            path.pop()

        visited[row][column] = False

    search(0, 0)
    return paths


def sudoku_solutions(board: list[list[int]], limit: Optional[int] = None) -> list[list[list[int]]]:
    """Solve Sudoku with constraint checking and recursive undo."""
    if len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("Sudoku board must be 9x9")

    for row in board:
        if any(value < 0 or value > 9 for value in row):
            raise ValueError("Sudoku values must be between 0 and 9")

    working = [row.copy() for row in board]
    solutions: list[list[list[int]]] = []

    def valid(row: int, column: int, value: int) -> bool:
        if value in working[row]:
            return False

        if any(working[r][column] == value for r in range(9)):
            return False

        box_row = (row // 3) * 3
        box_column = (column // 3) * 3

        for r in range(box_row, box_row + 3):
            for c in range(box_column, box_column + 3):
                if working[r][c] == value:
                    return False

        return True

    def select_cell() -> Optional[tuple[int, int, list[int]]]:
        """Choose the empty cell with the fewest legal candidates.

        This is a constraint-ordering heuristic that reduces unnecessary
        branches compared with simply choosing the first empty cell.
        """
        best: Optional[tuple[int, int, list[int]]] = None

        for row in range(9):
            for column in range(9):
                if working[row][column] != 0:
                    continue

                candidates = [
                    value
                    for value in range(1, 10)
                    if valid(row, column, value)
                ]

                if not candidates:
                    return row, column, []

                if best is None or len(candidates) < len(best[2]):
                    best = row, column, candidates

        return best

    def search() -> None:
        if limit is not None and len(solutions) >= limit:
            return

        selected = select_cell()

        if selected is None:
            solutions.append([row.copy() for row in working])
            return

        row, column, candidates = selected

        if not candidates:
            return

        for value in candidates:
            working[row][column] = value
            search()
            working[row][column] = 0

            if limit is not None and len(solutions) >= limit:
                return

    search()
    return solutions


def validate_parentheses(text: str) -> bool:
    """Use backtracking to test all valid next bracket choices.

    This intentionally demonstrates state-space exploration. For production
    validation, a linear stack-based parser is preferable.
    """
    pairs = {")": "(", "]": "[", "}": "{"}
    opening = set(pairs.values())

    def search(index: int, stack: list[str]) -> bool:
        if index == len(text):
            return not stack

        character = text[index]

        if character in opening:
            stack.append(character)
            valid = search(index + 1, stack)
            stack.pop()
            return valid

        if character in pairs:
            if not stack or stack[-1] != pairs[character]:
                return False

            opening_character = stack.pop()
            valid = search(index + 1, stack)
            stack.append(opening_character)
            return valid

        return search(index + 1, stack)

    return search(0, [])


@dataclass
class SearchStats:
    visited_states: int = 0
    pruned_states: int = 0
    solutions: int = 0


def constrained_schedule(
    people: list[str],
    slots: list[str],
    unavailable: dict[str, set[str]],
    conflict_pairs: set[frozenset[str]],
) -> tuple[list[dict[str, str]], SearchStats]:
    """Assign every person to a slot while respecting constraints."""
    if len(slots) < len(people):
        return [], SearchStats()

    stats = SearchStats()
    assignment: dict[str, str] = {}
    used_slots: set[str] = set()
    results: list[dict[str, str]] = []

    def violates_conflict(person: str) -> bool:
        for assigned_person in assignment:
            if frozenset((person, assigned_person)) in conflict_pairs:
                return True
        return False

    def search() -> None:
        stats.visited_states += 1

        if len(assignment) == len(people):
            results.append(assignment.copy())
            stats.solutions += 1
            return

        # Minimum remaining values: choose the person with the fewest
        # currently legal slots to expose contradictions early.
        remaining_people = [p for p in people if p not in assignment]

        best_person: Optional[str] = None
        best_slots: list[str] = []

        for person in remaining_people:
            legal = [
                slot
                for slot in slots
                if slot not in used_slots
                and slot not in unavailable.get(person, set())
                and not violates_conflict(person)
            ]

            if best_person is None or len(legal) < len(best_slots):
                best_person = person
                best_slots = legal

        if best_person is None or not best_slots:
            stats.pruned_states += 1
            return

        for slot in best_slots:
            assignment[best_person] = slot
            used_slots.add(slot)

            search()

            used_slots.remove(slot)
            del assignment[best_person]

    search()
    return results, stats


def print_matrix(matrix: Iterable[Iterable[object]]) -> None:
    for row in matrix:
        print(" ".join(map(str, row)))


def main() -> None:
    print("Backtracking: decision trees, constraints, and undo operations")

    print("\nBinary decision tree")
    print(generate_binary_strings(3))

    print("\nInclude/exclude state-space exploration")
    print(generate_subsets([10, 20, 30]))

    print("\nPermutation search with used-state tracking")
    print(permutations([1, 2, 3]))

    print("\nConstraint-based combination search")
    print(combination_sum([2, 3, 6, 7], 7))

    print("\nN-Queens constraint propagation")
    queens = solve_n_queens(4)
    for solution in queens:
        print()
        print_matrix(solution)

    print("\nMaze state-space exploration")
    maze = [
        [0, 0, 1, 0],
        [1, 0, 1, 0],
        [0, 0, 0, 0],
        [0, 1, 1, 0],
    ]
    print(maze_paths(maze))

    print("\nSudoku constraint search")
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
    solved = sudoku_solutions(sudoku, limit=1)
    if solved:
        print_matrix(solved[0])

    print("\nBacktracking as a constrained scheduling engine")
    people = ["Alice", "Bob", "Carol", "David"]
    slots = ["09:00", "10:00", "11:00", "12:00"]
    unavailable = {
        "Alice": {"12:00"},
        "Bob": {"09:00"},
        "Carol": {"11:00"},
        "David": set(),
    }
    conflicts = {
        frozenset(("Alice", "Carol")),
    }

    schedules, stats = constrained_schedule(
        people,
        slots,
        unavailable,
        conflicts,
    )
    print("First valid schedules:")
    for schedule in schedules[:3]:
        print(schedule)
    print(
        f"Visited states={stats.visited_states}, "
        f"pruned={stats.pruned_states}, "
        f"solutions={stats.solutions}"
    )

    print("\nBacktracking parser example")
    for expression in ("([]{})", "([)]", "((()))"):
        print(expression, "->", validate_parentheses(expression))


if __name__ == "__main__":
    main()
