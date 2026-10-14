"use strict";

/*
 * Deque Engineering in JavaScript.
 *
 * This implementation focuses on:
 * - A reusable double-ended queue.
 * - Monotonic queues for streaming window extrema.
 * - Event-driven processing of incoming measurements.
 * - Async iterable consumption and bounded-memory considerations.
 * - Input validation and automated correctness checks.
 *
 * Run with Node.js 18 or later:
 *     node deque_engineering.js
 */

class Deque {
    constructor(initialCapacity = 16) {
        if (!Number.isSafeInteger(initialCapacity) || initialCapacity < 1) {
            throw new RangeError("Capacity must be a positive safe integer.");
        }

        this.buffer = new Array(initialCapacity);
        this.head = 0;
        this.size = 0;
    }

    get length() {
        return this.size;
    }

    get isEmpty() {
        return this.size === 0;
    }

    _physicalIndex(logicalIndex) {
        return (this.head + logicalIndex) % this.buffer.length;
    }

    _grow() {
        const expanded = new Array(this.buffer.length * 2);

        for (let i = 0; i < this.size; i += 1) {
            expanded[i] = this.buffer[this._physicalIndex(i)];
        }

        this.buffer = expanded;
        this.head = 0;
    }

    pushBack(value) {
        if (this.size === this.buffer.length) {
            this._grow();
        }

        this.buffer[this._physicalIndex(this.size)] = value;
        this.size += 1;
    }

    pushFront(value) {
        if (this.size === this.buffer.length) {
            this._grow();
        }

        this.head = (this.head - 1 + this.buffer.length) %
            this.buffer.length;
        this.buffer[this.head] = value;
        this.size += 1;
    }

    popFront() {
        if (this.isEmpty) {
            throw new RangeError("Cannot remove from an empty deque.");
        }

        const value = this.buffer[this.head];
        this.buffer[this.head] = undefined;
        this.head = (this.head + 1) % this.buffer.length;
        this.size -= 1;

        if (this.size === 0) {
            this.head = 0;
        }

        return value;
    }

    popBack() {
        if (this.isEmpty) {
            throw new RangeError("Cannot remove from an empty deque.");
        }

        const index = this._physicalIndex(this.size - 1);
        const value = this.buffer[index];
        this.buffer[index] = undefined;
        this.size -= 1;

        if (this.size === 0) {
            this.head = 0;
        }

        return value;
    }

    front() {
        if (this.isEmpty) {
            throw new RangeError("An empty deque has no front element.");
        }
        return this.buffer[this.head];
    }

    back() {
        if (this.isEmpty) {
            throw new RangeError("An empty deque has no back element.");
        }
        return this.buffer[this._physicalIndex(this.size - 1)];
    }

    toArray() {
        return Array.from(
            { length: this.size },
            (_, index) => this.buffer[this._physicalIndex(index)]
        );
    }
}

function validateValues(values) {
    if (!Array.isArray(values)) {
        throw new TypeError("Expected an array of numeric measurements.");
    }

    // Reject NaN and infinities because comparisons with NaN do not define
    // a reliable monotonic ordering.
    for (const value of values) {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            throw new TypeError("Every measurement must be a finite number.");
        }
    }

    return values;
}

function validateWindow(values, k) {
    if (!Number.isSafeInteger(k)) {
        throw new TypeError("Window size must be a safe integer.");
    }

    if (values.length === 0 || k < 1 || k > values.length) {
        throw new RangeError("Window size must fit the nonempty input.");
    }
}

function slidingWindowMaximum(values, k) {
    validateValues(values);
    validateWindow(values, k);

    const candidates = new Deque();
    const result = [];

    for (let index = 0; index < values.length; index += 1) {
        while (
            !candidates.isEmpty &&
            candidates.front() <= index - k
        ) {
            candidates.popFront();
        }

        // The newest value dominates all trailing candidates no larger
        // than itself for every future window containing the new value.
        while (
            !candidates.isEmpty &&
            values[candidates.back()] <= values[index]
        ) {
            candidates.popBack();
        }

        candidates.pushBack(index);

        if (index >= k - 1) {
            result.push(values[candidates.front()]);
        }
    }

    return result;
}

