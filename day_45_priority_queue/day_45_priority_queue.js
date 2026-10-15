"use strict";

/*
 * Priority-based processing in Node.js.
 *
 * Demonstrates a binary heap, stable job scheduling, an event-driven
 * worker simulation, asynchronous completion, cancellation, reprioritization,
 * bounded admission, and policy tests.
 *
 * Run with: node priority_queue.js
 */

const assert = require("node:assert/strict");

class BinaryHeap {
    constructor(compare) {
        if (typeof compare !== "function") {
            throw new TypeError("A comparison function is required");
        }
        this.items = [];
        this.compare = compare;
    }

    get size() {
        return this.items.length;
    }

    peek() {
        return this.items[0];
    }

    push(value) {
        this.items.push(value);
        this.#siftUp(this.items.length - 1);
    }

    pop() {
        if (this.items.length === 0) return undefined;

        const root = this.items[0];
        const last = this.items.pop();

        if (this.items.length > 0) {
            this.items[0] = last;
            this.#siftDown(0);
        }
        return root;
    }

    #siftUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);
            if (this.compare(this.items[index], this.items[parent]) >= 0) {
                break;
            }
            [this.items[index], this.items[parent]] =
                [this.items[parent], this.items[index]];
            index = parent;
        }
    }

    #siftDown(index) {
        const length = this.items.length;

        while (true) {
            const left = 2 * index + 1;
            const right = left + 1;
            let best = index;

            if (left < length &&
                this.compare(this.items[left], this.items[best]) < 0) {
                best = left;
            }
            if (right < length &&
                this.compare(this.items[right], this.items[best]) < 0) {
                best = right;
            }
            if (best === index) break;

            [this.items[index], this.items[best]] =
                [this.items[best], this.items[index]];
            index = best;
        }
    }

    assertInvariant() {
        for (let child = 1; child < this.items.length; child++) {
            const parent = Math.floor((child - 1) / 2);
            assert.ok(
                this.compare(this.items[parent], this.items[child]) <= 0,
                "Heap parent must not rank below its child"
            );
        }
        return true;
    }
}

function compareJobs(a, b) {
    // Higher priority first; insertion sequence resolves ties.
    return b.priority - a.priority || a.sequence - b.sequence;
}

class JobScheduler extends EventTarget {
    constructor(capacity = 100) {
        super();
        if (!Number.isInteger(capacity) || capacity < 1) {
            throw new RangeError("Capacity must be a positive integer");
        }

        this.capacity = capacity;
        this.sequence = 0;
        this.heap = new BinaryHeap(compareJobs);
        this.live = new Map();
    }

    submit({ id, description, priority, durationMs = 0 }) {
        if (typeof id !== "string" || id.trim() === "") {
            throw new TypeError("Job ID must be a non-empty string");
        }
        if (typeof description !== "string" || !description.trim()) {
            throw new TypeError("Job description is required");
        }
        if (!Number.isInteger(priority) || priority < 0 || priority > 100) {
            throw new RangeError("Priority must be an integer from 0 to 100");
        }
        if (!Number.isFinite(durationMs) || durationMs < 0) {
            throw new RangeError("Duration must be non-negative");
        }
        if (this.live.has(id)) throw new Error(`Duplicate job: ${id}`);
        if (this.live.size >= this.capacity) {
            throw new Error("Scheduler capacity reached");
        }

        const job = {
            id,
            description,
            priority,
            durationMs,
            sequence: this.sequence++,
            version: this.sequence,
            state: "queued"
        };

        this.live.set(id, job);
        this.heap.push(job);
        this.#emit("submitted", { id, priority });
        return { ...job };
    }

    reprioritize(id, priority) {
        if (!Number.isInteger(priority) || priority < 0 || priority > 100) {
            throw new RangeError("Priority must be an integer from 0 to 100");
        }
        const previous = this.live.get(id);
        if (!previous || previous.state !== "queued") {
            throw new Error(`Job is not queued: ${id}`);
        }

        // Versioned replacement invalidates the old heap node without
        // needing an expensive arbitrary-index deletion operation.
        const updated = {
            ...previous,
            priority,
            sequence: this.sequence++,
            version: this.sequence
        };
        this.live.set(id, updated);
        this.heap.push(updated);
        this.#emit("reprioritized", { id, priority });
    }

