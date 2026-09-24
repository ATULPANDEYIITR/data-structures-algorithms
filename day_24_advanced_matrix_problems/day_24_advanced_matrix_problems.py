"""
Advanced Matrix Problems
========================

A self-contained study program covering:

1. Matrix representation and traversal
2. Transpose
3. In-place transpose for square matrices
4. Rotation by 90 degrees clockwise and counterclockwise
5. General matrix rotation
6. Spiral traversal
7. Boundary traversal
8. Diagonal traversal
9. Searching in row-wise and column-wise sorted matrices
10. Searching in a globally sorted matrix
11. Prefix-sum matrices
12. Rectangle-sum queries
13. Difference matrices
14. 2D range updates
15. Maximum submatrix sum
16. Largest rectangle of ones
17. Island/grid traversal
18. Shortest path in a binary grid
19. Number of islands
20. Connected components
21. Flood fill
22. Dynamic-programming grid problems
23. Sudoku validation
24. Sparse matrix representation
25. Matrix multiplication
26. Strassen-style recursive multiplication for square matrices
27. Complexity analysis
28. Edge cases and validation
29. Testing and practical engineering considerations

The program uses only the Python standard library.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, Optional


Number = int | float


# ---------------------------------------------------------------------------
# Basic validation and display
# ---------------------------------------------------------------------------

def validate_matrix(matrix: list[list[Number]], *, allow_empty: bool = False) -> None:
    """Validate that a matrix is rectangular."""
    if not isinstance(matrix, list):
        raise TypeError("Matrix must be a list of lists.")

    if not matrix:
        if allow_empty:
            return
        raise ValueError("Matrix must not be empty.")

    if not all(isinstance(row, list) for row in matrix):
        raise TypeError("Every matrix row must be a list.")

    column_count = len(matrix[0])

    if column_count == 0:
        raise ValueError("Matrix rows must not be empty.")

    if any(len(row) != column_count for row in matrix):
        raise ValueError("Matrix must be rectangular.")


def validate_same_shape(
    first: list[list[Number]],
    second: list[list[Number]],
) -> None:
    """Ensure two matrices have the same dimensions."""
    validate_matrix(first)
    validate_matrix(second)

    if len(first) != len(second) or len(first[0]) != len(second[0]):
        raise ValueError("Matrices must have identical dimensions.")


def validate_square_matrix(matrix: list[list[Number]]) -> None:
    """Ensure that a matrix is square."""
    validate_matrix(matrix)

    if len(matrix) != len(matrix[0]):
        raise ValueError("Operation requires a square matrix.")


def print_matrix(matrix: list[list[Number]], title: str = "") -> None:
    """Print a matrix in a readable form."""
    if title:
        print(f"\n{title}")

    for row in matrix:
        print(" ".join(f"{value:>6}" for value in row))


def clone_matrix(matrix: list[list[Number]]) -> list[list[Number]]:
    """Create a shallow row-by-row copy of a matrix."""
    validate_matrix(matrix)
    return [row[:] for row in matrix]


# ---------------------------------------------------------------------------
# Fundamental matrix operations
# ---------------------------------------------------------------------------

def transpose(matrix: list[list[Number]]) -> list[list[Number]]:
    """
    Return the transpose.

    A matrix with shape rows x columns becomes columns x rows.
    """
    validate_matrix(matrix)

    return [
        [matrix[row][column] for row in range(len(matrix))]
        for column in range(len(matrix[0]))
    ]


def transpose_square_in_place(matrix: list[list[Number]]) -> None:
    """
    Transpose a square matrix in place.

    Only elements above the main diagonal are swapped with their
    corresponding elements below the diagonal.
    """
    validate_square_matrix(matrix)

    size = len(matrix)

    for row in range(size):
        for column in range(row + 1, size):
            matrix[row][column], matrix[column][row] = (
                matrix[column][row],
                matrix[row][column],
            )


def rotate_90_clockwise(matrix: list[list[Number]]) -> list[list[Number]]:
    """
    Rotate any rectangular matrix 90 degrees clockwise.

    For a square matrix this can be implemented in place by transpose
    followed by reversing every row. This version supports rectangles too.
    """
    validate_matrix(matrix)

    return [
        [matrix[row][column] for row in range(len(matrix) - 1, -1, -1)]
        for column in range(len(matrix[0]))
    ]


def rotate_90_counterclockwise(matrix: list[list[Number]]) -> list[list[Number]]:
    """Rotate any rectangular matrix 90 degrees counterclockwise."""
    validate_matrix(matrix)

    return [
        [matrix[row][column] for row in range(len(matrix[0]) - 1, -1, -1)]
        for row in range(len(matrix))
    ]


def rotate_square_in_place_clockwise(matrix: list[list[Number]]) -> None:
    """
    Rotate a square matrix 90 degrees clockwise in place.

    Technique:
        1. Transpose.
        2. Reverse every row.

    Time: O(n^2)
    Extra space: O(1)
    """
    validate_square_matrix(matrix)

    transpose_square_in_place(matrix)

    for row in matrix:
        row.reverse()


def rotate_square_in_place_counterclockwise(matrix: list[list[Number]]) -> None:
    """
    Rotate a square matrix 90 degrees counterclockwise in place.

    Technique:
        1. Transpose.
        2. Reverse the order of rows.
    """
    validate_square_matrix(matrix)

    transpose_square_in_place(matrix)
    matrix.reverse()


def rotate_square(matrix: list[list[Number]], degrees: int) -> list[list[Number]]:
    """
    Rotate a square matrix by a multiple of 90 degrees.

    Positive degrees mean clockwise rotation.
    Negative degrees mean counterclockwise rotation.
    """
    validate_square_matrix(matrix)

    if degrees % 90 != 0:
        raise ValueError("Rotation angle must be a multiple of 90 degrees.")

    result = clone_matrix(matrix)

    rotations = (degrees // 90) % 4

    for _ in range(rotations):
        rotate_square_in_place_clockwise(result)

    return result


# ---------------------------------------------------------------------------
# Traversal algorithms
# ---------------------------------------------------------------------------

def row_major_traversal(matrix: list[list[Number]]) -> list[Number]:
    """Visit every element from left to right, top to bottom."""
    validate_matrix(matrix)

    return [value for row in matrix for value in row]


def boundary_traversal(matrix: list[list[Number]]) -> list[Number]:
    """
    Return matrix boundary elements in clockwise order.

    Handles single-row and single-column matrices separately so that
    corners are not duplicated.
    """
    validate_matrix(matrix)

    rows = len(matrix)
    columns = len(matrix[0])

    if rows == 1:
        return matrix[0][:]

    if columns == 1:
        return [matrix[row][0] for row in range(rows)]

    result: list[Number] = []

    result.extend(matrix[0])

    for row in range(1, rows):
        result.append(matrix[row][columns - 1])

    for column in range(columns - 2, -1, -1):
        result.append(matrix[rows - 1][column])

    for row in range(rows - 2, 0, -1):
        result.append(matrix[row][0])

    return result


def spiral_traversal(matrix: list[list[Number]]) -> list[Number]:
    """
    Traverse a matrix in clockwise spiral order.

    Four boundaries shrink toward the center:
        top, bottom, left, right.
    """
    validate_matrix(matrix)

    top = 0
    bottom = len(matrix) - 1
    left = 0
    right = len(matrix[0]) - 1

    result: list[Number] = []

    while top <= bottom and left <= right:
        for column in range(left, right + 1):
            result.append(matrix[top][column])
        top += 1

        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1

        if top <= bottom:
            for column in range(right, left - 1, -1):
                result.append(matrix[bottom][column])
            bottom -= 1

        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1

    return result


def diagonal_traversal(matrix: list[list[Number]]) -> list[list[Number]]:
    """
    Return all diagonals grouped by diagonal.

    Elements sharing row + column belong to the same anti-diagonal.
    """
    validate_matrix(matrix)

    rows = len(matrix)
    columns = len(matrix[0])
    result: list[list[Number]] = []

    for diagonal_index in range(rows + columns - 1):
        diagonal: list[Number] = []

        for row in range(rows):
            column = diagonal_index - row

            if 0 <= column < columns:
                diagonal.append(matrix[row][column])

        result.append(diagonal)

    return result


# ---------------------------------------------------------------------------
# Searching sorted matrices
# ---------------------------------------------------------------------------

def binary_search_row(row: list[Number], target: Number) -> int:
    """Binary search a sorted one-dimensional row."""
    left = 0
    right = len(row) - 1

    while left <= right:
        middle = (left + right) // 2

        if row[middle] == target:
            return middle

        if row[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def search_sorted_matrix_binary(
    matrix: list[list[Number]],
    target: Number,
) -> Optional[tuple[int, int]]:
    """
    Search a matrix where each row is sorted independently.

    Complexity:
        O(rows * log(columns))
    """
    validate_matrix(matrix)

    for row_index, row in enumerate(matrix):
        column_index = binary_search_row(row, target)

        if column_index != -1:
            return row_index, column_index

    return None


def search_row_column_sorted_matrix(
    matrix: list[list[Number]],
    target: Number,
) -> Optional[tuple[int, int]]:
    """
    Search a matrix sorted left-to-right in every row and
    top-to-bottom in every column.

    Start at the top-right corner:
        target smaller -> move left
        target larger  -> move down

    Complexity: O(rows + columns)
    Extra space: O(1)
    """
    validate_matrix(matrix)

    rows = len(matrix)
    columns = len(matrix[0])

    row = 0
    column = columns - 1

    while row < rows and column >= 0:
        value = matrix[row][column]

        if value == target:
            return row, column

        if value > target:
            column -= 1
        else:
            row += 1

    return None


def search_fully_sorted_matrix(
    matrix: list[list[Number]],
    target: Number,
) -> Optional[tuple[int, int]]:
    """
    Search a matrix that behaves like one sorted one-dimensional array.

    Assumption:
        Every row is sorted and the first value of a row is greater than
        the last value of the previous row.
    """
    validate_matrix(matrix)

    rows = len(matrix)
    columns = len(matrix[0])

    left = 0
    right = rows * columns - 1

    while left <= right:
        middle = (left + right) // 2
        row = middle // columns
        column = middle % columns

        value = matrix[row][column]

        if value == target:
            return row, column

        if value < target:
            left = middle + 1
        else:
            right = middle - 1

    return None


# ---------------------------------------------------------------------------
# Prefix-sum matrices
# ---------------------------------------------------------------------------

def build_prefix_sum(matrix: list[list[Number]]) -> list[list[Number]]:
    """
    Build a 2D prefix-sum matrix with one extra row and column.

    prefix[r + 1][c + 1] contains the sum of rectangle
    matrix[0:r + 1][0:c + 1].
    """
    validate_matrix(matrix)

    rows = len(matrix)
    columns = len(matrix[0])

    prefix = [[0] * (columns + 1) for _ in range(rows + 1)]

    for row in range(rows):
        running_sum = 0

        for column in range(columns):
            running_sum += matrix[row][column]

            prefix[row + 1][column + 1] = (
                prefix[row][column + 1]
                + running_sum
            )

    return prefix


def rectangle_sum(
    prefix: list[list[Number]],
    top: int,
    left: int,
    bottom: int,
    right: int,
) -> Number:
    """
    Query a rectangular sum from a prefix matrix.

    Coordinates are inclusive and refer to the original matrix.
    """
    if top < 0 or left < 0 or bottom < top or right < left:
        raise ValueError("Invalid rectangle coordinates.")

    if bottom + 1 >= len(prefix) or right + 1 >= len(prefix[0]):
        raise IndexError("Rectangle exceeds matrix dimensions.")

    return (
        prefix[bottom + 1][right + 1]
        - prefix[top][right + 1]
        - prefix[bottom + 1][left]
        + prefix[top][left]
    )


# ---------------------------------------------------------------------------
# Difference matrix and range updates
# ---------------------------------------------------------------------------

def range_add(
    matrix: list[list[Number]],
    top: int,
    left: int,
    bottom: int,
    right: int,
    value: Number,
) -> None:
    """Naively add a value to every cell inside a rectangle."""
    validate_matrix(matrix)

    rows = len(matrix)
    columns = len(matrix[0])

    if not (
        0 <= top <= bottom < rows
        and 0 <= left <= right < columns
    ):
        raise ValueError("Invalid update rectangle.")

    for row in range(top, bottom + 1):
        for column in range(left, right + 1):
            matrix[row][column] += value


def build_difference_matrix(rows: int, columns: int) -> list[list[int]]:
    """
    Create an empty difference matrix.

    Rectangle updates can be represented using four corner changes.
    """
    if rows <= 0 or columns <= 0:
        raise ValueError("Dimensions must be positive.")

    return [[0] * (columns + 1) for _ in range(rows + 1)]


def difference_rectangle_update(
    difference: list[list[Number]],
    top: int,
    left: int,
    bottom: int,
    right: int,
    value: Number,
) -> None:
    """
    Record a rectangle addition using a 2D difference matrix.

    The actual values are reconstructed later using prefix accumulation.
    """
    rows = len(difference) - 1
    columns = len(difference[0]) - 1

    if not (
        0 <= top <= bottom < rows
        and 0 <= left <= right < columns
    ):
        raise ValueError("Invalid rectangle coordinates.")

    difference[top][left] += value
    difference[bottom + 1][left] -= value
    difference[top][right + 1] -= value
    difference[bottom + 1][right + 1] += value


def materialize_difference_matrix(
    difference: list[list[Number]],
) -> list[list[Number]]:
    """Convert a 2D difference matrix into actual cell values."""
    if len(difference) < 2 or len(difference[0]) < 2:
        raise ValueError("Difference matrix is too small.")

    rows = len(difference) - 1
    columns = len(difference[0]) - 1

    result = [[0] * columns for _ in range(rows)]

    for row in range(rows):
        for column in range(columns):
            value = difference[row][column]

            if row > 0:
                value += result[row - 1][column]

            if column > 0:
                value += result[row][column - 1]

            if row > 0 and column > 0:
                value -= result[row - 1][column - 1]

            result[row][column] = value

    return result


# ---------------------------------------------------------------------------
# Matrix multiplication
# ---------------------------------------------------------------------------

def multiply_matrices(
    first: list[list[Number]],
    second: list[list[Number]],
) -> list[list[Number]]:
    """
    Classical matrix multiplication.

    If A is m x n and B is n x p, result is m x p.

    Time: O(m * n * p)
    """
    validate_matrix(first)
    validate_matrix(second)

    first_rows = len(first)
    first_columns = len(first[0])
    second_rows = len(second)
    second_columns = len(second[0])

    if first_columns != second_rows:
        raise ValueError(
            "Matrix dimensions are incompatible for multiplication."
        )

    result = [
        [0] * second_columns
        for _ in range(first_rows)
    ]

    for row in range(first_rows):
        for shared in range(first_columns):
            first_value = first[row][shared]

            for column in range(second_columns):
                result[row][column] += (
                    first_value * second[shared][column]
                )

    return result


def identity_matrix(size: int) -> list[list[int]]:
    """Create an identity matrix."""
    if size <= 0:
        raise ValueError("Size must be positive.")

    return [
        [1 if row == column else 0 for column in range(size)]
        for row in range(size)
    ]


def matrix_power(matrix: list[list[Number]], exponent: int) -> list[list[Number]]:
    """
    Compute A^exponent using binary exponentiation.

    Time: O(n^3 log exponent) using classical multiplication.
    """
    validate_square_matrix(matrix)

    if exponent < 0:
        raise ValueError("Exponent must be non-negative.")

    result = identity_matrix(len(matrix))
    base = clone_matrix(matrix)

    while exponent:
        if exponent & 1:
            result = multiply_matrices(result, base)

        base = multiply_matrices(base, base)
        exponent >>= 1

    return result


# ---------------------------------------------------------------------------
# Maximum submatrix sum
# ---------------------------------------------------------------------------

def maximum_subarray_sum(values: list[Number]) -> Number:
    """Kadane's algorithm for one-dimensional maximum subarray sum."""
    if not values:
        raise ValueError("Input cannot be empty.")

    current = values[0]
    best = values[0]

    for value in values[1:]:
        current = max(value, current + value)
        best = max(best, current)

    return best