function slidingWindowMinimum(values, k) {
    validateValues(values);
    validateWindow(values, k);

    const candidates = new Deque();
    const result = [];

    for (let index = 0; index < values.length; index += 1) {
        while (
            !candidates.isEmpty &&
            candidates.front() <= index - k
        ) {
            candidates.popFront();
        }

        while (
            !candidates.isEmpty &&
            values[candidates.back()] >= values[index]
        ) {
            candidates.popBack();
        }

        candidates.pushBack(index);

        if (index >= k - 1) {
            result.push(values[candidates.front()]);
        }
    }

    return result;
}

function slidingWindowExtrema(values, k) {
    validateValues(values);
    validateWindow(values, k);

    const minima = new Deque();
    const maxima = new Deque();
    const result = [];

    for (let index = 0; index < values.length; index += 1) {
        while (!minima.isEmpty && minima.front() <= index - k) {
            minima.popFront();
        }

        while (!maxima.isEmpty && maxima.front() <= index - k) {
            maxima.popFront();
        }

        while (
            !minima.isEmpty &&
            values[minima.back()] >= values[index]
        ) {
            minima.popBack();
        }

        while (
            !maxima.isEmpty &&
            values[maxima.back()] <= values[index]
        ) {
            maxima.popBack();
        }

        minima.pushBack(index);
        maxima.pushBack(index);

        if (index >= k - 1) {
            result.push({
                minimum: values[minima.front()],
                maximum: values[maxima.front()]
            });
        }
    }

    return result;
}

class SlidingWindowMonitor {
    constructor(windowSize, onWindow) {
        if (!Number.isSafeInteger(windowSize) || windowSize < 1) {
            throw new RangeError("Window size must be a positive integer.");
        }

        if (typeof onWindow !== "function") {
            throw new TypeError("A window callback is required.");
        }

        this.windowSize = windowSize;
        this.onWindow = onWindow;
        this.index = 0;
        this.minima = new Deque();
        this.maxima = new Deque();
    }

    addMeasurement(value) {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            throw new TypeError("Measurement must be finite.");
        }

        const index = this.index;
        this.index += 1;

        while (
            !this.minima.isEmpty &&
            this.minima.front() <= index - this.windowSize
        ) {
            this.minima.popFront();
        }

        while (
            !this.maxima.isEmpty &&
            this.maxima.front() <= index - this.windowSize
        ) {
            this.maxima.popFront();
        }

        while (
            !this.minima.isEmpty &&
            this.minima.back().value >= value
        ) {
            this.minima.popBack();
        }

        while (
            !this.maxima.isEmpty &&
            this.maxima.back().value <= value
        ) {
            this.maxima.popBack();
        }

        this.minima.pushBack({ index, value });
        this.maxima.pushBack({ index, value });

        if (this.index >= this.windowSize) {
            this.onWindow({
                endIndex: index,
                minimum: this.minima.front().value,
                maximum: this.maxima.front().value
            });
        }
    }
}

/*
 * A second monitor with explicit index/value records illustrates streaming
 * without retaining the entire input history.
 */
class StreamingWindowExtrema {
    constructor(windowSize) {
        if (!Number.isSafeInteger(windowSize) || windowSize < 1) {
            throw new RangeError("Window size must be a positive integer.");
        }

        this.windowSize = windowSize;
        this.nextIndex = 0;
        this.minimumCandidates = new Deque();
        this.maximumCandidates = new Deque();
    }

    push(value) {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            throw new TypeError("Measurement must be finite.");
        }

        const index = this.nextIndex++;

        while (
            !this.minimumCandidates.isEmpty &&
            this.minimumCandidates.front().index <= index - this.windowSize
        ) {
            this.minimumCandidates.popFront();
        }

        while (
            !this.maximumCandidates.isEmpty &&
            this.maximumCandidates.front().index <= index - this.windowSize
        ) {
            this.maximumCandidates.popFront();
        }

        while (
            !this.minimumCandidates.isEmpty &&
            this.minimumCandidates.back().value >= value
        ) {
            this.minimumCandidates.popBack();
        }

        while (
            !this.maximumCandidates.isEmpty &&
            this.maximumCandidates.back().value <= value
        ) {
            this.maximumCandidates.popBack();
        }

