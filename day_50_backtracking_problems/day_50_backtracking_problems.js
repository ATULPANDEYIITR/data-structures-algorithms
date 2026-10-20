"use strict";

/*
 * Backtracking case study:
 * - subsets and unique subsets
 * - permutations and unique permutations
 * - combinations
 * - N-Queens
 * - Sudoku
 * - grid path finding
 *
 * The implementation uses generators for potentially large result sets.
 * A caller can stop iteration early, which prevents unnecessary memory use.
 */

function validateArray(values, name) {
    if (!Array.isArray(values)) {
        throw new TypeError(`${name} must be an array`);
    }
    if (values.some((value) => value === null || value === undefined)) {
        throw new TypeError(`${name} cannot contain null or undefined`);
    }
}

function* subsets(values) {
    validateArray(values, "values");
    const current = [];

    function* backtrack(index) {
        if (index === values.length) {
            yield [...current];
            return;
        }

        yield* backtrack(index + 1);

        current.push(values[index]);
        yield* backtrack(index + 1);
        current.pop();
    }

    yield* backtrack(0);
}

function* uniqueSubsets(values) {
    validateArray(values, "values");

    const sorted = [...values].sort((a, b) => a - b);
    const current = [];

    function* backtrack(start) {
        yield [...current];

        for (let index = start; index < sorted.length; index++) {
            if (index > start && sorted[index] === sorted[index - 1]) {
                continue;
            }

            current.push(sorted[index]);
            yield* backtrack(index + 1);
            current.pop();
        }
    }

    yield* backtrack(0);
}

function* permutations(values) {
    validateArray(values, "values");

    const unique = new Set(values);
    if (unique.size !== values.length) {
        throw new Error("permutations requires distinct values");
    }

    const current = [];
    const used = new Array(values.length).fill(false);

    function* backtrack() {
        if (current.length === values.length) {
            yield [...current];
            return;
        }

        for (let index = 0; index < values.length; index++) {
            if (used[index]) continue;

            used[index] = true;
            current.push(values[index]);

            yield* backtrack();

            current.pop();
            used[index] = false;
        }
    }

    yield* backtrack();
}

function* uniquePermutations(values) {
    validateArray(values, "values");

    const sorted = [...values].sort((a, b) => a - b);
    const current = [];
    const used = new Array(sorted.length).fill(false);

    function* backtrack() {
        if (current.length === sorted.length) {
            yield [...current];
            return;
        }

        for (let index = 0; index < sorted.length; index++) {
            if (used[index]) continue;

            if (
                index > 0 &&
                sorted[index] === sorted[index - 1] &&
                !used[index - 1]
            ) {
                continue;
            }

            used[index] = true;
            current.push(sorted[index]);

            yield* backtrack();

            current.pop();
            used[index] = false;
        }
    }

    yield* backtrack();
}

function* combinations(values, k) {
    validateArray(values, "values");

    if (!Number.isInteger(k)) {
        throw new TypeError("k must be an integer");
    }

    if (k < 0 || k > values.length) {
        return;
    }

    const current = [];

    function* backtrack(start) {
        if (current.length === k) {
            yield [...current];
            return;
        }

        const needed = k - current.length;
        const lastIndex = values.length - needed;

        for (let index = start; index <= lastIndex; index++) {
            current.push(values[index]);
            yield* backtrack(index + 1);
            current.pop();
        }
    }

    if (k === 0) {
        yield [];
        return;
    }

    yield* backtrack(0);
}

function solveNQueens(n) {
    if (!Number.isInteger(n) || n < 1) {
        throw new RangeError("n must be a positive integer");
    }

    const board = Array.from({ length: n }, () => Array(n).fill("."));
    const columns = new Set();
    const descending = new Set();
    const ascending = new Set();
    const solutions = [];

    function backtrack(row) {
        if (row === n) {
            solutions.push(board.map((line) => line.join("")));
            return;
        }

        for (let column = 0; column < n; column++) {
            if (columns.has(column)) continue;
            if (descending.has(row - column)) continue;
            if (ascending.has(row + column)) continue;

            board[row][column] = "Q";
            columns.add(column);
            descending.add(row - column);
            ascending.add(row + column);

            backtrack(row + 1);

            ascending.delete(row + column);
            descending.delete(row - column);
            columns.delete(column);
            board[row][column] = ".";
        }
    }

    backtrack(0);
    return solutions;
}

function validateSudoku(board) {
    if (
        !Array.isArray(board) ||
        board.length !== 9 ||
        board.some((row) => !Array.isArray(row) || row.length !== 9)
    ) {
        throw new TypeError("Sudoku board must be a 9x9 array");
    }

    for (const row of board) {
        for (const value of row) {
            if (!Number.isInteger(value) || value < 0 || value > 9) {
                throw new TypeError("Sudoku cells must contain integers from 0 to 9");
            }
        }
    }
}

