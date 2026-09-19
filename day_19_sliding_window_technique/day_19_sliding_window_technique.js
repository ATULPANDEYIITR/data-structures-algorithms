"use strict";

/*
 * Sliding Window Technique
 *
 * This file complements the Python study implementation with JavaScript
 * examples. It covers arrays, strings, frequency maps, fixed windows,
 * variable windows, monotonic deques, validation, error handling,
 * performance, and an application-style event stream example.
 *
 * Run with:
 *     node sliding-window.js
 */

// ---------------------------------------------------------------------------
// 1. Fixed-size numeric windows
// ---------------------------------------------------------------------------

function maximumSumFixedWindow(numbers, k) {
    if (!Array.isArray(numbers)) {
        throw new TypeError("numbers must be an array");
    }
    if (!Number.isInteger(k) || k <= 0 || k > numbers.length) {
        throw new RangeError("k must satisfy 1 <= k <= numbers.length");
    }

    let windowSum = 0;

    for (let index = 0; index < k; index++) {
        windowSum += numbers[index];
    }

    let best = windowSum;

    for (let right = k; right < numbers.length; right++) {
        windowSum += numbers[right];
        windowSum -= numbers[right - k];
        best = Math.max(best, windowSum);
    }

    return best;
}

function minimumSumFixedWindow(numbers, k) {
    if (!Number.isInteger(k) || k <= 0 || k > numbers.length) {
        throw new RangeError("Invalid window size");
    }

    let windowSum = numbers.slice(0, k).reduce((sum, value) => sum + value, 0);
    let best = windowSum;

    for (let right = k; right < numbers.length; right++) {
        windowSum += numbers[right] - numbers[right - k];
        best = Math.min(best, windowSum);
    }

    return best;
}

// ---------------------------------------------------------------------------
// 2. Fixed-size windows with a monotonic deque
// ---------------------------------------------------------------------------

function maximumInEachWindow(numbers, k) {
    if (!Number.isInteger(k) || k <= 0 || k > numbers.length) {
        throw new RangeError("Invalid window size");
    }

    // JavaScript arrays do not have an efficient deque primitive.
    // A head pointer avoids repeated shift(), which is O(n).
    const candidates = [];
    let head = 0;
    const result = [];

    for (let right = 0; right < numbers.length; right++) {
        while (head < candidates.length &&
               candidates[head] <= right - k) {
            head++;
        }

        while (candidates.length > head &&
               numbers[candidates[candidates.length - 1]] <= numbers[right]) {
            candidates.pop();
        }

        candidates.push(right);

        if (right >= k - 1) {
            result.push(numbers[candidates[head]]);
        }

        // Periodically compact the backing array.
        if (head > 1024 && head * 2 > candidates.length) {
            candidates.splice(0, head);
            head = 0;
        }
    }

    return result;
}

function minimumInEachWindow(numbers, k) {
    if (!Number.isInteger(k) || k <= 0 || k > numbers.length) {
        throw new RangeError("Invalid window size");
    }

    const candidates = [];
    let head = 0;
    const result = [];

    for (let right = 0; right < numbers.length; right++) {
        while (head < candidates.length &&
               candidates[head] <= right - k) {
            head++;
        }

        while (candidates.length > head &&
               numbers[candidates[candidates.length - 1]] >= numbers[right]) {
            candidates.pop();
        }

        candidates.push(right);

        if (right >= k - 1) {
            result.push(numbers[candidates[head]]);
        }

        if (head > 1024 && head * 2 > candidates.length) {
            candidates.splice(0, head);
            head = 0;
        }
    }

    return result;
}

// ---------------------------------------------------------------------------
// 3. Frequency-map helper
// ---------------------------------------------------------------------------

function increment(map, key) {
    map.set(key, (map.get(key) ?? 0) + 1);
}

function decrement(map, key) {
    const next = (map.get(key) ?? 0) - 1;

    if (next <= 0) {
        map.delete(key);
    } else {
        map.set(key, next);
    }
}

// ---------------------------------------------------------------------------
// 4. Longest substring without repeating characters
// ---------------------------------------------------------------------------

