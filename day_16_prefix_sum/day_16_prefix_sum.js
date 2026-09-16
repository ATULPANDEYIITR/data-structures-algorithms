/**
 * Prefix Sum: Practical JavaScript Study File
 *
 * This file progresses from basic one-dimensional prefix sums to
 * two-dimensional queries, subarray problems, difference arrays, Fenwick
 * trees, and application-oriented examples.
 *
 * It uses only standard JavaScript features and can run in Node.js or
 * another modern JavaScript runtime.
 */

// ---------------------------------------------------------------------------
// 1. Basic prefix sum
// ---------------------------------------------------------------------------

function buildPrefixSum(values) {
    // prefix[i] stores the sum of values[0] through values[i - 1].
    // prefix[0] is deliberately zero so ranges beginning at index 0
    // require no special case.
    const prefix = new Array(values.length + 1).fill(0);

    for (let index = 0; index < values.length; index += 1) {
        prefix[index + 1] = prefix[index] + values[index];
    }

    return prefix;
}

function rangeSum(prefix, left, right) {
    if (
        left < 0 ||
        right < left ||
        right + 1 >= prefix.length
    ) {
        throw new RangeError("Invalid inclusive range");
    }

    return prefix[right + 1] - prefix[left];
}

function naiveRangeSum(values, left, right) {
    if (left < 0 || right < left || right >= values.length) {
        throw new RangeError("Invalid range");
    }

    let total = 0;

    for (let index = left; index <= right; index += 1) {
        total += values[index];
    }

    return total;
}


// ---------------------------------------------------------------------------
// 2. Static range-query class
// ---------------------------------------------------------------------------

class PrefixRangeQuery {
    constructor(values) {
        this.values = Object.freeze([...values]);
        this.prefix = buildPrefixSum(this.values);
    }

    query(left, right) {
        return rangeSum(this.prefix, left, right);
    }
}


// ---------------------------------------------------------------------------
// 3. Conditional counting
// ---------------------------------------------------------------------------

function buildPredicatePrefix(values, predicate) {
    // Convert the condition into 0/1 values, then prefix-sum them.
    const flags = values.map(value => predicate(value) ? 1 : 0);
    return buildPrefixSum(flags);
}

function demonstrateConditionalCounting() {
    const values = [3, 12, 7, 18, 5, 20, 9];
    const evenPrefix = buildPredicatePrefix(
        values,
        value => value % 2 === 0
    );

    console.log(
        "Even values in [1, 5]:",
        rangeSum(evenPrefix, 1, 5)
    );
}


// ---------------------------------------------------------------------------
// 4. Two-dimensional prefix sums
// ---------------------------------------------------------------------------

function build2DPrefix(matrix) {
    if (matrix.length === 0) {
        return [[0]];
    }

    const columns = matrix[0].length;

    if (matrix.some(row => row.length !== columns)) {
        throw new Error("Matrix rows must have equal lengths");
    }

    const prefix = Array.from(
        { length: matrix.length + 1 },
        () => new Array(columns + 1).fill(0)
    );

    for (let row = 0; row < matrix.length; row += 1) {
        for (let column = 0; column < columns; column += 1) {
            prefix[row + 1][column + 1] =
                matrix[row][column] +
                prefix[row][column + 1] +
                prefix[row + 1][column] -
                prefix[row][column];
        }
    }

    return prefix;
}

function rectangleSum(prefix, top, left, bottom, right) {
    if (top > bottom || left > right) {
        throw new RangeError("Invalid rectangle");
    }

    return (
        prefix[bottom + 1][right + 1] -
        prefix[top][right + 1] -
        prefix[bottom + 1][left] +
        prefix[top][left]
    );
}


// ---------------------------------------------------------------------------
// 5. Counting subarrays with a target sum
// ---------------------------------------------------------------------------

function countSubarraysWithSum(values, target) {
    /*
     * Let P[j] be a prefix sum.
     *
     * A subarray from i through j has sum target when:
     *
     *     P[j + 1] - P[i] = target
     *
     * Therefore:
     *
     *     P[i] = P[j + 1] - target
     *
     * A Map stores how many times each previous prefix sum occurred.
     */
    const frequencies = new Map([[0, 1]]);
    let currentSum = 0;
    let answer = 0;

    for (const value of values) {
        currentSum += value;

        answer += frequencies.get(currentSum - target) ?? 0;

        frequencies.set(
            currentSum,
            (frequencies.get(currentSum) ?? 0) + 1
        );
    }

    return answer;
}


// ---------------------------------------------------------------------------
// 6. Longest subarray with a target sum
// ---------------------------------------------------------------------------

function longestSubarrayWithSum(values, target) {
    // Store the earliest index for each prefix sum.
    // The earliest occurrence gives the longest possible interval later.
    const firstSeen = new Map([[0, -1]]);
    let currentSum = 0;
    let best = null;

    for (let index = 0; index < values.length; index += 1) {
        currentSum += values[index];

        const needed = currentSum - target;

        if (firstSeen.has(needed)) {
            const candidateLeft = firstSeen.get(needed) + 1;
            const candidateRight = index;

            if (
                best === null ||
                candidateRight - candidateLeft >
                best.right - best.left
            ) {
                best = {
                    left: candidateLeft,
                    right: candidateRight
                };
            }
        }

        if (!firstSeen.has(currentSum)) {
            firstSeen.set(currentSum, index);
        }
    }

    return best;
}


