"""
Matrix Traversal Algorithms
===========================

A self-contained study program covering:

1. Row-wise traversal
2. Column-wise traversal
3. Main and secondary diagonal traversal
4. Boundary traversal
5. Spiral traversal
6. Zigzag traversal
7. Transpose-related traversal concepts
8. Rectangular, square, single-row, single-column, empty, and singleton matrices
9. Validation and error handling
10. Complexity analysis
11. Comparison of traversal strategies
12. A practical matrix-processing demonstration

The examples use only the Python standard library.
"""

from __future__ import annotations

from typing import Callable, Iterable, List, Sequence, Tuple


Matrix = List[List[int]]
Coordinate = Tuple[int, int]


# ---------------------------------------------------------------------------
# Basic utilities
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def validate_matrix(matrix: Matrix, allow_empty: bool = True) -> Tuple[int, int]:
    """
    Validate that the input is a rectangular matrix.

    A matrix is represented as a list of rows, where every row has the same
    number of columns.

    Returns:
        (number_of_rows, number_of_columns)

    Raises:
        TypeError: if the matrix is not a list of lists.
        ValueError: if rows have different lengths or an empty matrix is
                    disallowed.
    """
    if not isinstance(matrix, list):
        raise TypeError("Matrix must be a list of lists.")

    if not matrix:
        if allow_empty:
            return 0, 0
        raise ValueError("Matrix cannot be empty.")

    if not all(isinstance(row, list) for row in matrix):
        raise TypeError("Every matrix row must be a list.")

    column_count = len(matrix[0])

    if column_count == 0:
        if allow_empty:
            return len(matrix), 0
        raise ValueError("Matrix rows cannot be empty.")

    for row_index, row in enumerate(matrix):
        if len(row) != column_count:
            raise ValueError(
                f"Matrix is not rectangular: row 0 has {column_count} "
                f"columns but row {row_index} has {len(row)}."
            )

    return len(matrix), column_count


def format_values(values: Sequence[int]) -> str:
    """Return traversal values in a compact mathematical-style format."""
    return " -> ".join(str(value) for value in values)


def print_matrix(matrix: Matrix) -> None:
    """Display a matrix with aligned columns."""
    rows, columns = validate_matrix(matrix)

    if rows == 0 or columns == 0:
        print("[empty matrix]")
        return

    width = max(len(str(value)) for row in matrix for value in row)

    for row in matrix:
        print(" ".join(f"{value:>{width}}" for value in row))


# ---------------------------------------------------------------------------
# 1. Row-wise traversal
# ---------------------------------------------------------------------------

def row_wise_traversal(matrix: Matrix) -> List[int]:
    """
    Visit every row from left to right, starting with the first row.

    Example:

        1 2 3
        4 5 6
        7 8 9

    Result:

        1 2 3 4 5 6 7 8 9

    Time: O(R * C)
    Extra traversal space: O(R * C) for the returned list.
    """
    rows, columns = validate_matrix(matrix)

    result: List[int] = []

    for row in range(rows):
        for column in range(columns):
            result.append(matrix[row][column])

    return result


# ---------------------------------------------------------------------------
# 2. Column-wise traversal
# ---------------------------------------------------------------------------

def column_wise_traversal(matrix: Matrix) -> List[int]:
    """
    Visit every column from top to bottom, starting with the first column.

    Example:

        1 2 3
        4 5 6
        7 8 9

    Result:

        1 4 7 2 5 8 3 6 9

    Time: O(R * C)
    """
    rows, columns = validate_matrix(matrix)

    result: List[int] = []

    for column in range(columns):
        for row in range(rows):
            result.append(matrix[row][column])

    return result


# ---------------------------------------------------------------------------
# 3. Main diagonal traversal
# ---------------------------------------------------------------------------

