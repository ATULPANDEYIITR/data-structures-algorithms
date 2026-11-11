"use strict";

/*
 * Heap Operations and Event-Driven Priority Queue
 * Node.js 18+
 *
 * Implements:
 * - Binary min-heap and max-heap
 * - Heap construction and heapify
 * - Insert, extract, delete and update
 * - Heap sort
 * - Stable priority scheduling
 * - Event-driven processing
 * - Validation and automated tests
 */

const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");

class EmptyHeapError extends Error {}
class HeapValidationError extends Error {}

class BinaryHeap {
    constructor(values = [], mode = "min") {
        if (!["min", "max"].includes(mode)) {
            throw new HeapValidationError("Mode must be min or max.");
        }

        this.mode = mode;
        this.data = [...values];

        for (const value of this.data) {
            this.validate(value);
        }

        this.heapify();
    }

    validate(value) {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            throw new HeapValidationError(
                "Heap values must be finite numbers."
            );
        }
    }

    higherPriority(a, b) {
        return this.mode === "min" ? a < b : a > b;
    }

    swap(i, j) {
        [this.data[i], this.data[j]] =
            [this.data[j], this.data[i]];
    }

    siftUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (!this.higherPriority(
                this.data[index],
                this.data[parent]
            )) break;

            this.swap(index, parent);
            index = parent;
        }
    }

    siftDown(index, size = this.data.length) {
        while (true) {
            const left = index * 2 + 1;
            const right = index * 2 + 2;
            let best = index;

            if (
                left < size &&
                this.higherPriority(this.data[left], this.data[best])
            ) {
                best = left;
            }

            if (
                right < size &&
                this.higherPriority(this.data[right], this.data[best])
            ) {
                best = right;
            }

            if (best === index) break;

            this.swap(index, best);
            index = best;
        }
    }

    heapify() {
        for (
            let i = Math.floor(this.data.length / 2) - 1;
            i >= 0;
            i--
        ) {
            this.siftDown(i);
        }
    }

    insert(value) {
        this.validate(value);
        this.data.push(value);
        this.siftUp(this.data.length - 1);
    }

    peek() {
        if (!this.data.length) {
            throw new EmptyHeapError("Heap is empty.");
        }

        return this.data[0];
    }

    extract() {
        if (!this.data.length) {
            throw new EmptyHeapError("Heap is empty.");
        }

        const result = this.data[0];
        const last = this.data.pop();

        if (this.data.length) {
            this.data[0] = last;
            this.siftDown(0);
        }

        return result;
    }

    deleteAt(index) {
        if (!Number.isInteger(index) ||
            index < 0 ||
            index >= this.data.length) {
            throw new RangeError("Invalid heap index.");
        }

        const removed = this.data[index];
        const last = this.data.pop();

        if (index < this.data.length) {
            this.data[index] = last;

            if (
                index > 0 &&
                this.higherPriority(
                    last,
                    this.data[Math.floor((index - 1) / 2)]
                )
            ) {
                this.siftUp(index);
            } else {
                this.siftDown(index);
            }
        }

        return removed;
    }

    update(index, value) {
        if (!Number.isInteger(index) ||
            index < 0 ||
            index >= this.data.length) {
            throw new RangeError("Invalid heap index.");
        }

        this.validate(value);

        const old = this.data[index];
        this.data[index] = value;

        if (this.higherPriority(value, old)) {
            this.siftUp(index);
        } else {
            this.siftDown(index);
        }
    }

    deleteValue(value) {
        const index = this.data.indexOf(value);

        if (index === -1) return false;

        this.deleteAt(index);
        return true;
    }

    isValid() {
        for (let i = 1; i < this.data.length; i++) {
            const parent = Math.floor((i - 1) / 2);

            if (this.higherPriority(
                this.data[i],
                this.data[parent]
            )) return false;
        }

        return true;
    }

    sortedValues() {
        const copy = new BinaryHeap(this.data, this.mode);
        const result = [];

        while (copy.size) result.push(copy.extract());

        return result;
    }

    get size() {
        return this.data.length;
    }
}

/*
 * Stable priority scheduling.
 * A monotonically increasing sequence breaks priority ties.
 */
class PriorityQueue {
    constructor() {
        this.heap = [];
        this.sequence = 0;
        this.activeIds = new Set();
    }

    higherPriority(a, b) {
        if (a.priority !== b.priority) {
            return a.priority > b.priority;
        }

        return a.sequence < b.sequence;
    }

    swap(i, j) {
        [this.heap[i], this.heap[j]] =
            [this.heap[j], this.heap[i]];
    }

    siftUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (!this.higherPriority(
                this.heap[index],
                this.heap[parent]
            )) break;

