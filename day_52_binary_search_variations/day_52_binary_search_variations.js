"use strict";

/*
 * Binary-search variations using a half-open interval [left, right).
 *
 * The lower-bound and upper-bound primitives are deliberately separated
 * from exact-search logic because duplicate handling depends on where the
 * search boundary is moved after a match.
 */

function assertSorted(values) {
    for (let i = 1; i < values.length; i++) {
        if (values[i - 1] > values[i]) {
            throw new Error("Binary search requires sorted input.");
        }
    }
}

function lowerBound(values, target) {
    let left = 0;
    let right = values.length;

    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);

        if (values[mid] < target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }

    return left;
}

function upperBound(values, target) {
    let left = 0;
    let right = values.length;

    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);

        if (values[mid] <= target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }

    return left;
}

function exactSearch(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);

        if (values[mid] === target) {
            return mid;
        }

        if (values[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return -1;
}

function firstOccurrence(values, target) {
    const index = lowerBound(values, target);
    return index < values.length && values[index] === target ? index : -1;
}

function lastOccurrence(values, target) {
    const index = upperBound(values, target) - 1;
    return index >= 0 && values[index] === target ? index : -1;
}

function insertionPosition(values, target) {
    return lowerBound(values, target);
}

function occurrenceRange(values, target) {
    const first = firstOccurrence(values, target);

    if (first === -1) {
        return [-1, -1];
    }

    return [first, upperBound(values, target) - 1];
}

function countOccurrences(values, target) {
    return upperBound(values, target) - lowerBound(values, target);
}

function evaluateTarget(values, target) {
    return {
        target,
        exact: exactSearch(values, target),
        first: firstOccurrence(values, target),
        last: lastOccurrence(values, target),
        lowerBound: lowerBound(values, target),
        upperBound: upperBound(values, target),
        insertionPosition: insertionPosition(values, target),
        range: occurrenceRange(values, target),
        count: countOccurrences(values, target)
    };
}

function runTests() {
    const cases = [
        { values: [], targets: [0, 5] },
        { values: [5], targets: [4, 5, 6] },
        { values: [2, 2, 2, 2], targets: [1, 2, 3] },
        { values: [1, 2, 2, 4, 5, 5, 5, 9], targets: [0, 2, 3, 5, 10] },
        { values: [-8, -3, -3, 0, 7], targets: [-9, -3, 7, 8] }
    ];

    for (const testCase of cases) {
        assertSorted(testCase.values);

        for (const target of testCase.targets) {
            const lower = lowerBound(testCase.values, target);
            const upper = upperBound(testCase.values, target);

            if (lower < 0 || lower > testCase.values.length) {
                throw new Error("Invalid lower bound.");
            }

            if (upper < lower || upper > testCase.values.length) {
                throw new Error("Invalid upper bound.");
            }

            const expectedCount = testCase.values.filter(
                value => value === target
            ).length;

            if (countOccurrences(testCase.values, target) !== expectedCount) {
                throw new Error("Duplicate count verification failed.");
            }
        }
    }

    let rejected = false;

    try {
        assertSorted([3, 1, 2]);
    } catch {
        rejected = true;
    }

    if (!rejected) {
        throw new Error("Unsorted input was not rejected.");
    }

    console.log("All JavaScript verification tests passed.");
}

function main() {
    const values = [1, 2, 2, 2, 4, 4, 7, 9, 9, 12];
    const targets = [0, 2, 3, 4, 9, 13];

    assertSorted(values);

    console.table(targets.map(target => evaluateTarget(values, target)));
    runTests();
}

main();
