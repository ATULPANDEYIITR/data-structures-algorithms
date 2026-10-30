"use strict";

/*
 * Non-comparison sorting pipeline for Node.js 18+.
 *
 * Features:
 * - Counting sort for bounded safe-integer ranges.
 * - LSD radix sort for signed safe integers.
 * - Bucket sort for finite JavaScript numbers.
 * - Automatic strategy selection.
 * - Event-driven job lifecycle.
 * - Promise-based execution and pre-execution cancellation.
 * - Correctness checks and performance measurement.
 */

const { EventEmitter } = require("node:events");
const { performance } = require("node:perf_hooks");

const ALGORITHMS = Object.freeze({
    AUTO: "auto",
    COUNTING: "counting",
    RADIX: "radix",
    BUCKET: "bucket",
    COMPARISON: "comparison"
});

const JOB_STATES = Object.freeze({
    QUEUED: "queued",
    RUNNING: "running",
    COMPLETED: "completed",
    FAILED: "failed",
    CANCELLED: "cancelled"
});

class SortingError extends Error {
    constructor(message) {
        super(message);
        this.name = "SortingError";
    }
}

function validateArray(values, maxItems = 1_000_000) {
    if (!Array.isArray(values)) {
        throw new SortingError("Input must be an array.");
    }

    if (values.length > maxItems) {
        throw new SortingError(`Input exceeds ${maxItems} values.`);
    }

    // Array.from preserves the validation of missing or sparse elements.
    const copy = Array.from(values);

    if (copy.some((value) => value === undefined || value === null)) {
        throw new SortingError("Input contains an empty array element.");
    }

    return copy;
}

function validateSafeIntegers(values) {
    const data = validateArray(values);

    for (const value of data) {
        if (!Number.isSafeInteger(value)) {
            throw new SortingError(
                "Integer algorithms require safe JavaScript integers."
            );
        }
    }

    return data;
}

function validateFiniteNumbers(values) {
    const data = validateArray(values);

    for (const value of data) {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            throw new SortingError(
                "Bucket sorting accepts finite JavaScript numbers only."
            );
        }
    }

    return data;
}

function countingSort(values, maxRange = 1_000_000) {
    const data = validateSafeIntegers(values);

    if (!Number.isSafeInteger(maxRange) || maxRange < 1) {
        throw new SortingError("maxRange must be a positive safe integer.");
    }

    if (data.length < 2) {
        return data;
    }

    const minimum = Math.min(...data);
    const maximum = Math.max(...data);

    // BigInt prevents precision loss in range calculations.
    const spanBig = BigInt(maximum) - BigInt(minimum) + 1n;

    if (spanBig > BigInt(maxRange)) {
        throw new SortingError(
            `Counting sort range exceeds the configured limit of ${maxRange}.`
        );
    }

    const span = Number(spanBig);
    const counts = new Array(span).fill(0);

    for (const value of data) {
        counts[value - minimum]++;
    }

    const output = [];

    for (let offset = 0; offset < span; offset++) {
        const frequency = counts[offset];

        for (let occurrence = 0; occurrence < frequency; occurrence++) {
            output.push(minimum + offset);
        }
    }

    return output;
}

function radixSort(values) {
    const data = validateSafeIntegers(values);

    if (data.length < 2) {
        return data;
    }

    const minimum = Math.min(...data);
    let keys = data.map((value) => BigInt(value) - BigInt(minimum));
    let output = data.slice();

    const maximumKey = keys.reduce(
        (maximum, key) => key > maximum ? key : maximum,
        0n
    );

    if (maximumKey === 0n) {
        return output;
    }

    const base = 256n;
    let placeValue = 1n;

    while (maximumKey / placeValue > 0n) {
        const counts = new Array(256).fill(0);

        for (const key of keys) {
            const digit = Number((key / placeValue) % base);
            counts[digit]++;
        }

        // Prefix sums identify the final position of each digit.
        let total = 0;

        for (let digit = 0; digit < 256; digit++) {
            total += counts[digit];
            counts[digit] = total;
        }

        const nextOutput = new Array(data.length);
        const nextKeys = new Array(data.length);

        // Reverse traversal makes the pass stable.
        for (let index = data.length - 1; index >= 0; index--) {
            const digit = Number((keys[index] / placeValue) % base);
            const destination = --counts[digit];

            nextOutput[destination] = output[index];
            nextKeys[destination] = keys[index];
        }

        output = nextOutput;
        keys = nextKeys;
        placeValue *= base;
    }

    return output;
}

function insertionSort(values) {
    for (let index = 1; index < values.length; index++) {
        const current = values[index];
        let position = index - 1;

        while (position >= 0 && values[position] > current) {
            values[position + 1] = values[position];
            position--;
        }

        values[position + 1] = current;
    }

    return values;
}

