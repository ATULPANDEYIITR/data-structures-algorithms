'use strict';

/*
 * Elementary sorting study:
 * Bubble Sort, Selection Sort, and Insertion Sort.
 *
 * The implementation uses JavaScript-specific structures and asynchronous
 * event processing to model a repository-like stream of sorting jobs.
 */

const { performance } = require('node:perf_hooks');

class SortError extends Error {
    constructor(message) {
        super(message);
        this.name = 'SortError';
    }
}

const Algorithm = Object.freeze({
    BUBBLE: 'Bubble Sort',
    SELECTION: 'Selection Sort',
    INSERTION: 'Insertion Sort'
});

function validateInput(values) {
    if (!Array.isArray(values)) {
        throw new SortError('Input must be an array.');
    }

    const copy = [...values];

    for (let i = 1; i < copy.length; i++) {
        if (
            typeof copy[i - 1] !== 'number' ||
            typeof copy[i] !== 'number' ||
            !Number.isFinite(copy[i - 1]) ||
            !Number.isFinite(copy[i])
        ) {
            throw new SortError(
                'This implementation requires finite numeric values.'
            );
        }
    }

    return copy;
}

function createStats() {
    return {
        comparisons: 0,
        swaps: 0,
        writes: 0,
        elapsedMilliseconds: 0
    };
}

function bubbleSort(values) {
    const data = validateInput(values);
    const stats = createStats();
    const start = performance.now();

    for (let end = data.length - 1; end > 0; end--) {
        let changed = false;

        for (let i = 0; i < end; i++) {
            stats.comparisons++;

            if (data[i] > data[i + 1]) {
                [data[i], data[i + 1]] = [data[i + 1], data[i]];
                stats.swaps++;
                stats.writes += 2;
                changed = true;
            }
        }

        if (!changed) {
            break;
        }
    }

    stats.elapsedMilliseconds = performance.now() - start;
    return { values: data, stats };
}

function selectionSort(values) {
    const data = validateInput(values);
    const stats = createStats();
    const start = performance.now();

    for (let i = 0; i < data.length - 1; i++) {
        let minimumIndex = i;

        for (let j = i + 1; j < data.length; j++) {
            stats.comparisons++;

            if (data[j] < data[minimumIndex]) {
                minimumIndex = j;
            }
        }

        if (minimumIndex !== i) {
            [data[i], data[minimumIndex]] = [
                data[minimumIndex],
                data[i]
            ];
            stats.swaps++;
            stats.writes += 2;
        }
    }

    stats.elapsedMilliseconds = performance.now() - start;
    return { values: data, stats };
}

function insertionSort(values) {
    const data = validateInput(values);
    const stats = createStats();
    const start = performance.now();

    for (let i = 1; i < data.length; i++) {
        const key = data[i];
        stats.writes++;

        let j = i - 1;

        while (j >= 0) {
            stats.comparisons++;

            if (data[j] <= key) {
                break;
            }

            data[j + 1] = data[j];
            stats.writes++;
            j--;
        }

        data[j + 1] = key;
        stats.writes++;
    }

    stats.elapsedMilliseconds = performance.now() - start;
    return { values: data, stats };
}

const sorters = new Map([
    [Algorithm.BUBBLE, bubbleSort],
    [Algorithm.SELECTION, selectionSort],
    [Algorithm.INSERTION, insertionSort]
]);

function isSorted(values) {
    for (let i = 1; i < values.length; i++) {
        if (values[i - 1] > values[i]) {
            return false;
        }
    }
    return true;
}

function sameMultiset(a, b) {
    const counts = new Map();

    for (const value of a) {
        counts.set(value, (counts.get(value) ?? 0) + 1);
    }

    for (const value of b) {
        const next = (counts.get(value) ?? 0) - 1;

        if (next < 0) {
            return false;
        }

        if (next === 0) {
            counts.delete(value);
        } else {
            counts.set(value, next);
        }
    }

    return counts.size === 0;
}

