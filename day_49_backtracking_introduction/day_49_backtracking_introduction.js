"use strict";

/*
 * Backtracking is modeled here as an explicit search process:
 *
 * state -> choose -> validate -> recurse -> undo
 *
 * The JavaScript implementation emphasizes closures, event-style tracing,
 * generators, immutable snapshots at solution boundaries, and asynchronous
 * traversal of a search tree.
 */

function generateBinaryStrings(length) {
    if (!Number.isInteger(length) || length < 0) {
        throw new RangeError("length must be a non-negative integer");
    }

    const results = [];
    const path = [];

    function search() {
        if (path.length === length) {
            results.push(path.join(""));
            return;
        }

        for (const choice of ["0", "1"]) {
            path.push(choice);
            search();
            path.pop();
        }
    }

    search();
    return results;
}

function* generateSubsets(values) {
    const path = [];

    function* search(index) {
        if (index === values.length) {
            yield [...path];
            return;
        }

        // Exclude the current item.
        yield* search(index + 1);

        // Include the current item and restore the path afterward.
        path.push(values[index]);
        yield* search(index + 1);
        path.pop();
    }

    yield* search(0);
}

function generatePermutations(values) {
    const results = [];
    const path = [];
    const used = new Array(values.length).fill(false);

    function search() {
        if (path.length === values.length) {
            results.push([...path]);
            return;
        }

        for (let index = 0; index < values.length; index += 1) {
            if (used[index]) {
                continue;
            }

            used[index] = true;
            path.push(values[index]);

            search();

            path.pop();
            used[index] = false;
        }
    }

    search();
    return results;
}

function solveNQueens(n) {
    if (!Number.isInteger(n) || n <= 0) {
        throw new RangeError("n must be positive");
    }

    const board = Array.from({ length: n }, () => Array(n).fill("."));
    const columns = new Set();
    const diagonals = new Set();
    const antiDiagonals = new Set();
    const solutions = [];

    function search(row) {
        if (row === n) {
            solutions.push(board.map(line => line.join("")));
            return;
        }

        for (let column = 0; column < n; column += 1) {
            const diagonal = row - column;
            const antiDiagonal = row + column;

            if (
                columns.has(column) ||
                diagonals.has(diagonal) ||
                antiDiagonals.has(antiDiagonal)
            ) {
                continue;
            }

            board[row][column] = "Q";
            columns.add(column);
            diagonals.add(diagonal);
            antiDiagonals.add(antiDiagonal);

            search(row + 1);

            board[row][column] = ".";
            columns.delete(column);
            diagonals.delete(diagonal);
            antiDiagonals.delete(antiDiagonal);
        }
    }

    search(0);
    return solutions;
}

function findMazePaths(maze) {
    if (!Array.isArray(maze) || maze.length === 0 || maze[0].length === 0) {
        return [];
    }

    const rows = maze.length;
    const columns = maze[0].length;

    if (maze.some(row => row.length !== columns)) {
        throw new TypeError("maze must be rectangular");
    }

    if (maze[0][0] !== 0 || maze[rows - 1][columns - 1] !== 0) {
        return [];
    }

    const visited = Array.from(
        { length: rows },
        () => Array(columns).fill(false)
    );
    const path = [];
    const results = [];

    const directions = [
        ["D", 1, 0],
        ["R", 0, 1],
        ["U", -1, 0],
        ["L", 0, -1]
    ];

    function search(row, column) {
        if (row === rows - 1 && column === columns - 1) {
            results.push(path.join(""));
            return;
        }

        visited[row][column] = true;

        for (const [symbol, rowDelta, columnDelta] of directions) {
            const nextRow = row + rowDelta;
            const nextColumn = column + columnDelta;

            if (
                nextRow < 0 ||
                nextRow >= rows ||
                nextColumn < 0 ||
                nextColumn >= columns ||
                maze[nextRow][nextColumn] !== 0 ||
                visited[nextRow][nextColumn]
            ) {
                continue;
            }

            path.push(symbol);
            search(nextRow, nextColumn);
            path.pop();
        }

        visited[row][column] = false;
    }

    search(0, 0);
    return results;
}