            this.swap(index, parent);
            index = parent;
        }
    }

    siftDown(index) {
        while (true) {
            const left = 2 * index + 1;
            const right = 2 * index + 2;
            let best = index;

            if (
                left < this.heap.length &&
                this.higherPriority(this.heap[left], this.heap[best])
            ) best = left;

            if (
                right < this.heap.length &&
                this.higherPriority(this.heap[right], this.heap[best])
            ) best = right;

            if (best === index) break;

            this.swap(index, best);
            index = best;
        }
    }

    enqueue(task) {
        if (!task || typeof task.id !== "string" ||
            !task.id.trim()) {
            throw new HeapValidationError("Task ID is required.");
        }

        if (!Number.isSafeInteger(task.priority)) {
            throw new HeapValidationError(
                "Priority must be a safe integer."
            );
        }

        if (typeof task.description !== "string" ||
            !task.description.trim()) {
            throw new HeapValidationError(
                "Task description is required."
            );
        }

        if (this.activeIds.has(task.id)) {
            throw new HeapValidationError(
                `Duplicate active task: ${task.id}`
            );
        }

        const entry = Object.freeze({
            id: task.id,
            description: task.description,
            priority: task.priority,
            sequence: this.sequence++
        });

        this.heap.push(entry);
        this.activeIds.add(entry.id);
        this.siftUp(this.heap.length - 1);
    }

    peek() {
        if (!this.heap.length) {
            throw new EmptyHeapError("Priority queue is empty.");
        }

        return this.heap[0];
    }

    dequeue() {
        if (!this.heap.length) {
            throw new EmptyHeapError("Priority queue is empty.");
        }

        const result = this.heap[0];
        const last = this.heap.pop();

        if (this.heap.length) {
            this.heap[0] = last;
            this.siftDown(0);
        }

        this.activeIds.delete(result.id);
        return result;
    }

    get size() {
        return this.heap.length;
    }
}

/*
 * Event-driven task processor.
 * Tasks are selected by priority, not insertion order.
 */
class TaskProcessor extends EventEmitter {
    constructor() {
        super();
        this.queue = new PriorityQueue();
        this.completed = new Map();
    }

    submit(task) {
        this.queue.enqueue(task);
        this.emit("submitted", task);
    }

    async processNext(handler) {
        if (typeof handler !== "function") {
            throw new TypeError("A task handler is required.");
        }

        if (!this.queue.size) return null;

        const task = this.queue.dequeue();
        this.emit("processing", task);

        try {
            const result = await handler(task);

            this.completed.set(task.id, {
                status: "completed",
                result
            });

            this.emit("completed", task, result);

            return result;
        } catch (error) {
            this.completed.set(task.id, {
                status: "failed",
                error: error.message
            });

            this.emit("failed", task, error);
            throw error;
        }
    }
}

function heapSort(values, descending = false) {
    const heap = new BinaryHeap(
        values,
        descending ? "max" : "min"
    );

    return heap.sortedValues();
}

async function demonstration() {
    console.log("MIN HEAP");

    const minHeap = new BinaryHeap(
        [40, 10, 30, 5, 20, 50]
    );

    console.log("Initial:", minHeap.data);
    console.log("Minimum:", minHeap.peek());
    console.log("Extracted:", minHeap.extract());

    minHeap.insert(2);
    minHeap.deleteValue(30);

    console.log("After modifications:", minHeap.data);
    console.log("Valid:", minHeap.isValid());

    console.log("\nMAX HEAP");

    const maxHeap = new BinaryHeap(
        [40, 10, 30, 5, 20, 50],
        "max"
    );

    console.log("Maximum:", maxHeap.extract());

    console.log("\nHEAP SORT");
    console.log(heapSort([12, 4, 19, 1, 8, 15, 3]));
    console.log(heapSort([12, 4, 19, 1, 8, 15, 3], true));

    console.log("\nEVENT-DRIVEN PRIORITY PROCESSOR");

    const processor = new TaskProcessor();

    processor.on("submitted", task =>
        console.log("Submitted:", task.id)
    );

    processor.on("completed", task =>
        console.log("Completed:", task.id)
    );

    processor.on("failed", task =>
        console.log("Failed:", task.id)
    );

    processor.submit({
        id: "T101",
        description: "Database backup",
        priority: 3
    });

    processor.submit({
        id: "T102",
        description: "Security incident",
        priority: 10
    });

    processor.submit({
        id: "T103",
        description: "Monitoring",
        priority: 5
    });

    while (processor.queue.size) {
        await processor.processNext(async task => {
            return `Processed ${task.description}`;
        });
    }
}

function runTests() {
    const min = new BinaryHeap([9, 4, 7, 1, 3]);

    assert.equal(min.extract(), 1);
    assert.equal(min.isValid(), true);

    const max = new BinaryHeap([9, 4, 7], "max");
    assert.equal(max.extract(), 9);

    const heap = new BinaryHeap([5, 10, 15]);
    heap.update(2, 1);
    assert.equal(heap.peek(), 1);

    assert.equal(
        heapSort([8, 3, 5, 1]).join(","),
        "1,3,5,8"
    );

    assert.throws(
        () => new BinaryHeap([], "invalid"),
        HeapValidationError
    );

    assert.throws(
        () => new BinaryHeap([NaN]),
        HeapValidationError
    );

    assert.throws(
        () => new BinaryHeap().extract(),
        EmptyHeapError
    );

    const queue = new PriorityQueue();

    queue.enqueue({
        id: "A",
        description: "Normal",
        priority: 1
    });

    queue.enqueue({
        id: "B",
        description: "Critical",
        priority: 10
    });

    assert.equal(queue.dequeue().id, "B");

    console.log("\nAll JavaScript tests passed.");
}

if (require.main === module) {
    runTests();

    demonstration().catch(error => {
        console.error("Execution failed:", error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    BinaryHeap,
    PriorityQueue,
    TaskProcessor,
    heapSort,
    EmptyHeapError,
    HeapValidationError
};