def maximum_submatrix_sum(matrix: list[list[Number]]) -> Number:
    """
    Find the maximum sum of any rectangular submatrix.

    Compress pairs of rows into a one-dimensional array and apply
    Kadane's algorithm.

    Complexity: O(rows^2 * columns)
    """
    validate_matrix(matrix)

    rows = len(matrix)
    columns = len(matrix[0])

    best = None

    for top in range(rows):
        compressed = [0] * columns

        for bottom in range(top, rows):
            for column in range(columns):
                compressed[column] += matrix[bottom][column]

            candidate = maximum_subarray_sum(compressed)

            if best is None or candidate > best:
                best = candidate

    assert best is not None
    return best


# ---------------------------------------------------------------------------
# Largest rectangle of ones
# ---------------------------------------------------------------------------

def largest_rectangle_histogram(heights: list[int]) -> int:
    """
    Largest rectangle in a histogram using a monotonic stack.

    Complexity: O(n).
    """
    stack: list[int] = []
    best = 0

    extended = heights + [0]

    for index, height in enumerate(extended):
        while stack and extended[stack[-1]] > height:
            top_index = stack.pop()
            rectangle_height = extended[top_index]

            left_boundary = stack[-1] if stack else -1
            width = index - left_boundary - 1

            best = max(best, rectangle_height * width)

        stack.append(index)

    return best


