"use strict";

/*
 * HEAP INTRODUCTION
 *
 * Complete binary trees, array representation, min-heaps,
 * max-heaps, priority queues, event-driven scheduling,
 * heap construction, validation, and heap sorting.
 *
 * Runtime: Node.js 18+
 * Dependencies: None
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

const HeapType = Object.freeze({
    MIN: "min",
    MAX: "max"
});

class BinaryHeap {
    constructor(type = HeapType.MIN, values = []) {
        if (!Object.values(HeapType).includes(type)) {
            throw new TypeError("Unsupported heap type");
        }

        if (!Array.isArray(values)) {
            throw new TypeError("Initial values must be an array");
        }

        this.type = type;
        this.data = [...values];
        this.statistics = {
            insertions: 0,
            removals: 0,
            comparisons: 0,
            swaps: 0
        };

        this._validateValues();

        // Bottom-up construction takes O(n) time.
        for (let i = Math.floor(this.size / 2) - 1; i >= 0; i--) {
            this.siftDown(i);
        }
    }

    get size() {
        return this.data.length;
    }

    get isEmpty() {
        return this.size === 0;
    }

    _validateValues() {
        for (const value of this.data) {
            if (typeof value !== "number" || !Number.isFinite(value)) {
                throw new TypeError("Heap values must be finite numbers");
            }
        }
    }

    _validateValue(value) {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            throw new TypeError("Heap values must be finite numbers");
        }
    }

    parent(index) {
        this._validateIndex(index);
        return index === 0 ? null : Math.floor((index - 1) / 2);
    }

    left(index) {
        this._validateIndex(index);
        const child = 2 * index + 1;
        return child < this.size ? child : null;
    }

    right(index) {
        this._validateIndex(index);
        const child = 2 * index + 2;
        return child < this.size ? child : null;
    }

    _validateIndex(index) {
        if (!Number.isInteger(index) || index < 0 || index >= this.size) {
            throw new RangeError("Invalid heap index");
        }
    }

    hasHigherPriority(a, b) {
        this.statistics.comparisons++;

        return this.type === HeapType.MIN
            ? a < b
            : a > b;
    }

    swap(i, j) {
        [this.data[i], this.data[j]] = [this.data[j], this.data[i]];
        this.statistics.swaps++;
    }

    siftUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (!this.hasHigherPriority(this.data[index], this.data[parent])) {
                break;
            }

            this.swap(index, parent);
            index = parent;
        }
    }

    siftDown(index) {
        while (true) {
            let best = index;
            const left = 2 * index + 1;
            const right = 2 * index + 2;

            if (
                left < this.size &&
                this.hasHigherPriority(this.data[left], this.data[best])
            ) {
                best = left;
            }

            if (
                right < this.size &&
                this.hasHigherPriority(this.data[right], this.data[best])
            ) {
                best = right;
            }

            if (best === index) {
                return;
            }

            this.swap(index, best);
            index = best;
        }
    }

    peek() {
        if (this.isEmpty) {
            throw new Error("Cannot inspect an empty heap");
        }

        return this.data[0];
    }

    push(value) {
        this._validateValue(value);

        this.data.push(value);
        this.statistics.insertions++;

        this.siftUp(this.size - 1);
    }

    pop() {
        if (this.isEmpty) {
            throw new Error("Cannot remove from an empty heap");
        }

        const result = this.data[0];
        const last = this.data.pop();

        this.statistics.removals++;

        if (!this.isEmpty) {
            this.data[0] = last;
            this.siftDown(0);
        }

        return result;
    }

    replaceRoot(value) {
        this._validateValue(value);

        if (this.isEmpty) {
            throw new Error("Cannot replace root of an empty heap");
        }

        const previous = this.data[0];
        this.data[0] = value;
        this.siftDown(0);

        return previous;
    }

    validate() {
        for (let i = 1; i < this.size; i++) {
            const parent = Math.floor((i - 1) / 2);

            const violation = this.type === HeapType.MIN
                ? this.data[i] < this.data[parent]
                : this.data[i] > this.data[parent];

            if (violation) {
                return false;
            }
        }

        return true;
    }

    levels() {
        const result = [];
        let start = 0;
        let width = 1;

        while (start < this.size) {
            result.push(this.data.slice(start, start + width));
            start += width;
            width *= 2;
        }

        return result;
    }

    snapshot() {
        return {
            type: this.type,
            values: [...this.data],
            size: this.size,
            valid: this.validate(),
            statistics: { ...this.statistics }
        };
    }
}


/*
 * An event-driven priority queue.
 *
 * EventEmitter separates scheduling operations from
 * consumers interested in insertion and execution events.
 */

class PriorityScheduler extends EventEmitter {
    constructor() {
        super();

        this.heap = new BinaryHeap(HeapType.MIN);
        this.tasks = new Map();
        this.nextId = 1;
        this.sequence = 0;
    }

    schedule(name, priority) {
        if (typeof name !== "string" || !name.trim()) {
            throw new TypeError("Task name cannot be empty");
        }

        if (!Number.isInteger(priority) || priority < 1 || priority > 10) {
            throw new RangeError("Priority must be an integer from 1 to 10");
        }

        const task = Object.freeze({
            id: this.nextId++,
            name: name.trim(),
            priority,
            sequence: this.sequence++
        });

        this.tasks.set(task.id, task);

        // Smaller priority numbers execute first.
        this.heap.push(task.priority * 1000000 + task.sequence);

        this.emit("scheduled", task);

        return task.id;
    }

