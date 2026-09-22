"""
Matrix Fundamentals
===================

A comprehensive standalone study program covering:
- Matrix terminology and representation
- Rows, columns, dimensions, indices, elements
- Construction and validation
- Traversal patterns
- Input and output
- Updating and insertion concepts
- Addition, subtraction, scalar multiplication
- Matrix multiplication
- Transpose
- Symmetry
- Diagonal operations
- Row/column operations
- Searching
- Rotation
- Boundary and spiral traversal
- Determinant and inverse for small square matrices
- Gaussian elimination
- Sparse matrices
- Prefix sums
- Matrix transformations
- Complexity analysis
- Validation, errors, and edge cases

Run:
    python matrix_fundamentals.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple
import math
import random


Number = float | int


# ---------------------------------------------------------------------------
# 1. BASIC REPRESENTATION
# ---------------------------------------------------------------------------

Matrix = List[List[Number]]


def print_matrix(matrix: Matrix, title: Optional[str] = None) -> None:
    """Print a matrix in a readable rectangular form."""
    if title:
        print(f"\n{title}")

    if not matrix:
        print("[]")
        return

    for row in matrix:
        print(" ".join(f"{value:8}" for value in row))


def matrix_shape(matrix: Matrix) -> Tuple[int, int]:
    """
    Return (rows, columns).

    A matrix is rectangular when every row has the same number of columns.
    """
    if not matrix:
        return 0, 0

    columns = len(matrix[0])

    if any(len(row) != columns for row in matrix):
        raise ValueError("Matrix must be rectangular.")

    return len(matrix), columns


def validate_matrix(matrix: Matrix, allow_empty: bool = True) -> None:
    """Validate that a nested list is a proper rectangular matrix."""
    if not isinstance(matrix, list):
        raise TypeError("Matrix must be represented by a list of rows.")

    if not matrix:
        if allow_empty:
            return
        raise ValueError("Matrix cannot be empty.")

    if not all(isinstance(row, list) for row in matrix):
        raise TypeError("Every matrix row must be a list.")

    columns = len(matrix[0])

    if any(len(row) != columns for row in matrix):
        raise ValueError("All rows must contain the same number of elements.")


def create_matrix(rows: int, columns: int, fill: Number = 0) -> Matrix:
    """
    Create a matrix safely.

    Each row is created independently. Using [[fill] * columns] repeatedly
    can cause aliasing when the row contains mutable objects.
    """
    if rows < 0 or columns < 0:
        raise ValueError("Dimensions cannot be negative.")

    return [[fill for _ in range(columns)] for _ in range(rows)]


def identity_matrix(size: int) -> Matrix:
    """Create an n x n identity matrix."""
    if size < 0:
        raise ValueError("Size cannot be negative.")

    matrix = create_matrix(size, size)

    for i in range(size):
        matrix[i][i] = 1

    return matrix


# ---------------------------------------------------------------------------
# 2. ELEMENT ACCESS AND UPDATES
# ---------------------------------------------------------------------------

def get_element(matrix: Matrix, row: int, column: int) -> Number:
    """Access matrix[row][column] using zero-based indexing."""
    validate_matrix(matrix, allow_empty=False)

    rows, columns = matrix_shape(matrix)

    if not 0 <= row < rows or not 0 <= column < columns:
        raise IndexError("Matrix index is outside the valid range.")

    return matrix[row][column]


def set_element(matrix: Matrix, row: int, column: int, value: Number) -> None:
    """Update one matrix element."""
    validate_matrix(matrix, allow_empty=False)

    rows, columns = matrix_shape(matrix)

    if not 0 <= row < rows or not 0 <= column < columns:
        raise IndexError("Matrix index is outside the valid range.")

    matrix[row][column] = value


def insert_row(matrix: Matrix, index: int, row: Sequence[Number]) -> None:
    """
    Insert a row.

    Inserting into a two-dimensional array usually means creating a new
    rectangular structure or shifting existing rows.
    """
    validate_matrix(matrix)

    if matrix:
        columns = len(matrix[0])
        if len(row) != columns:
            raise ValueError("Inserted row has an incompatible length.")
    elif index not in (0,):
        raise IndexError("The only valid insertion index for an empty matrix is 0.")

    if not 0 <= index <= len(matrix):
        raise IndexError("Row insertion index out of range.")

    matrix.insert(index, list(row))


def insert_column(matrix: Matrix, index: int, column: Sequence[Number]) -> None:
    """Insert one value into every row at the specified column position."""
    validate_matrix(matrix, allow_empty=False)

    rows, columns = matrix_shape(matrix)

    if len(column) != rows:
        raise ValueError("Inserted column must contain one value per row.")

    if not 0 <= index <= columns:
        raise IndexError("Column insertion index out of range.")

    for row_number, row in enumerate(matrix):
        row.insert(index, column[row_number])


# ---------------------------------------------------------------------------
# 3. TRAVERSAL
# ---------------------------------------------------------------------------

def row_major_traversal(matrix: Matrix) -> List[Number]:
    """Visit every element from left to right, top to bottom."""
    validate_matrix(matrix)
    return [value for row in matrix for value in row]


def column_major_traversal(matrix: Matrix) -> List[Number]:
    """Visit every element column by column."""
    validate_matrix(matrix)

    if not matrix:
        return []

    rows, columns = matrix_shape(matrix)

    return [
        matrix[row][column]
        for column in range(columns)
        for row in range(rows)
    ]


def diagonal_traversal(matrix: Matrix) -> List[Number]:
    """
    Return the main diagonal where it exists.

    For a rectangular matrix, traversal stops at min(rows, columns).
    """
    validate_matrix(matrix)

    if not matrix:
        return []

    rows, columns = matrix_shape(matrix)

    return [matrix[i][i] for i in range(min(rows, columns))]


def anti_diagonal_traversal(matrix: Matrix) -> List[Number]:
    """Traverse the top-right to bottom-left diagonal."""
    validate_matrix(matrix)

    if not matrix:
        return []

    rows, columns = matrix_shape(matrix)

    return [
        matrix[i][columns - 1 - i]
        for i in range(min(rows, columns))
    ]


def boundary_traversal(matrix: Matrix) -> List[Number]:
    """Traverse the outer boundary without duplicating corners."""
    validate_matrix(matrix)

    if not matrix:
        return []

    rows, columns = matrix_shape(matrix)

    if rows == 1:
        return matrix[0][:]

    if columns == 1:
        return [matrix[i][0] for i in range(rows)]

    result = []

    result.extend(matrix[0])

    for row in range(1, rows - 1):
        result.append(matrix[row][columns - 1])

    result.extend(reversed(matrix[rows - 1]))

    for row in range(rows - 2, 0, -1):
        result.append(matrix[row][0])

    return result


def spiral_traversal(matrix: Matrix) -> List[Number]:
    """Return matrix elements in clockwise spiral order."""
    validate_matrix(matrix)

    if not matrix:
        return []

    rows, columns = matrix_shape(matrix)

    top = 0
    bottom = rows - 1
    left = 0
    right = columns - 1
    result = []

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


# ---------------------------------------------------------------------------
# 4. BASIC MATRIX OPERATIONS
# ---------------------------------------------------------------------------

def add_matrices(a: Matrix, b: Matrix) -> Matrix:
    """Element-wise matrix addition."""
    validate_matrix(a)
    validate_matrix(b)

    if matrix_shape(a) != matrix_shape(b):
        raise ValueError("Matrices must have identical dimensions.")

    return [
        [a[i][j] + b[i][j] for j in range(len(a[0]))]
        for i in range(len(a))
    ]


def subtract_matrices(a: Matrix, b: Matrix) -> Matrix:
    """Element-wise matrix subtraction."""
    validate_matrix(a)
    validate_matrix(b)

    if matrix_shape(a) != matrix_shape(b):
        raise ValueError("Matrices must have identical dimensions.")

    return [
        [a[i][j] - b[i][j] for j in range(len(a[0]))]
        for i in range(len(a))
    ]


def scalar_multiply(matrix: Matrix, scalar: Number) -> Matrix:
    """Multiply every matrix element by one scalar."""
    validate_matrix(matrix)

    return [
        [value * scalar for value in row]
        for row in matrix
    ]


def matrix_multiply(a: Matrix, b: Matrix) -> Matrix:
    """
    Standard matrix multiplication.

    If A is m x n and B is n x p, the result is m x p.
    Each result element is a dot product of a row of A and a column of B.
    """
    validate_matrix(a)
    validate_matrix(b)

    if not a or not b:
        return []

    a_rows, a_columns = matrix_shape(a)
    b_rows, b_columns = matrix_shape(b)

    if a_columns != b_rows:
        raise ValueError(
            "Matrix multiplication requires A's column count "
            "to equal B's row count."
        )

    result = create_matrix(a_rows, b_columns)

    for i in range(a_rows):
        for j in range(b_columns):
            total = 0
            for k in range(a_columns):
                total += a[i][k] * b[k][j]
            result[i][j] = total

    return result


def transpose(matrix: Matrix) -> Matrix:
    """Exchange rows and columns."""
    validate_matrix(matrix)

    if not matrix:
        return []

    rows, columns = matrix_shape(matrix)

    return [
        [matrix[row][column] for row in range(rows)]
        for column in range(columns)
    ]


# ---------------------------------------------------------------------------
# 5. DIAGONALS, SYMMETRY, AND ROW/COLUMN OPERATIONS
# ---------------------------------------------------------------------------

def is_square(matrix: Matrix) -> bool:
    """Check whether rows equal columns."""
    validate_matrix(matrix)

    rows, columns = matrix_shape(matrix)
    return rows == columns


def is_symmetric(matrix: Matrix) -> bool:
    """
    A real square matrix is symmetric when A[i][j] == A[j][i].
    """
    validate_matrix(matrix)

    if not is_square(matrix):
        return False

    size = len(matrix)

    for i in range(size):
        for j in range(i + 1, size):
            if matrix[i][j] != matrix[j][i]:
                return False

    return True


def main_diagonal_sum(matrix: Matrix) -> Number:
    """Calculate the main diagonal sum."""
    if not is_square(matrix):
        raise ValueError("Diagonal sum in this function requires a square matrix.")

    return sum(matrix[i][i] for i in range(len(matrix)))


def secondary_diagonal_sum(matrix: Matrix) -> Number:
    """Calculate the secondary diagonal sum."""
    if not is_square(matrix):
        raise ValueError("Diagonal sum requires a square matrix.")

    size = len(matrix)

    return sum(matrix[i][size - 1 - i] for i in range(size))


def row_sums(matrix: Matrix) -> List[Number]:
    """Return the sum of every row."""
    validate_matrix(matrix)
    return [sum(row) for row in matrix]


def column_sums(matrix: Matrix) -> List[Number]:
    """Return the sum of every column."""
    validate_matrix(matrix)

    if not matrix:
        return []

    rows, columns = matrix_shape(matrix)

    return [
        sum(matrix[row][column] for row in range(rows))
        for column in range(columns)
    ]


def swap_rows(matrix: Matrix, first: int, second: int) -> None:
    """Swap two rows in place."""
    validate_matrix(matrix, allow_empty=False)

    rows, _ = matrix_shape(matrix)

    if not 0 <= first < rows or not 0 <= second < rows:
        raise IndexError("Row index out of range.")

    matrix[first], matrix[second] = matrix[second], matrix[first]


def swap_columns(matrix: Matrix, first: int, second: int) -> None:
    """Swap two columns in place."""
    validate_matrix(matrix, allow_empty=False)

    rows, columns = matrix_shape(matrix)

    if not 0 <= first < columns or not 0 <= second < columns:
        raise IndexError("Column index out of range.")

    for row in range(rows):
        matrix[row][first], matrix[row][second] = (
            matrix[row][second],
            matrix[row][first],
        )


# ---------------------------------------------------------------------------
# 6. SEARCHING
# ---------------------------------------------------------------------------

def find_all(matrix: Matrix, target: Number) -> List[Tuple[int, int]]:
    """Find every coordinate containing target."""
    validate_matrix(matrix)

    result = []

    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if value == target:
                result.append((row_index, column_index))

    return result


def find_maximum(matrix: Matrix) -> Tuple[Number, Tuple[int, int]]:
    """Return maximum value and its first coordinate."""
    validate_matrix(matrix, allow_empty=False)

    maximum = matrix[0][0]
    position = (0, 0)

    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value > maximum:
                maximum = value
                position = (i, j)

    return maximum, position


# ---------------------------------------------------------------------------
# 7. ROTATIONS
# ---------------------------------------------------------------------------

def rotate_clockwise(matrix: Matrix) -> Matrix:
    """
    Rotate a matrix 90 degrees clockwise.

    The operation works for rectangular matrices as well.
    """
    return [list(row) for row in zip(*reversed(matrix))]


def rotate_counterclockwise(matrix: Matrix) -> Matrix:
    """Rotate a matrix 90 degrees counterclockwise."""
    return [list(row) for row in zip(*matrix)][::-1]


def reverse_rows(matrix: Matrix) -> Matrix:
    """Flip the matrix horizontally."""
    return [list(reversed(row)) for row in matrix]


def reverse_columns(matrix: Matrix) -> Matrix:
    """Flip the matrix vertically."""
    return list(reversed(matrix))


# ---------------------------------------------------------------------------
# 8. DETERMINANT
# ---------------------------------------------------------------------------

def determinant(matrix: Matrix) -> Number:
    """
    Calculate a determinant using recursive cofactor expansion.

    This implementation is intended for learning and small matrices.
    Naive recursive determinant calculation becomes expensive quickly.
    """
    validate_matrix(matrix)

    if not is_square(matrix):
        raise ValueError("Determinant requires a square matrix.")

    size = len(matrix)

    if size == 0:
        return 1

    if size == 1:
        return matrix[0][0]

    if size == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    result = 0

    for column in range(size):
        minor = [
            [
                matrix[row][other_column]
                for other_column in range(size)
                if other_column != column
            ]
            for row in range(1, size)
        ]

        sign = -1 if column % 2 else 1
        result += sign * matrix[0][column] * determinant(minor)

    return result


# ---------------------------------------------------------------------------
# 9. GAUSSIAN ELIMINATION AND LINEAR SYSTEMS
# ---------------------------------------------------------------------------

def gaussian_elimination(matrix: Matrix, tolerance: float = 1e-10) -> Matrix:
    """
    Convert a matrix into reduced row-echelon form.

    Partial pivoting improves numerical stability by choosing the largest
    available pivot in the current column.
    """
    validate_matrix(matrix)

    if not matrix:
        return []

    result = [[float(value) for value in row] for row in matrix]
    rows, columns = matrix_shape(result)

    pivot_row = 0

    for pivot_column in range(columns):
        if pivot_row >= rows:
            break

        best_row = max(
            range(pivot_row, rows),
            key=lambda row: abs(result[row][pivot_column]),
        )

        if abs(result[best_row][pivot_column]) <= tolerance:
            continue

        result[pivot_row], result[best_row] = (
            result[best_row],
            result[pivot_row],
        )

        pivot = result[pivot_row][pivot_column]

        for column in range(columns):
            result[pivot_row][column] /= pivot

        for row in range(rows):
            if row == pivot_row:
                continue

            factor = result[row][pivot_column]

            if abs(factor) <= tolerance:
                continue

            for column in range(columns):
                result[row][column] -= factor * result[pivot_row][column]

        pivot_row += 1

    for i in range(rows):
        for j in range(columns):
            if abs(result[i][j]) < tolerance:
                result[i][j] = 0.0

    return result


def inverse_matrix(matrix: Matrix, tolerance: float = 1e-10) -> Matrix:
    """
    Calculate the inverse using Gauss-Jordan elimination.

    A square matrix is invertible only when it has full rank.
    """
    validate_matrix(matrix)

    if not is_square(matrix):
        raise ValueError("Only square matrices have inverses.")

    size = len(matrix)

    if size == 0:
        return []

    augmented = [
        [float(value) for value in matrix[row]] + identity_matrix(size)[row]
        for row in range(size)
    ]

    reduced = gaussian_elimination(augmented, tolerance=tolerance)

    for row in range(size):
        left_side = reduced[row][:size]

        if not math.isclose(
            max(abs(value) for value in left_side),
            1.0,
            abs_tol=1e-7,
        ):
            raise ValueError("Matrix is singular or numerically non-invertible.")

    return [row[size:] for row in reduced]


# ---------------------------------------------------------------------------
# 10. SPARSE MATRIX REPRESENTATION
# ---------------------------------------------------------------------------

@dataclass
class SparseMatrix:
    """
    Store only non-zero values.

    The dictionary key is (row, column), while the dimensions are stored
    separately.
    """

    rows: int
    columns: int
    values: dict[Tuple[int, int], Number]

    @classmethod
    def from_dense(cls, matrix: Matrix) -> "SparseMatrix":
        validate_matrix(matrix)

        rows, columns = matrix_shape(matrix)
        values = {}

        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                if value != 0:
                    values[(i, j)] = value

        return cls(rows, columns, values)

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
        if not 0 <= row < self.rows or not 0 <= column < self.columns:
            raise IndexError("Sparse matrix position is out of range.")

    def to_dense(self) -> Matrix:
        result = create_matrix(self.rows, self.columns)

        for (row, column), value in self.values.items():
            result[row][column] = value

        return result


# ---------------------------------------------------------------------------
# 11. TWO-DIMENSIONAL PREFIX SUMS
# ---------------------------------------------------------------------------

class PrefixSumMatrix:
    """
    Precompute rectangular-region sums.

    Construction: O(rows * columns)
    Query: O(1)
    """

    def __init__(self, matrix: Matrix):
        validate_matrix(matrix)

        rows, columns = matrix_shape(matrix)

        self.prefix = create_matrix(rows + 1, columns + 1)

        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                self.prefix[i][j] = (
                    matrix[i - 1][j - 1]
                    + self.prefix[i - 1][j]
                    + self.prefix[i][j - 1]
                    - self.prefix[i - 1][j - 1]
                )

    def query(
        self,
        top: int,
        left: int,
        bottom: int,
        right: int,
    ) -> Number:
        """
        Sum the inclusive rectangle:
            top <= row <= bottom
            left <= column <= right
        """
        rows = len(self.prefix) - 1
        columns = len(self.prefix[0]) - 1

        if not (
            0 <= top <= bottom < rows
            and 0 <= left <= right < columns
        ):
            raise IndexError("Invalid rectangular query.")

        return (
            self.prefix[bottom + 1][right + 1]
            - self.prefix[top][right + 1]
            - self.prefix[bottom + 1][left]
            + self.prefix[top][left]
        )


# ---------------------------------------------------------------------------
# 12. MATRIX COMPARISON
# ---------------------------------------------------------------------------

def matrices_equal(
    a: Matrix,
    b: Matrix,
    tolerance: float = 0.0,
) -> bool:
    """Compare matrices, optionally allowing floating-point tolerance."""
    validate_matrix(a)
    validate_matrix(b)

    if matrix_shape(a) != matrix_shape(b):
        return False

    for i in range(len(a)):
        for j in range(len(a[0]) if a else 0):
            if abs(float(a[i][j]) - float(b[i][j])) > tolerance:
                return False

    return True


# ---------------------------------------------------------------------------
# 13. EDUCATIONAL DEMONSTRATIONS
# ---------------------------------------------------------------------------

def demonstrate_fundamentals() -> None:
    print("\n" + "=" * 78)
    print("1. MATRIX FUNDAMENTALS")
    print("=" * 78)

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    print_matrix(matrix, "A 3 x 3 matrix:")
    print("Shape:", matrix_shape(matrix))
    print("Element at row 1, column 2:", get_element(matrix, 1, 2))

    set_element(matrix, 1, 2, 50)
    print_matrix(matrix, "After changing matrix[1][2] to 50:")

    print("Rows are the horizontal sequences.")
    print("Columns are the vertical sequences.")
    print("Python uses zero-based indexing.")


def demonstrate_traversals() -> None:
    print("\n" + "=" * 78)
    print("2. MATRIX TRAVERSALS")
    print("=" * 78)

    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
    ]

    print_matrix(matrix)

    print("Row-major:", row_major_traversal(matrix))
    print("Column-major:", column_major_traversal(matrix))
    print("Main diagonal:", diagonal_traversal(matrix))
    print("Anti-diagonal:", anti_diagonal_traversal(matrix))
    print("Boundary:", boundary_traversal(matrix))
    print("Spiral:", spiral_traversal(matrix))


def demonstrate_operations() -> None:
    print("\n" + "=" * 78)
    print("3. MATRIX OPERATIONS")
    print("=" * 78)

    a = [
        [1, 2],
        [3, 4],
    ]

    b = [
        [5, 6],
        [7, 8],
    ]

    print_matrix(a, "A:")
    print_matrix(b, "B:")

    print_matrix(add_matrices(a, b), "A + B:")
    print_matrix(subtract_matrices(a, b), "A - B:")
    print_matrix(scalar_multiply(a, 3), "3A:")
    print_matrix(matrix_multiply(a, b), "AB:")
    print_matrix(transpose(a), "Transpose of A:")


def demonstrate_insertions() -> None:
    print("\n" + "=" * 78)
    print("4. INSERTION CONCEPTS")
    print("=" * 78)

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
    ]

    insert_row(matrix, 1, [10, 11, 12])
    print_matrix(matrix, "After inserting a row:")

    insert_column(matrix, 2, [20, 21, 22])
    print_matrix(matrix, "After inserting a column:")


def demonstrate_diagonals_and_properties() -> None:
    print("\n" + "=" * 78)
    print("5. DIAGONALS AND MATRIX PROPERTIES")
    print("=" * 78)

    matrix = [
        [2, 5, 7],
        [5, 3, 8],
        [7, 8, 4],
    ]

    print_matrix(matrix)
    print("Square:", is_square(matrix))
    print("Symmetric:", is_symmetric(matrix))
    print("Main diagonal sum:", main_diagonal_sum(matrix))
    print("Secondary diagonal sum:", secondary_diagonal_sum(matrix))
    print("Row sums:", row_sums(matrix))
    print("Column sums:", column_sums(matrix))


def demonstrate_rotations() -> None:
    print("\n" + "=" * 78)
    print("6. ROTATIONS AND REFLECTIONS")
    print("=" * 78)

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
    ]

    print_matrix(matrix, "Original:")
    print_matrix(rotate_clockwise(matrix), "90 degrees clockwise:")
    print_matrix(rotate_counterclockwise(matrix), "90 degrees counterclockwise:")
    print_matrix(reverse_rows(matrix), "Horizontal reflection:")
    print_matrix(reverse_columns(matrix), "Vertical reflection:")


def demonstrate_linear_algebra() -> None:
    print("\n" + "=" * 78)
    print("7. DETERMINANTS, INVERSE, AND GAUSSIAN ELIMINATION")
    print("=" * 78)

    matrix = [
        [4, 7],
        [2, 6],
    ]

    print_matrix(matrix, "A:")
    print("det(A):", determinant(matrix))

    inverse = inverse_matrix(matrix)
    print_matrix(inverse, "A^-1:")

    product = matrix_multiply(matrix, inverse)
    print_matrix(product, "A * A^-1:")

    system = [
        [2, 1, 5],
        [4, -6, -2],
    ]

    print_matrix(system, "Augmented linear system:")
    print_matrix(
        gaussian_elimination(system),
        "Reduced row-echelon form:",
    )


def demonstrate_sparse_matrices() -> None:
    print("\n" + "=" * 78)
    print("8. SPARSE MATRICES")
    print("=" * 78)

    dense = [
        [0, 0, 0, 9],
        [0, 0, 0, 0],
        [0, 5, 0, 0],
        [0, 0, 0, 0],
    ]

    sparse = SparseMatrix.from_dense(dense)

    print_matrix(dense, "Dense representation:")
    print("Stored non-zero entries:", sparse.values)
    print("Value at (0, 3):", sparse.get(0, 3))

    sparse.set(1, 1, 12)
    sparse.set(0, 3, 0)

    print_matrix(sparse.to_dense(), "After sparse updates:")


def demonstrate_prefix_sums() -> None:
    print("\n" + "=" * 78)
    print("9. TWO-DIMENSIONAL PREFIX SUMS")
    print("=" * 78)

    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
    ]

    print_matrix(matrix)

    prefix = PrefixSumMatrix(matrix)

    print("Sum of rows 0..1 and columns 1..2:")
    print(prefix.query(0, 1, 1, 2))

    print("Sum of the entire matrix:")
    print(prefix.query(0, 0, 2, 3))


def demonstrate_searching() -> None:
    print("\n" + "=" * 78)
    print("10. SEARCHING")
    print("=" * 78)

    matrix = [
        [4, 8, 2],
        [8, 1, 9],
        [7, 8, 3],
    ]

    print_matrix(matrix)
    print("Positions containing 8:", find_all(matrix, 8))

    maximum, position = find_maximum(matrix)
    print("Maximum:", maximum)
    print("Maximum position:", position)


def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 78)
    print("11. EDGE CASES AND ERROR HANDLING")
    print("=" * 78)

    examples = [
        ("Empty matrix", []),
        ("Single element", [[42]]),
        ("Single row", [[1, 2, 3, 4]]),
        ("Single column", [[1], [2], [3]]),
    ]

    for name, matrix in examples:
        print(f"\n{name}:")
        print_matrix(matrix)
        print("Shape:", matrix_shape(matrix))
        print("Spiral:", spiral_traversal(matrix))

    try:
        matrix_multiply([[1, 2]], [[1, 2]])
    except ValueError as error:
        print("\nInvalid multiplication caught:", error)

    try:
        add_matrices([[1, 2]], [[1], [2]])
    except ValueError as error:
        print("Invalid addition caught:", error)

    try:
        determinant([[1, 2, 3], [4, 5, 6]])
    except ValueError as error:
        print("Invalid determinant caught:", error)


def demonstrate_random_matrix() -> None:
    print("\n" + "=" * 78)
    print("12. RANDOM MATRIX")
    print("=" * 78)

    random.seed(42)

    matrix = [
        [random.randint(0, 9) for _ in range(5)]
        for _ in range(4)
    ]

    print_matrix(matrix, "Deterministic random 4 x 5 matrix:")
    print("Row sums:", row_sums(matrix))
    print("Column sums:", column_sums(matrix))
    print("Spiral:", spiral_traversal(matrix))


def explain_complexity() -> None:
    print("\n" + "=" * 78)
    print("13. COMPLEXITY REFERENCE")
    print("=" * 78)

    complexity = {
        "Element access": "O(1)",
        "Update one element": "O(1)",
        "Full traversal": "O(rows * columns)",
        "Addition": "O(rows * columns)",
        "Transpose": "O(rows * columns)",
        "Naive matrix multiplication": "O(rows_A * cols_A * cols_B)",
        "Searching an unsorted matrix": "O(rows * columns)",
        "Prefix-sum construction": "O(rows * columns)",
        "Prefix-sum rectangle query": "O(1)",
        "Naive recursive determinant": "Very expensive as dimension grows",
    }

    for operation, complexity in complexity.items():
        print(f"{operation:40} {complexity}")


def main() -> None:
    demonstrate_fundamentals()
    demonstrate_traversals()
    demonstrate_operations()
    demonstrate_insertions()
    demonstrate_diagonals_and_properties()
    demonstrate_rotations()
    demonstrate_linear_algebra()
    demonstrate_sparse_matrices()
    demonstrate_prefix_sums()
    demonstrate_searching()
    demonstrate_edge_cases()
    demonstrate_random_matrix()
    explain_complexity()

    print("\n" + "=" * 78)
    print("MATRIX FUNDAMENTALS PRACTICE COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    main()