def largest_rectangle_of_ones(matrix: list[list[int]]) -> int:
    """
    Find the largest all-1 rectangular area in a binary matrix.

    Each row becomes the base of a histogram.
    """
    validate_matrix(matrix)

    if any(value not in (0, 1) for row in matrix for value in row):
        raise ValueError("Matrix must contain only 0 and 1.")

    columns = len(matrix[0])
    heights = [0] * columns
    best = 0

    for row in matrix:
        for column in range(columns):
            if row[column] == 1:
                heights[column] += 1
            else:
                heights[column] = 0

        best = max(best, largest_rectangle_histogram(heights))

    return best


# ---------------------------------------------------------------------------
# Grid traversal and graph-style problems
# ---------------------------------------------------------------------------

DIRECTIONS_4 = (
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
)

DIRECTIONS_8 = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


def validate_binary_grid(grid: list[list[int]]) -> None:
    validate_matrix(grid)

    if any(value not in (0, 1) for row in grid for value in row):
        raise ValueError("Grid must contain only 0 and 1.")


def flood_fill(
    grid: list[list[int]],
    start_row: int,
    start_column: int,
    replacement: int,
) -> list[list[int]]:
    """
    Replace a connected region using breadth-first search.

    This version returns a copy instead of modifying the input.
    """
    validate_matrix(grid)

    rows = len(grid)
    columns = len(grid[0])

    if not (
        0 <= start_row < rows
        and 0 <= start_column < columns
    ):
        raise IndexError("Starting position is outside the grid.")

    result = clone_matrix(grid)
    original = result[start_row][start_column]

    if original == replacement:
        return result

    queue = deque([(start_row, start_column)])
    result[start_row][start_column] = replacement

    while queue:
        row, column = queue.popleft()

        for row_delta, column_delta in DIRECTIONS_4:
            next_row = row + row_delta
            next_column = column + column_delta

            if not (
                0 <= next_row < rows
                and 0 <= next_column < columns
            ):
                continue

            if result[next_row][next_column] != original:
                continue

            result[next_row][next_column] = replacement
            queue.append((next_row, next_column))

    return result


