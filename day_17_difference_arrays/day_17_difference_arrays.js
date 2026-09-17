/*
 * Difference Arrays
 * =================
 *
 * A difference array stores changes between adjacent values.
 *
 * For:
 *     values = [a0, a1, a2, ...]
 *
 * the difference array is:
 *     d[0] = a0
 *     d[i] = a[i] - a[i - 1]
 *
 * A range addition:
 *     values[left ... right] += amount
 *
 * becomes:
 *     difference[left]     += amount
 *     difference[right + 1] -= amount
 *
 * A prefix sum reconstructs the final array.
 *
 * This file demonstrates:
 * - basic construction
 * - O(1) range updates
 * - sentinel slots
 * - interval coverage
 * - static range sums
 * - event processing
 * - 2D rectangle updates
 * - coordinate compression
 * - randomized verification
 * - performance comparison
 * - a realistic server-capacity case study
 *
 * Run with:
 *     node difference-arrays.js
 */

"use strict";


// ---------------------------------------------------------------------------
// 1. BASIC DIFFERENCE ARRAY
// ---------------------------------------------------------------------------

function buildDifferenceArray(values) {
    if (values.length === 0) {
        return [];
    }

    const difference = new Array(values.length);
    difference[0] = values[0];

    for (let i = 1; i < values.length; i += 1) {
        difference[i] = values[i] - values[i - 1];
    }

    return difference;
}


function reconstructFromDifference(difference) {
    const values = new Array(difference.length);
    let runningValue = 0;

    for (let i = 0; i < difference.length; i += 1) {
        runningValue += difference[i];
        values[i] = runningValue;
    }

    return values;
}


// ---------------------------------------------------------------------------
// 2. RANGE ADDITION
// ---------------------------------------------------------------------------

function rangeAdditions(n, updates) {
    if (!Number.isInteger(n) || n < 0) {
        throw new RangeError("n must be a non-negative integer.");
    }

    const difference = new Array(n + 1).fill(0);

    for (const [left, right, amount] of updates) {
        if (
            !Number.isInteger(left) ||
            !Number.isInteger(right) ||
            left < 0 ||
            right >= n ||
            left > right
        ) {
            throw new RangeError(`Invalid inclusive range [${left}, ${right}].`);
        }

        difference[left] += amount;
        difference[right + 1] -= amount;
    }

    return reconstructFromDifference(difference).slice(0, n);
}


// ---------------------------------------------------------------------------
// 3. NAIVE REFERENCE IMPLEMENTATION
// ---------------------------------------------------------------------------

function naiveRangeAdditions(n, updates) {
    const values = new Array(n).fill(0);

    for (const [left, right, amount] of updates) {
        for (let index = left; index <= right; index += 1) {
            values[index] += amount;
        }
    }

    return values;
}


// ---------------------------------------------------------------------------
// 4. STATIC RANGE SUMS
// ---------------------------------------------------------------------------

function prefixSums(values) {
    const prefix = new Array(values.length + 1).fill(0);

    for (let i = 0; i < values.length; i += 1) {
        prefix[i + 1] = prefix[i] + values[i];
    }

    return prefix;
}


function rangeSum(prefix, left, right) {
    if (left < 0 || right < left || right + 1 >= prefix.length) {
        throw new RangeError("Invalid query range.");
    }

    return prefix[right + 1] - prefix[left];
}


// ---------------------------------------------------------------------------
// 5. INTERVAL COVERAGE
// ---------------------------------------------------------------------------

function intervalCoverage(maximumCoordinate, intervals) {
    const difference = new Array(maximumCoordinate + 2).fill(0);

    for (const [left, right] of intervals) {
        if (
            left < 0 ||
            right > maximumCoordinate ||
            left > right
        ) {
            throw new RangeError("Invalid interval.");
        }

        difference[left] += 1;
        difference[right + 1] -= 1;
    }

    const coverage = new Array(maximumCoordinate + 1);
    let active = 0;

    for (let coordinate = 0; coordinate <= maximumCoordinate; coordinate += 1) {
        active += difference[coordinate];
        coverage[coordinate] = active;
    }

    return coverage;
}


// ---------------------------------------------------------------------------
// 6. EVENT SWEEP FOR HALF-OPEN INTERVALS
// ---------------------------------------------------------------------------

function maximumConcurrentIntervals(intervals) {
    const events = new Map();

    for (const [start, end] of intervals) {
        if (start > end) {
            throw new RangeError("Interval start cannot exceed end.");
        }

        events.set(start, (events.get(start) || 0) + 1);
        events.set(end, (events.get(end) || 0) - 1);
    }

    let active = 0;
    let maximum = 0;
    let maximumTime = null;

    const sortedTimes = [...events.keys()].sort((a, b) => a - b);

    for (const time of sortedTimes) {
        active += events.get(time);

        if (active > maximum) {
            maximum = active;
            maximumTime = time;
        }
    }

    return { maximum, maximumTime };
}


