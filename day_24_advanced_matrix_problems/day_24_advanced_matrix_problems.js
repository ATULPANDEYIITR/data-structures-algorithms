/*
 * Advanced Matrix Problems
 *
 * This file demonstrates matrix algorithms from fundamental operations
 * through grid algorithms, prefix sums, searching, dynamic programming,
 * sparse representation, and practical image-style processing.
 *
 * Runtime: Node.js or a modern browser JavaScript engine.
 */

"use strict";

// -----------------------------------------------------------------------------
// Validation and display helpers
// -----------------------------------------------------------------------------

function validateMatrix(matrix, allowEmpty = false) {
    if (!Array.isArray(matrix)) {
        throw new TypeError("Matrix must be an array of arrays.");
    }

    if (matrix.length === 0) {
        if (allowEmpty) return;
        throw new Error("Matrix must not be empty.");
    }

    if (!matrix.every(Array.isArray)) {
        throw new TypeError("Every matrix row must be an array.");
    }

    const columns = matrix[0].length;

    if (columns === 0) {
        throw new Error("Matrix rows must not be empty.");
    }

    if (!matrix.every(row => row.length === columns)) {
        throw new Error("Matrix must be rectangular.");
    }
}

function validateSquareMatrix(matrix) {
    validateMatrix(matrix);

    if (matrix.length !== matrix[0].length) {
        throw new Error("Operation requires a square matrix.");
    }
}

function cloneMatrix(matrix) {
    validateMatrix(matrix);
    return matrix.map(row => [...row]);
}

function printMatrix(matrix, title = "") {
    if (title) {
        console.log(`\n${title}`);
    }

    for (const row of matrix) {
        console.log(row.map(value => String(value).padStart(5)).join(" "));
    }
}

// -----------------------------------------------------------------------------
// Fundamental matrix operations
// -----------------------------------------------------------------------------

function transpose(matrix) {
    validateMatrix(matrix);

    const rows = matrix.length;
    const columns = matrix[0].length;

    return Array.from(
        { length: columns },
        (_, column) =>
            Array.from(
                { length: rows },
                (_, row) => matrix[row][column]
            )
    );
}

function transposeSquareInPlace(matrix) {
    validateSquareMatrix(matrix);

    for (let row = 0; row < matrix.length; row++) {
        for (let column = row + 1; column < matrix.length; column++) {
            [matrix[row][column], matrix[column][row]] =
                [matrix[column][row], matrix[row][column]];
        }
    }
}

function rotate90Clockwise(matrix) {
    validateMatrix(matrix);

    const rows = matrix.length;
    const columns = matrix[0].length;

    return Array.from(
        { length: columns },
        (_, column) =>
            Array.from(
                { length: rows },
                (_, offset) => matrix[rows - 1 - offset][column]
            )
    );
}

function rotate90Counterclockwise(matrix) {
    validateMatrix(matrix);

    const rows = matrix.length;
    const columns = matrix[0].length;

    return Array.from(
        { length: columns },
        (_, column) =>
            Array.from(
                { length: rows },
                (_, offset) => matrix[offset][columns - 1 - column]
            )
    );
}

function rotateSquareInPlaceClockwise(matrix) {
    validateSquareMatrix(matrix);

    transposeSquareInPlace(matrix);

    for (const row of matrix) {
        row.reverse();
    }
}

function rotateSquare(matrix, degrees) {
    validateSquareMatrix(matrix);

    if (degrees % 90 !== 0) {
        throw new Error("Degrees must be a multiple of 90.");
    }

    const result = cloneMatrix(matrix);
    const rotations = ((degrees / 90) % 4 + 4) % 4;

    for (let i = 0; i < rotations; i++) {
        rotateSquareInPlaceClockwise(result);
    }

    return result;
}

// -----------------------------------------------------------------------------
// Traversal
// -----------------------------------------------------------------------------