    cancel(id) {
        const job = this.live.get(id);
        if (!job || job.state !== "queued") {
            throw new Error(`Queued job not found: ${id}`);
        }
        this.live.delete(id);
        this.#emit("cancelled", { id });
    }

    #isCurrent(job) {
        return this.live.get(job.id) === job;
    }

    #takeNext() {
        while (this.heap.size > 0) {
            const job = this.heap.pop();
            if (this.#isCurrent(job) && job.state === "queued") {
                return job;
            }
        }
        return undefined;
    }

    #emit(type, detail) {
        this.dispatchEvent(new CustomEvent(type, { detail }));
    }

    async runOne() {
        const job = this.#takeNext();
        if (!job) return null;

        job.state = "running";
        this.#emit("started", { id: job.id });

        try {
            // This models asynchronous work without blocking the event loop.
            await new Promise(resolve => setTimeout(resolve, job.durationMs));
            job.state = "completed";
            this.live.delete(job.id);
            this.#emit("completed", { id: job.id });
            return { id: job.id, state: job.state };
        } catch (error) {
            job.state = "failed";
            this.live.delete(job.id);
            this.#emit("failed", { id: job.id, message: error.message });
            throw error;
        }
    }

    queuedSnapshot() {
        return [...this.live.values()]
            .filter(job => job.state === "queued")
            .sort(compareJobs)
            .map(job => ({ ...job }));
    }
}

async function main() {
    console.log("=== Binary heap ===");
    const heap = new BinaryHeap((a, b) => a - b);
    [14, 3, 9, 1, 7, 2].forEach(value => heap.push(value));
    heap.assertInvariant();
    const sorted = [];
    while (heap.size) sorted.push(heap.pop());
    console.log("Min-heap removal order:", sorted);

    console.log("\n=== Event-driven scheduler ===");
    const scheduler = new JobScheduler(6);

    for (const eventName of [
        "submitted", "reprioritized", "cancelled", "started", "completed"
    ]) {
        scheduler.addEventListener(eventName, event => {
            console.log(`[${eventName}]`, event.detail);
        });
    }

    scheduler.submit({
        id: "INC-41",
        description: "Investigate payment outage",
        priority: 100,
        durationMs: 5
    });
    scheduler.submit({
        id: "BUILD-12",
        description: "Build release candidate",
        priority: 60,
        durationMs: 3
    });
    scheduler.submit({
        id: "REPORT-8",
        description: "Generate weekly report",
        priority: 20,
        durationMs: 1
    });

    scheduler.reprioritize("BUILD-12", 85);
    scheduler.cancel("REPORT-8");

    console.log("Queue snapshot:", scheduler.queuedSnapshot());
    console.log("Processed:", await scheduler.runOne());
    console.log("Processed:", await scheduler.runOne());
    console.log("Empty result:", await scheduler.runOne());

    console.log("\n=== Policy tests ===");
    const tests = new JobScheduler(1);
    tests.submit({
        id: "ONLY",
        description: "Capacity test",
        priority: 50
    });

    assert.throws(() => tests.submit({
        id: "OVERFLOW",
        description: "Rejected",
        priority: 10
    }), /capacity/);

    assert.throws(() => tests.submit({
        id: "ONLY",
        description: "Duplicate",
        priority: 10
    }), /Duplicate/);

    assert.throws(() => tests.reprioritize("UNKNOWN", 20), /not queued/);
    assert.equal((await tests.runOne()).state, "completed");
    assert.equal(await tests.runOne(), null);

    const tieHeap = new BinaryHeap(compareJobs);
    tieHeap.push({ id: "first", priority: 5, sequence: 1 });
    tieHeap.push({ id: "second", priority: 5, sequence: 2 });
    assert.equal(tieHeap.pop().id, "first");

    console.log("All assertions passed.");
}

main().catch(error => {
    console.error("Scheduler failed:", error);
    process.exitCode = 1;
});