function bucketSort(values, bucketCount) {
    const data = validateFiniteNumbers(values);

    if (data.length < 2) {
        return data;
    }

    const count = bucketCount === undefined
        ? Math.max(1, Math.ceil(Math.sqrt(data.length)))
        : bucketCount;

    if (
        !Number.isSafeInteger(count) ||
        count < 1 ||
        count > 10_000
    ) {
        throw new SortingError(
            "bucketCount must be a safe integer between 1 and 10000."
        );
    }

    let minimum = Infinity;
    let maximum = -Infinity;

    for (const value of data) {
        minimum = Math.min(minimum, value);
        maximum = Math.max(maximum, value);
    }

    if (minimum === maximum) {
        return data;
    }

    /*
     * Scaling before subtraction avoids overflow for ranges such as
     * [-Number.MAX_VALUE, Number.MAX_VALUE].
     */
    const scale = Math.max(Math.abs(minimum), Math.abs(maximum), 1);
    const scaledMinimum = minimum / scale;
    const scaledMaximum = maximum / scale;
    const scaledRange = scaledMaximum - scaledMinimum;

    const buckets = Array.from(
        { length: count },
        () => []
    );

    for (const value of data) {
        const normalized = (
            (value / scale - scaledMinimum) / scaledRange
        );

        let index = Math.floor(normalized * count);
        index = Math.max(0, Math.min(count - 1, index));

        buckets[index].push(value);
    }

    const result = [];

    for (const bucket of buckets) {
        insertionSort(bucket);
        result.push(...bucket);
    }

    return result;
}

function comparisonSort(values) {
    return validateFiniteNumbers(values).sort((a, b) => a - b);
}

function selectAlgorithm(values, maxCountingRange = 1_000_000) {
    const data = validateFiniteNumbers(values);

    if (data.length === 0) {
        return ALGORITHMS.COUNTING;
    }

    if (data.some((value) => !Number.isSafeInteger(value))) {
        return ALGORITHMS.BUCKET;
    }

    const minimum = Math.min(...data);
    const maximum = Math.max(...data);
    const span = BigInt(maximum) - BigInt(minimum) + 1n;
    const relativeLimit = BigInt(Math.max(256, data.length * 16));

    if (
        span <= BigInt(maxCountingRange) &&
        span <= relativeLimit
    ) {
        return ALGORITHMS.COUNTING;
    }

    return ALGORITHMS.RADIX;
}

function executeAlgorithm(values, algorithm, limits) {
    switch (algorithm) {
        case ALGORITHMS.COUNTING:
            return countingSort(values, limits.maxCountingRange);

        case ALGORITHMS.RADIX:
            return radixSort(values);

        case ALGORITHMS.BUCKET:
            return bucketSort(values);

        case ALGORITHMS.COMPARISON:
            return comparisonSort(values);

        default:
            throw new SortingError(`Unsupported algorithm: ${algorithm}`);
    }
}

function sameMultiset(first, second) {
    if (first.length !== second.length) {
        return false;
    }

    const frequencies = new Map();

    for (const value of first) {
        frequencies.set(
            value,
            (frequencies.get(value) || 0) + 1
        );
    }

    for (const value of second) {
        const frequency = frequencies.get(value);

        if (frequency === undefined || frequency === 0) {
            return false;
        }

        if (frequency === 1) {
            frequencies.delete(value);
        } else {
            frequencies.set(value, frequency - 1);
        }
    }

    return frequencies.size === 0;
}

class SortingPipeline extends EventEmitter {
    constructor({
        maxItems = 1_000_000,
        maxCountingRange = 1_000_000
    } = {}) {
        super();

        if (!Number.isSafeInteger(maxItems) || maxItems < 0) {
            throw new SortingError("maxItems must be non-negative.");
        }

        if (
            !Number.isSafeInteger(maxCountingRange) ||
            maxCountingRange < 1
        ) {
            throw new SortingError("Invalid counting range limit.");
        }

        this.limits = Object.freeze({
            maxItems,
            maxCountingRange
        });

        this.jobs = new Map();
    }

    getState(jobId) {
        const job = this.jobs.get(jobId);
        return job ? job.state : null;
    }

    getJob(jobId) {
        const job = this.jobs.get(jobId);

        if (!job) {
            return null;
        }

        return Object.freeze({
            id: job.id,
            state: job.state,
            algorithm: job.algorithm,
            inputSize: job.inputSize,
            elapsedMs: job.elapsedMs
        });
    }

    transition(job, nextState, details = {}) {
        job.state = nextState;

        const event = Object.freeze({
            jobId: job.id,
            state: nextState,
            ...details
        });

        this.emit("state", event);
    }