def count_islands(grid: list[list[int]]) -> int:
    """
    Count connected groups of 1s using four-directional adjacency.

    Complexity: O(rows * columns).
    """
    validate_binary_grid(grid)

    rows = len(grid)
    columns = len(grid[0])
    visited = [[False] * columns for _ in range(rows)]

    island_count = 0

    for row in range(rows):
        for column in range(columns):
            if grid[row][column] == 0 or visited[row][column]:
                continue

            island_count += 1
            queue = deque([(row, column)])
            visited[row][column] = True

            while queue:
                current_row, current_column = queue.popleft()

                for row_delta, column_delta in DIRECTIONS_4:
                    next_row = current_row + row_delta
                    next_column = current_column + column_delta

                    if not (
                        0 <= next_row < rows
                        and 0 <= next_column < columns
                    ):
                        continue

                    if visited[next_row][next_column]:
                        continue

                    if grid[next_row][next_column] == 0:
                        continue

                    visited[next_row][next_column] = True
                    queue.append((next_row, next_column))

    return island_count


def largest_island_area(grid: list[list[int]]) -> int:
    """Return the largest four-directionally connected island."""
    validate_binary_grid(grid)

    rows = len(grid)
    columns = len(grid[0])
    visited = [[False] * columns for _ in range(rows)]
    largest = 0

    for row in range(rows):
        for column in range(columns):
            if grid[row][column] == 0 or visited[row][column]:
                continue

            area = 0
            queue = deque([(row, column)])
            visited[row][column] = True

            while queue:
                current_row, current_column = queue.popleft()
                area += 1

                for row_delta, column_delta in DIRECTIONS_4:
                    next_row = current_row + row_delta
                    next_column = current_column + column_delta

                    if not (
                        0 <= next_row < rows
                        and 0 <= next_column < columns
                    ):
                        continue

                    if (
                        grid[next_row][next_column] == 1
                        and not visited[next_row][next_column]
                    ):
                        visited[next_row][next_column] = True
                        queue.append((next_row, next_column))

            largest = max(largest, area)

    return largest


