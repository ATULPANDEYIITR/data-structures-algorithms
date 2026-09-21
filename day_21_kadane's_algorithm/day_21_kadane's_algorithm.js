"use strict";

/*
 * Kadane's Algorithm: Maximum and Minimum Subarray Study
 *
 * This file complements the Python implementation with JavaScript-specific
 * demonstrations of:
 * - arrays and contiguous ranges
 * - Kadane's algorithm
 * - index recovery
 * - minimum subarray
 * - circular subarrays
 * - fixed-size sliding windows
 * - prefix sums
 * - monotonic deque logic
 * - maximum product subarray
 * - one-deletion dynamic programming
 * - streaming state
 * - randomized verification
 * - JavaScript number and BigInt considerations
 *
 * Run with:
 * node kadane.js
 */

// ---------------------------------------------------------------------------
// Utility functions
// ---------------------------------------------------------------------------

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function validateNonEmpty(numbers) {
    if (!Array.isArray(numbers) || numbers.length === 0) {
        throw new Error("The array must contain at least one element.");
    }

    for (const value of numbers) {
        if (!Number.isFinite(value) || !Number.isInteger(value)) {
            throw new Error("This implementation expects finite integers.");
        }
    }
}

function validateK(numbers, k) {
    validateNonEmpty(numbers);

    if (!Number.isInteger(k) || k < 1 || k > numbers.length) {
        throw new Error("k must satisfy 1 <= k <= numbers.length.");
    }
}

// ---------------------------------------------------------------------------
// 1. Basic Kadane
// ---------------------------------------------------------------------------

function kadane(numbers) {
    validateNonEmpty(numbers);

    let bestEndingHere = numbers[0];
    let bestSoFar = numbers[0];

    for (let i = 1; i < numbers.length; i++) {
        const value = numbers[i];

        // Either extend the previous subarray or start again here.
        bestEndingHere = Math.max(value, bestEndingHere + value);
        bestSoFar = Math.max(bestSoFar, bestEndingHere);
    }

    return bestSoFar;
}

// ---------------------------------------------------------------------------
// 2. Recover the actual subarray
// ---------------------------------------------------------------------------

function kadaneWithIndices(numbers) {
    validateNonEmpty(numbers);

    let bestEndingHere = numbers[0];
    let bestSoFar = numbers[0];

    let currentStart = 0;
    let bestStart = 0;
    let bestEnd = 0;

    for (let i = 1; i < numbers.length; i++) {
        const value = numbers[i];

        if (value > bestEndingHere + value) {
            bestEndingHere = value;
            currentStart = i;
        } else {
            bestEndingHere += value;
        }

        if (bestEndingHere > bestSoFar) {
            bestSoFar = bestEndingHere;
            bestStart = currentStart;
            bestEnd = i;
        }
    }

    return {
        sum: bestSoFar,
        start: bestStart,
        end: bestEnd,
        values: numbers.slice(bestStart, bestEnd + 1)
    };
}

// ---------------------------------------------------------------------------
// 3. Minimum subarray
// ---------------------------------------------------------------------------

function minimumSubarray(numbers) {
    validateNonEmpty(numbers);

    let minimumEndingHere = numbers[0];
    let minimumSoFar = numbers[0];

    for (let i = 1; i < numbers.length; i++) {
        const value = numbers[i];

        minimumEndingHere = Math.min(
            value,
            minimumEndingHere + value
        );

        minimumSoFar = Math.min(
            minimumSoFar,
            minimumEndingHere
        );
    }

    return minimumSoFar;
}

function minimumSubarrayWithIndices(numbers) {
    validateNonEmpty(numbers);

    let bestEndingHere = numbers[0];
    let bestSoFar = numbers[0];

    let currentStart = 0;
    let bestStart = 0;
    let bestEnd = 0;

    for (let i = 1; i < numbers.length; i++) {
        const value = numbers[i];

        if (value < bestEndingHere + value) {
            bestEndingHere = value;
            currentStart = i;
        } else {
            bestEndingHere += value;
        }

        if (bestEndingHere < bestSoFar) {
            bestSoFar = bestEndingHere;
            bestStart = currentStart;
            bestEnd = i;
        }
    }

    return {
        sum: bestSoFar,
        start: bestStart,
        end: bestEnd
    };
}

