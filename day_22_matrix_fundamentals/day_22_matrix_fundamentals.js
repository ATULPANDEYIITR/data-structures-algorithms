/*
 * Matrix Fundamentals
 * ====================
 *
 * A standalone JavaScript study file covering:
 * - Matrix representation
 * - Dimensions and indexing
 * - Construction and validation
 * - Traversal
 * - Element updates and insertion
 * - Matrix arithmetic
 * - Matrix multiplication
 * - Transpose
 * - Diagonals and symmetry
 * - Searching
 * - Rotation and reflection
 * - Determinant
 * - Gaussian elimination
 * - Sparse matrices
 * - Prefix sums
 * - Error handling and edge cases
 *
 * Run with:
 *     node matrix_fundamentals.js
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. REPRESENTATION AND VALIDATION
// -----------------------------------------------------------------------------

function validateMatrix(matrix, allowEmpty = true) {
    if (!Array.isArray(matrix)) {
        throw new TypeError("Matrix must be an array of rows.");
    }

    if (matrix.length === 0) {
        if (allowEmpty) return;
        throw new Error("Matrix cannot be empty.");
    }

    if (!matrix.every(row => Array.isArray(row))) {
        throw new TypeError("Every matrix row must be an array.");
    }

    const columns = matrix[0].length;

    if (!matrix.every(row => row.length === columns)) {
        throw new Error("Matrix must be rectangular.");
    }
}

function shape(matrix) {
    validateMatrix(matrix);

    if (matrix.length === 0) {
        return [0, 0];
    }

    return [matrix.length, matrix[0].length];
}

function createMatrix(rows, columns, fill = 0) {
    if (!Number.isInteger(rows) || !Number.isInteger(columns)) {
        throw new TypeError("Dimensions must be integers.");
    }

    if (rows < 0 || columns < 0) {
        throw new RangeError("Dimensions cannot be negative.");
    }

    return Array.from(
        { length: rows },
        () => Array(columns).fill(fill)
    );
}

function printMatrix(matrix, title = "") {
    if (title) {
        console.log(`\n${title}`);
    }

    if (matrix.length === 0) {
        console.log("[]");
        return;
    }

    for (const row of matrix) {
        console.log(row.map(value => String(value).padStart(6)).join(" "));
    }
}

function identityMatrix(size) {
    const result = createMatrix(size, size);

    for (let i = 0; i < size; i++) {
        result[i][i] = 1;
    }

    return result;
}

// -----------------------------------------------------------------------------
// 2. ELEMENT ACCESS, UPDATE, AND INSERTION
// -----------------------------------------------------------------------------

function getElement(matrix, row, column) {
    validateMatrix(matrix, false);

    if (
        row < 0 ||
        row >= matrix.length ||
        column < 0 ||
        column >= matrix[0].length
    ) {
        throw new RangeError("Matrix index is outside the valid range.");
    }

    return matrix[row][column];
}

function setElement(matrix, row, column, value) {
    validateMatrix(matrix, false);

    if (
        row < 0 ||
        row >= matrix.length ||
        column < 0 ||
        column >= matrix[0].length
    ) {
        throw new RangeError("Matrix index is outside the valid range.");
    }

    matrix[row][column] = value;
}

function insertRow(matrix, index, newRow) {
    validateMatrix(matrix);

    if (matrix.length > 0 && newRow.length !== matrix[0].length) {
        throw new Error("Inserted row has incompatible dimensions.");
    }

    if (index < 0 || index > matrix.length) {
        throw new RangeError("Row insertion index is invalid.");
    }

    matrix.splice(index, 0, [...newRow]);
}

function insertColumn(matrix, index, values) {
    validateMatrix(matrix, false);

    const [rows, columns] = shape(matrix);

    if (values.length !== rows) {
        throw new Error("Column must contain one value per row.");
    }

    if (index < 0 || index > columns) {
        throw new RangeError("Column insertion index is invalid.");
    }

    for (let row = 0; row < rows; row++) {
        matrix[row].splice(index, 0, values[row]);
    }
}

// -----------------------------------------------------------------------------
// 3. TRAVERSAL
// -----------------------------------------------------------------------------

function rowMajor(matrix) {
    validateMatrix(matrix);

    return matrix.flat();
}

function columnMajor(matrix) {
    validateMatrix(matrix);

    if (matrix.length === 0) return [];

    const [rows, columns] = shape(matrix);
    const result = [];

    for (let column = 0; column < columns; column++) {
        for (let row = 0; row < rows; row++) {
            result.push(matrix[row][column]);
        }
    }

    return result;
}

function mainDiagonal(matrix) {
    validateMatrix(matrix);

    const [rows, columns] = shape(matrix);
    const result = [];

    for (let i = 0; i < Math.min(rows, columns); i++) {
        result.push(matrix[i][i]);
    }

    return result;
}

function secondaryDiagonal(matrix) {
    validateMatrix(matrix);

    const [rows, columns] = shape(matrix);
    const result = [];

    for (let i = 0; i < Math.min(rows, columns); i++) {
        result.push(matrix[i][columns - 1 - i]);
    }

    return result;
}

function boundaryTraversal(matrix) {
    validateMatrix(matrix);

    if (matrix.length === 0) return [];

    const [rows, columns] = shape(matrix);

    if (rows === 1) return [...matrix[0]];

    if (columns === 1) {
        return matrix.map(row => row[0]);
    }

    const result = [];

    for (let column = 0; column < columns; column++) {
        result.push(matrix[0][column]);
    }

    for (let row = 1; row < rows - 1; row++) {
        result.push(matrix[row][columns - 1]);
    }

    for (let column = columns - 1; column >= 0; column--) {
        result.push(matrix[rows - 1][column]);
    }

    for (let row = rows - 2; row >= 1; row--) {
        result.push(matrix[row][0]);
    }

    return result;
}

function spiralTraversal(matrix) {
    validateMatrix(matrix);

    if (matrix.length === 0) return [];

    const [rows, columns] = shape(matrix);

    let top = 0;
    let bottom = rows - 1;
    let left = 0;
    let right = columns - 1;

    const result = [];

    while (top <= bottom && left <= right) {
        for (let column = left; column <= right; column++) {
            result.push(matrix[top][column]);
        }
        top++;

        for (let row = top; row <= bottom; row++) {
            result.push(matrix[row][right]);
        }
        right--;

        if (top <= bottom) {
            for (let column = right; column >= left; column--) {
                result.push(matrix[bottom][column]);
            }
            bottom--;
        }

        if (left <= right) {
            for (let row = bottom; row >= top; row--) {
                result.push(matrix[row][left]);
            }
            left++;
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// 4. ARITHMETIC OPERATIONS
// -----------------------------------------------------------------------------

function requireSameShape(a, b) {
    const shapeA = shape(a);
    const shapeB = shape(b);

    if (shapeA[0] !== shapeB[0] || shapeA[1] !== shapeB[1]) {
        throw new Error("Matrices must have identical dimensions.");
    }
}

function addMatrices(a, b) {
    validateMatrix(a);
    validateMatrix(b);
    requireSameShape(a, b);

    return a.map((row, i) =>
        row.map((value, j) => value + b[i][j])
    );
}

function subtractMatrices(a, b) {
    validateMatrix(a);
    validateMatrix(b);
    requireSameShape(a, b);

    return a.map((row, i) =>
        row.map((value, j) => value - b[i][j])
    );
}

function scalarMultiply(matrix, scalar) {
    validateMatrix(matrix);

    return matrix.map(row =>
        row.map(value => value * scalar)
    );
}

function multiplyMatrices(a, b) {
    validateMatrix(a);
    validateMatrix(b);

    const [aRows, aColumns] = shape(a);
    const [bRows, bColumns] = shape(b);

    if (aColumns !== bRows) {
        throw new Error(
            "A's column count must equal B's row count."
        );
    }

    const result = createMatrix(aRows, bColumns);

    for (let i = 0; i < aRows; i++) {
        for (let j = 0; j < bColumns; j++) {
            for (let k = 0; k < aColumns; k++) {
                result[i][j] += a[i][k] * b[k][j];
            }
        }
    }

    return result;
}

function transpose(matrix) {
    validateMatrix(matrix);

    if (matrix.length === 0) return [];

    const [rows, columns] = shape(matrix);

    return Array.from(
        { length: columns },
        (_, column) =>
            Array.from(
                { length: rows },
                (_, row) => matrix[row][column]
            )
    );
}

// -----------------------------------------------------------------------------
// 5. PROPERTIES AND SEARCH
// -----------------------------------------------------------------------------

function isSquare(matrix) {
    const [rows, columns] = shape(matrix);
    return rows === columns;
}

function isSymmetric(matrix, tolerance = 0) {
    validateMatrix(matrix);

    if (!isSquare(matrix)) return false;

    const size = matrix.length;

    for (let i = 0; i < size; i++) {
        for (let j = i + 1; j < size; j++) {
            if (Math.abs(matrix[i][j] - matrix[j][i]) > tolerance) {
                return false;
            }
        }
    }

    return true;
}

function rowSums(matrix) {
    validateMatrix(matrix);
    return matrix.map(row => row.reduce((sum, value) => sum + value, 0));
}

function columnSums(matrix) {
    validateMatrix(matrix);

    if (matrix.length === 0) return [];

    const [, columns] = shape(matrix);
    const sums = Array(columns).fill(0);

    for (const row of matrix) {
        for (let column = 0; column < columns; column++) {
            sums[column] += row[column];
        }
    }

    return sums;
}

function findAll(matrix, target) {
    validateMatrix(matrix);

    const positions = [];

    for (let i = 0; i < matrix.length; i++) {
        for (let j = 0; j < matrix[i].length; j++) {
            if (matrix[i][j] === target) {
                positions.push([i, j]);
            }
        }
    }

    return positions;
}

// -----------------------------------------------------------------------------
// 6. ROTATIONS
// -----------------------------------------------------------------------------

function rotateClockwise(matrix) {
    return transpose(matrix).map(row => [...row].reverse());
}

function rotateCounterClockwise(matrix) {
    return transpose(matrix).reverse();
}

function reverseRows(matrix) {
    return matrix.map(row => [...row].reverse());
}

function reverseColumns(matrix) {
    return [...matrix].reverse().map(row => [...row]);
}

// -----------------------------------------------------------------------------
// 7. DETERMINANT
// -----------------------------------------------------------------------------

function determinant(matrix) {
    validateMatrix(matrix);

    if (!isSquare(matrix)) {
        throw new Error("Determinant requires a square matrix.");
    }

    const size = matrix.length;

    if (size === 0) return 1;

    if (size === 1) return matrix[0][0];

    if (size === 2) {
        return (
            matrix[0][0] * matrix[1][1] -
            matrix[0][1] * matrix[1][0]
        );
    }

    let result = 0;

    for (let column = 0; column < size; column++) {
        const minor = [];

        for (let row = 1; row < size; row++) {
            const minorRow = [];

            for (let otherColumn = 0; otherColumn < size; otherColumn++) {
                if (otherColumn !== column) {
                    minorRow.push(matrix[row][otherColumn]);
                }
            }

            minor.push(minorRow);
        }

        const sign = column % 2 === 0 ? 1 : -1;

        result += sign * matrix[0][column] * determinant(minor);
    }

    return result;
}

// -----------------------------------------------------------------------------
// 8. GAUSS-JORDAN ELIMINATION
// -----------------------------------------------------------------------------

function gaussianElimination(matrix, tolerance = 1e-10) {
    validateMatrix(matrix);

    const result = matrix.map(row => row.map(Number));

    if (result.length === 0) return result;

    const [rows, columns] = shape(result);
    let pivotRow = 0;

    for (let pivotColumn = 0; pivotColumn < columns; pivotColumn++) {
        if (pivotRow >= rows) break;

        let bestRow = pivotRow;

        for (let row = pivotRow + 1; row < rows; row++) {
            if (
                Math.abs(result[row][pivotColumn]) >
                Math.abs(result[bestRow][pivotColumn])
            ) {
                bestRow = row;
            }
        }

        if (Math.abs(result[bestRow][pivotColumn]) <= tolerance) {
            continue;
        }

        [result[pivotRow], result[bestRow]] =
            [result[bestRow], result[pivotRow]];

        const pivot = result[pivotRow][pivotColumn];

        for (let column = 0; column < columns; column++) {
            result[pivotRow][column] /= pivot;
        }

        for (let row = 0; row < rows; row++) {
            if (row === pivotRow) continue;

            const factor = result[row][pivotColumn];

            if (Math.abs(factor) <= tolerance) continue;

            for (let column = 0; column < columns; column++) {
                result[row][column] -=
                    factor * result[pivotRow][column];
            }
        }

        pivotRow++;
    }

    for (let row = 0; row < rows; row++) {
        for (let column = 0; column < columns; column++) {
            if (Math.abs(result[row][column]) < tolerance) {
                result[row][column] = 0;
            }
        }
    }

    return result;
}

function inverseMatrix(matrix, tolerance = 1e-10) {
    validateMatrix(matrix);

    if (!isSquare(matrix)) {
        throw new Error("Only square matrices have inverses.");
    }

    const size = matrix.length;

    if (size === 0) return [];

    const identity = identityMatrix(size);

    const augmented = matrix.map((row, i) => [
        ...row.map(Number),
        ...identity[i]
    ]);

    const reduced = gaussianElimination(augmented, tolerance);

    for (let row = 0; row < size; row++) {
        for (let column = 0; column < size; column++) {
            const expected = row === column ? 1 : 0;

            if (
                Math.abs(reduced[row][column] - expected) >
                1e-7
            ) {
                throw new Error("Matrix is singular or non-invertible.");
            }
        }
    }

    return reduced.map(row => row.slice(size));
}

// -----------------------------------------------------------------------------
// 9. SPARSE MATRIX
// -----------------------------------------------------------------------------

class SparseMatrix {
    constructor(rows, columns) {
        if (rows < 0 || columns < 0) {
            throw new Error("Dimensions cannot be negative.");
        }

        this.rows = rows;
        this.columns = columns;
        this.values = new Map();
    }

    key(row, column) {
        return `${row},${column}`;
    }

    validatePosition(row, column) {
        if (
            row < 0 ||
            row >= this.rows ||
            column < 0 ||
            column >= this.columns
        ) {
            throw new RangeError("Position is outside the matrix.");
        }
    }

    set(row, column, value) {
        this.validatePosition(row, column);

        const key = this.key(row, column);

        if (value === 0) {
            this.values.delete(key);
        } else {
            this.values.set(key, value);
        }
    }

    get(row, column) {
        this.validatePosition(row, column);
        return this.values.get(this.key(row, column)) ?? 0;
    }

    toDense() {
        const result = createMatrix(this.rows, this.columns);

        for (const [key, value] of this.values.entries()) {
            const [row, column] = key.split(",").map(Number);
            result[row][column] = value;
        }

        return result;
    }

    static fromDense(matrix) {
        validateMatrix(matrix);

        const [rows, columns] = shape(matrix);
        const sparse = new SparseMatrix(rows, columns);

        for (let row = 0; row < rows; row++) {
            for (let column = 0; column < columns; column++) {
                if (matrix[row][column] !== 0) {
                    sparse.set(row, column, matrix[row][column]);
                }
            }
        }

        return sparse;
    }
}

// -----------------------------------------------------------------------------
// 10. TWO-DIMENSIONAL PREFIX SUMS
// -----------------------------------------------------------------------------

class PrefixSumMatrix {
    constructor(matrix) {
        validateMatrix(matrix);

        const [rows, columns] = shape(matrix);

        this.prefix = createMatrix(rows + 1, columns + 1);

        for (let row = 1; row <= rows; row++) {
            for (let column = 1; column <= columns; column++) {
                this.prefix[row][column] =
                    matrix[row - 1][column - 1] +
                    this.prefix[row - 1][column] +
                    this.prefix[row][column - 1] -
                    this.prefix[row - 1][column - 1];
            }
        }
    }

    query(top, left, bottom, right) {
        const rows = this.prefix.length - 1;
        const columns = this.prefix[0].length - 1;

        if (
            top < 0 ||
            left < 0 ||
            bottom >= rows ||
            right >= columns ||
            top > bottom ||
            left > right
        ) {
            throw new RangeError("Invalid rectangular query.");
        }

        return (
            this.prefix[bottom + 1][right + 1] -
            this.prefix[top][right + 1] -
            this.prefix[bottom + 1][left] +
            this.prefix[top][left]
        );
    }
}

// -----------------------------------------------------------------------------
// 11. DEMONSTRATIONS
// -----------------------------------------------------------------------------

function demonstrateBasics() {
    console.log("\n" + "=".repeat(78));
    console.log("1. MATRIX BASICS");
    console.log("=".repeat(78));

    const matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ];

    printMatrix(matrix, "Original matrix:");
    console.log("Shape:", shape(matrix));
    console.log("matrix[1][2]:", getElement(matrix, 1, 2));

    setElement(matrix, 1, 2, 50);
    printMatrix(matrix, "After updating one element:");
}

function demonstrateTraversal() {
    console.log("\n" + "=".repeat(78));
    console.log("2. TRAVERSAL");
    console.log("=".repeat(78));

    const matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ];

    printMatrix(matrix);
    console.log("Row-major:", rowMajor(matrix));
    console.log("Column-major:", columnMajor(matrix));
    console.log("Main diagonal:", mainDiagonal(matrix));
    console.log("Secondary diagonal:", secondaryDiagonal(matrix));
    console.log("Boundary:", boundaryTraversal(matrix));
    console.log("Spiral:", spiralTraversal(matrix));
}

function demonstrateOperations() {
    console.log("\n" + "=".repeat(78));
    console.log("3. MATRIX ARITHMETIC");
    console.log("=".repeat(78));

    const a = [
        [1, 2],
        [3, 4]
    ];

    const b = [
        [5, 6],
        [7, 8]
    ];

    printMatrix(addMatrices(a, b), "A + B:");
    printMatrix(subtractMatrices(a, b), "A - B:");
    printMatrix(scalarMultiply(a, 3), "3A:");
    printMatrix(multiplyMatrices(a, b), "AB:");
    printMatrix(transpose(a), "Transpose of A:");
}

function demonstrateInsertion() {
   