function longestUniqueSubstring(text) {
    const lastSeen = new Map();
    let left = 0;
    let bestStart = 0;
    let bestLength = 0;

    // Array.from handles Unicode code points better than text[index],
    // although grapheme clusters such as emoji + modifiers may still
    // consist of multiple code points.
    const characters = Array.from(text);

    for (let right = 0; right < characters.length; right++) {
        const character = characters[right];

        if (lastSeen.has(character) && lastSeen.get(character) >= left) {
            left = lastSeen.get(character) + 1;
        }

        lastSeen.set(character, right);

        const length = right - left + 1;

        if (length > bestLength) {
            bestLength = length;
            bestStart = left;
        }
    }

    return {
        length: bestLength,
        substring: characters.slice(bestStart, bestStart + bestLength).join("")
    };
}

// ---------------------------------------------------------------------------
// 5. Longest substring with at most K distinct characters
// ---------------------------------------------------------------------------

function longestSubstringAtMostKDistinct(text, k) {
    if (k <= 0) {
        return { length: 0, substring: "" };
    }

    const characters = Array.from(text);
    const frequency = new Map();

    let left = 0;
    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < characters.length; right++) {
        increment(frequency, characters[right]);

        while (frequency.size > k) {
            decrement(frequency, characters[left]);
            left++;
        }

        const length = right - left + 1;

        if (length > bestLength) {
            bestLength = length;
            bestStart = left;
        }
    }

    return {
        length: bestLength,
        substring: characters.slice(bestStart, bestStart + bestLength).join("")
    };
}

// ---------------------------------------------------------------------------
// 6. Minimum window substring
// ---------------------------------------------------------------------------

function minimumWindowSubstring(text, required) {
    const source = Array.from(text);
    const target = Array.from(required);

    if (target.length === 0 || source.length === 0) {
        return "";
    }

    const requiredCounts = new Map();

    for (const character of target) {
        increment(requiredCounts, character);
    }

    const windowCounts = new Map();
    const requiredKinds = requiredCounts.size;

    let satisfiedKinds = 0;
    let left = 0;
    let bestStart = 0;
    let bestLength = Infinity;

    for (let right = 0; right < source.length; right++) {
        const character = source[right];
        increment(windowCounts, character);

        if (
            requiredCounts.has(character) &&
            windowCounts.get(character) === requiredCounts.get(character)
        ) {
            satisfiedKinds++;
        }

        while (satisfiedKinds === requiredKinds) {
            const length = right - left + 1;

            if (length < bestLength) {
                bestLength = length;
                bestStart = left;
            }

            const outgoing = source[left];
            decrement(windowCounts, outgoing);

            if (
                requiredCounts.has(outgoing) &&
                (windowCounts.get(outgoing) ?? 0) <
                    requiredCounts.get(outgoing)
            ) {
                satisfiedKinds--;
            }

            left++;
        }
    }

    return bestLength === Infinity
        ? ""
        : source.slice(bestStart, bestStart + bestLength).join("");
}

// ---------------------------------------------------------------------------
// 7. Anagram/permutation detection
// ---------------------------------------------------------------------------

function containsPermutation(text, pattern) {
    const source = Array.from(text);
    const target = Array.from(pattern);

    if (target.length === 0) {
        return true;
    }

    if (target.length > source.length) {
        return false;
    }

    const targetCounts = new Map();
    const windowCounts = new Map();

    for (const character of target) {
        increment(targetCounts, character);
    }

    let left = 0;
    let matchingKinds = 0;

    for (let right = 0; right < source.length; right++) {
        const character = source[right];
        increment(windowCounts, character);

        if (
            targetCounts.has(character) &&
            windowCounts.get(character) === targetCounts.get(character)
        ) {
            matchingKinds++;
        }

        if (right - left + 1 > target.length) {
            const outgoing = source[left];
            decrement(windowCounts, outgoing);

            if (
                targetCounts.has(outgoing) &&
                (windowCounts.get(outgoing) ?? 0) <
                    targetCounts.get(outgoing)
            ) {
                matchingKinds--;
            }

            left++;
        }

        if (matchingKinds === targetCounts.size &&
            right - left + 1 === target.length) {
            return true;
        }
    }

    return false;
}

// ---------------------------------------------------------------------------
// 8. Variable-size numeric window
// ---------------------------------------------------------------------------

function minimumLengthSubarrayAtLeastTarget(numbers, target) {
    if (target <= 0) {
        return 0;
    }

    // This implementation assumes non-negative numbers.
    let left = 0;
    let sum = 0;
    let best = Infinity;

    for (let right = 0; right < numbers.length; right++) {
        sum += numbers[right];

        while (sum >= target) {
            best = Math.min(best, right - left + 1);
            sum -= numbers[left];
            left++;
        }
    }

    return best === Infinity ? 0 : best;
}