// ---------------------------------------------------------------------------
// 7. Difference array for repeated range updates
// ---------------------------------------------------------------------------

function applyRangeAdditions(size, operations) {
    /*
     * Instead of modifying every element in [left, right], record two
     * boundary events. A final prefix sum turns these events into values.
     */
    const difference = new Array(size + 1).fill(0);

    for (const [left, right, amount] of operations) {
        if (
            left < 0 ||
            right < left ||
            right >= size
        ) {
            throw new RangeError("Invalid update range");
        }

        difference[left] += amount;
        difference[right + 1] -= amount;
    }

    const result = new Array(size);
    let running = 0;

    for (let index = 0; index < size; index += 1) {
        running += difference[index];
        result[index] = running;
    }

    return result;
}


// ---------------------------------------------------------------------------
// 8. Prefix XOR
// ---------------------------------------------------------------------------

function buildPrefixXOR(values) {
    const prefix = new Array(values.length + 1).fill(0);

    for (let index = 0; index < values.length; index += 1) {
        prefix[index + 1] = prefix[index] ^ values[index];
    }

    return prefix;
}

function xorRangeQuery(prefix, left, right) {
    // XOR is self-inverse: x ^ x = 0.
    return prefix[right + 1] ^ prefix[left];
}


// ---------------------------------------------------------------------------
// 9. Fenwick tree
// ---------------------------------------------------------------------------

class FenwickTree {
    constructor(values) {
        this.size = values.length;
        this.tree = new Array(this.size + 1).fill(0);

        for (let index = 0; index < values.length; index += 1) {
            this.add(index + 1, values[index]);
        }
    }

    add(oneBasedIndex, delta) {
        if (
            oneBasedIndex < 1 ||
            oneBasedIndex > this.size
        ) {
            throw new RangeError("Fenwick index out of range");
        }

        let index = oneBasedIndex;

        while (index <= this.size) {
            this.tree[index] += delta;
            index += index & -index;
        }
    }

    prefixSum(count) {
        if (count < 0 || count > this.size) {
            throw new RangeError("Fenwick prefix length out of range");
        }

        let index = count;
        let total = 0;

        while (index > 0) {
            total += this.tree[index];
            index -= index & -index;
        }

        return total;
    }

    rangeSum(left, right) {
        if (
            left < 0 ||
            right < left ||
            right >= this.size
        ) {
            throw new RangeError("Invalid range");
        }

        return (
            this.prefixSum(right + 1) -
            this.prefixSum(left)
        );
    }
}


// ---------------------------------------------------------------------------
// 10. Segment tree
// ---------------------------------------------------------------------------

class SegmentTree {
    constructor(values) {
        this.size = 1;

        while (this.size < values.length) {
            this.size *= 2;
        }

        this.tree = new Array(this.size * 2).fill(0);

        for (let index = 0; index < values.length; index += 1) {
            this.tree[this.size + index] = values[index];
        }

        for (
            let index = this.size - 1;
            index > 0;
            index -= 1
        ) {
            this.tree[index] =
                this.tree[index * 2] +
                this.tree[index * 2 + 1];
        }
    }

    update(index, value) {
        if (index < 0 || index >= this.size) {
            throw new RangeError("Segment-tree index out of range");
        }

        let position = this.size + index;
        this.tree[position] = value;

        while (position > 1) {
            position = Math.floor(position / 2);

            this.tree[position] =
                this.tree[position * 2] +
                this.tree[position * 2 + 1];
        }
    }

    query(left, right) {
        if (
            left < 0 ||
            right < left ||
            right >= this.size
        ) {
            throw new RangeError("Invalid range");
        }

        let l = this.size + left;
        let r = this.size + right;
        let result = 0;

        while (l <= r) {
            if (l % 2 === 1) {
                result += this.tree[l];
                l += 1;
            }

            if (r % 2 === 0) {
                result += this.tree[r];
                r -= 1;
            }

            l = Math.floor(l / 2);
            r = Math.floor(r / 2);
        }

        return result;
    }
}


// ---------------------------------------------------------------------------
// 11. Exact arithmetic note for JavaScript
// ---------------------------------------------------------------------------

function demonstrateNumberLimitations() {
    /*
     * JavaScript's ordinary Number is IEEE-754 double precision.
     * Integer arithmetic is exact only through Number.MAX_SAFE_INTEGER.
     *
     * BigInt is appropriate when prefix sums can exceed that exact range.
     */
    const safeValues = [
        Number.MAX_SAFE_INTEGER - 2,
        1,
        1
    ];

    const safePrefix = buildPrefixSum(safeValues);

    console.log(
        "Safe integer prefix:",
        safePrefix
    );

    const bigValues = [
        9007199254740991n,
        10n,
        20n
    ];

    const bigPrefix = [0n];

    for (const value of bigValues) {
        bigPrefix.push(bigPrefix.at(-1) + value);
    }

    console.log(
        "BigInt prefix:",
        bigPrefix
    );
}


