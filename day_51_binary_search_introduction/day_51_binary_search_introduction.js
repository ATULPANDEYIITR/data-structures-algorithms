"use strict";

/*
 * Binary Search Introduction.
 * Runtime: Node.js 18+
 *
 * The implementation uses a sorted numeric array and a closed interval
 * [left, right]. A separate lowerBound operation demonstrates how the
 * same boundary idea supports insertion-position queries.
 */

class BinarySearchError extends Error {
    constructor(message) {
        super(message);
        this.name = "BinarySearchError";
    }
}

function validateSorted(values) {
    if (!Array.isArray(values)) {
        throw new BinarySearchError("Input must be an array.");
    }

    for (let i = 1; i < values.length; i += 1) {
        if (!Number.isFinite(values[i - 1]) || !Number.isFinite(values[i])) {
            throw new BinarySearchError("All values must be finite numbers.");
        }

        if (values[i - 1] > values[i]) {
            throw new BinarySearchError(
                "Binary search requires non-decreasing sorted data."
            );
        }
    }
}

function binarySearchIterative(values, target) {
    validateSorted(values);

    if (!Number.isFinite(target)) {
        throw new BinarySearchError("Target must be a finite number.");
    }

    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] === target) {
            return middle;
        }

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

function binarySearchRecursive(values, target, left = 0, right = values.length - 1) {
    if (left === 0 && right === values.length - 1) {
        validateSorted(values);
        if (!Number.isFinite(target)) {
            throw new BinarySearchError("Target must be a finite number.");
        }
    }

    if (left > right) {
        return -1;
    }

    const middle = left + Math.floor((right - left) / 2);

    if (values[middle] === target) {
        return middle;
    }

    if (values[middle] < target) {
        return binarySearchRecursive(values, target, middle + 1, right);
    }

    return binarySearchRecursive(values, target, left, middle - 1);
}

function lowerBound(values, target) {
    validateSorted(values);

    let left = 0;
    let right = values.length;

    while (left < right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] < target) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return left;
}

function upperBound(values, target) {
    validateSorted(values);

    let left = 0;
    let right = values.length;

    while (left < right) {
        const middle = left + Math.floor((right - left) / 2);

        if (values[middle] <= target) {
            left = middle + 1;
        } else {
            right = middle;
        }
    }

    return left;
}

class SearchSession {
    constructor(values) {
        validateSorted(values);
        this.values = Object.freeze([...values]);
        this.history = [];
    }

    find(target) {
        const index = binarySearchIterative(this.values, target);

        this.history.push({
            target,
            index,
            found: index !== -1,
            timestamp: new Date().toISOString()
        });

        return index;
    }

    report() {
        return {
            size: this.values.length,
            queries: this.history.length,
            successfulQueries: this.history.filter((item) => item.found).length
        };
    }
}

async function runDemo() {
    const values = [-20, -10, -1, 0, 4, 4, 4, 9, 15, 21, 42];
    const session = new SearchSession(values);

    console.log("Sorted data:", values);

    for (const target of [-20, 4, 5, 42, 100]) {
        const iterative = session.find(target);
        const recursive = binarySearchRecursive(values, target);
        const first = lowerBound(values, target);
        const after = upperBound(values, target);

        console.log({
            target,
            iterative,
            recursive,
            insertionPosition: first,
            matchingRange:
                first < values.length && values[first] === target
                    ? [first, after - 1]
                    : null
        });
    }

    console.log("Session report:", session.report());

    try {
        binarySearchIterative([1, 7, 3, 9], 7);
    } catch (error) {
        console.log("Validation failure handled:", error.message);
    }
}

runDemo().catch((error) => {
    console.error("Unexpected failure:", error);
    process.exitCode = 1;
});