// ---------------------------------------------------------------------------
// 7. TWO-DIMENSIONAL DIFFERENCE ARRAY
// ---------------------------------------------------------------------------

function rectangleUpdates2D(rows, columns, updates) {
    const difference = Array.from(
        { length: rows + 1 },
        () => new Array(columns + 1).fill(0)
    );

    for (const [top, left, bottom, right, amount] of updates) {
        if (
            top < 0 ||
            left < 0 ||
            bottom >= rows ||
            right >= columns ||
            top > bottom ||
            left > right
        ) {
            throw new RangeError("Invalid rectangle.");
        }

        difference[top][left] += amount;
        difference[bottom + 1][left] -= amount;
        difference[top][right + 1] -= amount;
        difference[bottom + 1][right + 1] += amount;
    }

    const result = Array.from(
        { length: rows },
        () => new Array(columns).fill(0)
    );

    for (let row = 0; row < rows; row += 1) {
        for (let column = 0; column < columns; column += 1) {
            const above = row > 0 ? result[row - 1][column] : 0;
            const leftValue = column > 0 ? result[row][column - 1] : 0;
            const diagonal =
                row > 0 && column > 0
                    ? result[row - 1][column - 1]
                    : 0;

            result[row][column] =
                difference[row][column] +
                above +
                leftValue -
                diagonal;
        }
    }

    return result;
}


// ---------------------------------------------------------------------------
// 8. COORDINATE COMPRESSION
// ---------------------------------------------------------------------------

function compressedIntervalAdditions(intervals) {
    /*
     * Intervals use half-open notation [left, right).
     *
     * The coordinate domain can be enormous, so only coordinates where the
     * value can change are stored.
     */
    if (intervals.length === 0) {
        return [];
    }

    const coordinates = [
        ...new Set(
            intervals.flatMap(([left, right]) => [left, right])
        )
    ].sort((a, b) => a - b);

    const indexOf = new Map(
        coordinates.map((coordinate, index) => [coordinate, index])
    );

    const difference = new Array(coordinates.length + 1).fill(0);

    for (const [left, right, amount] of intervals) {
        if (left >= right) {
            throw new RangeError("Require left < right.");
        }

        difference[indexOf.get(left)] += amount;
        difference[indexOf.get(right)] -= amount;
    }

    const segments = [];
    let running = 0;

    for (let i = 0; i < coordinates.length - 1; i += 1) {
        running += difference[i];

        if (running !== 0) {
            segments.push([
                coordinates[i],
                coordinates[i + 1],
                running
            ]);
        }
    }

    return segments;
}


// ---------------------------------------------------------------------------
// 9. RANDOMIZED DIFFERENTIAL TESTING
// ---------------------------------------------------------------------------

function randomInteger(minimum, maximum) {
    return Math.floor(
        Math.random() * (maximum - minimum + 1)
    ) + minimum;
}


function randomizedTest(testCases = 300) {
    for (let test = 0; test < testCases; test += 1) {
        const n = randomInteger(0, 30);
        const updateCount = randomInteger(0, 40);
        const updates = [];

        for (let i = 0; i < updateCount; i += 1) {
            if (n === 0) {
                break;
            }

            const left = randomInteger(0, n - 1);
            const right = randomInteger(left, n - 1);
            const amount = randomInteger(-20, 20);

            updates.push([left, right, amount]);
        }

        const optimized = rangeAdditions(n, updates);
        const reference = naiveRangeAdditions(n, updates);

        if (JSON.stringify(optimized) !== JSON.stringify(reference)) {
            throw new Error(
                `Randomized test failed.\n` +
                `n=${n}\n` +
                `updates=${JSON.stringify(updates)}\n` +
                `optimized=${JSON.stringify(optimized)}\n` +
                `reference=${JSON.stringify(reference)}`
            );
        }
    }

    console.log(`Randomized tests passed: ${testCases}`);
}


// ---------------------------------------------------------------------------
// 10. REALISTIC SERVER-CAPACITY CASE STUDY
// ---------------------------------------------------------------------------

class ServerCapacityPlanner {
    /*
     * The planner models scheduled changes in server capacity.
     *
     * Each change applies to every deployment slot in an inclusive range:
     *
     *     [startSlot, endSlot] += capacityChange
     *
     * Difference arrays are suitable because changes are collected first and
     * the final capacity profile is generated afterward.
     */
    constructor(slotCount, baseCapacity) {
        if (!Number.isInteger(slotCount) || slotCount < 0) {
            throw new RangeError("slotCount must be non-negative.");
        }

        this.slotCount = slotCount;
        this.baseCapacity = baseCapacity;
        this.difference = new Array(slotCount + 1).fill(0);
    }

