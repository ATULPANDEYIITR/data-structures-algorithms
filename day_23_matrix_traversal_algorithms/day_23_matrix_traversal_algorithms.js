"use strict";

/*
 * Matrix Traversal Algorithms
 * ===========================
 *
 * This file demonstrates:
 *   - Row-wise traversal
 *   - Column-wise traversal
 *   - Main and secondary diagonals
 *   - Boundary traversal
 *   - Clockwise spiral traversal
 *   - Row and column zigzag traversal
 *   - Coordinate-based traversal
 *   - Matrix transposition
 *   - Validation and error handling
 *   - Correctness tests
 *   - Practical matrix analysis
 *
 * The implementation uses standard JavaScript only and can run in Node.js.
 */

// -----------------------------------------------------------------------------
// Basic utilities
// -----------------------------------------------------------------------------

function validateMatrix(matrix, allowEmpty = true) {
    if (!Array.isArray(matrix)) {
        throw new TypeError("Matrix must be an array of arrays.");
    }

    if (matrix.length === 0) {
        if (allowEmpty) {
            return { rows: 0, columns: 0 };
        }

        throw new RangeError("Matrix cannot be empty.");
    }

    if (!matrix.every(Array.isArray)) {
        throw new TypeError("Every matrix row must be an array.");
    }

    const columns = matrix[0].length;

    if (columns === 0) {
        if (allowEmpty) {
            return { rows: matrix.length, columns: 0 };
        }

        throw new RangeError("Matrix rows cannot be empty.");
    }

    for (let row = 0; row < matrix.length; row += 1) {
        if (matrix[row].length !== columns) {
            throw new RangeError(
                `Matrix is not rectangular: row 0 has ${columns} columns ` +
                `but row ${row} has ${matrix[row].length}.`
            );
        }
    }

    return {
        rows: matrix.length,
        columns
    };
}

function formatValues(values) {
    return values.join(" -> ");
}

function printMatrix(matrix) {
    const { rows, columns } = validateMatrix(matrix);

    if (rows === 0 || columns === 0) {
        console.log("[empty matrix]");
        return;
    }

    const width = Math.max(
        ...matrix.flat().map((value) => String(value).length)
    );

    for (const row of matrix) {
        console.log(
            row.map((value) => String(value).padStart(width)).join(" ")
        );
    }
}

// -----------------------------------------------------------------------------
// 1. Row-wise traversal
// -----------------------------------------------------------------------------

function rowWiseTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);
    const result = [];

    for (let row = 0; row < rows; row += 1) {
        for (let column = 0; column < columns; column += 1) {
            result.push(matrix[row][column]);
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// 2. Column-wise traversal
// -----------------------------------------------------------------------------

function columnWiseTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);
    const result = [];

    for (let column = 0; column < columns; column += 1) {
        for (let row = 0; row < rows; row += 1) {
            result.push(matrix[row][column]);
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// 3. Main diagonal
// -----------------------------------------------------------------------------

function mainDiagonalTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);
    const length = Math.min(rows, columns);
    const result = [];

    for (let index = 0; index < length; index += 1) {
        result.push(matrix[index][index]);
    }

    return result;
}

// -----------------------------------------------------------------------------
// 4. Secondary diagonal
// -----------------------------------------------------------------------------

function secondaryDiagonalTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);
    const length = Math.min(rows, columns);
    const result = [];

    for (let index = 0; index < length; index += 1) {
        result.push(matrix[index][length - 1 - index]);
    }

    return result;
}

// -----------------------------------------------------------------------------
// 5. Boundary traversal
// -----------------------------------------------------------------------------

function boundaryTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);

    if (rows === 0 || columns === 0) {
        return [];
    }

    const result = [];

    // Top edge.
    for (let column = 0; column < columns; column += 1) {
        result.push(matrix[0][column]);
    }

    // Right edge.
    for (let row = 1; row < rows; row += 1) {
        result.push(matrix[row][columns - 1]);
    }

    // Bottom edge.
    if (rows > 1) {
        for (let column = columns - 2; column >= 0; column -= 1) {
            result.push(matrix[rows - 1][column]);
        }
    }

    // Left edge.
    if (columns > 1) {
        for (let row = rows - 2; row >= 1; row -= 1) {
            result.push(matrix[row][0]);
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// 6. Spiral traversal
// -----------------------------------------------------------------------------

function spiralTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);

    if (rows === 0 || columns === 0) {
        return [];
    }

    const result = [];

    let top = 0;
    let bottom = rows - 1;
    let left = 0;
    let right = columns - 1;

    while (top <= bottom && left <= right) {
        // Move across the top side.
        for (let column = left; column <= right; column += 1) {
            result.push(matrix[top][column]);
        }
        top += 1;

        // Move down the right side.
        for (let row = top; row <= bottom; row += 1) {
            result.push(matrix[row][right]);
        }
        right -= 1;

        // Move across the bottom side.
        if (top <= bottom) {
            for (let column = right; column >= left; column -= 1) {
                result.push(matrix[bottom][column]);
            }
            bottom -= 1;
        }

        // Move up the left side.
        if (left <= right) {
            for (let row = bottom; row >= top; row -= 1) {
                result.push(matrix[row][left]);
            }
            left += 1;
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// 7. Row zigzag
// -----------------------------------------------------------------------------

function rowZigzagTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);
    const result = [];

    for (let row = 0; row < rows; row += 1) {
        if (row % 2 === 0) {
            for (let column = 0; column < columns; column += 1) {
                result.push(matrix[row][column]);
            }
        } else {
            for (let column = columns - 1; column >= 0; column -= 1) {
                result.push(matrix[row][column]);
            }
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// 8. Column zigzag
// -----------------------------------------------------------------------------

function columnZigzagTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);
    const result = [];

    for (let column = 0; column < columns; column += 1) {
        if (column % 2 === 0) {
            for (let row = 0; row < rows; row += 1) {
                result.push(matrix[row][column]);
            }
        } else {
            for (let row = rows - 1; row >= 0; row -= 1) {
                result.push(matrix[row][column]);
            }
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// 9. Coordinate-based traversal
// -----------------------------------------------------------------------------

function spiralCoordinateTraversal(matrix) {
    const { rows, columns } = validateMatrix(matrix);

    if (rows === 0 || columns === 0) {
        return [];
    }

    const coordinates = [];

    let top = 0;
    let bottom = rows - 1;
    let left = 0;
    let right = columns - 1;

    while (top <= bottom && left <= right) {
        for (let column = left; column <= right; column += 1) {
            coordinates.push([top, column]);
        }
        top += 1;

        for (let row = top; row <= bottom; row += 1) {
            coordinates.push([row, right]);
        }
        right -= 1;

        if (top <= bottom) {
            for (let column = right; column >= left; column -= 1) {
                coordinates.push([bottom, column]);
            }
            bottom -= 1;
        }

        if (left <= right) {
            for (let row = bottom; row >= top; row -= 1) {
                coordinates.push([row, left]);
            }
            left += 1;
        }
    }

    return coordinates;
}

function valuesFromCoordinates(matrix, coordinates) {
    const { rows, columns } = validateMatrix(matrix);
    const values = [];

    for (const [row, column] of coordinates) {
        if (
            row < 0 ||
            row >= rows ||
            column < 0 ||
            column >= columns
        ) {
            throw new RangeError(
                `Coordinate (${row}, ${column}) is outside the matrix.`
            );
        }

        values.push(matrix[row][column]);
    }

    return values;
}

// -----------------------------------------------------------------------------
// 10. Transpose
// -----------------------------------------------------------------------------

function transpose(matrix) {
    const { rows, columns } = validateMatrix(matrix);

    if (rows === 0 || columns === 0) {
        return [];
    }

    const result = [];

    for (let column = 0; column < columns; column += 1) {
        const newRow = [];

        for (let row = 0; row < rows; row += 1) {
            newRow.push(matrix[row][column]);
        }

        result.push(newRow);
    }

    return result;
}

// -----------------------------------------------------------------------------
// 11. Functional-style traversal helper
// -----------------------------------------------------------------------------

function mapTraversal(matrix, traversalFunction, mapper) {
    /*
     * Traversal and processing are separate concerns.
     *
     * First the traversal determines the visiting order.
     * Then the mapper transforms each visited value.
     */
    const values = traversalFunction(matrix);
    return values.map(mapper);
}

// -----------------------------------------------------------------------------
// 12. Correctness testing
// -----------------------------------------------------------------------------

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function assertFullTraversal(matrix, traversalFunction) {
    const { rows, columns } = validateMatrix(matrix);
    const values = traversalFunction(matrix);

    assert(
        values.length === rows * columns,
        `${traversalFunction.name} visited ${values.length} cells; ` +
        `expected ${rows * columns}.`
    );

    const expectedValues = matrix.flat().sort((a, b) => a - b);
    const actualValues = [...values].sort((a, b) => a - b);

    assert(
        JSON.stringify(expectedValues) === JSON.stringify(actualValues),
        `${traversalFunction.name} did not visit exactly the matrix cells.`
    );
}

function runTests() {
    const matrices = [
        [],
        [[1]],
        [[1, 2, 3, 4]],
        [[1], [2], [3], [4]],
        [[1, 2], [3, 4]],
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ],
        [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ]
    ];

    const fullTraversals = [
        rowWiseTraversal,
        columnWiseTraversal,
        spiralTraversal,
        rowZigzagTraversal,
        columnZigzagTraversal
    ];

    for (const matrix of matrices) {
        for (const traversal of fullTraversals) {
            assertFullTraversal(matrix, traversal);
        }
    }

    assert(
        JSON.stringify(
            boundaryTraversal([
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ])
        ) === JSON.stringify([1, 2, 3, 6, 9, 8, 7, 4]),
        "Boundary traversal is incorrect."
    );

    assert(
        JSON.stringify(
            mainDiagonalTraversal([
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ])
        ) === JSON.stringify([1, 5, 9]),
        "Main diagonal traversal is incorrect."
    );

    assert(
        JSON.stringify(
            secondaryDiagonalTraversal([
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ])
        ) === JSON.stringify([3, 5, 7]),
        "Secondary diagonal traversal is incorrect."
    );

    console.log("All JavaScript tests passed.");
}

// -----------------------------------------------------------------------------
// 13. Practical analysis
// -----------------------------------------------------------------------------

function matrixStatistics(matrix) {
    const rowValues = rowWiseTraversal(matrix);
    const spiralValues = spiralTraversal(matrix);
    const boundaryValues = boundaryTraversal(matrix);

    if (rowValues.length === 0) {
        return {
            cellCount: 0,
            minimum: null,
            maximum: null,
            sum: 0,
            spiralFirst: null,
            spiralLast: null,
            boundarySum: 0
        };
    }

    return {
        cellCount: rowValues.length,
        minimum: Math.min(...rowValues),
        maximum: Math.max(...rowValues),
        sum: rowValues.reduce((sum, value) => sum + value, 0),
        spiralFirst: spiralValues[0],
        spiralLast: spiralValues[spiralValues.length - 1],
        boundarySum: boundaryValues.reduce(
            (sum, value) => sum + value,
            0
        )
    };
}

// -----------------------------------------------------------------------------
// 14. Edge cases
// -----------------------------------------------------------------------------

function demonstrateEdgeCases() {
    const matrices = {
        empty: [],
        singleElement: [[42]],
        singleRow: [[1, 2, 3, 4, 5]],
        singleColumn: [[1], [2], [3], [4], [5]],
        rectangular: [
            [1, 2, 3, 4],
            [5, 6, 7, 8]
        ]
    };

    for (const [name, matrix] of Object.entries(matrices)) {
        console.log(`\n--- ${name} ---`);
        printMatrix(matrix);

        console.log(
            "Row-wise:",
            formatValues(rowWiseTraversal(matrix))
        );
        console.log(
            "Column-wise:",
            formatValues(columnWiseTraversal(matrix))
        );
        console.log(
            "Boundary:",
            formatValues(boundaryTraversal(matrix))
        );
        console.log(
            "Spiral:",
            formatValues(spiralTraversal(matrix))
        );
        console.log(
            "Row zigzag:",
            formatValues(rowZigzagTraversal(matrix))
        );
    }
}

// -----------------------------------------------------------------------------
// 15. Error handling
// -----------------------------------------------------------------------------

function demonstrateValidationErrors() {
    const invalidMatrices = [
        [[1, 2], [3]],
        [[1], [2, 3]],
        [1, 2, 3]
    ];

    console.log("\n--- Validation errors ---");

    for (const matrix of invalidMatrices) {
        try {
            validateMatrix(matrix);
        } catch (error) {
            console.log(
                `Rejected ${JSON.stringify(matrix)}: ${error.message}`
            );
        }
    }
}

// -----------------------------------------------------------------------------
// 16. Main demonstration
// -----------------------------------------------------------------------------

function main() {
    const matrix = [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20]
    ];

    console.log("=== Matrix Traversal Algorithms ===");
    console.log("\nInput matrix:");
    printMatrix(matrix);

    console.log("\n=== Traversals ===");

    const traversalExamples = [
        ["Row-wise", rowWiseTraversal],
        ["Column-wise", columnWiseTraversal],
        ["Boundary", boundaryTraversal],
        ["Spiral", spiralTraversal],
        ["Row zigzag", rowZigzagTraversal],
        ["Column zigzag", columnZigzagTraversal]
    ];

    for (const [name, functionReference] of traversalExamples) {
        console.log(
            `${name.padEnd(18)}: ` +
            formatValues(functionReference(matrix))
        );
    }

    const squareMatrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ];

    console.log("\n=== Diagonals ===");
    printMatrix(squareMatrix);
    console.log(
        "Main diagonal:",
        formatValues(mainDiagonalTraversal(squareMatrix))
    );
    console.log(
        "Secondary diagonal:",
        formatValues(secondaryDiagonalTraversal(squareMatrix))
    );

    console.log("\n=== Coordinate-based spiral traversal ===");

    const coordinates = spiralCoordinateTraversal(matrix);
    const values = valuesFromCoordinates(matrix, coordinates);

    coordinates.forEach(([row, column], index) => {
        console.log(
            `(${row}, ${column}) -> ${values[index]}`
        );
    });

    console.log("\n=== Transpose ===");
    printMatrix(transpose(matrix));

    console.log("\n=== Functional processing ===");

    const doubledSpiralValues = mapTraversal(
        matrix,
        spiralTraversal,
        (value) => value * 2
    );

    console.log(
        "Doubled spiral values:",
        formatValues(doubledSpiralValues)
    );

    console.log("\n=== Matrix statistics ===");
    console.table(matrixStatistics(matrix));

    runTests();
    demonstrateEdgeCases();
    demonstrateValidationErrors();
}

main();