def main_diagonal_traversal(matrix: Matrix) -> List[int]:
    """
    Visit the main diagonal.

    For a square matrix:

        1 2 3
        4 5 6
        7 8 9

    Main diagonal:

        1 5 9

    The main diagonal exists for every matrix with at least one row and one
    column. Its length is min(rows, columns).

    Time: O(min(R, C))
    """
    rows, columns = validate_matrix(matrix)

    length = min(rows, columns)

    return [matrix[index][index] for index in range(length)]


# ---------------------------------------------------------------------------
# 4. Secondary diagonal traversal
# ---------------------------------------------------------------------------

def secondary_diagonal_traversal(matrix: Matrix) -> List[int]:
    """
    Visit the secondary diagonal.

    For a 3 x 3 matrix:

        1 2 3
        4 5 6
        7 8 9

    Secondary diagonal:

        3 5 7

    The secondary diagonal is naturally defined for square matrices.
    For a rectangular matrix this implementation uses the largest square
    region that starts at the top-left corner.

    Time: O(min(R, C))
    """
    rows, columns = validate_matrix(matrix)

    length = min(rows, columns)

    if length == 0:
        return []

    return [
        matrix[index][length - 1 - index]
        for index in range(length)
    ]


# ---------------------------------------------------------------------------
# 5. Boundary traversal
# ---------------------------------------------------------------------------

def boundary_traversal(matrix: Matrix) -> List[int]:
    """
    Traverse only the outside boundary in clockwise order.

    Example:

        1 2 3 4
        5 6 7 8
        9 10 11 12

    Result:

        1 2 3 4 8 12 11 10 9 5

    Important edge cases:
        - Empty matrix
        - One row
        - One column
        - Single element

    Time: O(R + C)
    """
    rows, columns = validate_matrix(matrix)

    if rows == 0 or columns == 0:
        return []

    result: List[int] = []

    # Top edge: left -> right.
    for column in range(columns):
        result.append(matrix[0][column])

    # Right edge: top -> bottom.
    for row in range(1, rows):
        result.append(matrix[row][columns - 1])

    # Bottom edge: right -> left.
    # Avoid repeating the top edge for a single-row matrix.
    if rows > 1:
        for column in range(columns - 2, -1, -1):
            result.append(matrix[rows - 1][column])

    # Left edge: bottom -> top.
    # Avoid repeating corners and avoid repeating the right edge in a
    # single-column matrix.
    if columns > 1:
        for row in range(rows - 2, 0, -1):
            result.append(matrix[row][0])

    return result


# ---------------------------------------------------------------------------
# 6. Spiral traversal
# ---------------------------------------------------------------------------

def spiral_traversal(matrix: Matrix) -> List[int]:
    """
    Traverse a matrix in clockwise spiral order.

    Example:

        1  2  3  4
        5  6  7  8
        9 10 11 12

    Result:

        1 2 3 4 8 12 11 10 9 5 6 7

    The algorithm maintains four boundaries:

        top
        bottom
        left
        right

    After processing one side, the corresponding boundary moves inward.

    Time: O(R * C)
    Extra space: O(R * C) for the returned result.
    """
    rows, columns = validate_matrix(matrix)

    if rows == 0 or columns == 0:
        return []

    result: List[int] = []

    top = 0
    bottom = rows - 1
    left = 0
    right = columns - 1

    while top <= bottom and left <= right:
        # Top row: left -> right.
        for column in range(left, right + 1):
            result.append(matrix[top][column])
        top += 1

        # Right column: top -> bottom.
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1

        # Bottom row: right -> left.
        # The condition prevents duplication when no row remains.
        if top <= bottom:
            for column in range(right, left - 1, -1):
                result.append(matrix[bottom][column])
            bottom -= 1

        # Left column: bottom -> top.
        # The condition prevents duplication when no column remains.
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1

    return result


# ---------------------------------------------------------------------------
# 7. Zigzag traversal
# ---------------------------------------------------------------------------

