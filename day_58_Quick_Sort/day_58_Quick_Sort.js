"use strict";

const { performance } = require("node:perf_hooks");

const PivotStrategy = Object.freeze({
    FIRST: "first",
    LAST: "last",
    MIDDLE: "middle",
    MEDIAN_OF_THREE: "median_of_three",
    RANDOM: "random"
});

const PartitionStrategy = Object.freeze({
    LOMUTO: "lomuto",
    HOARE: "hoare"
});

class QuickSorter {
    constructor({
        pivotStrategy = PivotStrategy.MEDIAN_OF_THREE,
        partitionStrategy = PartitionStrategy.HOARE,
        seed = 42
    } = {}) {
        if (!Object.values(PivotStrategy).includes(pivotStrategy)) {
            throw new TypeError(`Unsupported pivot strategy: ${pivotStrategy}`);
        }

        if (!Object.values(PartitionStrategy).includes(partitionStrategy)) {
            throw new TypeError(
                `Unsupported partition strategy: ${partitionStrategy}`
            );
        }

        this.pivotStrategy = pivotStrategy;
        this.partitionStrategy = partitionStrategy;
        this.randomState = seed >>> 0;
    }

    nextRandom() {
        // Deterministic linear congruential generator for reproducible tests.
        this.randomState =
            (1664525 * this.randomState + 1013904223) >>> 0;
        return this.randomState / 0x100000000;
    }

    sort(input) {
        if (!Array.isArray(input)) {
            throw new TypeError("Input must be an array.");
        }

        if (!input.every(Number.isSafeInteger)) {
            throw new TypeError(
                "Every element must be a JavaScript safe integer."
            );
        }

        const data = [...input];
        const stats = {
            comparisons: 0,
            swaps: 0,
            partitions: 0,
            maxStackDepth: 0
        };

        if (data.length < 2) {
            return { result: data, stats };
        }

        // An explicit stack avoids dependence on JavaScript call-stack depth.
        const stack = [[0, data.length - 1, 1]];

        while (stack.length > 0) {
            stats.maxStackDepth = Math.max(
                stats.maxStackDepth,
                stack.length
            );

            const [low, high, depth] = stack.pop();

            if (low >= high) {
                continue;
            }

            stats.partitions++;

            if (this.partitionStrategy === PartitionStrategy.LOMUTO) {
                const pivotIndex = this.choosePivot(data, low, high, stats);
                const split = this.lomuto(
                    data,
                    low,
                    high,
                    pivotIndex,
                    stats
                );

                // Push the larger range first so the smaller range is
                // processed earlier, reducing explicit stack growth.
                const left = [low, split - 1, depth + 1];
                const right = [split + 1, high, depth + 1];

                if (split - low > high - split) {
                    if (left[0] < left[1]) stack.push(left);
                    if (right[0] < right[1]) stack.push(right);
                } else {
                    if (right[0] < right[1]) stack.push(right);
                    if (left[0] < left[1]) stack.push(left);
                }
            } else {
                const pivotIndex = this.choosePivot(data, low, high, stats);
                const split = this.hoare(
                    data,
                    low,
                    high,
                    data[pivotIndex],
                    stats
                );

                const left = [low, split, depth + 1];
                const right = [split + 1, high, depth + 1];

                if (split - low + 1 > high - split) {
                    if (left[0] < left[1]) stack.push(left);
                    if (right[0] < right[1]) stack.push(right);
                } else {
                    if (right[0] < right[1]) stack.push(right);
                    if (left[0] < left[1]) stack.push(left);
                }
            }
        }

        return { result: data, stats };
    }

    choosePivot(data, low, high, stats) {
        if (this.pivotStrategy === PivotStrategy.FIRST) return low;
        if (this.pivotStrategy === PivotStrategy.LAST) return high;
        if (this.pivotStrategy === PivotStrategy.MIDDLE) {
            return low + Math.floor((high - low) / 2);
        }
        if (this.pivotStrategy === PivotStrategy.RANDOM) {
            return low + Math.floor(
                this.nextRandom() * (high - low + 1)
            );
        }

        const middle = low + Math.floor((high - low) / 2);
        const a = data[low];
        const b = data[middle];
        const c = data[high];

        stats.comparisons += 3;

        if ((a <= b && b <= c) || (c <= b && b <= a)) {
            return middle;
        }
        if ((b <= a && a <= c) || (c <= a && a <= b)) {
            return low;
        }
        return high;
    }