    submit({ id, values, algorithm = ALGORITHMS.AUTO, signal }) {
        if (typeof id !== "string" || id.trim().length === 0) {
            throw new SortingError("A non-empty job ID is required.");
        }

        if (this.jobs.has(id)) {
            throw new SortingError(`Duplicate job ID: ${id}`);
        }

        const data = validateArray(values, this.limits.maxItems);

        if (!Object.values(ALGORITHMS).includes(algorithm)) {
            throw new SortingError(`Unsupported algorithm: ${algorithm}`);
        }

        const job = {
            id,
            state: JOB_STATES.QUEUED,
            algorithm,
            inputSize: data.length,
            elapsedMs: null
        };

        // Register before scheduling so duplicate submissions cannot race.
        this.jobs.set(id, job);

        const promise = new Promise((resolve, reject) => {
            setImmediate(() => {
                if (signal && signal.aborted) {
                    this.transition(job, JOB_STATES.CANCELLED);
                    reject(new SortingError(`Job ${id} was cancelled.`));
                    return;
                }

                try {
                    this.transition(job, JOB_STATES.RUNNING);

                    const selected = algorithm === ALGORITHMS.AUTO
                        ? selectAlgorithm(data, this.limits.maxCountingRange)
                        : algorithm;

                    const started = performance.now();
                    const result = executeAlgorithm(
                        data,
                        selected,
                        this.limits
                    );
                    const elapsedMs = performance.now() - started;

                    const reference = data.slice().sort((a, b) => a - b);

                    if (
                        result.length !== reference.length ||
                        result.some((value, index) => (
                            value !== reference[index]
                        )) ||
                        !sameMultiset(data, result)
                    ) {
                        throw new SortingError(
                            "Sorting result failed correctness verification."
                        );
                    }

                    job.algorithm = selected;
                    job.elapsedMs = elapsedMs;

                    const output = Object.freeze({
                        jobId: id,
                        state: JOB_STATES.COMPLETED,
                        algorithm: selected,
                        values: Object.freeze(result.slice()),
                        inputSize: data.length,
                        elapsedMs
                    });

                    this.transition(job, JOB_STATES.COMPLETED, {
                        algorithm: selected,
                        elapsedMs
                    });

                    this.emit("completed", output);
                    resolve(output);
                } catch (error) {
                    this.transition(job, JOB_STATES.FAILED, {
                        message: error.message
                    });

                    this.emit("failed", {
                        jobId: id,
                        error
                    });

                    reject(error);
                }
            });
        });

        return promise;
    }
}

async function main() {
    const pipeline = new SortingPipeline();

    pipeline.on("state", (event) => {
        console.log(
            `[${event.jobId}] state=${event.state}`,
            event.algorithm ? `algorithm=${event.algorithm}` : ""
        );
    });

    pipeline.on("completed", (event) => {
        console.log(
            `[${event.jobId}] completed in ${event.elapsedMs.toFixed(3)} ms`
        );
    });

    pipeline.on("failed", ({ jobId, error }) => {
        console.error(`[${jobId}] failed: ${error.message}`);
    });

    const jobs = [
        {
            id: "sensor-integer-batch",
            values: [12, -5, 0, 12, 7, -5, 100, 3],
            algorithm: ALGORITHMS.AUTO
        },
        {
            id: "wide-integer-batch",
            values: [
                9_000_000_000,
                -8_000_000_000,
                0,
                42,
                -1,
                9_000_000_000
            ],
            algorithm: ALGORITHMS.AUTO
        },
        {
            id: "latency-measurements",
            values: [0.42, 0.32, 0.23, 0.52, 0.25, 0.47, 0.51],
            algorithm: ALGORITHMS.AUTO
        }
    ];

    const results = await Promise.all(
        jobs.map((job) => pipeline.submit(job))
    );

    for (const result of results) {
        console.log(`\n${result.jobId}`);
        console.log("Algorithm:", result.algorithm);
        console.log("Sorted values:", result.values);
    }

    // A cancelled queued job is rejected before its sorting operation starts.
    const controller = new AbortController();
    controller.abort();

    try {
        await pipeline.submit({
            id: "cancelled-batch",
            values: [3, 2, 1],
            signal: controller.signal
        });
    } catch (error) {
        console.log("\nExpected cancellation:", error.message);
    }

    console.log("\nJob registry:");
    for (const job of pipeline.jobs.values()) {
        console.log(pipeline.getJob(job.id));
    }

    // Verify error handling and memory-allocation safeguards.
    try {
        countingSort([0, 10_000], 100);
    } catch (error) {
        console.log("\nExpected range rejection:", error.message);
    }

    try {
        bucketSort([1, Number.POSITIVE_INFINITY]);
    } catch (error) {
        console.log("Expected numeric rejection:", error.message);
    }
}

if (require.main === module) {
    main().catch((error) => {
        console.error(error);
        process.exitCode = 1;
    });
}

module.exports = {
    ALGORITHMS,
    JOB_STATES,
    SortingError,
    SortingPipeline,
    countingSort,
    radixSort,
    bucketSort,
    comparisonSort,
    selectAlgorithm
};
