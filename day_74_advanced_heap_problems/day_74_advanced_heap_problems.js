"use strict";

/*
 * Advanced Heap Problems
 *
 * JavaScript implementation using:
 * - Custom binary heaps
 * - Event-driven scheduling
 * - Promise-based task execution
 * - Streaming median
 * - K-way merge
 * - Greedy project selection
 * - Greedy refueling
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

// ============================================================
// 1. GENERIC BINARY HEAP
// ============================================================

class BinaryHeap {
    constructor(compare) {
        if (typeof compare !== "function") {
            throw new TypeError("Comparator required");
        }

        this.items = [];
        this.compare = compare;
    }

    get size() {
        return this.items.length;
    }

    isEmpty() {
        return this.size === 0;
    }

    peek() {
        return this.items[0] ?? null;
    }

    push(value) {
        this.items.push(value);
        this.#siftUp(this.size - 1);
    }

    pop() {
        if (this.isEmpty()) return null;

        const result = this.items[0];
        const last = this.items.pop();

        if (!this.isEmpty()) {
            this.items[0] = last;
            this.#siftDown(0);
        }

        return result;
    }

    #siftUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.compare(
                this.items[index],
                this.items[parent]
            ) >= 0) {
                break;
            }

            [this.items[index], this.items[parent]] =
                [this.items[parent], this.items[index]];

            index = parent;
        }
    }

    #siftDown(index) {
        const length = this.size;

        while (true) {
            let smallest = index;
            const left = index * 2 + 1;
            const right = left + 1;

            if (
                left < length &&
                this.compare(
                    this.items[left],
                    this.items[smallest]
                ) < 0
            ) {
                smallest = left;
            }

            if (
                right < length &&
                this.compare(
                    this.items[right],
                    this.items[smallest]
                ) < 0
            ) {
                smallest = right;
            }

            if (smallest === index) break;

            [this.items[index], this.items[smallest]] =
                [this.items[smallest], this.items[index]];

            index = smallest;
        }
    }
}


// ============================================================
// 2. STREAMING MEDIAN
// ============================================================

class StreamingMedian {
    constructor() {
        this.lower = new BinaryHeap((a, b) => b - a);
        this.upper = new BinaryHeap((a, b) => a - b);
    }

    add(value) {
        if (!Number.isFinite(value)) {
            throw new TypeError("Value must be finite");
        }

        this.lower.push(value);

        if (
            !this.upper.isEmpty() &&
            this.lower.peek() > this.upper.peek()
        ) {
            this.upper.push(this.lower.pop());
        }

        if (this.lower.size > this.upper.size + 1) {
            this.upper.push(this.lower.pop());
        } else if (this.upper.size > this.lower.size) {
            this.lower.push(this.upper.pop());
        }
    }

    median() {
        if (this.lower.isEmpty()) {
            throw new Error("Median of empty stream is undefined");
        }

        if (this.lower.size > this.upper.size) {
            return this.lower.peek();
        }

        return (this.lower.peek() + this.upper.peek()) / 2;
    }

    get size() {
        return this.lower.size + this.upper.size;
    }
}


// ============================================================
// 3. EVENT-DRIVEN PRIORITY SCHEDULER
// ============================================================

class PriorityScheduler extends EventEmitter {
    constructor() {
        super();

        this.queue = new BinaryHeap(
            (a, b) =>
                a.priority - b.priority ||
                a.sequence - b.sequence
        );

        this.sequence = 0;
        this.taskIds = new Set();
        this.completed = new Map();
        this.running = false;
    }

    submit({ id, priority, execute }) {
        if (typeof id !== "string" || !id.trim()) {
            throw new TypeError("Valid task ID required");
        }

        if (this.taskIds.has(id)) {
            throw new Error(`Duplicate task: ${id}`);
        }

        if (!Number.isSafeInteger(priority) || priority < 0) {
            throw new RangeError("Invalid priority");
        }

        if (typeof execute !== "function") {
            throw new TypeError("Task must have an execute function");
        }

        const task = Object.freeze({
            id,
            priority,
            sequence: this.sequence++,
            execute
        });

        this.taskIds.add(id);
        this.queue.push(task);

        this.emit("submitted", { id, priority });
    }

    async run() {
        if (this.running) {
            throw new Error("Scheduler is already running");
        }

        this.running = true;

        try {
            while (!this.queue.isEmpty()) {
                const task = this.queue.pop();

                this.emit("started", task.id);

                try {
                    const result = await task.execute();

                    this.completed.set(task.id, {
                        status: "completed",
                        result
                    });

                    this.emit("completed", task.id, result);
                } catch (error) {
                    this.completed.set(task.id, {
                        status: "failed",
                        error: error.message
                    });

                    this.emit("failed", task.id, error);
                }
            }
        } finally {
            this.running = false;
        }

        return new Map(this.completed);
    }
}


// ============================================================
// 4. K-WAY MERGE
// ============================================================

function mergeKSortedLists(lists) {
    if (!Array.isArray(lists)) {
        throw new TypeError("Expected an array of lists");
    }

    for (const list of lists) {
        if (!Array.isArray(list)) {
            throw new TypeError("Each sequence must be an array");
        }

        for (let i = 1; i < list.length; i++) {
            if (list[i - 1] > list[i]) {
                throw new RangeError("Input lists must be sorted");
            }
        }
    }

    const heap = new BinaryHeap(
        (a, b) =>
            a.value - b.value ||
            a.listIndex - b.listIndex ||
            a.elementIndex - b.elementIndex
    );

    lists.forEach((list, listIndex) => {
        if (list.length > 0) {
            heap.push({
                value: list[0],
                listIndex,
                elementIndex: 0
            });
        }
    });

    const result = [];

    while (!heap.isEmpty()) {
        const current = heap.pop();

        result.push(current.value);

        const nextIndex = current.elementIndex + 1;
        const list = lists[current.listIndex];

        if (nextIndex < list.length) {
            heap.push({
                value: list[nextIndex],
                listIndex: current.listIndex,
                elementIndex: nextIndex
            });
        }
    }

    return result;
}


// ============================================================
// 5. MAXIMUM CAPITAL
// ============================================================

function maximizeCapital(initialCapital, projects, limit) {
    if (
        !Number.isFinite(initialCapital) ||
        initialCapital < 0 ||
        !Number.isSafeInteger(limit) ||
        limit < 0
    ) {
        throw new RangeError("Invalid capital or project limit");
    }

    const ids = new Set();

    const sorted = projects.map(project => {
        const {
            id,
            requiredCapital,
            profit
        } = project;

        if (
            typeof id !== "string" ||
            !id.trim() ||
            ids.has(id) ||
            !Number.isFinite(requiredCapital) ||
            !Number.isFinite(profit) ||
            requiredCapital < 0 ||
            profit < 0
        ) {
            throw new Error("Invalid or duplicate project");
        }

        ids.add(id);

        return Object.freeze({
            id,
            requiredCapital,
            profit
        });
    }).sort(
        (a, b) =>
            a.requiredCapital - b.requiredCapital
    );

    // Negative profit makes the max heap work with a min heap.
    const affordable = new BinaryHeap(
        (a, b) => b.profit - a.profit
    );

    let capital = initialCapital;
    let index = 0;
    const selected = [];

    while (selected.length < limit) {
        while (
            index < sorted.length &&
            sorted[index].requiredCapital <= capital
        ) {
            affordable.push(sorted[index]);
            index++;
        }

        if (
            affordable.isEmpty() ||
            affordable.peek().profit === 0
        ) {
            break;
        }

        const project = affordable.pop();

        capital += project.profit;
        selected.push(project.id);
    }

    return {
        finalCapital: capital,
        selected
    };
}


// ============================================================
// 6. MINIMUM REFUELING STOPS
// ============================================================

function minimumRefuelingStops(target, initialFuel, stations) {
    if (
        !Number.isFinite(target) ||
        !Number.isFinite(initialFuel) ||
        target < 0 ||
        initialFuel < 0
    ) {
        throw new RangeError("Invalid target or fuel");
    }

    const sorted = stations.map((station, index) => {
        if (
            !Number.isFinite(station.position) ||
            !Number.isFinite(station.fuel) ||
            station.position < 0 ||
            station.position > target ||
            station.fuel < 0
        ) {
            throw new RangeError("Invalid station");
        }

        return {
            ...station,
            index
        };
    }).sort((a, b) => a.position - b.position);

    for (let i = 1; i < sorted.length; i++) {
        if (sorted[i - 1].position === sorted[i].position) {
            throw new Error("Station positions must be unique");
        }
    }

    const fuelHeap = new BinaryHeap(
        (a, b) =>
            b.fuel - a.fuel ||
            a.index - b.index
    );

    let reachable = initialFuel;
    const selected = [];

    for (const station of sorted) {
        while (reachable < station.position) {
            if (fuelHeap.isEmpty()) {
                return { stops: -1, selected: [] };
            }

            const best = fuelHeap.pop();

            reachable += best.fuel;
            selected.push(best.index);
        }

        fuelHeap.push(station);
    }

    while (reachable < target) {
        if (fuelHeap.isEmpty()) {
            return { stops: -1, selected: [] };
        }

        const best = fuelHeap.pop();

        reachable += best.fuel;
        selected.push(best.index);
    }

    return {
        stops: selected.length,
        selected
    };
}


// ============================================================
// 7. DEADLINE-BASED GREEDY SCHEDULING
// ============================================================

function maximizeDeadlineProfit(tasks) {
    const ids = new Set();

    const sorted = tasks.map(task => {
        if (
            typeof task.id !== "string" ||
            !task.id.trim() ||
            ids.has(task.id) ||
            !Number.isSafeInteger(task.deadline) ||
            task.deadline <= 0 ||
            !Number.isFinite(task.profit) ||
            task.profit < 0
        ) {
            throw new Error("Invalid deadline task");
        }

        ids.add(task.id);

        return { ...task };
    }).sort((a, b) => a.deadline - b.deadline);

    const selected = new BinaryHeap(
        (a, b) =>
            a.profit - b.profit ||
            a.id.localeCompare(b.id)
    );

    let totalProfit = 0;

    for (const task of sorted) {
        selected.push(task);
        totalProfit += task.profit;

        if (selected.size > task.deadline) {
            totalProfit -= selected.pop().profit;
        }
    }

    return {
        totalProfit,
        selected: selected.items
            .map(task => task.id)
            .sort()
    };
}


// ============================================================
// 8. TESTING AND EXECUTION
// ============================================================

async function main() {

    console.log("\nADVANCED HEAP PROBLEMS");
    console.log("=".repeat(55));

    console.log("\n1. Streaming Median");

    const median = new StreamingMedian();

    for (const value of [12, 4, 5, 3, 8, 7]) {
        median.add(value);
        console.log(value, "=>", median.median());
    }

    assert.equal(median.median(), 6);

    console.log("\n2. Event-Driven Scheduling");

    const scheduler = new PriorityScheduler();

    scheduler.on("submitted", event => {
        console.log("Submitted:", event.id);
    });

    scheduler.on("completed", id => {
        console.log("Completed:", id);
    });

    scheduler.on("failed", (id, error) => {
        console.error("Failed:", id, error.message);
    });

    scheduler.submit({
        id: "backup",
        priority: 3,
        execute: async () => "Backup complete"
    });

    scheduler.submit({
        id: "security",
        priority: 1,
        execute: async () => "Security scan complete"
    });

    scheduler.submit({
        id: "report",
        priority: 2,
        execute: async () => "Report generated"
    });

    await scheduler.run();

    assert.equal(
        scheduler.completed.get("security").status,
        "completed"
    );

    console.log("\n3. Merge K Sorted Lists");

    const merged = mergeKSortedLists([
        [1, 4, 7],
        [2, 5, 8],
        [3, 6, 9]
    ]);

    console.log(merged);

    assert.deepEqual(
        merged,
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
    );

    console.log("\n4. Maximum Capital");

    const capitalResult = maximizeCapital(
        1,
        [
            { id: "Infrastructure", requiredCapital: 0, profit: 2 },
            { id: "Analytics", requiredCapital: 1, profit: 5 },
            { id: "Security", requiredCapital: 2, profit: 8 },
            { id: "Cloud", requiredCapital: 5, profit: 10 }
        ],
        3
    );

    console.log(capitalResult);

    assert.equal(capitalResult.finalCapital, 16);

    console.log("\n5. Minimum Refueling Stops");

    const refuelResult = minimumRefuelingStops(
        100,
        10,
        [
            { position: 10, fuel: 60 },
            { position: 20, fuel: 30 },
            { position: 30, fuel: 30 },
            { position: 60, fuel: 40 }
        ]
    );

    console.log(refuelResult);

    assert.equal(refuelResult.stops, 2);

    console.log("\n6. Deadline Scheduling");

    const deadlineResult = maximizeDeadlineProfit([
        { id: "A", deadline: 2, profit: 100 },
        { id: "B", deadline: 1, profit: 19 },
        { id: "C", deadline: 2, profit: 27 },
        { id: "D", deadline: 1, profit: 25 },
        { id: "E", deadline: 3, profit: 15 }
    ]);

    console.log(deadlineResult);

    assert.equal(deadlineResult.totalProfit, 142);

    console.log("\n7. Edge Case Validation");

    assert.throws(() => median.median() === null);

    assert.throws(
        () => mergeKSortedLists([[3, 1]])
    );

    assert.equal(
        minimumRefuelingStops(100, 10, []).stops,
        -1
    );

    assert.throws(
        () => maximizeCapital(-1, [], 2)
    );

    console.log("All assertions passed.");
}

main().catch(error => {
    console.error("Application failure:", error);
    process.exitCode = 1;
});