// ---------------------------------------------------------------------------
// 9. Exactly K distinct subarrays
// ---------------------------------------------------------------------------

function countSubarraysAtMostKDistinct(numbers, k) {
    if (k < 0) {
        return 0;
    }

    const frequency = new Map();
    let left = 0;
    let result = 0;

    for (let right = 0; right < numbers.length; right++) {
        increment(frequency, numbers[right]);

        while (frequency.size > k) {
            decrement(frequency, numbers[left]);
            left++;
        }

        // Every start from left through right forms a valid subarray.
        result += right - left + 1;
    }

    return result;
}

function countSubarraysExactlyKDistinct(numbers, k) {
    return countSubarraysAtMostKDistinct(numbers, k) -
           countSubarraysAtMostKDistinct(numbers, k - 1);
}

// ---------------------------------------------------------------------------
// 10. Longest binary window with at most K zeroes
// ---------------------------------------------------------------------------

function longestOnesWithKFlips(binaryNumbers, k) {
    if (k < 0) {
        throw new RangeError("k cannot be negative");
    }

    let left = 0;
    let zeroes = 0;
    let best = 0;

    for (let right = 0; right < binaryNumbers.length; right++) {
        const value = binaryNumbers[right];

        if (value !== 0 && value !== 1) {
            throw new TypeError("Input must contain only 0 or 1");
        }

        if (value === 0) {
            zeroes++;
        }

        while (zeroes > k) {
            if (binaryNumbers[left] === 0) {
                zeroes--;
            }
            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}

// ---------------------------------------------------------------------------
// 11. Bounded-difference window using two monotonic queues
// ---------------------------------------------------------------------------

function longestSubarrayBoundedDifference(numbers, limit) {
    const maxQueue = [];
    const minQueue = [];
    let maxHead = 0;
    let minHead = 0;

    let left = 0;
    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < numbers.length; right++) {
        const value = numbers[right];

        while (
            maxQueue.length > maxHead &&
            numbers[maxQueue[maxQueue.length - 1]] <= value
        ) {
            maxQueue.pop();
        }
        maxQueue.push(right);

        while (
            minQueue.length > minHead &&
            numbers[minQueue[minQueue.length - 1]] >= value
        ) {
            minQueue.pop();
        }
        minQueue.push(right);

        while (
            numbers[maxQueue[maxHead]] -
                numbers[minQueue[minHead]] > limit
        ) {
            if (maxQueue[maxHead] === left) {
                maxHead++;
            }
            if (minQueue[minHead] === left) {
                minHead++;
            }
            left++;
        }

        const length = right - left + 1;

        if (length > bestLength) {
            bestLength = length;
            bestStart = left;
        }

        if (maxHead > 1024 && maxHead * 2 > maxQueue.length) {
            maxQueue.splice(0, maxHead);
            maxHead = 0;
        }

        if (minHead > 1024 && minHead * 2 > minQueue.length) {
            minQueue.splice(0, minHead);
            minHead = 0;
        }
    }

    return {
        length: bestLength,
        window: numbers.slice(bestStart, bestStart + bestLength)
    };
}

// ---------------------------------------------------------------------------
// 12. Event-stream monitoring case study
// ---------------------------------------------------------------------------

class RollingMetric {
    /*
     * A production-style monitoring component often needs a rolling metric
     * over the most recent N measurements.
     *
     * This class demonstrates:
     *   - fixed-size windows
     *   - incremental updates
     *   - validation
     *   - average calculation
     *   - threshold detection
     */
    constructor(windowSize, threshold) {
        if (!Number.isInteger(windowSize) || windowSize <= 0) {
            throw new RangeError("windowSize must be positive");
        }

        if (!Number.isFinite(threshold)) {
            throw new TypeError("threshold must be finite");
        }

        this.windowSize = windowSize;
        this.threshold = threshold;
        this.values = [];
        this.start = 0;
        this.sum = 0;
    }

    add(value) {
        if (!Number.isFinite(value)) {
            throw new TypeError("Metric values must be finite numbers");
        }

        this.values.push(value);
        this.sum += value;

        if (this.values.length - this.start > this.windowSize) {
            this.sum -= this.values[this.start];
            this.start++;
        }

        const size = this.values.length - this.start;
        const average = this.sum / size;

        return {
            size,
            average,
            thresholdExceeded: average > this.threshold
        };
    }

    currentWindow() {
        return this.values.slice(this.start);
    }
}

// ---------------------------------------------------------------------------
// 13. Assertions
// ---------------------------------------------------------------------------

function runAssertions() {
    console.assert(
        maximumSumFixedWindow([2, 1, 5, 1, 3, 2], 3) === 9
    );

    console.assert(
        minimumSumFixedWindow([2, 1, 5, 1, 3, 2], 3) === 6
    );

    console.assert(
        JSON.stringify(
            maximumInEachWindow([1, 3, -1, -3, 5, 3, 6, 7], 3)
        ) === JSON.stringify([3, 3, 5, 5, 6, 7])
    );

    console.assert(
        JSON.stringify(
            minimumInEachWindow([1, 3, -1, -3, 5, 3, 6, 7], 3)
        ) === JSON.stringify([-1, -3, -3, -3, 3, 3])
    );

    console.assert(
        minimumLengthSubarrayAtLeastTarget([2, 3, 1, 2, 4, 3], 7) === 2
    );

    console.assert(longestUniqueSubstring("abcabcbb").length === 3);

    console.assert(
        longestSubstringAtMostKDistinct("eceba", 2).length === 3
    );

    console.assert(
        minimumWindowSubstring("ADOBECODEBANC", "ABC") === "BANC"
    );

    console.assert(containsPermutation("oidbcaf", "abc") === true);

    console.assert(
        countSubarraysExactlyKDistinct([1, 2, 1, 2, 3], 2) === 7
    );

    console.assert(
        longestOnesWithKFlips([1, 1, 1, 0, 0, 0, 1, 1, 1, 1], 2) === 6
    );

    const bounded = longestSubarrayBoundedDifference([8, 2, 4, 7], 4);
    console.assert(bounded.length === 2);
    console.assert(JSON.stringify(bounded.window) === JSON.stringify([2, 4]));
}

// ---------------------------------------------------------------------------
// 14. Demonstration
// ---------------------------------------------------------------------------

function demonstrate() {
    console.log("\n=== FIXED-SIZE WINDOW ===");

    const numbers = [2, 1, 5, 1, 3, 2];

    console.log(
        "Maximum sum:",
        maximumSumFixedWindow(numbers, 3)
    );

    console.log(
        "Minimum sum:",
        minimumSumFixedWindow(numbers, 3)
    );

    console.log(
        "Maximum of each window:",
        maximumInEachWindow(
            [1, 3, -1, -3, 5, 3, 6, 7],
            3
        )
    );

    console.log(
        "Minimum of each window:",
        minimumInEachWindow(
            [1, 3, -1, -3, 5, 3, 6, 7],
            3
        )
    );

    console.log("\n=== STRING WINDOWS ===");

    console.log(
        "Longest unique substring:",
        longestUniqueSubstring("abcabcbb")
    );

    console.log(
        "At most two distinct:",
        longestSubstringAtMostKDistinct("eceba", 2)
    );

    console.log(
        "Minimum window:",
        minimumWindowSubstring("ADOBECODEBANC", "ABC")
    );

    console.log(
        "Permutation exists:",
        containsPermutation("oidbcaf", "abc")
    );

    console.log("\n=== VARIABLE WINDOWS ===");

    console.log(
        "Minimum length:",
        minimumLengthSubarrayAtLeastTarget([2, 3, 1, 2, 4, 3], 7)
    );

    console.log(
        "Exactly two distinct:",
        countSubarraysExactlyKDistinct([1, 2, 1, 2, 3], 2)
    );

    console.log(
        "Longest binary window:",
        longestOnesWithKFlips([1, 0, 1, 1, 0, 0, 1, 1], 2)
    );

    console.log("\n=== BOUNDED DIFFERENCE ===");

    console.log(
        longestSubarrayBoundedDifference([8, 2, 4, 7], 4)
    );

    console.log("\n=== ROLLING MONITOR ===");

    const monitor = new RollingMetric(3, 80);

    for (const value of [70, 90, 100, 95, 60]) {
        console.log(
            `Added ${value}:`,
            monitor.add(value),
            "window:",
            monitor.currentWindow()
        );
    }
}

function main() {
    demonstrate();
    runAssertions();
    console.log("\nAll JavaScript assertions passed.");
}

main();