def zigzag_row_traversal(matrix: Matrix) -> List[int]:
    """
    Traverse rows alternately from left-to-right and right-to-left.

    Example:

        1 2 3
        4 5 6
        7 8 9

    Result:

        1 2 3 6 5 4 7 8 9

    This is sometimes called snake traversal.

    Time: O(R * C)
    """
    rows, columns = validate_matrix(matrix)

    result: List[int] = []

    for row in range(rows):
        if row % 2 == 0:
            for column in range(columns):
                result.append(matrix[row][column])
        else:
            for column in range(columns - 1, -1, -1):
                result.append(matrix[row][column])

    return result


# ---------------------------------------------------------------------------
# 8. Column zigzag traversal
# ---------------------------------------------------------------------------

def zigzag_column_traversal(matrix: Matrix) -> List[int]:
    """
    Traverse columns alternately from top-to-bottom and bottom-to-top.

    Example:

        1 2 3
        4 5 6
        7 8 9

    Result:

        1 4 7 9 6 3 2 5 8

    Time: O(R * C)
    """
    rows, columns = validate_matrix(matrix)

    result: List[int] = []

    for column in range(columns):
        if column % 2 == 0:
            for row in range(rows):
                result.append(matrix[row][column])
        else:
            for row in range(rows - 1, -1, -1):
                result.append(matrix[row][column])

    return result


# ---------------------------------------------------------------------------
# 9. Coordinate-based traversal
# ---------------------------------------------------------------------------

def coordinates_row_wise(matrix: Matrix) -> List[Coordinate]:
    """Return matrix coordinates in row-wise order."""
    rows, columns = validate_matrix(matrix)

    return [
        (row, column)
        for row in range(rows)
        for column in range(columns)
    ]


def values_from_coordinates(
    matrix: Matrix,
    coordinates: Iterable[Coordinate],
) -> List[int]:
    """
    Convert a coordinate sequence into matrix values.

    This separates traversal logic from data access and is useful when
    implementing more sophisticated traversal strategies.
    """
    rows, columns = validate_matrix(matrix)

    result: List[int] = []

    for row, column in coordinates:
        if not (0 <= row < rows and 0 <= column < columns):
            raise IndexError(
                f"Coordinate ({row}, {column}) is outside the matrix."
            )
        result.append(matrix[row][column])

    return result


# ---------------------------------------------------------------------------
# 10. Transpose
# ---------------------------------------------------------------------------

def transpose(matrix: Matrix) -> Matrix:
    """
    Return the transpose of a matrix.

    Transposition converts:

        a b c
        d e f

    into:

        a d
        b e
        c f

    Time: O(R * C)
    Space: O(R * C) for the new matrix.
    """
    rows, columns = validate_matrix(matrix)

    if rows == 0 or columns == 0:
        return []

    return [
        [matrix[row][column] for row in range(rows)]
        for column in range(columns)
    ]


# ---------------------------------------------------------------------------
# 11. In-place spiral layer reasoning
# ---------------------------------------------------------------------------

def spiral_layers(matrix: Matrix) -> List[List[int]]:
    """
    Return each spiral layer separately.

    This makes the relationship between spiral traversal and concentric
    rectangular layers explicit.
    """
    rows, columns = validate_matrix(matrix)

    if rows == 0 or columns == 0:
        return []

    layers: List[List[int]] = []

    top = 0
    bottom = rows - 1
    left = 0
    right = columns - 1

    while top <= bottom and left <= right:
        layer: List[int] = []

        for column in range(left, right + 1):
            layer.append(matrix[top][column])
        top += 1

        for row in range(top, bottom + 1):
            layer.append(matrix[row][right])
        right -= 1

        if top <= bottom:
            for column in range(right, left - 1, -1):
                layer.append(matrix[bottom][column])
            bottom -= 1

        if left <= right:
            for row in range(bottom, top - 1, -1):
                layer.append(matrix[row][left])
            left += 1

        layers.append(layer)

    return layers


# ---------------------------------------------------------------------------
# 12. Generic traversal framework
# ---------------------------------------------------------------------------