function generateDatasets(size = 250, seed = 42) {
    // A deterministic generator keeps performance comparisons reproducible.
    let state = seed >>> 0;

    function nextRandom() {
        state = (1664525 * state + 1013904223) >>> 0;
        return state / 0x100000000;
    }

    const random = Array.from(
        { length: size },
        () => Math.floor(nextRandom() * size * 4)
    );

    const sorted = Array.from({ length: size }, (_, i) => i);
    const reverse = [...sorted].reverse();
    const duplicates = Array.from(
        { length: size },
        () => Math.floor(nextRandom() * 10)
    );

    const nearlySorted = [...sorted];

    for (let i = 0; i < size - 1; i += Math.max(1, Math.floor(size / 20))) {
        [nearlySorted[i], nearlySorted[i + 1]] = [
            nearlySorted[i + 1],
            nearlySorted[i]
        ];
    }

    return {
        random,
        sorted,
        reverse,
        duplicates,
        nearlySorted
    };
}

class SortJobQueue {
    constructor() {
        this.jobs = [];
        this.processing = false;
    }

    add(name, algorithm, values) {
        if (!sorters.has(algorithm)) {
            throw new SortError(`Unsupported algorithm: ${algorithm}`);
        }

        this.jobs.push({ name, algorithm, values: [...values] });
    }

    async process(handler) {
        if (this.processing) {
            throw new SortError('Queue is already processing.');
        }

        this.processing = true;

        try {
            while (this.jobs.length > 0) {
                const job = this.jobs.shift();
                const sorter = sorters.get(job.algorithm);

                // Yield between jobs so long-running work does not monopolize
                // an event-driven Node.js process.
                await new Promise(resolve => setImmediate(resolve));

                const result = sorter(job.values);
                handler(job, result);
            }
        } finally {
            this.processing = false;
        }
    }
}

function runCorrectnessTests() {
    const cases = [
        [],
        [1],
        [2, 1],
        [1, 2, 3],
        [5, 4, 3, 2, 1],
        [3, 1, 3, 2, 1, 2],
        [-4, 7, 0, -1, 5]
    ];

    for (const [algorithm, sorter] of sorters) {
        for (const input of cases) {
            const original = [...input];
            const result = sorter(input);

            if (!isSorted(result.values)) {
                throw new Error(`${algorithm} failed sortedness.`);
            }

            if (!sameMultiset(original, result.values)) {
                throw new Error(`${algorithm} changed the input multiset.`);
            }

            if (JSON.stringify(input) !== JSON.stringify(original)) {
                throw new Error(`${algorithm} mutated caller input.`);
            }
        }
    }

    console.log('Correctness suite: PASS');
}

function printResult(dataset, algorithm, result) {
    const s = result.stats;

    console.log(
        `${dataset.padEnd(15)} | ` +
        `${algorithm.padEnd(16)} | ` +
        `${String(s.comparisons).padStart(11)} | ` +
        `${String(s.swaps).padStart(6)} | ` +
        `${String(s.writes).padStart(6)} | ` +
        `${s.elapsedMilliseconds.toFixed(3).padStart(9)} ms`
    );
}

async function main() {
    runCorrectnessTests();

    const datasets = generateDatasets();
    const queue = new SortJobQueue();

    console.log('\nDataset         | Algorithm        | Comparisons | Swaps | Writes |      Time');
    console.log('-'.repeat(82));

    for (const [dataset, values] of Object.entries(datasets)) {
        for (const algorithm of sorters.keys()) {
            queue.add(dataset, algorithm, values);
        }
    }

    await queue.process((job, result) => {
        printResult(job.name, job.algorithm, result);
    });

    try {
        bubbleSort([1, 'invalid']);
    } catch (error) {
        if (!(error instanceof SortError)) {
            throw error;
        }
        console.log('\nValidation failure: heterogeneous input rejected');
    }

    const example = [5, 2, 4, 1, 3];

    console.log('\nExample');
    console.log(`Input:      ${example.join(', ')}`);
    console.log(`Bubble:     ${bubbleSort(example).values.join(', ')}`);
    console.log(`Selection:  ${selectionSort(example).values.join(', ')}`);
    console.log(`Insertion:  ${insertionSort(example).values.join(', ')}`);

    console.log('\nComplexity');
    console.log('Bubble:    best O(n) with early termination; average/worst O(n²).');
    console.log('Selection: best/average/worst O(n²); few swaps.');
    console.log('Insertion: best O(n); average/worst O(n²).');
    console.log('All implementations use O(1) auxiliary array space.');
    console.log('Bubble and Insertion are stable under the implemented comparisons.');
    console.log('Selection is not generally stable.');
}

main().catch(error => {
    console.error(`Fatal error: ${error.message}`);
    process.exitCode = 1;
});