    executeNext() {
        if (this.heap.isEmpty) {
            throw new Error("No pending tasks");
        }

        const encoded = this.heap.pop();
        const priority = Math.floor(encoded / 1000000);
        const sequence = encoded % 1000000;

        let selected = null;

        for (const task of this.tasks.values()) {
            if (
                task.priority === priority &&
                task.sequence === sequence
            ) {
                selected = task;
                break;
            }
        }

        if (!selected) {
            throw new Error("Scheduler state is inconsistent");
        }

        this.tasks.delete(selected.id);
        this.emit("executed", selected);

        return selected;
    }

    pending() {
        return [...this.tasks.values()].sort(
            (a, b) => a.priority - b.priority || a.sequence - b.sequence
        );
    }
}


/*
 * Generic numerical heap sort.
 * A min-heap produces ascending order.
 */

function heapSort(values) {
    const heap = new BinaryHeap(HeapType.MIN, values);
    const result = [];

    while (!heap.isEmpty) {
        result.push(heap.pop());
    }

    return result;
}


function demonstrateTreeRepresentation() {
    const tree = [10, 20, 30, 40, 50, 60, 70];

    console.log("\nCOMPLETE BINARY TREE");

    tree.forEach((value, index) => {
        const parent = index === 0
            ? null
            : tree[Math.floor((index - 1) / 2)];

        const left = tree[2 * index + 1] ?? null;
        const right = tree[2 * index + 2] ?? null;

        console.log({
            value,
            parent,
            left,
            right
        });
    });
}


function demonstrateHeaps() {
    const values = [40, 10, 30, 50, 20, 60, 70];

    const minHeap = new BinaryHeap(HeapType.MIN, values);
    const maxHeap = new BinaryHeap(HeapType.MAX, values);

    console.log("\nMIN-HEAP:", minHeap.snapshot());
    console.log("MAX-HEAP:", maxHeap.snapshot());

    console.log("Minimum:", minHeap.peek());
    console.log("Maximum:", maxHeap.peek());

    minHeap.push(5);
    console.log("After inserting 5:", minHeap.snapshot());

    console.log("Removed:", minHeap.pop());

    console.log("Min-heap valid:", minHeap.validate());
    console.log("Max-heap valid:", maxHeap.validate());

    console.log("Tree levels:", minHeap.levels());
}


function demonstrateScheduler() {
    const scheduler = new PriorityScheduler();

    scheduler.on("scheduled", task => {
        console.log("Scheduled:", task.name, task.priority);
    });

    scheduler.on("executed", task => {
        console.log("Executed:", task.name);
    });

    scheduler.schedule("Database backup", 4);
    scheduler.schedule("Security incident", 1);
    scheduler.schedule("Generate report", 7);
    scheduler.schedule("Production outage", 1);

    console.log("\nPENDING:", scheduler.pending());

    while (scheduler.heap.size > 0) {
        scheduler.executeNext();
    }
}


async function saveResults() {
    const values = [45, 12, 78, 3, 24, 56, 9];
    const heap = new BinaryHeap(HeapType.MIN, values);

    const result = {
        heap: heap.snapshot(),
        sorted: heapSort(values),
        treeLevels: heap.levels()
    };

    // Fixed output filename prevents arbitrary path selection.
    await fs.writeFile(
        "heap_results.json",
        JSON.stringify(result, null, 2),
        { encoding: "utf8", mode: 0o600 }
    );

    console.log("\nResults saved to heap_results.json");
}


function runTests() {
    const min = new BinaryHeap(HeapType.MIN, [9, 4, 7, 1, 3]);
    const max = new BinaryHeap(HeapType.MAX, [9, 4, 7, 1, 3]);

    console.assert(min.peek() === 1);
    console.assert(max.peek() === 9);

    min.push(0);
    console.assert(min.pop() === 0);

    console.assert(min.validate());
    console.assert(max.validate());

    console.assert(
        JSON.stringify(heapSort([5, 1, 4, 2, 3])) ===
        JSON.stringify([1, 2, 3, 4, 5])
    );

    console.assert(heapSort([]).length === 0);

    try {
        new BinaryHeap(HeapType.MIN, [1, Infinity]);
        throw new Error("Expected invalid-number validation");
    } catch (error) {
        if (!(error instanceof TypeError)) {
            throw error;
        }
    }

    try {
        min.pop();
        while (!min.isEmpty) {
            min.pop();
        }
        min.pop();
        throw new Error("Expected empty-heap error");
    } catch (error) {
        if (error.message !== "Cannot remove from an empty heap") {
            throw error;
        }
    }

    console.log("\nAll tests passed.");
}


async function main() {
    console.log("HEAP INTRODUCTION");
    console.log("=================");

    demonstrateTreeRepresentation();
    demonstrateHeaps();
    demonstrateScheduler();

    console.log("\nHEAP SORT:");
    console.log(heapSort([12, 4, 19, 1, 8, 3, 15]));

    runTests();

    await saveResults();
}


main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