def demonstrate_traversal(
    name: str,
    traversal_function: Callable[[Matrix], List[int]],
    matrix: Matrix,
) -> None:
    """Run and display any traversal function using a common interface."""
    values = traversal_function(matrix)
    print(f"{name:<32}: {format_values(values)}")


# ---------------------------------------------------------------------------
# 13. Correctness helpers
# ---------------------------------------------------------------------------

def assert_traversal_contains_every_cell(
    matrix: Matrix,
    traversal_function: Callable[[Matrix], List[int]],
) -> None:
    """
    Verify that a traversal visits exactly R*C cells.

    This catches common mistakes such as:
        - skipping a corner
        - visiting a cell twice
        - stopping too early
    """
    rows, columns = validate_matrix(matrix)
    result = traversal_function(matrix)

    expected_count = rows * columns

    if len(result) != expected_count:
        raise AssertionError(
            f"{traversal_function.__name__} returned {len(result)} values; "
            f"expected {expected_count}."
        )


def run_correctness_tests() -> None:
    """Run deterministic correctness tests over several matrix shapes."""
    matrices = [
        [],
        [[1]],
        [[1, 2, 3]],
        [[1], [2], [3]],
        [
            [1, 2],
            [3, 4],
        ],
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
        [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
        ],
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12],
        ],
    ]

    full_traversals = [
        row_wise_traversal,
        column_wise_traversal,
        spiral_traversal,
        zigzag_row_traversal,
        zigzag_column_traversal,
    ]

    for matrix in matrices:
        for traversal in full_traversals:
            assert_traversal_contains_every_cell(matrix, traversal)

    assert row_wise_traversal([[1, 2], [3, 4]]) == [1, 2, 3, 4]
    assert column_wise_traversal([[1, 2], [3, 4]]) == [1, 3, 2, 4]
    assert spiral_traversal([[1, 2], [3, 4]]) == [1, 2, 4, 3]
    assert zigzag_row_traversal([[1, 2], [3, 4]]) == [1, 2, 4, 3]

    assert boundary_traversal(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    ) == [1, 2, 3, 6, 9, 8, 7, 4]

    assert main_diagonal_traversal(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    ) == [1, 5, 9]

    assert secondary_diagonal_traversal(
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    ) == [3, 5, 7]

    print("All deterministic traversal tests passed.")


# ---------------------------------------------------------------------------
# 14. Edge-case demonstrations
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    """Show how traversal algorithms behave for unusual matrix shapes."""
    matrices = {
        "empty": [],
        "single element": [[42]],
        "single row": [[1, 2, 3, 4, 5]],
        "single column": [[1], [2], [3], [4], [5]],
        "rectangular": [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
        ],
    }

    traversal_functions = [
        ("row-wise", row_wise_traversal),
        ("column-wise", column_wise_traversal),
        ("boundary", boundary_traversal),
        ("spiral", spiral_traversal),
        ("row zigzag", zigzag_row_traversal),
        ("column zigzag", zigzag_column_traversal),
    ]

    for matrix_name, matrix in matrices.items():
        print_section(f"Edge case: {matrix_name}")
        print_matrix(matrix)

        for name, function in traversal_functions:
            print(f"{name:<20}: {format_values(function(matrix))}")


# ---------------------------------------------------------------------------
# 15. Invalid matrix demonstrations
# ---------------------------------------------------------------------------

def demonstrate_validation_errors() -> None:
    """Demonstrate why rectangular validation matters."""
    invalid_matrices = [
        [[1, 2], [3]],
        [[1], [2, 3, 4]],
        [1, 2, 3],  # Not a list of rows.
    ]

    print_section("Validation and error handling")

    for invalid_matrix in invalid_matrices:
        try:
            validate_matrix(invalid_matrix)  # type: ignore[arg-type]
        except (TypeError, ValueError) as error:
            print(f"Rejected {invalid_matrix!r}: {error}")


# ---------------------------------------------------------------------------
# 16. Practical matrix analysis
# ---------------------------------------------------------------------------