// ---------------------------------------------------------------------------
// 12. Performance comparison
// ---------------------------------------------------------------------------

function demonstratePerformance() {
    const values = Array.from(
        { length: 20_000 },
        (_, index) => (index * 17) % 101 - 50
    );

    const queries = Array.from(
        { length: 5_000 },
        (_, index) => {
            const left = (index * 37) % values.length;
            const right =
                Math.min(
                    values.length - 1,
                    left + ((index * 13) % 500)
                );

            return [left, right];
        }
    );

    const startNaive = performance.now();
    let naiveTotal = 0;

    for (const [left, right] of queries) {
        naiveTotal += naiveRangeSum(values, left, right);
    }

    const naiveTime = performance.now() - startNaive;

    const startPrefix = performance.now();
    const prefix = buildPrefixSum(values);
    let prefixTotal = 0;

    for (const [left, right] of queries) {
        prefixTotal += rangeSum(prefix, left, right);
    }

    const prefixTime = performance.now() - startPrefix;

    if (naiveTotal !== prefixTotal) {
        throw new Error("Performance comparison produced different results");
    }

    console.log(
        `Naive: ${naiveTime.toFixed(3)} ms; ` +
        `Prefix: ${prefixTime.toFixed(3)} ms`
    );
}


// ---------------------------------------------------------------------------
// 13. Correctness tests
// ---------------------------------------------------------------------------

function assertEqual(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(
            `${message}: expected ${expected}, received ${actual}`
        );
    }
}

function runTests() {
    const values = [4, 2, 7, 1, 5, 3];
    const prefix = buildPrefixSum(values);

    assertEqual(
        rangeSum(prefix, 1, 4),
        15,
        "Basic range sum"
    );

    assertEqual(
        naiveRangeSum(values, 1, 4),
        15,
        "Naive range sum"
    );

    const matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ];

    const matrixPrefix = build2DPrefix(matrix);

    assertEqual(
        rectangleSum(matrixPrefix, 1, 1, 2, 2),
        28,
        "Rectangle sum"
    );

    assertEqual(
        countSubarraysWithSum([1, 2, 1, 2, 1], 3),
        4,
        "Subarray count"
    );

    assertEqual(
        applyRangeAdditions(
            6,
            [[1, 3, 5], [2, 5, 2], [0, 1, 4]]
        ).join(","),
        "4,9,7,7,2,2",
        "Difference array"
    );

    const fenwick = new FenwickTree([2, 4, 6, 8, 10]);

    assertEqual(
        fenwick.rangeSum(1, 3),
        18,
        "Fenwick query"
    );

    fenwick.add(3, 5);

    assertEqual(
        fenwick.rangeSum(1, 3),
        23,
        "Fenwick update"
    );

    const segment = new SegmentTree([2, 4, 6, 8, 10]);

    assertEqual(
        segment.query(1, 3),
        18,
        "Segment query"
    );

    segment.update(2, 11);

    assertEqual(
        segment.query(1, 3),
        23,
        "Segment update"
    );

    console.log("All JavaScript tests passed.");
}


// ---------------------------------------------------------------------------
// 14. Main demonstration
// ---------------------------------------------------------------------------

function main() {
    console.log("PREFIX SUM STUDY PROGRAM");
    console.log("========================");

    const values = [4, 2, 7, 1, 5, 3];
    const prefix = buildPrefixSum(values);

    console.log("Values:", values);
    console.log("Prefix:", prefix);
    console.log("Sum [1, 4]:", rangeSum(prefix, 1, 4));

    demonstrateConditionalCounting();

    const matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ];

    const matrixPrefix = build2DPrefix(matrix);

    console.log(
        "2D rectangle [0..1][1..3]:",
        rectangleSum(matrixPrefix, 0, 1, 1, 3)
    );

    console.log(
        "Subarrays with sum 3:",
        countSubarraysWithSum([1, 2, 1, 2, 1], 3)
    );

    console.log(
        "Longest target-sum subarray:",
        longestSubarrayWithSum([1, -1, 5, -2, 3], 3)
    );

    console.log(
        "Range additions:",
        applyRangeAdditions(
            6,
            [[1, 3, 5], [2, 5, 2], [0, 1, 4]]
        )
    );

    const xorValues = [5, 2, 7, 3, 9];
    const xorPrefix = buildPrefixXOR(xorValues);

    console.log(
        "Prefix XOR [1, 3]:",
        xorRangeQuery(xorPrefix, 1, 3)
    );

    const queryStructure = new PrefixRangeQuery([10, 20, 30, 40, 50]);

    console.log(
        "Immutable query [1, 3]:",
        queryStructure.query(1, 3)
    );

    const fenwick = new FenwickTree([2, 4, 6, 8, 10]);

    console.log(
        "Fenwick [1, 3]:",
        fenwick.rangeSum(1, 3)
    );

    demonstrateNumberLimitations();
    demonstratePerformance();
    runTests();
}

main();