// ---------------------------------------------------------------------------
// 4. Circular maximum
// ---------------------------------------------------------------------------

function maximumCircularSubarray(numbers) {
    validateNonEmpty(numbers);

    const ordinaryMaximum = kadane(numbers);

    // total - minimum represents a wrapping range.
    // For all-negative arrays this would create the empty complement,
    // so ordinary Kadane must be returned.
    if (ordinaryMaximum < 0) {
        return ordinaryMaximum;
    }

    const total = numbers.reduce((sum, value) => sum + value, 0);
    const minimum = minimumSubarray(numbers);

    return Math.max(
        ordinaryMaximum,
        total - minimum
    );
}

// ---------------------------------------------------------------------------
// 5. Circular minimum
// ---------------------------------------------------------------------------

function minimumCircularSubarray(numbers) {
    validateNonEmpty(numbers);

    const ordinaryMinimum = minimumSubarray(numbers);

    // For all-positive arrays, total - maximum represents an empty
    // complement and must not be treated as a valid non-empty subarray.
    if (ordinaryMinimum > 0) {
        return ordinaryMinimum;
    }

    const total = numbers.reduce((sum, value) => sum + value, 0);
    const maximum = kadane(numbers);

    return Math.min(
        ordinaryMinimum,
        total - maximum
    );
}

// ---------------------------------------------------------------------------
// 6. Fixed-length maximum
// ---------------------------------------------------------------------------

function maximumFixedLengthSubarray(numbers, k) {
    validateK(numbers, k);

    let windowSum = 0;

    for (let i = 0; i < k; i++) {
        windowSum += numbers[i];
    }

    let bestSum = windowSum;
    let bestStart = 0;

    for (let right = k; right < numbers.length; right++) {
        windowSum += numbers[right];
        windowSum -= numbers[right - k];

        const start = right - k + 1;

        if (windowSum > bestSum) {
            bestSum = windowSum;
            bestStart = start;
        }
    }

    return {
        sum: bestSum,
        start: bestStart,
        end: bestStart + k - 1
    };
}

// ---------------------------------------------------------------------------
// 7. Prefix sums
// ---------------------------------------------------------------------------

function buildPrefixSums(numbers) {
    const prefix = new Array(numbers.length + 1);
    prefix[0] = 0;

    for (let i = 0; i < numbers.length; i++) {
        prefix[i + 1] = prefix[i] + numbers[i];
    }

    return prefix;
}

// ---------------------------------------------------------------------------
// 8. Maximum subarray with at most k elements
// ---------------------------------------------------------------------------

function maximumSubarrayAtMostK(numbers, k) {
    validateK(numbers, k);

    const prefix = buildPrefixSums(numbers);

    // JavaScript does not have a standard deque with O(1) popleft().
    // head points to the logical front so Array.shift() is avoided.
    const deque = [];
    let head = 0;

    deque.push(0);

    let best = Number.NEGATIVE_INFINITY;

    for (let right = 1; right < prefix.length; right++) {
        while (
            head < deque.length &&
            deque[head] < right - k
        ) {
            head++;
        }

        best = Math.max(
            best,
            prefix[right] - prefix[deque[head]]
        );

        while (
            deque.length > head &&
            prefix[deque[deque.length - 1]] >= prefix[right]
        ) {
            deque.pop();
        }

        deque.push(right);

        // Periodically compact the array so stale front entries do not
        // accumulate forever in very long streams.
        if (head > 1024 && head * 2 > deque.length) {
            deque.splice(0, head);
            head = 0;
        }
    }

    return best;
}

// ---------------------------------------------------------------------------
// 9. Maximum subarray with at least k elements
// ---------------------------------------------------------------------------

function maximumSubarrayAtLeastK(numbers, k) {
    validateK(numbers, k);

    const prefix = buildPrefixSums(numbers);

    let minimumPrefix = prefix[0];
    let best = Number.NEGATIVE_INFINITY;

    for (let right = k; right < prefix.length; right++) {
        minimumPrefix = Math.min(
            minimumPrefix,
            prefix[right - k]
        );

        best = Math.max(
            best,
            prefix[right] - minimumPrefix
        );
    }

    return best;
}