        this.minimumCandidates.pushBack({ index, value });
        this.maximumCandidates.pushBack({ index, value });

        if (this.nextIndex < this.windowSize) {
            return null;
        }

        return {
            startIndex: index - this.windowSize + 1,
            endIndex: index,
            minimum: this.minimumCandidates.front().value,
            maximum: this.maximumCandidates.front().value
        };
    }
}

async function consumeMeasurements(source, monitor) {
    // Async iteration supports files, network streams, and asynchronous
    // generators. Each yielded value is processed before the next arrives.
    for await (const measurement of source) {
        monitor.addMeasurement(measurement);
    }
}

async function* sensorReadings() {
    for (const reading of [18.2, 19.1, 17.4, 20.6, 21.3, 16.8, 18.9]) {
        yield reading;
        await Promise.resolve();
    }
}

function bruteForceExtrema(values, k) {
    validateValues(values);
    validateWindow(values, k);

    return Array.from(
        { length: values.length - k + 1 },
        (_, start) => {
            const window = values.slice(start, start + k);
            return {
                minimum: Math.min(...window),
                maximum: Math.max(...window)
            };
        }
    );
}

function runTests() {
    const cases = [
        { values: [1], k: 1 },
        { values: [4, 4, 4, 4], k: 2 },
        { values: [-8, -3, -9, -1], k: 2 },
        { values: [1, 9, 2, 8, 3, 7], k: 6 },
        { values: [2, 1, 2, 1, 2], k: 1 }
    ];

    for (const testCase of cases) {
        const actual = slidingWindowExtrema(
            testCase.values,
            testCase.k
        );
        const expected = bruteForceExtrema(
            testCase.values,
            testCase.k
        );

        if (JSON.stringify(actual) !== JSON.stringify(expected)) {
            throw new Error("A deterministic test failed.");
        }
    }

    const monitor = new StreamingWindowExtrema(3);
    const streamResults = [4, 2, 12, 3, 8].map(
        value => monitor.push(value)
    ).filter(Boolean);

    if (streamResults[0].minimum !== 2 ||
        streamResults[0].maximum !== 12) {
        throw new Error("Streaming monitor test failed.");
    }

    for (const invalid of [
        () => slidingWindowMaximum([], 1),
        () => slidingWindowMaximum([1, 2], 0),
        () => slidingWindowMinimum([1, NaN], 1),
        () => slidingWindowMaximum([1, 2], 1.5)
    ]) {
        let rejected = false;

        try {
            invalid();
        } catch (error) {
            rejected = error instanceof TypeError ||
                error instanceof RangeError;
        }

        if (!rejected) {
            throw new Error("Invalid input was not rejected.");
        }
    }

    console.log("All deterministic tests passed.");
}

async function main() {
    console.log("=== Deque operations ===");

    const deque = new Deque(2);
    deque.pushFront(20);
    deque.pushFront(10);
    deque.pushBack(30);

    console.log("Deque contents:", deque.toArray());
    console.log("Front removal:", deque.popFront());
    console.log("Back removal:", deque.popBack());

    const measurements = [1, 3, -1, -3, 5, 3, 6, 7];
    const windowSize = 3;

    console.log("\n=== Sliding window ===");
    console.log("Maximum:", slidingWindowMaximum(measurements, windowSize));
    console.log("Minimum:", slidingWindowMinimum(measurements, windowSize));
    console.log(
        "Both extrema:",
        slidingWindowExtrema(measurements, windowSize)
    );

    console.log("\n=== Event-driven monitor ===");

    const monitor = new SlidingWindowMonitor(3, result => {
        console.log("Completed window:", result);
    });

    for (const measurement of [18, 20, 17, 22, 16, 19]) {
        monitor.addMeasurement(measurement);
    }

    console.log("\n=== Asynchronous input ===");

    const streamMonitor = new StreamingWindowExtrema(3);
    const output = [];

    await consumeMeasurements(sensorReadings(), {
        addMeasurement(value) {
            const result = streamMonitor.push(value);
            if (result !== null) {
                output.push(result);
            }
        }
    });

    console.log("Stream extrema:", output);

    runTests();
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