function boundaryTraversal(matrix) {
    validateMatrix(matrix);

    const rows = matrix.length;
    const columns = matrix[0].length;

    if (rows === 1) return [...matrix[0]];

    if (columns === 1) {
        return matrix.map(row => row[0]);
    }

    const result = [];

    for (let column = 0; column < columns; column++) {
        result.push(matrix[0][column]);
    }

    for (let row = 1; row < rows; row++) {
        result.push(matrix[row][columns - 1]);
    }

    for (let column = columns - 2; column >= 0; column--) {
        result.push(matrix[rows - 1][column]);
    }

    for (let row = rows - 2; row > 0; row--) {
        result.push(matrix[row][0]);
    }

    return result;
}

function spiralTraversal(matrix) {
    validateMatrix(matrix);

    let top = 0;
    let bottom = matrix.length - 1;
    let left = 0;
    let right = matrix[0].length - 1;

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
// Searching
// -----------------------------------------------------------------------------

function binarySearch(array, target) {
    let left = 0;
    let right = array.length - 1;

    while (left <= right) {
        const middle = Math.floor((left + right) / 2);

        if (array[middle] === target) return middle;

        if (array[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

function searchSortedMatrixByRows(matrix, target) {
    validateMatrix(matrix);

    for (let row = 0; row < matrix.length; row++) {
        const column = binarySearch(matrix[row], target);

        if (column !== -1) {
            return [row, column];
        }
    }

    return null;
}

function searchRowColumnSortedMatrix(matrix, target) {
    validateMatrix(matrix);

    let row = 0;
    let column = matrix[0].length - 1;

    while (
        row < matrix.length &&
        column >= 0
    ) {
        const value = matrix[row][column];

        if (value === target) {
            return [row, column];
        }

        if (value > target) {
            column--;
        } else {
            row++;
        }
    }

    return null;
}

function searchFullySortedMatrix(matrix, target) {
    validateMatrix(matrix);

    const rows = matrix.length;
    const columns = matrix[0].length;

    let left = 0;
    let right = rows * columns - 1;

    while (left <= right) {
        const middle = Math.floor((left + right) / 2);

        const row = Math.floor(middle / columns);
        const column = middle % columns;
        const value = matrix[row][column];

        if (value === target) {
            return [row, column];
        }

        if (value < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return null;
}

// -----------------------------------------------------------------------------
// Prefix sums
// -----------------------------------------------------------------------------

function buildPrefixSum(matrix) {
    validateMatrix(matrix);

    const rows = matrix.length;
    const columns = matrix[0].length;

    const prefix = Array.from(
        { length: rows + 1 },
        () => Array(columns + 1).fill(0)
    );

    for (let row = 0; row < rows; row++) {
        let runningSum = 0;

        for (let column = 0; column < columns; column++) {
            runningSum += matrix[row][column];

            prefix[row + 1][column + 1] =
                prefix[row][column + 1] +
                runningSum;
        }
    }

    return prefix;
}

function rectangleSum(prefix, top, left, bottom, right) {
    if (
        top < 0 ||
        left < 0 ||
        bottom < top ||
        right < left
    ) {
        throw new Error("Invalid rectangle.");
    }

    if (
        bottom + 1 >= prefix.length ||
        right + 1 >= prefix[0].length
    ) {
        throw new Error("Rectangle exceeds matrix dimensions.");
    }

    return (
        prefix[bottom + 1][right + 1] -
        prefix[top][right + 1] -
        prefix[bottom + 1][left] +
        prefix[top][left]
    );
}

// -----------------------------------------------------------------------------
// Difference matrix
// -----------------------------------------------------------------------------

function createDifferenceMatrix(rows, columns) {
    if (rows <= 0 || columns <= 0) {
        throw new Error("Dimensions must be positive.");
    }

    return Array.from(
        { length: rows + 1 },
        () => Array(columns + 1).fill(0)
    );
}

function differenceRectangleUpdate(
    difference,
    top,
    left,
    bottom,
    right,
    value
) {
    const rows = difference.length - 1;
    const columns = difference[0].length - 1;

    if (
        top < 0 ||
        left < 0 ||
        bottom >= rows ||
        right >= columns ||
        top > bottom ||
        left > right
    ) {
        throw new Error("Invalid update rectangle.");
    }

    difference[top][left] += value;
    difference[bottom + 1][left] -= value;
    difference[top][right + 1] -= value;
    difference[bottom + 1][right + 1] += value;
}

function materializeDifferenceMatrix(difference) {
    const rows = difference.length - 1;
    const columns = difference[0].length - 1;

    const result = Array.from(
        { length: rows },
        () => Array(columns).fill(0)
    );

    for (let row = 0; row < rows; row++) {
        for (let column = 0; column < columns; column++) {
            let value = difference[row][column];

            if (row > 0) {
                value += result[row - 1][column];
            }

            if (column > 0) {
                value += result[row][column - 1];
            }

            if (row > 0 && column > 0) {
                value -= result[row - 1][column - 1];
            }

            result[row][column] = value;
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// Matrix multiplication and exponentiation
// -----------------------------------------------------------------------------

function multiplyMatrices(first, second) {
    validateMatrix(first);
    validateMatrix(second);

    const firstRows = first.length;
    const firstColumns = first[0].length;
    const secondRows = second.length;
    const secondColumns = second[0].length;

    if (firstColumns !== secondRows) {
        throw new Error(
            "Incompatible matrix dimensions for multiplication."
        );
    }

    const result = Array.from(
        { length: firstRows },
        () => Array(secondColumns).fill(0)
    );

    for (let row = 0; row < firstRows; row++) {
        for (let shared = 0; shared < firstColumns; shared++) {
            const value = first[row][shared];

            for (let column = 0; column < secondColumns; column++) {
                result[row][column] +=
                    value * second[shared][column];
            }
        }
    }

    return result;
}

function identityMatrix(size) {
    return Array.from(
        { length: size },
        (_, row) =>
            Array.from(
                { length: size },
                (_, column) => row === column ? 1 : 0
            )
    );
}

function matrixPower(matrix, exponent) {
    validateSquareMatrix(matrix);

    if (!Number.isInteger(exponent) || exponent < 0) {
        throw new Error("Exponent must be a non-negative integer.");
    }

    let result = identityMatrix(matrix.length);
    let base = cloneMatrix(matrix);
    let power = exponent;

    while (power > 0) {
        if (power % 2 === 1) {
            result = multiplyMatrices(result, base);
        }

        base = multiplyMatrices(base, base);
        power = Math.floor(power / 2);
    }

    return result;
}

// -----------------------------------------------------------------------------
// Maximum submatrix sum
// -----------------------------------------------------------------------------

function maximumSubarraySum(values) {
    if (values.length === 0) {
        throw new Error("Array must not be empty.");
    }

    let current = values[0];
    let best = values[0];

    for (let i = 1; i < values.length; i++) {
        current = Math.max(values[i], current + values[i]);
        best = Math.max(best, current);
    }

    return best;
}

function maximumSubmatrixSum(matrix) {
    validateMatrix(matrix);

    const rows = matrix.length;
    const columns = matrix[0].length;
    let best = -Infinity;

    for (let top = 0; top < rows; top++) {
        const compressed = Array(columns).fill(0);

        for (let bottom = top; bottom < rows; bottom++) {
            for (let column = 0; column < columns; column++) {
                compressed[column] += matrix[bottom][column];
            }

            best = Math.max(
                best,
                maximumSubarraySum(compressed)
            );
        }
    }

    return best;
}

// -----------------------------------------------------------------------------
// Largest rectangle of ones
// -----------------------------------------------------------------------------

function largestRectangleHistogram(heights) {
    const stack = [];
    let best = 0;
    const extended = [...heights, 0];

    for (let index = 0; index < extended.length; index++) {
        while (
            stack.length > 0 &&
            extended[stack[stack.length - 1]] > extended[index]
        ) {
            const top = stack.pop();
            const height = extended[top];
            const leftBoundary =
                stack.length > 0
                    ? stack[stack.length - 1]
                    : -1;

            const width = index - leftBoundary - 1;

            best = Math.max(
                best,
                height * width
            );
        }

        stack.push(index);
    }

    return best;
}

function largestRectangleOfOnes(matrix) {
    validateMatrix(matrix);

    if (!matrix.every(row =>
        row.every(value => value === 0 || value === 1)
    )) {
        throw new Error("Matrix must be binary.");
    }

    const columns = matrix[0].length;
    const heights = Array(columns).fill(0);
    let best = 0;

    for (const row of matrix) {
        for (let column = 0; column < columns; column++) {
            heights[column] =
                row[column] === 1
                    ? heights[column] + 1
                    : 0;
        }

        best = Math.max(
            best,
            largestRectangleHistogram(heights)
        );
    }

    return best;
}

// -----------------------------------------------------------------------------
// Grid algorithms
// -----------------------------------------------------------------------------

const DIRECTIONS_4 = [
    [-1, 0],
    [1, 0],
    [0, -1],
    [0, 1]
];

function validateBinaryGrid(grid) {
    validateMatrix(grid);

    if (!grid.every(row =>
        row.every(value => value === 0 || value === 1)
    )) {
        throw new Error("Grid must contain only 0 and 1.");
    }
}

function floodFill(grid, startRow, startColumn, replacement) {
    validateMatrix(grid);

    const result = cloneMatrix(grid);
    const rows = result.length;
    const columns = result[0].length;

    if (
        startRow < 0 ||
        startRow >= rows ||
        startColumn < 0 ||
        startColumn >= columns
    ) {
        throw new Error("Starting point is outside the grid.");
    }

    const original = result[startRow][startColumn];

    if (original === replacement) {
        return result;
    }

    // JavaScript arrays do not have a native deque, so a moving head index
    // avoids the O(n) cost that repeated shift() operations can introduce.
    const queue = [[startRow, startColumn]];
    let head = 0;

    result[startRow][startColumn] = replacement;

    while (head < queue.length) {
        const [row, column] = queue[head++];

        for (const [dr, dc] of DIRECTIONS_4) {
            const nextRow = row + dr;
            const nextColumn = column + dc;

            if (
                nextRow < 0 ||
                nextRow >= rows ||
                nextColumn < 0 ||
                nextColumn >= columns
            ) {
                continue;
            }

            if (result[nextRow][nextColumn] !== original) {
                continue;
            }

            result[nextRow][nextColumn] = replacement;
            queue.push([nextRow, nextColumn]);
        }
    }

    return result;
}

function countIslands(grid) {
    validateBinaryGrid(grid);

    const rows = grid.length;
    const columns = grid[0].length;

    const visited = Array.from(
        { length: rows },
        () => Array(columns).fill(false)
    );

    let islands = 0;

    for (let row = 0; row < rows; row++) {
        for (let column = 0; column < columns; column++) {
            if (
                grid[row][column] === 0 ||
                visited[row][column]
            ) {
                continue;
            }

            islands++;

            const queue = [[row, column]];
            let head = 0;

            visited[row][column] = true;

            while (head < queue.length) {
                const [currentRow, currentColumn] = queue[head++];

                for (const [dr, dc] of DIRECTIONS_4) {
                    const nextRow = currentRow + dr;
                    const nextColumn = currentColumn + dc;

                    if (
                        nextRow < 0 ||
                        nextRow >= rows ||
                        nextColumn < 0 ||
                        nextColumn >= columns
                    ) {
                        continue;
                    }

                    if (
                        visited[nextRow][nextColumn] ||
                        grid[nextRow][nextColumn] === 0
                    ) {
                        continue;
                    }

                    visited[nextRow][nextColumn] = true;
                    queue.push([nextRow, nextColumn]);
                }
            }
        }
    }

    return islands;
}

function shortestPathBinaryGrid(grid, start, goal) {
    validateBinaryGrid(grid);

    const rows = grid.length;
    const columns = grid[0].length;

    const inBounds = ([row, column]) =>
        row >= 0 &&
        row < rows &&
        column >= 0 &&
        column < columns;

    if (!inBounds(start) || !inBounds(goal)) {
        throw new Error("Start or goal is outside the grid.");
    }

    if (
        grid[start[0]][start[1]] !== 0 ||
        grid[goal[0]][goal[1]] !== 0
    ) {
        return -1;
    }

    const key = ([row, column]) => `${row},${column}`;
    const visited = new Set([key(start)]);
    const queue = [[start[0], start[1], 0]];
    let head = 0;

    while (head < queue.length) {
        const [row, column, distance] = queue[head++];

        if (row === goal[0] && column === goal[1]) {
            return distance;
        }

        for (const [dr, dc] of DIRECTIONS_4) {
            const next = [row + dr, column + dc];

            if (!inBounds(next)) continue;
            if (grid[next[0]][next[1]] !== 0) continue;

            const nextKey = key(next);

            if (visited.has(nextKey)) continue;

            visited.add(nextKey);
            queue.push([next[0], next[1], distance + 1]);
        }
    }

    return -1;
}

// -----------------------------------------------------------------------------
// Dynamic programming on a grid
// -----------------------------------------------------------------------------

function minimumCostGridPath(costs) {
    validateMatrix(costs);

    const rows = costs.length;
    const columns = costs[0].length;

    const dp = Array.from(
        { length: rows },
        () => Array(columns).fill(0)
    );

    dp[0][0] = costs[0][0];

    for (let column = 1; column < columns; column++) {
        dp[0][column] =
            dp[0][column - 1] +
            costs[0][column];
    }

    for (let row = 1; row < rows; row++) {
        dp[row][0] =
            dp[row - 1][0] +
            costs[row][0];
    }

    for (let row = 1; row < rows; row++) {
        for (let column = 1; column < columns; column++) {
            dp[row][column] =
                costs[row][column] +
                Math.min(
                    dp[row - 1][column],
                    dp[row][column - 1]
                );
        }
    }

    return dp[rows - 1][columns - 1];
}

// -----------------------------------------------------------------------------
// Sparse matrix using Map
// -----------------------------------------------------------------------------

class SparseMatrix {
    constructor(rows, columns) {
        if (rows <= 0 || columns <= 0) {
            throw new Error("Dimensions must be positive.");
        }

        this.rows = rows;
        this.columns = columns;

        // Map keys are "row,column". Only non-zero values are stored.
        this.values = new Map();
    }

    _key(row, column) {
        this._validatePosition(row, column);
        return `${row},${column}`;
    }

    _validatePosition(row, column) {
        if (
            row < 0 ||
            row >= this.rows ||
            column < 0 ||
            column >= this.columns
        ) {
            throw new Error("Position is outside the matrix.");
        }
    }

    get(row, column) {
        return this.values.get(this._key(row, column)) ?? 0;
    }

    set(row, column, value) {
        const key = this._key(row, column);

        if (value === 0) {
            this.values.delete(key);
        } else {
            this.values.set(key, value);
        }
    }

    toDense() {
        const matrix = Array.from(
            { length: this.rows },
            () => Array(this.columns).fill(0)
        );

        for (const [key, value] of this.values) {
            const [row, column] = key.split(",").map(Number);
            matrix[row][column] = value;
        }

        return matrix;
    }

    get nonZeroCount() {
        return this.values.size;
    }

    get density() {
        return this.nonZeroCount / (this.rows * this.columns);
    }
}

// -----------------------------------------------------------------------------
// Async matrix processing
// -----------------------------------------------------------------------------

async function processMatrixAsync(matrix) {
    /*
     * Promise-based asynchronous processing is useful when matrix work is
     * integrated into an application pipeline. This example does not claim
     * that JavaScript's event loop makes CPU-heavy matrix multiplication
     * automatically parallel. Heavy CPU work can block the event loop and
     * should use Web Workers or worker_threads when necessary.
     */
    validateMatrix(matrix);

    await Promise.resolve();

    return {
        rows: matrix.length,
        columns: matrix[0].length,
        sum: matrix
            .flat()
            .reduce((total, value) => total + value, 0),
        transpose: transpose(matrix)
    };
}

// -----------------------------------------------------------------------------
// Testing
// -----------------------------------------------------------------------------

function assertEqual(actual, expected, message) {
    const actualText = JSON.stringify(actual);
    const expectedText = JSON.stringify(expected);

    if (actualText !== expectedText) {
        throw new Error(
            `${message}\nExpected: ${expectedText}\nActual: ${actualText}`
        );
    }
}

function runTests() {
    const matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ];

    assertEqual(
        transpose(matrix),
        [
            [1, 4, 7],
            [2, 5, 8],
            [3, 6, 9]
        ],
        "Transpose failed."
    );

    assertEqual(
        rotate90Clockwise(matrix),
        [
            [7, 4, 1],
            [8, 5, 2],
            [9, 6, 3]
        ],
        "Clockwise rotation failed."
    );

    assertEqual(
        rotate90Counterclockwise(matrix),
        [
            [3, 6, 9],
            [2, 5, 8],
            [1, 4, 7]
        ],
        "Counterclockwise rotation failed."
    );

    assertEqual(
        spiralTraversal(matrix),
        [1, 2, 3, 6, 9, 8, 7, 4, 5],
        "Spiral traversal failed."
    );

    const sortedMatrix = [
        [1, 4, 7, 11],
        [2, 5, 8, 12],
        [3, 6, 9, 16],
        [10, 13, 14, 17]
    ];

    assertEqual(
        searchRowColumnSortedMatrix(sortedMatrix, 9),
        [2, 2],
        "Staircase search failed."
    );

    const fullySorted = [
        [1, 3, 5],
        [7, 9, 11],
        [13, 15, 17]
    ];

    assertEqual(
        searchFullySortedMatrix(fullySorted, 15),
        [2, 1],
        "Flattened binary search failed."
    );

    const prefix = buildPrefixSum([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]);

    assertEqual(
        rectangleSum(prefix, 1, 1, 2, 2),
        28,
        "Rectangle sum failed."
    );

    assertEqual(
        multiplyMatrices(
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]]
        ),
        [[19, 22], [43, 50]],
        "Matrix multiplication failed."
    );

    assertEqual(
        matrixPower(
            [[1, 1], [1, 0]],
            5
        ),
        [[8, 5], [5, 3]],
        "Matrix power failed."
    );

    assertEqual(
        largestRectangleOfOnes([
            [1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ]),
        9,
        "Largest rectangle failed."
    );

    assertEqual(
        countIslands([
            [1, 1, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 1]
        ]),
        2,
        "Island counting failed."
    );

    assertEqual(
        shortestPathBinaryGrid(
            [
                [0, 1, 0, 0],
                [0, 1, 0, 1],
                [0, 0, 0, 1],
                [1, 1, 0, 0]
            ],
            [0, 0],
            [3, 3]
        ),
        6,
        "Shortest path failed."
    );

    const sparse = new SparseMatrix(3, 4);
    sparse.set(0, 3, 7);
    sparse.set(2, 1, 3);

    assertEqual(
        sparse.toDense(),
        [
            [0, 0, 0, 7],
            [0, 0, 0, 0],
            [0, 3, 0, 0]
        ],
        "Sparse matrix failed."
    );

    console.log("All JavaScript tests passed.");
}

// -----------------------------------------------------------------------------
// Demonstration
// -----------------------------------------------------------------------------

async function main() {
    console.log("=".repeat(80));
    console.log("ADVANCED MATRIX PROBLEMS");
    console.log("=".repeat(80));

    const matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ];

    printMatrix(matrix, "Original matrix");
    printMatrix(transpose(matrix), "Transpose");
    printMatrix(rotate90Clockwise(matrix), "90-degree clockwise rotation");
    printMatrix(
        rotate90Counterclockwise(matrix),
        "90-degree counterclockwise rotation"
    );

    console.log("\nBoundary traversal:");
    console.log(boundaryTraversal(matrix));

    console.log("\nSpiral traversal:");
    console.log(spiralTraversal(matrix));

    const sortedMatrix = [
        [1, 4, 7, 10],
        [2, 5, 8, 12],
        [3, 6, 9, 16],
        [11, 13, 14, 20]
    ];

    console.log(
        "\nRow-wise binary search:",
        searchSortedMatrixByRows(sortedMatrix, 14)
    );

    console.log(
        "Staircase search:",
        searchRowColumnSortedMatrix(sortedMatrix, 14)
    );

    const prefix = buildPrefixSum([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]);

    printMatrix(prefix, "Prefix sum matrix");

    console.log(
        "\nRectangle sum:",
        rectangleSum(prefix, 1, 1, 2, 2)
    );

    const difference = createDifferenceMatrix(5, 6);

    differenceRectangleUpdate(
        difference,
        1,
        1,
        3,
        4,
        10
    );

    differenceRectangleUpdate(
        difference,
        0,
        2,
        2,
        5,
        5
    );

    printMatrix(
        materializeDifferenceMatrix(difference),
        "Difference-matrix updates"
    );

    printMatrix(
        multiplyMatrices(
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]]
        ),
        "Matrix multiplication"
    );

    printMatrix(
        matrixPower(
            [[1, 1], [1, 0]],
            10
        ),
        "Matrix power"
    );

    console.log(
        "\nMaximum submatrix sum:",
        maximumSubmatrixSum([
            [2, -1, 3],
            [-4, 5, -2],
            [1, 2, 6]
        ])
    );

    console.log(
        "\nLargest all-1 rectangle:",
        largestRectangleOfOnes([
            [1, 0, 1, 1, 1],
            [1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ])
    );

    const grid = [
        [1, 1, 0, 0, 0],
        [1, 0, 0, 1, 1],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 0, 0]
    ];

    console.log("\nIsland count:", countIslands(grid));

    printMatrix(
        floodFill(
            [
                [1, 1, 1, 2],
                [1, 1, 0, 2],
                [1, 0, 0, 2]
            ],
            0,
            0,
            9
        ),
        "Flood fill"
    );

    console.log(
        "\nShortest path:",
        shortestPathBinaryGrid(
            [
                [0, 1, 0, 0, 0],
                [0, 1, 0, 1, 0],
                [0, 0, 0, 1, 0],
                [1, 1, 0, 0, 0]
            ],
            [0, 0],
            [3, 4]
        )
    );

    console.log(
        "\nMinimum grid cost:",
        minimumCostGridPath([
            [1, 3, 1, 2],
            [1, 5, 1, 1],
            [4, 2, 1, 3]
        ])
    );

    const sparse = new SparseMatrix(4, 4);
    sparse.set(0, 3, 7);
    sparse.set(2, 1, 3);

    console.log("\nSparse matrix density:", sparse.density);
    printMatrix(sparse.toDense(), "Sparse matrix converted to dense");

    const asyncResult = await processMatrixAsync([
        [1, 2],
        [3, 4]
    ]);

    console.log("\nAsynchronous processing result:");
    console.log(asyncResult);

    runTests();
}

main().catch(error => {
    console.error("Program failed:", error.message);
    process.exitCode = 1;
});