// ---------------------------------------------------------------------------
// 10. Maximum product subarray
// ---------------------------------------------------------------------------

function maximumProductSubarray(numbers) {
    validateNonEmpty(numbers);

    let maximumEnding = numbers[0];
    let minimumEnding = numbers[0];
    let best = numbers[0];

    for (let i = 1; i < numbers.length; i++) {
        const value = numbers[i];

        const candidates = [
            value,
            maximumEnding * value,
            minimumEnding * value
        ];

        maximumEnding = Math.max(...candidates);
        minimumEnding = Math.min(...candidates);

        best = Math.max(best, maximumEnding);
    }

    return best;
}

// ---------------------------------------------------------------------------
// 11. Maximum sum with one deletion
// ---------------------------------------------------------------------------

function maximumSubarrayOneDeletion(numbers) {
    validateNonEmpty(numbers);

    let noDeletion = numbers[0];
    let oneDeletion = Number.NEGATIVE_INFINITY;
    let best = numbers[0];

    for (let i = 1; i < numbers.length; i++) {
        const value = numbers[i];

        const previousNoDeletion = noDeletion;
        const previousOneDeletion = oneDeletion;

        noDeletion = Math.max(
            value,
            previousNoDeletion + value
        );

        // Delete the current value, or continue after an earlier deletion.
        oneDeletion = Math.max(
            value,
            previousOneDeletion + value,
            previousNoDeletion
        );

        best = Math.max(
            best,
            noDeletion,
            oneDeletion
        );
    }

    return best;
}

// ---------------------------------------------------------------------------
// 12. Target-sum subarray counting
// ---------------------------------------------------------------------------

function countSubarraysWithSum(numbers, target) {
    const frequency = new Map();
    frequency.set(0, 1);

    let prefix = 0;
    let count = 0;

    for (const value of numbers) {
        prefix += value;

        count += frequency.get(prefix - target) ?? 0;

        frequency.set(
            prefix,
            (frequency.get(prefix) ?? 0) + 1
        );
    }

    return count;
}

// ---------------------------------------------------------------------------
// 13. Streaming Kadane
// ---------------------------------------------------------------------------

class StreamingKadane {
    constructor() {
        this.hasValue = false;
        this.bestEndingHere = 0;
        this.bestSoFar = Number.NEGATIVE_INFINITY;
    }

    add(value) {
        if (!Number.isFinite(value)) {
            throw new Error("Streaming input must be finite.");
        }

        if (!this.hasValue) {
            this.bestEndingHere = value;
            this.bestSoFar = value;
            this.hasValue = true;
        } else {
            this.bestEndingHere = Math.max(
                value,
                this.bestEndingHere + value
            );

            this.bestSoFar = Math.max(
                this.bestSoFar,
                this.bestEndingHere
            );
        }

        return this.bestSoFar;
    }

    result() {
        if (!this.hasValue) {
            throw new Error("No values have been added.");
        }

        return this.bestSoFar;
    }
}

// ---------------------------------------------------------------------------
// 14. Brute-force reference implementation
// ---------------------------------------------------------------------------

function bruteForceMaximumSubarray(numbers) {
    validateNonEmpty(numbers);

    let best = numbers[0];

    for (let start = 0; start < numbers.length; start++) {
        let sum = 0;

        for (let end = start; end < numbers.length; end++) {
            sum += numbers[end];
            best = Math.max(best, sum);
        }
    }

    return best;
}

// ---------------------------------------------------------------------------
// 15. BigInt variant
// ---------------------------------------------------------------------------

function kadaneBigInt(numbers) {
    if (!Array.isArray(numbers) || numbers.length === 0) {
        throw new Error("A non-empty BigInt array is required.");
    }

    for (const value of numbers) {
        if (typeof value !== "bigint") {
            throw new Error("Every value must be a BigInt.");
        }
    }

    let bestEndingHere = numbers[0];
    let bestSoFar = numbers[0];

    for (let i = 1; i < numbers.length; i++) {
        const value = numbers[i];

        bestEndingHere =
            value > bestEndingHere + value
                ? value
                : bestEndingHere + value;

        if (bestEndingHere > bestSoFar) {
            bestSoFar = bestEndingHere;
        }
    }

    return bestSoFar;
}

