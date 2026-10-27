"use strict";

/*
 * Merge Sort: an event-driven policy and sorting model.
 *
 * This implementation uses a reusable merge buffer and an iterative
 * bottom-up strategy. It complements a recursive implementation by
 * eliminating recursion depth concerns while retaining O(n log n) time.
 */

class MergeSortError extends Error {
    constructor(message) {
        super(message);
        this.name = "MergeSortError";
    }
}

class MergeSortEngine {
    constructor({ key = value => value, descending = false } = {}) {
        if (typeof key !== "function") {
            throw new MergeSortError("key must be a function.");
        }

        this.key = key;
        this.descending = descending;
        this.comparisons = 0;
        this.merges = 0;
    }

    compare(left, right) {
        this.comparisons += 1;

        const a = this.key(left);
        const b = this.key(right);

        if (this.descending) {
            if (a > b) return -1;
            if (a < b) return 1;
            return 0;
        }

        if (a < b) return -1;
        if (a > b) return 1;
        return 0;
    }

    sort(input) {
        if (!Array.isArray(input)) {
            throw new MergeSortError("Input must be an array.");
        }

        const values = [...input];

        // Validate keys before sorting.
        for (const value of values) {
            try {
                this.key(value);
            } catch (error) {
                throw new MergeSortError(
                    `Key evaluation failed: ${error.message}`
                );
            }
        }

        this.comparisons = 0;
        this.merges = 0;

        if (values.length < 2) {
            return {
                values,
                comparisons: 0,
                merges: 0
            };
        }

        let source = values;
        let target = new Array(values.length);

        // Bottom-up merge sort processes runs of width 1, 2, 4, 8, ...
        for (let width = 1; width < values.length; width *= 2) {
            for (let left = 0; left < values.length; left += width * 2) {
                const middle = Math.min(left + width, values.length);
                const right = Math.min(left + width * 2, values.length);

                this.merge(source, target, left, middle, right);
            }

            [source, target] = [target, source];
        }

        // Depending on the number of passes, source may be the temporary
        // buffer rather than the original array.
        const result = source.slice();

        return {
            values: result,
            comparisons: this.comparisons,
            merges: this.merges
        };
    }

    merge(source, target, left, middle, right) {
        this.merges += 1;

        let i = left;
        let j = middle;
        let k = left;

        while (i < middle && j < right) {
            // <= is represented by compare === -1 or 0. Selecting the
            // left value on equality preserves stability.
            if (this.compare(source[i], source[j]) <= 0) {
                target[k++] = source[i++];
            } else {
                target[k++] = source[j++];
            }
        }

        while (i < middle) {
            target[k++] = source[i++];
        }

        while (j < right) {
            target[k++] = source[j++];
        }
    }
}

class SortEventBus {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (typeof listener !== "function") {
            throw new TypeError("Listener must be a function.");
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        this.listeners.get(eventName).add(listener);

        return () => this.listeners.get(eventName)?.delete(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName);

        if (!listeners) {
            return;
        }

        for (const listener of listeners) {
            try {
                listener(payload);
            } catch (error) {
                console.error(`Event listener failed for ${eventName}:`, error);
            }
        }
    }
}

class SortingService {
    constructor() {
        this.events = new SortEventBus();
    }

    async sortRecords(records, options = {}) {
        this.events.emit("sort:start", {
            count: Array.isArray(records) ? records.length : 0
        });

        try {
            // Promise.resolve keeps the service suitable for an application
            // where records may later come from asynchronous storage.
            const result = await Promise.resolve().then(() => {
                const engine = new MergeSortEngine(options);
                return engine.sort(records);
            });

            this.events.emit("sort:complete", result);
            return result;
        } catch (error) {
            this.events.emit("sort:error", {
                message: error.message
            });
            throw error;
        }
    }
}

function assertEqual(actual, expected, message) {
    const a = JSON.stringify(actual);
    const b = JSON.stringify(expected);

    if (a !== b) {
        throw new Error(`${message}\nExpected: ${b}\nActual: ${a}`);
    }
}

async function main() {
    const service = new SortingService();

    service.events.on("sort:start", ({ count }) => {
        console.log(`Starting sort for ${count} records.`);
    });

    service.events.on("sort:complete", result => {
        console.log(
            `Completed: ${result.comparisons} comparisons, ` +
            `${result.merges} merges.`
        );
    });

    service.events.on("sort:error", error => {
        console.error(`Sort failed: ${error.message}`);
    });

    const numbers = [9, 4, 7, 1, 3, 8, 2, 6, 5];

    const ascending = await service.sortRecords(numbers);
    assertEqual(
        ascending.values,
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "Ascending sort failed."
    );

    console.log("Ascending:", ascending.values);

    const descending = await service.sortRecords(numbers, {
        descending: true
    });

    assertEqual(
        descending.values,
        [9, 8, 7, 6, 5, 4, 3, 2, 1],
        "Descending sort failed."
    );

    console.log("Descending:", descending.values);

    const users = [
        { id: 1, name: "Asha", score: 90 },
        { id: 2, name: "Ravi", score: 70 },
        { id: 3, name: "Maya", score: 90 },
        { id: 4, name: "Karan", score: 70 }
    ];

    const byScore = await service.sortRecords(users, {
        key: user => user.score
    });

    assertEqual(
        byScore.values.map(user => user.id),
        [2, 4, 1, 3],
        "Stable object sort failed."
    );

    console.log("Stable object ordering:", byScore.values);

    try {
        await service.sortRecords("not-an-array");
    } catch (error) {
        console.log("Expected validation failure:", error.message);
    }

    // Empty and singleton inputs are valid and require no merge work.
    const empty = await service.sortRecords([]);
    const singleton = await service.sortRecords([42]);

    assertEqual(empty.values, [], "Empty input failed.");
    assertEqual(singleton.values, [42], "Singleton input failed.");

    console.log("Edge cases: PASSED");
}

main().catch(error => {
    console.error("Fatal error:", error);
    process.exitCode = 1;
});