def shortest_path_binary_grid(
    grid: list[list[int]],
    start: tuple[int, int],
    goal: tuple[int, int],
) -> int:
    """
    Shortest path through zero-valued cells.

    Movement uses four directions and every move has unit cost.
    BFS therefore finds the shortest path.

    Returns -1 if no path exists.
    """
    validate_binary_grid(grid)

    rows = len(grid)
    columns = len(grid[0])

    for position in (start, goal):
        row, column = position

        if not (0 <= row < rows and 0 <= column < columns):
            raise IndexError("Start or goal lies outside the grid.")

    if grid[start[0]][start[1]] != 0 or grid[goal[0]][goal[1]] != 0:
        return -1

    queue = deque([(start[0], start[1], 0)])
    visited = {start}

    while queue:
        row, column, distance = queue.popleft()

        if (row, column) == goal:
            return distance

        for row_delta, column_delta in DIRECTIONS_4:
            next_position = (
                row + row_delta,
                column + column_delta,
            )

            next_row, next_column = next_position

            if not (
                0 <= next_row < rows
                and 0 <= next_column < columns
            ):
                continue

            if next_position in visited:
                continue

            if grid[next_row][next_column] != 0:
                continue

            visited.add(next_position)
            queue.append((next_row, next_column, distance + 1))

    return -1


def minimum_cost_grid_path(
    costs: list[list[int]],
) -> Number:
    """
    Dynamic programming for a path from the top-left to bottom-right.

    Only right and down movement is allowed.
    """
    validate_matrix(costs)

    rows = len(costs)
    columns = len(costs[0])

    dp = [[0] * columns for _ in range(rows)]
    dp[0][0] = costs[0][0]

    for column in range(1, columns):
        dp[0][column] = dp[0][column - 1] + costs[0][column]

    for row in range(1, rows):
        dp[row][0] = dp[row - 1][0] + costs[row][0]

    for row in range(1, rows):
        for column in range(1, columns):
            dp[row][column] = costs[row][column] + min(
                dp[row - 1][column],
                dp[row][column - 1],
            )

    return dp[-1][-1]


# ---------------------------------------------------------------------------
# Sudoku validation
# ---------------------------------------------------------------------------