// JavaScript Number is floating-point. Integer arithmetic is exact only
// within the safe integer range. BigInt is appropriate when sums may exceed
// Number.MAX_SAFE_INTEGER, but Number and BigInt cannot be mixed directly.

// ---------------------------------------------------------------------------
// 16. Demonstrations
// ---------------------------------------------------------------------------

function demonstrate() {
    console.log("=".repeat(78));
    console.log("KADANE'S ALGORITHM STUDY");
    console.log("=".repeat(78));

    const numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4];

    console.log("\nBasic Kadane:");
    console.log(kadane(numbers));

    console.log("\nRecovered range:");
    console.log(kadaneWithIndices(numbers));

    console.log("\nMinimum subarray:");
    console.log(minimumSubarrayWithIndices(numbers));

    console.log("\nCircular maximum:");
    console.log(maximumCircularSubarray([5, -3, 5]));

    console.log("\nCircular minimum:");
    console.log(minimumCircularSubarray([5, -3, 5]));

    console.log("\nFixed-length maximum:");
    console.log(
        maximumFixedLengthSubarray(
            [1, 2, 3, -2, 5],
            3
        )
    );

    console.log("\nAt most k:");
    console.log(
        maximumSubarrayAtMostK(
            [2, -1, 2, 3, -9, 4, 6, -2],
            4
        )
    );

    console.log("\nAt least k:");
    console.log(
        maximumSubarrayAtLeastK(
            [2, -1, 2, 3, -9, 4, 6, -2],
            3
        )
    );

    console.log("\nMaximum product:");
    console.log(
        maximumProductSubarray([2, 3, -2, 4])
    );

    console.log("\nOne deletion:");
    console.log(
        maximumSubarrayOneDeletion([1, -2, 0, 3])
    );

    console.log("\nCount target-sum subarrays:");
    console.log(
        countSubarraysWithSum([1, 1, 1], 2)
    );

    console.log("\nStreaming:");
    const stream = new StreamingKadane();

    for (const value of numbers) {
        console.log(
            `Added ${value}: ${stream.add(value)}`
        );
    }

    console.log("\nBigInt:");
    console.log(
        kadaneBigInt([
            9007199254740992n,
            -1n,
            5n
        ])
    );
}

// ---------------------------------------------------------------------------
// 17. Randomized verification
// ---------------------------------------------------------------------------

function randomInteger(min, max) {
    return Math.floor(
        Math.random() * (max - min + 1)
    ) + min;
}

function verifyKadane() {
    for (let test = 0; test < 1000; test++) {
        const length = randomInteger(1, 10);
        const numbers = Array.from(
            { length },
            () => randomInteger(-10, 10)
        );

        const expected = bruteForceMaximumSubarray(numbers);
        const actual = kadane(numbers);

        assert(
            expected === actual,
            `Mismatch for ${JSON.stringify(numbers)}`
        );
    }

    console.log(
        "\nRandomized Kadane verification: PASSED"
    );
}

// ---------------------------------------------------------------------------
// 18. Edge-case tests
// ---------------------------------------------------------------------------

function runAssertions() {
    assert(
        kadane([-2, 1, -3, 4, -1, 2, 1, -5, 4]) === 6,
        "classic Kadane example"
    );

    assert(
        kadane([-8, -3, -6, -2, -5]) === -2,
        "all-negative array"
    );

    assert(
        kadane([7]) === 7,
        "single element"
    );

    assert(
        maximumCircularSubarray([5, -3, 5]) === 10,
        "circular maximum"
    );

    assert(
        maximumCircularSubarray([-3, -2, -1]) === -1,
        "circular all-negative"
    );

    assert(
        minimumSubarray([3, -4, 2, -1]) === -4,
        "minimum subarray"
    );

    assert(
        maximumProductSubarray([2, 3, -2, 4]) === 6,
        "maximum product"
    );

    assert(
        maximumSubarrayOneDeletion([1, -2, 0, 3]) === 4,
        "one deletion"
    );

    assert(
        countSubarraysWithSum([1, 1, 1], 2) === 2,
        "target sum counting"
    );

    console.log(
        "Deterministic assertions: PASSED"
    );
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
    demonstrate();
    runAssertions();
    verifyKadane();

    console.log("\nAll JavaScript demonstrations completed.");
}

main();
