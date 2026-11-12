"use strict";

/*
 * Heap Problems: Event-driven heap processing.
 * Runtime: Node.js 18+
 * No external dependencies.
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

class HeapError extends Error {}
class EmptyHeapError extends HeapError {}
class InvalidInputError extends HeapError {}

class BinaryHeap {
    constructor(compare = (a, b) => a - b, values = []) {
        if (typeof compare !== "function") {
            throw new InvalidInputError("Comparator must be a function.");
        }

        this.compare = compare;
        this.data = [...values];
        this.heapify();
    }

    get size() {
        return this.data.length;
    }

    get empty() {
        return this.size === 0;
    }

    heapify() {
        for (let i = Math.floor(this.size / 2) - 1; i >= 0; i--) {
            this.siftDown(i);
        }
    }

    siftUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.compare(this.data[index], this.data[parent]) >= 0) {
                break;
            }

            [this.data[index], this.data[parent]] =
                [this.data[parent], this.data[index]];

            index = parent;
        }
    }

    siftDown(index) {
        while (true) {
            const left = index * 2 + 1;
            const right = left + 1;
            let best = index;

            if (
                left < this.size &&
                this.compare(this.data[left], this.data[best]) < 0
            ) {
                best = left;
            }

            if (
                right < this.size &&
                this.compare(this.data[right], this.data[best]) < 0
            ) {
                best = right;
            }

            if (best === index) break;

            [this.data[index], this.data[best]] =
                [this.data[best], this.data[index]];

            index = best;
        }
    }

    push(value) {
        this.data.push(value);
        this.siftUp(this.size - 1);
    }

    peek() {
        if (this.empty) {
            throw new EmptyHeapError("Heap is empty.");
        }

        return this.data[0];
    }

    pop() {
        if (this.empty) {
            throw new EmptyHeapError("Cannot remove from an empty heap.");
        }

        const result = this.data[0];
        const last = this.data.pop();

        if (!this.empty) {
            this.data[0] = last;
            this.siftDown(0);
        }

        return result;
    }

    replaceRoot(value) {
        if (this.empty) {
            throw new EmptyHeapError("Cannot replace an empty heap root.");
        }

        const result = this.data[0];
        this.data[0] = value;
        this.siftDown(0);
        return result;
    }
}

function validateInteger(value, name = "value") {
    if (!Number.isSafeInteger(value)) {
        throw new InvalidInputError(`${name} must be a safe integer.`);
    }
}

function validateK(k, length, allowZero = false) {
    if (!Number.isSafeInteger(k)) {
        throw new InvalidInputError("k must be an integer.");
    }

    if (k < (allowZero ? 0 : 1) || k > length) {
        throw new InvalidInputError(`Invalid k: ${k}.`);
    }
}

function kthLargest(values, k) {
    validateK(k, values.length);

    const heap = new BinaryHeap(
        (a, b) => a - b,
        values.slice(0, k)
    );

    for (let i = k; i < values.length; i++) {
        validateInteger(values[i]);

        if (values[i] > heap.peek()) {
            heap.replaceRoot(values[i]);
        }
    }

    return heap.peek();
}

function kthSmallest(values, k) {
    validateK(k, values.length);

    const heap = new BinaryHeap(
        (a, b) => b - a,
        values.slice(0, k)
    );

    for (let i = k; i < values.length; i++) {
        validateInteger(values[i]);

        if (values[i] < heap.peek()) {
            heap.replaceRoot(values[i]);
        }
    }

    return heap.peek();
}

function topK(values, k) {
    if (!Number.isSafeInteger(k) || k < 0) {
        throw new InvalidInputError("k must be nonnegative.");
    }

    if (k === 0) return [];

    const heap = new BinaryHeap((a, b) => a - b);

    for (const value of values) {
        validateInteger(value);

        if (heap.size < k) {
            heap.push(value);
        } else if (value > heap.peek()) {
            heap.replaceRoot(value);
        }
    }

    return heap.data.slice().sort((a, b) => b - a);
}

function topKFrequent(values, k) {
    if (!Number.isSafeInteger(k) || k < 0) {
        throw new InvalidInputError("k must be nonnegative.");
    }

    const counts = new Map();

    for (const value of values) {
        counts.set(value, (counts.get(value) || 0) + 1);
    }

    const heap = new BinaryHeap((a, b) => {
        if (a.frequency !== b.frequency) {
            return a.frequency - b.frequency;
        }

        return b.firstSeen - a.firstSeen;
    });

    let sequence = 0;

    for (const [value, frequency] of counts) {
        const entry = { value, frequency, firstSeen: sequence++ };

        if (heap.size < k) {
            heap.push(entry);
        } else if (k > 0) {
            const root = heap.peek();

            if (
                frequency > root.frequency ||
                (frequency === root.frequency &&
                    entry.firstSeen < root.firstSeen)
            ) {
                heap.replaceRoot(entry);
            }
        }
    }

    return heap.data
        .slice()
        .sort((a, b) =>
            b.frequency - a.frequency ||
            a.firstSeen - b.firstSeen
        )
        .map(({ value, frequency }) => ({ value, frequency }));
}

function mergeSortedArrays(arrays) {
    const heap = new BinaryHeap((a, b) =>
        a.value - b.value ||
        a.arrayIndex - b.arrayIndex
    );

    arrays.forEach((array, arrayIndex) => {
        for (let i = 0; i < array.length; i++) {
            validateInteger(array[i]);

            if (i > 0 && array[i] < array[i - 1]) {
                throw new InvalidInputError(
                    `Array ${arrayIndex} is not sorted.`
                );
            }
        }

        if (array.length > 0) {
            heap.push({
                value: array[0],
                arrayIndex,
                elementIndex: 0
            });
        }
    });

    const result = [];

    while (!heap.empty) {
        const current = heap.pop();
        result.push(current.value);

        const nextIndex = current.elementIndex + 1;
        const array = arrays[current.arrayIndex];

        if (nextIndex < array.length) {
            heap.push({
                value: array[nextIndex],
                arrayIndex: current.arrayIndex,
                elementIndex: nextIndex
            });
        }
    }

    return result;
}

class RunningMedian {
    constructor() {
        this.lower = new BinaryHeap((a, b) => b - a);
        this.upper = new BinaryHeap((a, b) => a - b);
    }

    add(value) {
        validateInteger(value);

        if (this.lower.empty || value <= this.lower.peek()) {
            this.lower.push(value);
        } else {
            this.upper.push(value);
        }

        if (this.lower.size > this.upper.size + 1) {
            this.upper.push(this.lower.pop());
        } else if (this.upper.size > this.lower.size) {
            this.lower.push(this.upper.pop());
        }

        return this.median();
    }

    median() {
        if (this.lower.empty) {
            throw new EmptyHeapError("No stream values exist.");
        }

        if (this.lower.size > this.upper.size) {
            return this.lower.peek();
        }

        return (this.lower.peek() + this.upper.peek()) / 2;
    }
}

class KthLargestStream {
    constructor(k) {
        if (!Number.isSafeInteger(k) || k < 1) {
            throw new InvalidInputError("k must be positive.");
        }

        this.k = k;
        this.heap = new BinaryHeap((a, b) => a - b);
    }

    add(value) {
        validateInteger(value);

        if (this.heap.size < this.k) {
            this.heap.push(value);
        } else if (value > this.heap.peek()) {
            this.heap.replaceRoot(value);
        }

        return this.heap.size === this.k ? this.heap.peek() : null;
    }
}

class HeapEventProcessor extends EventEmitter {
    constructor(k) {
        super();

        this.median = new RunningMedian();
        this.kth = new KthLargestStream(k);
        this.sequence = 0;
    }

    process(value) {
        const median = this.median.add(value);
        const kthLargest = this.kth.add(value);

        const event = Object.freeze({
            sequence: ++this.sequence,
            value,
            median,
            kthLargest
        });

        this.emit("processed", event);
        return event;
    }

    async processAsync(asyncIterable) {
        const results = [];

        // Sequential processing preserves event order and state consistency.
        for await (const value of asyncIterable) {
            results.push(this.process(value));
        }

        return results;
    }
}

async function* simulatedStream(values, delayMs = 0) {
    for (const value of values) {
        if (delayMs > 0) {
            await new Promise(resolve => setTimeout(resolve, delayMs));
        }

        yield value;
    }
}

async function runTests() {
    const values = [3, 2, 1, 5, 6, 4];

    assert.equal(kthLargest(values, 2), 5);
    assert.equal(kthSmallest(values, 2), 2);
    assert.deepEqual(topK(values, 3), [6, 5, 4]);

    assert.deepEqual(
        topKFrequent([1, 1, 2, 2, 2, 3], 2),
        [
            { value: 2, frequency: 3 },
            { value: 1, frequency: 2 }
        ]
    );

    assert.deepEqual(
        mergeSortedArrays([[1, 4], [2, 5], [3, 6]]),
        [1, 2, 3, 4, 5, 6]
    );

    const median = new RunningMedian();

    [5, 15, 1, 3].forEach(value => median.add(value));
    assert.equal(median.median(), 4);

    const processor = new HeapEventProcessor(3);
    const events = [];

    processor.on("processed", event => events.push(event));

    await processor.processAsync(
        simulatedStream([10, 20, 5, 30, 15, 40])
    );

    assert.equal(events.length, 6);
    assert.equal(events[3].kthLargest, 10);

    assert.throws(
        () => kthLargest([1, 2], 3),
        InvalidInputError
    );

    assert.throws(
        () => new BinaryHeap().pop(),
        EmptyHeapError
    );

    assert.throws(
        () => mergeSortedArrays([[3, 1]]),
        InvalidInputError
    );

    console.log("All heap tests passed.");
}

async function main() {
    const processor = new HeapEventProcessor(3);

    processor.on("processed", event => {
        console.log("Stream event:", event);
    });

    await processor.processAsync(
        simulatedStream([10, 20, 5, 30, 15, 40])
    );

    console.log("Kth largest:", kthLargest(
        [12, 3, 5, 7, 19, 4, 8, 15], 3
    ));

    console.log("Kth smallest:", kthSmallest(
        [12, 3, 5, 7, 19, 4, 8, 15], 3
    ));

    console.log("Top 4:", topK(
        [12, 3, 5, 7, 19, 4, 8, 15], 4
    ));

    console.log("Merged:", mergeSortedArrays([
        [1, 4, 7],
        [2, 5, 8],
        [3, 6, 9]
    ]));

    await runTests();
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