def is_valid_sudoku(board: list[list[str]]) -> bool:
    """
    Validate a 9x9 Sudoku board.

    Empty cells use ".".
    Each digit must occur at most once in every row, column and 3x3 box.
    """
    if len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("Sudoku board must be exactly 9x9.")

    valid_symbols = set("123456789.")

    if any(cell not in valid_symbols for row in board for cell in row):
        raise ValueError("Sudoku contains an invalid symbol.")

    rows = [set() for _ in range(9)]
    columns = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]

    for row in range(9):
        for column in range(9):
            value = board[row][column]

            if value == ".":
                continue

            box = (row // 3) * 3 + column // 3

            if value in rows[row]:
                return False

            if value in columns[column]:
                return False

            if value in boxes[box]:
                return False

            rows[row].add(value)
            columns[column].add(value)
            boxes[box].add(value)

    return True


# ---------------------------------------------------------------------------
# Sparse matrices
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SparseMatrix:
    """
    Coordinate-list sparse representation.

    Only non-zero elements are stored.
    """
    rows: int
    columns: int
    values: dict[tuple[int, int], Number]

    @classmethod
    def from_dense(cls, matrix: list[list[Number]]) -> "SparseMatrix":
        validate_matrix(matrix)

        values = {}

        for row, matrix_row in enumerate(matrix):
            for column, value in enumerate(matrix_row):
                if value != 0:
                    values[(row, column)] = value

        return cls(len(matrix), len(matrix[0]), values)

    def get(self, row: int, column: int) -> Number:
        self._validate_position(row, column)
        return self.values.get((row, column), 0)

    def set(self, row: int, column: int, value: Number) -> None:
        self._validate_position(row, column)

        if value == 0:
            self.values.pop((row, column), None)
        else:
            self.values[(row, column)] = value

    def _validate_position(self, row: int, column: int) -> None:
        if not (
            0 <= row < self.rows
            and 0 <= column < self.columns
        ):
            raise IndexError("Sparse-matrix position is invalid.")

    def to_dense(self) -> list[list[Number]]:
        result = [[0] * self.columns for _ in range(self.rows)]

        for (row, column), value in self.values.items():
            result[row][column] = value

        return result

    @property
    def non_zero_count(self) -> int:
        return len(self.values)

    @property
    def density(self) -> float:
        return self.non_zero_count / (self.rows * self.columns)


# ---------------------------------------------------------------------------
# Advanced matrix algorithm: recursive multiplication
# ---------------------------------------------------------------------------

def add_matrices(
    first: list[list[Number]],
    second: list[list[Number]],
) -> list[list[Number]]:
    validate_same_shape(first, second)

    return [
        [
            first[row][column] + second[row][column]
            for column in range(len(first[0]))
        ]
        for row in range(len(first))
    ]


def subtract_matrices(
    first: list[list[Number]],
    second: list[list[Number]],
) -> list[list[Number]]:
    validate_same_shape(first, second)

    return [
        [
            first[row][column] - second[row][column]
            for column in range(len(first[0]))
        ]
        for row in range(len(first))
    ]


def next_power_of_two(value: int) -> int:
    """Return the smallest power of two greater than or equal to value."""
    if value <= 0:
        raise ValueError("Value must be positive.")

    result = 1

    while result < value:
        result <<= 1

    return result


def pad_matrix(
    matrix: list[list[Number]],
    size: int,
) -> list[list[Number]]:
    validate_matrix(matrix)

    if size < max(len(matrix), len(matrix[0])):
        raise ValueError("Padding size is too small.")

    return [
        row[:] + [0] * (size - len(row))
        for row in matrix
    ] + [
        [0] * size
        for _ in range(size - len(matrix))
    ]


def trim_matrix(
    matrix: list[list[Number]],
    rows: int,
    columns: int,
) -> list[list[Number]]:
    return [
        row[:columns]
        for row in matrix[:rows]
    ]


def strassen_multiply(
    first: list[list[Number]],
    second: list[list[Number]],
) -> list[list[Number]]:
    """
    Strassen matrix multiplication for square matrices.

    The implementation pads non-power-of-two dimensions to the next
    power of two, performs recursive multiplication, then trims the result.

    The recurrence is approximately O(n^log2(7)), about O(n^2.807),
    although practical performance depends heavily on constant factors.
    """
    validate_matrix(first)
    validate_matrix(second)

    if len(first[0]) != len(second):
        raise ValueError(
            "Matrix dimensions are incompatible for multiplication."
        )

    original_rows = len(first)
    original_columns = len(second[0])
    shared_dimension = len(first[0])

    size = next_power_of_two(
        max(original_rows, original_columns, shared_dimension)
    )

    padded_first = pad_matrix(first, size)
    padded_second = pad_matrix(second, size)

    def recursive_multiply(
        left: list[list[Number]],
        right: list[list[Number]],
    ) -> list[list[Number]]:
        n = len(left)

        if n <= 2:
            return multiply_matrices(left, right)

        half = n // 2

        a11 = [row[:half] for row in left[:half]]
        a12 = [row[half:] for row in left[:half]]
        a21 = [row[:half] for row in left[half:]]
        a22 = [row[half:] for row in left[half:]]

        b11 = [row[:half] for row in right[:half]]
        b12 = [row[half:] for row in right[:half]]
        b21 = [row[:half] for row in right[half:]]
        b22 = [row[half:] for row in right[half:]]

        p1 = recursive_multiply(a11, subtract_matrices(b12, b22))
        p2 = recursive_multiply(add_matrices(a11, a12), b22)
        p3 = recursive_multiply(add_matrices(a21, a22), b11)
        p4 = recursive_multiply(a22, subtract_matrices(b21, b11))
        p5 = recursive_multiply(
            add_matrices(a11, a22),
            add_matrices(b11, b22),
        )
        p6 = recursive_multiply(
            subtract_matrices(a12, a22),
            add_matrices(b21, b22),
        )
        p7 = recursive_multiply(
            subtract_matrices(a11, a21),
            add_matrices(b11, b12),
        )

        c11 = add_matrices(
            subtract_matrices(add_matrices(p5, p4), p2),
            p6,
        )

        c12 = add_matrices(p1, p2)
        c21 = add_matrices(p3, p4)

        c22 = add_matrices(
            subtract_matrices(add_matrices(p5, p1), p3),
            p7,
        )

        result = []

        for row in range(half):
            result.append(c11[row] + c12[row])

        for row in range(half):
            result.append(c21[row] + c22[row])

        return result

    padded_result = recursive_multiply(padded_first, padded_second)

    return trim_matrix(
        padded_result,
        original_rows,
        original_columns,
    )


# ---------------------------------------------------------------------------
# Testing utilities
# ---------------------------------------------------------------------------

def assert_equal(actual, expected, description: str) -> None:
    """Small educational assertion helper."""
    if actual != expected:
        raise AssertionError(
            f"{description}\nExpected: {expected}\nActual: {actual}"
        )


def run_tests() -> None:
    """Run a representative collection of correctness tests."""
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    assert_equal(
        transpose(matrix),
        [
            [1, 4, 7],
            [2, 5, 8],
            [3, 6, 9],
        ],
        "Transpose failed.",
    )

    assert_equal(
        rotate_90_clockwise(matrix),
        [
            [7, 4, 1],
            [8, 5, 2],
            [9, 6, 3],
        ],
        "Clockwise rotation failed.",
    )

    assert_equal(
        rotate_90_counterclockwise(matrix),
        [
            [3, 6, 9],
            [2, 5, 8],
            [1, 4, 7],
        ],
        "Counterclockwise rotation failed.",
    )

    assert_equal(
        spiral_traversal(matrix),
        [1, 2, 3, 6, 9, 8, 7, 4, 5],
        "Spiral traversal failed.",
    )

    sorted_matrix = [
        [1, 4, 7, 11],
        [2, 5, 8, 12],
        [3, 6, 9, 16],
        [10, 13, 14, 17],
    ]

    assert_equal(
        search_row_column_sorted_matrix(sorted_matrix, 9),
        (2, 2),
        "Sorted-matrix search failed.",
    )

    globally_sorted = [
        [1, 3, 5],
        [7, 9, 11],
        [13, 15, 17],
    ]

    assert_equal(
        search_fully_sorted_matrix(globally_sorted, 15),
        (2, 1),
        "Fully sorted matrix search failed.",
    )

    prefix = build_prefix_sum([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ])

    assert_equal(
        rectangle_sum(prefix, 1, 1, 2, 2),
        28,
        "Rectangle sum failed.",
    )

    assert_equal(
        multiply_matrices(
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
        ),
        [[19, 22], [43, 50]],
        "Matrix multiplication failed.",
    )

    assert_equal(
        matrix_power([[1, 1], [1, 0]], 5),
        [[8, 5], [5, 3]],
        "Matrix exponentiation failed.",
    )

    binary_grid = [
        [0, 1, 0, 0],
        [0, 1, 0, 1],
        [0, 0, 0, 1],
        [1, 1, 0, 0],
    ]

    assert_equal(
        shortest_path_binary_grid(binary_grid, (0, 0), (3, 3)),
        6,
        "Shortest-path calculation failed.",
    )

    assert_equal(
        count_islands([
            [1, 1, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 1],
        ]),
        2,
        "Island counting failed.",
    )

    assert_equal(
        largest_rectangle_of_ones([
            [1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1],
        ]),
        9,
        "Largest rectangle of ones failed.",
    )

    dense = [
        [0, 0, 3],
        [0, 0, 0],
        [5, 0, 0],
    ]

    sparse = SparseMatrix.from_dense(dense)

    assert_equal(
        sparse.non_zero_count,
        2,
        "Sparse non-zero count failed.",
    )

    assert_equal(
        sparse.to_dense(),
        dense,
        "Sparse conversion failed.",
    )

    assert_equal(
        strassen_multiply(
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
        ),
        [[19, 22], [43, 50]],
        "Strassen multiplication failed.",
    )


# ---------------------------------------------------------------------------
# Demonstration program
# ---------------------------------------------------------------------------

def demonstrate() -> None:
    """Run the educational examples in a logical order."""

    print("=" * 80)
    print("ADVANCED MATRIX PROBLEMS")
    print("=" * 80)

    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
    ]

    print_matrix(matrix, "Original 3 x 4 matrix")

    print("\nRow-major traversal:")
    print(row_major_traversal(matrix))

    print_matrix(
        transpose(matrix),
        "Transpose: 4 x 3",
    )

    print("\nClockwise rotation of a rectangular matrix:")
    print_matrix(rotate_90_clockwise(matrix))

    print("\nCounterclockwise rotation of a rectangular matrix:")
    print_matrix(rotate_90_counterclockwise(matrix))

    square = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    print_matrix(square, "Square matrix before in-place rotation")
    rotate_square_in_place_clockwise(square)
    print_matrix(square, "Square matrix after 90-degree clockwise rotation")

    print("\nBoundary traversal:")
    print(boundary_traversal(matrix))

    print("\nSpiral traversal:")
    print(spiral_traversal(matrix))

    print("\nDiagonal traversal:")
    for index, diagonal in enumerate(diagonal_traversal(matrix)):
        print(f"Diagonal {index}: {diagonal}")

    sorted_matrix = [
        [1, 4, 7, 10],
        [2, 5, 8, 12],
        [3, 6, 9, 16],
        [11, 13, 14, 20],
    ]

    print_matrix(sorted_matrix, "Row-and-column sorted matrix")

    target = 14

    print(
        f"\nSearching for {target} with binary search per row:",
        search_sorted_matrix_binary(sorted_matrix, target),
    )

    print(
        f"Searching for {target} with staircase search:",
        search_row_column_sorted_matrix(sorted_matrix, target),
    )

    fully_sorted = [
        [1, 3, 5],
        [7, 9, 11],
        [13, 15, 17],
    ]

    print_matrix(
        fully_sorted,
        "Globally sorted matrix",
    )

    print(
        "\nBinary search across flattened logical positions:",
        search_fully_sorted_matrix(fully_sorted, 15),
    )

    numeric_matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
    ]

    prefix = build_prefix_sum(numeric_matrix)

    print_matrix(
        prefix,
        "2D prefix-sum matrix with sentinel row and column",
    )

    print(
        "\nRectangle sum for rows 1..2 and columns 1..3:",
        rectangle_sum(prefix, 1, 1, 2, 3),
    )

    difference = build_difference_matrix(5, 6)

    difference_rectangle_update(
        difference,
        top=1,
        left=1,
        bottom=3,
        right=4,
        value=10,
    )

    difference_rectangle_update(
        difference,
        top=0,
        left=2,
        bottom=2,
        right=5,
        value=5,
    )

    print_matrix(
        materialize_difference_matrix(difference),
        "Materialized 2D difference updates",
    )

    print("\nClassical matrix multiplication:")

    first = [
        [1, 2],
        [3, 4],
    ]

    second = [
        [5, 6],
        [7, 8],
    ]

    print_matrix(
        multiply_matrices(first, second),
        "A x B",
    )

    print("\nMatrix exponentiation:")
    print_matrix(
        matrix_power(
            [
                [1, 1],
                [1, 0],
            ],
            10,
        ),
        "Fibonacci transition matrix raised to the 10th power",
    )

    weighted_matrix = [
        [2, -1, 3],
        [-4, 5, -2],
        [1, 2, 6],
    ]

    print(
        "\nMaximum rectangular submatrix sum:",
        maximum_submatrix_sum(weighted_matrix),
    )

    binary_matrix = [
        [1, 0, 1, 1, 1],
        [1, 0, 1, 1, 1],
        [1, 1, 1, 1, 1],
    ]

    print_matrix(
        binary_matrix,
        "Binary matrix",
    )

    print(
        "\nLargest all-1 rectangle area:",
        largest_rectangle_of_ones(binary_matrix),
    )

    grid = [
        [1, 1, 0, 0, 0],
        [1, 0, 0, 1, 1],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 0, 0],
    ]

    print_matrix(grid, "Island grid")

    print("\nNumber of islands:", count_islands(grid))
    print("Largest island area:", largest_island_area(grid))

    flood_source = [
        [1, 1, 1, 2],
        [1, 1, 0, 2],
        [1, 0, 0, 2],
    ]

    print_matrix(
        flood_fill(flood_source, 0, 0, 9),
        "Flood fill from (0, 0)",
    )

    path_grid = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
    ]

    print_matrix(path_grid, "Binary path grid")

    print(
        "\nShortest path length:",
        shortest_path_binary_grid(
            path_grid,
            (0, 0),
            (3, 4),
        ),
    )

    cost_grid = [
        [1, 3, 1, 2],
        [1, 5, 1, 1],
        [4, 2, 1, 3],
    ]

    print_matrix(cost_grid, "Grid of movement costs")

    print(
        "\nMinimum top-left to bottom-right cost:",
        minimum_cost_grid_path(cost_grid),
    )

    sudoku = [
        list("53..7...."),
        list("6..195..."),
        list(".98....6."),
        list("8...6...3"),
        list("4..8.3..1"),
        list("7...2...6"),
        list(".6....28."),
        list("...419..5"),
        list("....8..79"),
    ]

    print("\nValid Sudoku board:", is_valid_sudoku(sudoku))

    sparse = SparseMatrix.from_dense([
        [0, 0, 0, 7],
        [0, 0, 0, 0],
        [0, 3, 0, 0],
        [0, 0, 0, 0],
    ])

    print("\nSparse matrix:")
    print(f"Dimensions: {sparse.rows} x {sparse.columns}")
    print(f"Non-zero values: {sparse.non_zero_count}")
    print(f"Density: {sparse.density:.2%}")
    print(f"Value at (2, 1): {sparse.get(2, 1)}")

    print("\nStrassen multiplication:")
    print_matrix(
        strassen_multiply(first, second),
        "Strassen result",
    )

    print("\nRunning correctness tests...")
    run_tests()
    print("All tests passed.")


if __name__ == "__main__":
    demonstrate()