    swap(data, i, j, stats) {
        if (i !== j) {
            [data[i], data[j]] = [data[j], data[i]];
            stats.swaps++;
        }
    }

    lomuto(data, low, high, pivotIndex, stats) {
        this.swap(data, pivotIndex, high, stats);
        const pivot = data[high];
        let store = low;

        for (let i = low; i < high; i++) {
            stats.comparisons++;
            if (data[i] <= pivot) {
                this.swap(data, i, store, stats);
                store++;
            }
        }

        this.swap(data, store, high, stats);
        return store;
    }

    hoare(data, low, high, pivot, stats) {
        let i = low - 1;
        let j = high + 1;

        while (true) {
            do {
                i++;
                stats.comparisons++;
            } while (data[i] < pivot);

            do {
                j--;
                stats.comparisons++;
            } while (data[j] > pivot);

            if (i >= j) {
                return j;
            }

            this.swap(data, i, j, stats);
        }
    }
}

function assertSorted(values) {
    for (let i = 1; i < values.length; i++) {
        if (values[i - 1] > values[i]) {
            throw new Error("Sorting invariant failed.");
        }
    }
}

function benchmark(name, values, sorter) {
    const start = performance.now();
    const { result, stats } = sorter.sort(values);
    const elapsed = performance.now() - start;

    assertSorted(result);

    console.log(`\n${name}`);
    console.log(`size=${result.length.toLocaleString()}`);
    console.log(`time=${elapsed.toFixed(3)} ms`);
    console.log(`comparisons=${stats.comparisons.toLocaleString()}`);
    console.log(`swaps=${stats.swaps.toLocaleString()}`);
    console.log(`partitions=${stats.partitions.toLocaleString()}`);
    console.log(`maxStackDepth=${stats.maxStackDepth}`);
}

async function processBatches(sorter, batches) {
    const output = [];

    for (const batch of batches) {
        await Promise.resolve();
        output.push(sorter.sort(batch));
    }

    return output;
}

async function main() {
    const examples = [
        [],
        [5],
        [3, 1, 4, 1, 5, 9, 2, 6],
        [7, 7, 7, 7],
        [5, 4, 3, 2, 1],
        [-4, 9, 0, -7, 3, 3, 1]
    ];

    const sorter = new QuickSorter({
        pivotStrategy: PivotStrategy.MEDIAN_OF_THREE,
        partitionStrategy: PartitionStrategy.HOARE
    });

    console.log("Quick Sort examples");

    for (const values of examples) {
        const { result, stats } = sorter.sort(values);
        console.log(
            `${JSON.stringify(values)} -> ${JSON.stringify(result)} ` +
            `(comparisons=${stats.comparisons}, swaps=${stats.swaps})`
        );
    }

    const generator = new QuickSorter({
        pivotStrategy: PivotStrategy.RANDOM,
        partitionStrategy: PartitionStrategy.HOARE,
        seed: 10
    });

    const randomValues = Array.from(
        { length: 10000 },
        () => Math.floor(generator.nextRandom() * 200001) - 100000
    );

    benchmark("Random input", randomValues, sorter);
    benchmark("Already sorted input", [...Array(10000).keys()], sorter);
    benchmark(
        "Reverse sorted input",
        [...Array(10000).keys()].reverse(),
        sorter
    );
    benchmark(
        "Duplicate-heavy input",
        Array(10000).fill(7),
        sorter
    );

    const batches = [
        [8, 3, 7, 4],
        [2, 1],
        [9, 5, 6, 3, 5]
    ];

    const results = await processBatches(sorter, batches);

    for (const { result } of results) {
        assertSorted(result);
    }

    console.log("\nAsynchronous batch processing completed:", results.length);

    for (const strategy of [
        PivotStrategy.FIRST,
        PivotStrategy.MIDDLE,
        PivotStrategy.MEDIAN_OF_THREE,
        PivotStrategy.RANDOM
    ]) {
        const testSorter = new QuickSorter({
            pivotStrategy: strategy,
            partitionStrategy: PartitionStrategy.HOARE,
            seed: 42
        });

        const { stats } = testSorter.sort([...Array(10000).keys()]);

        console.log(
            `${strategy.padEnd(16)} ` +
            `comparisons=${stats.comparisons.toLocaleString()} ` +
            `stack=${stats.maxStackDepth}`
        );
    }
}

main().catch(error => {
    console.error(`Quick Sort execution failed: ${error.message}`);
    process.exitCode = 1;
});