function solveSudoku(board) {
    validateSudoku(board);

    const rows = Array.from({ length: 9 }, () => new Set());
    const columns = Array.from({ length: 9 }, () => new Set());
    const boxes = Array.from({ length: 9 }, () => new Set());
    const empty = [];

    for (let row = 0; row < 9; row++) {
        for (let column = 0; column < 9; column++) {
            const value = board[row][column];

            if (value === 0) {
                empty.push([row, column]);
                continue;
            }

            const box = Math.floor(row / 3) * 3 + Math.floor(column / 3);

            if (
                rows[row].has(value) ||
                columns[column].has(value) ||
                boxes[box].has(value)
            ) {
                return false;
            }

            rows[row].add(value);
            columns[column].add(value);
            boxes[box].add(value);
        }
    }

    function backtrack() {
        if (empty.length === 0) {
            return true;
        }

        let bestIndex = -1;
        let bestCandidates = null;

        for (let index = 0; index < empty.length; index++) {
            const [row, column] = empty[index];
            const box = Math.floor(row / 3) * 3 + Math.floor(column / 3);
            const candidates = [];

            for (let value = 1; value <= 9; value++) {
                if (
                    !rows[row].has(value) &&
                    !columns[column].has(value) &&
                    !boxes[box].has(value)
                ) {
                    candidates.push(value);
                }
            }

            if (candidates.length === 0) {
                return false;
            }

            if (bestCandidates === null || candidates.length < bestCandidates.length) {
                bestIndex = index;
                bestCandidates = candidates;

                if (candidates.length === 1) {
                    break;
                }
            }
        }

        const [row, column] = empty.splice(bestIndex, 1)[0];
        const box = Math.floor(row / 3) * 3 + Math.floor(column / 3);

        for (const value of bestCandidates) {
            board[row][column] = value;
            rows[row].add(value);
            columns[column].add(value);
            boxes[box].add(value);

            if (backtrack()) {
                return true;
            }

            boxes[box].delete(value);
            columns[column].delete(value);
            rows[row].delete(value);
            board[row][column] = 0;
        }

        empty.splice(bestIndex, 0, [row, column]);
        return false;
    }

    return backtrack();
}

function findPaths(grid, start, target, maxPaths = 1000) {
    if (!Array.isArray(grid) || grid.length === 0 || !Array.isArray(grid[0])) {
        throw new TypeError("grid must be a non-empty rectangular array");
    }

    const rows = grid.length;
    const columns = grid[0].length;

    if (columns === 0 || grid.some((row) => !Array.isArray(row) || row.length !== columns)) {
        throw new TypeError("grid must be rectangular");
    }

    if (maxPaths < 1) {
        return [];
    }

    const inside = ({ row, column }) =>
        row >= 0 &&
        row < rows &&
        column >= 0 &&
        column < columns;

    if (!inside(start) || !inside(target)) {
        throw new RangeError("start and target must be inside the grid");
    }

    if (grid[start.row][start.column] !== 0 || grid[target.row][target.column] !== 0) {
        return [];
    }

    const directions = [
        [1, 0],
        [-1, 0],
        [0, 1],
        [0, -1],
    ];

    const path = [start];
    const visited = new Set([`${start.row},${start.column}`]);
    const paths = [];

    function backtrack(position) {
        if (paths.length >= maxPaths) {
            return;
        }

        if (position.row === target.row && position.column === target.column) {
            paths.push([...path]);
            return;
        }

        for (const [dr, dc] of directions) {
            const next = {
                row: position.row + dr,
                column: position.column + dc,
            };

            if (!inside(next)) continue;
            if (grid[next.row][next.column] !== 0) continue;

            const key = `${next.row},${next.column}`;
            if (visited.has(key)) continue;

            visited.add(key);
            path.push(next);

            backtrack(next);

            path.pop();
            visited.delete(key);
        }
    }

    backtrack(start);
    return paths;
}

function delay(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function evaluateAsyncSearch(grid, start, target) {
    // Yielding periodically models event-loop-friendly processing for large searches.
    await delay(0);
    return findPaths(grid, start, target, 1);
}

async function main() {
    console.log("Subsets:", [...subsets([1, 2, 3])]);
    console.log("Unique subsets:", [...uniqueSubsets([1, 2, 2])]);

    console.log("Permutations:", [...permutations([1, 2, 3])]);
    console.log("Unique permutations:", [...uniquePermutations([1, 1, 2])]);

    console.log("Combinations:", [...combinations([1, 2, 3, 4], 2)]);

    const queens = solveNQueens(4);
    console.log("4-Queens solutions:", queens.length);
    console.log(queens);

    const sudoku = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 0],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ];

    console.log("Sudoku solved:", solveSudoku(sudoku));
    console.table(sudoku);

    const maze = [
        [0, 0, 1, 0, 0],
        [1, 0, 1, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 1, 0],
    ];

    console.log(
        "Async maze result:",
        await evaluateAsyncSearch(
            maze,
            { row: 0, column: 0 },
            { row: 4, column: 4 }
        )
    );
}

main().catch((error) => {
    console.error(`Backtracking execution failed: ${error.message}`);
    process.exitCode = 1;
});