function combinationSum(candidates, target) {
    if (!Number.isInteger(target) || target < 0) {
        throw new RangeError("target must be a non-negative integer");
    }

    const values = [...new Set(candidates)].sort((a, b) => a - b);

    if (
        values.some(
            value => !Number.isInteger(value) || value <= 0
        )
    ) {
        throw new TypeError("candidates must contain positive integers");
    }

    const path = [];
    const results = [];

    function search(start, remaining) {
        if (remaining === 0) {
            results.push([...path]);
            return;
        }

        for (let index = start; index < values.length; index += 1) {
            const value = values[index];

            if (value > remaining) {
                break;
            }

            path.push(value);
            search(index, remaining - value);
            path.pop();
        }
    }

    search(0, target);
    return results;
}

class BacktrackingTracer {
    constructor() {
        this.events = [];
    }

    record(type, state) {
        this.events.push({
            type,
            state: structuredClone(state),
            timestamp: Date.now()
        });
    }

    print() {
        for (const event of this.events) {
            console.log(
                `${event.type}:`,
                JSON.stringify(event.state)
            );
        }
    }
}

function tracedSubsetSearch(values, tracer) {
    const path = [];
    const results = [];

    function search(index) {
        tracer.record("enter", { index, path });

        if (index === values.length) {
            results.push([...path]);
            tracer.record("solution", { path });
            return;
        }

        tracer.record("exclude", { value: values[index], path });
        search(index + 1);

        path.push(values[index]);
        tracer.record("choose", { value: values[index], path });
        search(index + 1);

        path.pop();
        tracer.record("undo", { value: values[index], path });
    }

    search(0);
    return results;
}

async function* asynchronousBinarySearch(length) {
    const path = [];

    async function* search() {
        if (path.length === length) {
            yield path.join("");
            return;
        }

        for (const choice of ["0", "1"]) {
            path.push(choice);

            // Yielding control demonstrates how a large search can cooperate
            // with an event-driven runtime instead of monopolizing the loop.
            await Promise.resolve();
            yield* search();

            path.pop();
        }
    }

    yield* search();
}

async function collectAsync(generator) {
    const values = [];
    for await (const value of generator) {
        values.push(value);
    }
    return values;
}

function canBalanceWeights(weights, target) {
    const ordered = [...weights].sort((a, b) => b - a);
    const remaining = target;

    function search(index, total) {
        if (total === target) {
            return true;
        }

        if (total > target || index === ordered.length) {
            return false;
        }

        const weight = ordered[index];

        // Include branch.
        if (search(index + 1, total + weight)) {
            return true;
        }

        // Exclude branch.
        return search(index + 1, total);
    }

    return search(0, remaining);
}

async function main() {
    console.log("Backtracking with JavaScript");

    console.log("\nBinary decision tree");
    console.log(generateBinaryStrings(3));

    console.log("\nGenerator-based subset exploration");
    console.log([...generateSubsets([4, 7, 9])]);

    console.log("\nPermutation search");
    console.log(generatePermutations(["API", "DB", "UI"]));

    console.log("\nConstraint pruning with N-Queens");
    const queens = solveNQueens(4);
    queens.forEach(solution => console.log(solution.join("\n"), "\n"));

    console.log("\nMaze path exploration");
    const maze = [
        [0, 0, 1, 0],
        [1, 0, 1, 0],
        [0, 0, 0, 0],
        [0, 1, 1, 0]
    ];
    console.log(findMazePaths(maze));

    console.log("\nReusable-choice combination search");
    console.log(combinationSum([2, 3, 6, 7], 7));

    console.log("\nSearch tracing");
    const tracer = new BacktrackingTracer();
    tracedSubsetSearch(["read", "write"], tracer);
    tracer.print();

    console.log("\nAsynchronous state-space traversal");
    console.log(await collectAsync(asynchronousBinarySearch(3)));

    console.log("\nConstraint satisfaction");
    console.log(canBalanceWeights([8, 5, 3, 2], 10));
}

main().catch(error => {
    console.error("Backtracking execution failed:", error.message);
    process.exitCode = 1;
});