def traversal_statistics(matrix: Matrix) -> dict:
    """
    Produce several traversal-derived statistics.

    The function demonstrates that traversal is often the first step of
    larger algorithms rather than an isolated programming exercise.
    """
    row_values = row_wise_traversal(matrix)
    spiral_values = spiral_traversal(matrix)
    boundary_values = boundary_traversal(matrix)

    if not row_values:
        return {
            "cell_count": 0,
            "minimum": None,
            "maximum": None,
            "sum": 0,
            "spiral_first": None,
            "spiral_last": None,
            "boundary_sum": 0,
        }

    return {
        "cell_count": len(row_values),
        "minimum": min(row_values),
        "maximum": max(row_values),
        "sum": sum(row_values),
        "spiral_first": spiral_values[0] if spiral_values else None,
        "spiral_last": spiral_values[-1] if spiral_values else None,
        "boundary_sum": sum(boundary_values),
    }


# ---------------------------------------------------------------------------
# 17. Coordinate-aware spiral traversal
# ---------------------------------------------------------------------------

def spiral_coordinate_traversal(matrix: Matrix) -> List[Coordinate]:
    """
    Return coordinates in spiral order.

    This is useful when the algorithm needs to know not only the value but
    also the physical location of that value.
    """
    rows, columns = validate_matrix(matrix)

    if rows == 0 or columns == 0:
        return []

    result: List[Coordinate] = []

    top = 0
    bottom = rows - 1
    left = 0
    right = columns - 1

    while top <= bottom and left <= right:
        for column in range(left, right + 1):
            result.append((top, column))
        top += 1

        for row in range(top, bottom + 1):
            result.append((row, right))
        right -= 1

        if top <= bottom:
            for column in range(right, left - 1, -1):
                result.append((bottom, column))
            bottom -= 1

        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append((row, left))
            left += 1

    return result


# ---------------------------------------------------------------------------
# 18. Demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    matrix: Matrix = [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20],
    ]

    print_section("Matrix Traversal Algorithms")

    print("Input matrix:")
    print_matrix(matrix)

    print_section("Basic traversals")

    demonstrate_traversal(
        "Row-wise traversal",
        row_wise_traversal,
        matrix,
    )

    demonstrate_traversal(
        "Column-wise traversal",
        column_wise_traversal,
        matrix,
    )

    demonstrate_traversal(
        "Boundary traversal",
        boundary_traversal,
        matrix,
    )

    demonstrate_traversal(
        "Spiral traversal",
        spiral_traversal,
        matrix,
    )

    demonstrate_traversal(
        "Row zigzag traversal",
        zigzag_row_traversal,
        matrix,
    )

    demonstrate_traversal(
        "Column zigzag traversal",
        zigzag_column_traversal,
        matrix,
    )

    print_section("Diagonal traversals")

    square_matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
    ]

    print_matrix(square_matrix)

    print(
        "Main diagonal     :",
        format_values(main_diagonal_traversal(square_matrix)),
    )
    print(
        "Secondary diagonal:",
        format_values(secondary_diagonal_traversal(square_matrix)),
    )

    print_section("Spiral layers")

    for layer_number, layer in enumerate(
        spiral_layers(matrix),
        start=1,
    ):
        print(f"Layer {layer_number}: {format_values(layer)}")

    print_section("Coordinate traversal")

    coordinates = spiral_coordinate_traversal(matrix)
    values = values_from_coordinates(matrix, coordinates)

    for coordinate, value in zip(coordinates, values):
        print(f"{coordinate} -> {value}")

    print_section("Transpose")

    print("Original:")
    print_matrix(matrix)

    print("\nTransposed:")
    print_matrix(transpose(matrix))

    print_section("Practical statistics")

    statistics = traversal_statistics(matrix)

    for key, value in statistics.items():
        print(f"{key:<16}: {value}")

    run_correctness_tests()
    demonstrate_edge_cases()
    demonstrate_validation_errors()


if __name__ == "__main__":
    main()