    scheduleCapacityChange(startSlot, endSlot, capacityChange) {
        if (
            startSlot < 0 ||
            endSlot >= this.slotCount ||
            startSlot > endSlot
        ) {
            throw new RangeError("Invalid deployment slot range.");
        }

        this.difference[startSlot] += capacityChange;
        this.difference[endSlot + 1] -= capacityChange;
    }

    buildCapacityProfile() {
        const profile = new Array(this.slotCount);
        let change = 0;

        for (let slot = 0; slot < this.slotCount; slot += 1) {
            change += this.difference[slot];
            profile[slot] = this.baseCapacity + change;
        }

        return profile;
    }

    minimumCapacity() {
        const profile = this.buildCapacityProfile();

        if (profile.length === 0) {
            return null;
        }

        return Math.min(...profile);
    }
}


// ---------------------------------------------------------------------------
// 11. PERFORMANCE DEMONSTRATION
// ---------------------------------------------------------------------------

function performanceDemo() {
    const n = 100000;
    const q = 20000;
    const updates = [];

    for (let i = 0; i < q; i += 1) {
        const left = randomInteger(0, n - 1);
        const right = randomInteger(left, n - 1);
        updates.push([left, right, randomInteger(-10, 10)]);
    }

    const optimizedStart = performance.now();
    const optimized = rangeAdditions(n, updates);
    const optimizedTime = performance.now() - optimizedStart;

    /*
     * The naive algorithm can require O(nq) operations in the worst case.
     * We use a smaller benchmark for it so this educational program remains
     * practical on ordinary computers.
     */
    const smallerN = 5000;
    const smallerUpdates = updates.slice(0, 1000);

    const naiveStart = performance.now();
    const reference = naiveRangeAdditions(smallerN, smallerUpdates);
    const naiveTime = performance.now() - naiveStart;

    console.log("\nPerformance demonstration");
    console.log(`Optimized: n=${n}, q=${q}, time=${optimizedTime.toFixed(3)} ms`);
    console.log(
        `Naive reference: n=${smallerN}, q=${smallerUpdates.length}, ` +
        `time=${naiveTime.toFixed(3)} ms`
    );

    /*
     * Prevent an optimizing runtime from making the benchmark meaningless
     * through unused values.
     */
    if (optimized.length !== n || reference.length !== smallerN) {
        throw new Error("Unexpected benchmark result size.");
    }
}


// ---------------------------------------------------------------------------
// 12. MAIN
// ---------------------------------------------------------------------------

function main() {
    console.log("=".repeat(72));
    console.log("DIFFERENCE ARRAYS: JAVASCRIPT STUDY");
    console.log("=".repeat(72));

    const values = [10, 13, 13, 20, 17];
    const difference = buildDifferenceArray(values);

    console.log("\nBasic construction");
    console.log("Original:     ", values);
    console.log("Difference:   ", difference);
    console.log(
        "Reconstructed:",
        reconstructFromDifference(difference)
    );

    const updates = [
        [1, 4, 3],
        [0, 2, 10],
        [3, 5, -2]
    ];

    console.log("\nRange additions");
    console.log("Result:", rangeAdditions(6, updates));

    const finalValues = rangeAdditions(
        8,
        [
            [0, 3, 5],
            [2, 6, 10],
            [5, 7, -3]
        ]
    );

    const prefix = prefixSums(finalValues);

    console.log("\nStatic range sums after reconstruction");
    console.log("Final values:", finalValues);
    console.log("Sum [1, 5]:", rangeSum(prefix, 1, 5));

    console.log("\nInterval coverage");
    console.log(
        intervalCoverage(
            7,
            [
                [1, 4],
                [2, 6],
                [4, 5]
            ]
        )
    );

    console.log("\nConcurrent half-open intervals");
    console.log(
        maximumConcurrentIntervals([
            [1, 5],
            [2, 7],
            [4, 6],
            [5, 8]
        ])
    );

    console.log("\nTwo-dimensional rectangle updates");
    const matrix = rectangleUpdates2D(
        3,
        4,
        [
            [0, 0, 1, 2, 5],
            [1, 1, 2, 3, 3]
        ]
    );

    matrix.forEach(row => console.log(row));

    console.log("\nCoordinate compression");
    console.log(
        compressedIntervalAdditions([
            [10, 1000000000, 5],
            [500, 700, 3],
            [600, 900, -2]
        ])
    );

    console.log("\nServer capacity case study");
    const planner = new ServerCapacityPlanner(8, 100);

    planner.scheduleCapacityChange(0, 3, 20);
    planner.scheduleCapacityChange(2, 6, 50);
    planner.scheduleCapacityChange(5, 7, -30);

    console.log("Capacity profile:", planner.buildCapacityProfile());
    console.log("Minimum capacity:", planner.minimumCapacity());

    randomizedTest();
    performanceDemo();

    console.log("\nAll JavaScript demonstrations completed successfully.");
}


main();
