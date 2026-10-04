"use strict";

/*
 * Linked List Reversal Laboratory
 *
 * This file uses JavaScript-specific features to model:
 * - iterative pointer reversal
 * - recursive reversal
 * - reverse-in-groups
 * - event-driven workflow reporting
 * - validation and invariant checking
 * - asynchronous execution of independent experiments
 *
 * Run with:
 *   node linked-list-reversal.js
 */

class ListNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

class SinglyLinkedList {
    constructor(values = []) {
        this.head = null;
        this.tail = null;
        this.size = 0;

        for (const value of values) {
            this.append(value);
        }
    }

    append(value) {
        const node = new ListNode(value);

        if (this.head === null) {
            this.head = node;
            this.tail = node;
        } else {
            this.tail.next = node;
            this.tail = node;
        }

        this.size += 1;
    }

    toArray() {
        const values = [];
        const visited = new Set();

        let current = this.head;

        while (current !== null) {
            if (visited.has(current)) {
                throw new Error("Cycle detected during traversal.");
            }

            visited.add(current);
            values.push(current.value);
            current = current.next;
        }

        return values;
    }

    toString() {
        return `${this.toArray().join(" -> ")} -> null`;
    }

    validate() {
        let count = 0;
        let current = this.head;
        let last = null;
        const visited = new Set();

        while (current !== null) {
            if (visited.has(current)) {
                throw new Error("Invariant violation: cycle detected.");
            }

            visited.add(current);
            count += 1;
            last = current;
            current = current.next;
        }

        if (count !== this.size) {
            throw new Error(
                `Invariant violation: expected ${this.size} nodes, found ${count}.`
            );
        }

        if (last !== this.tail) {
            throw new Error("Invariant violation: tail does not reference final node.");
        }

        if (this.tail !== null && this.tail.next !== null) {
            throw new Error("Invariant violation: tail.next must be null.");
        }

        return true;
    }

    reverseIterative() {
        let previous = null;
        let current = this.head;
        const oldHead = this.head;

        while (current !== null) {
            /*
             * JavaScript assignment is sequential here. Save the original
             * successor before overwriting current.next.
             */
            const nextNode = current.next;
            current.next = previous;
            previous = current;
            current = nextNode;
        }

        this.head = previous;
        this.tail = oldHead;
        return this;
    }

    reverseRecursive() {
        const oldHead = this.head;

        const reverse = (current, previous) => {
            if (current === null) {
                return previous;
            }

            const nextNode = current.next;
            current.next = previous;

            return reverse(nextNode, current);
        };

        this.head = reverse(this.head, null);
        this.tail = oldHead;
        return this;
    }

    reverseInGroups(k) {
        if (!Number.isInteger(k) || k < 1) {
            throw new RangeError("k must be a positive integer.");
        }

        if (k === 1 || this.head === null) {
            return this;
        }

        /*
         * A dummy node removes a special case for the first group.
         * groupPrevious always points to the node immediately before the
         * group currently being reversed.
         */
        const dummy = new ListNode(Symbol("dummy"));
        dummy.next = this.head;

        let groupPrevious = dummy;

        while (true) {
            let kth = groupPrevious;

            for (let i = 0; i < k; i += 1) {
                kth = kth.next;

                if (kth === null) {
                    this.head = dummy.next;
                    this.recomputeTail();
                    return this;
                }
            }

            const groupNext = kth.next;
            let previous = groupNext;
            let current = groupPrevious.next;

            while (current !== groupNext) {
                const nextNode = current.next;
                current.next = previous;
                previous = current;
                current = nextNode;
            }

            const oldGroupHead = groupPrevious.next;
            groupPrevious.next = kth;
            groupPrevious = oldGroupHead;
        }
    }

    reverseInGroupsRecursive(k) {
        if (!Number.isInteger(k) || k < 1) {
            throw new RangeError("k must be a positive integer.");
        }

        if (k === 1 || this.head === null) {
            return this;
        }

        const reverseGroups = (head) => {
            let probe = head;

            /*
             * Do not reverse a short final group. Checking availability before
             * changing links prevents partial reversal.
             */
            for (let i = 0; i < k; i += 1) {
                if (probe === null) {
                    return head;
                }
                probe = probe.next;
            }

            let previous = null;
            let current = head;

            for (let i = 0; i < k; i += 1) {
                const nextNode = current.next;
                current.next = previous;
                previous = current;
                current = nextNode;
            }

            head.next = reverseGroups(current);
            return previous;
        };

        const oldHead = this.head;
        this.head = reverseGroups(this.head);
        this.tail = oldHead;
        this.recomputeTail();

        return this;
    }

    recomputeTail() {
        if (this.head === null) {
            this.tail = null;
            return;
        }

        let current = this.head;

        while (current.next !== null) {
            current = current.next;
        }

        this.tail = current;
    }
}

function expectedGroupReversal(values, k) {
    if (k <= 1) {
        return [...values];
    }

    const result = [];

    for (let start = 0; start < values.length; start += k) {
        const group = values.slice(start, start + k);

        if (group.length === k) {
            result.push(...group.reverse());
        } else {
            result.push(...group);
        }
    }

    return result;
}

function assertArrayEqual(actual, expected, label) {
    const same =
        actual.length === expected.length &&
        actual.every((value, index) => value === expected[index]);

    if (!same) {
        throw new Error(
            `${label} failed.\nExpected: ${JSON.stringify(expected)}\nActual: ${JSON.stringify(actual)}`
        );
    }
}

function demonstrateIterative() {
    console.log("\n=== Iterative reversal ===");

    const list = new SinglyLinkedList([10, 20, 30, 40, 50]);

    console.log("Before:", list.toString());
    list.reverseIterative();
    list.validate();
    console.log("After: ", list.toString());

    assertArrayEqual(
        list.toArray(),
        [50, 40, 30, 20, 10],
        "Iterative reversal"
    );
}

function demonstrateRecursive() {
    console.log("\n=== Recursive reversal ===");

    const list = new SinglyLinkedList(["A", "B", "C", "D"]);

    console.log("Before:", list.toString());
    list.reverseRecursive();
    list.validate();
    console.log("After: ", list.toString());

    assertArrayEqual(
        list.toArray(),
        ["D", "C", "B", "A"],
        "Recursive reversal"
    );
}

function demonstrateGroups() {
    console.log("\n=== Reverse in groups ===");

    const scenarios = [
        { values: [1, 2, 3, 4, 5, 6, 7], k: 3 },
        { values: [1, 2, 3, 4, 5, 6], k: 2 },
        { values: [1, 2, 3, 4, 5], k: 4 },
        { values: [1, 2, 3], k: 5 }
    ];

    for (const { values, k } of scenarios) {
        const list = new SinglyLinkedList(values);
        list.reverseInGroups(k);
        list.validate();

        const expected = expectedGroupReversal(values, k);

        console.log(`Input ${JSON.stringify(values)}, k=${k}`);
        console.log("Output:", list.toArray());

        assertArrayEqual(
            list.toArray(),
            expected,
            `Group reversal k=${k}`
        );
    }
}

function demonstrateEventDrivenWorkflow() {
    console.log("\n=== Event-driven reversal workflow ===");

    const events = [];
    const listeners = new Map();

    function on(eventName, listener) {
        if (!listeners.has(eventName)) {
            listeners.set(eventName, []);
        }
        listeners.get(eventName).push(listener);
    }

    function emit(eventName, payload) {
        events.push({ eventName, payload });

        const handlers = listeners.get(eventName) ?? [];
        for (const handler of handlers) {
            handler(payload);
        }
    }

    on("reversal:start", ({ operation, size }) => {
        console.log(`Starting ${operation} on ${size} nodes.`);
    });

    on("reversal:complete", ({ operation, values }) => {
        console.log(`${operation} completed:`, values);
    });

    const list = new SinglyLinkedList([5, 10, 15, 20]);

    emit("reversal:start", {
        operation: "iterative-reversal",
        size: list.size
    });

    list.reverseIterative();

    emit("reversal:complete", {
        operation: "iterative-reversal",
        values: list.toArray()
    });

    console.log("Recorded events:", events.length);
}

async function demonstrateAsyncPipelines() {
    console.log("\n=== Asynchronous experiment pipeline ===");

    /*
     * Promise.all is useful when separate list experiments do not depend
     * on one another. JavaScript's event loop can schedule their completion
     * without introducing shared mutable state.
     */
    const experiments = [
        Promise.resolve().then(() => {
            const list = new SinglyLinkedList([1, 2, 3, 4]);
            list.reverseIterative();
            return { method: "iterative", result: list.toArray() };
        }),
        Promise.resolve().then(() => {
            const list = new SinglyLinkedList([1, 2, 3, 4]);
            list.reverseRecursive();
            return { method: "recursive", result: list.toArray() };
        }),
        Promise.resolve().then(() => {
            const list = new SinglyLinkedList([1, 2, 3, 4, 5, 6]);
            list.reverseInGroups(2);
            return { method: "groups", result: list.toArray() };
        })
    ];

    const results = await Promise.all(experiments);

    for (const result of results) {
        console.log(result.method, "=>", result.result);
    }
}

function demonstrateFailureHandling() {
    console.log("\n=== Validation and failure handling ===");

    const list = new SinglyLinkedList([1, 2, 3]);

    for (const invalidK of [0, -2, 1.5, NaN]) {
        try {
            list.reverseInGroups(invalidK);
        } catch (error) {
            console.log(
                `Rejected k=${String(invalidK)}:`,
                error instanceof Error ? error.message : String(error)
            );
        }
    }

    list.validate();
    console.log("List remained valid:", list.toArray());
}

function deterministicRandom(seed) {
    /*
     * Small deterministic generator makes correctness tests reproducible
     * without an external package.
     */
    let state = seed >>> 0;

    return () => {
        state = (1664525 * state + 1013904223) >>> 0;
        return state / 0x100000000;
    };
}

function runRandomizedChecks() {
    console.log("\n=== Randomized correctness checks ===");

    const random = deterministicRandom(20261005);

    for (let test = 0; test < 300; test += 1) {
        const length = Math.floor(random() * 31);
        const values = Array.from(
            { length },
            () => Math.floor(random() * 201) - 100
        );

        const iterative = new SinglyLinkedList(values);
        iterative.reverseIterative();

        assertArrayEqual(
            iterative.toArray(),
            [...values].reverse(),
            "Random iterative reversal"
        );
        iterative.validate();

        const recursive = new SinglyLinkedList(values);
        recursive.reverseRecursive();

        assertArrayEqual(
            recursive.toArray(),
            [...values].reverse(),
            "Random recursive reversal"
        );
        recursive.validate();

        const k = 1 + Math.floor(random() * 10);
        const grouped = new SinglyLinkedList(values);
        grouped.reverseInGroups(k);

        assertArrayEqual(
            grouped.toArray(),
            expectedGroupReversal(values, k),
            "Random group reversal"
        );
        grouped.validate();
    }

    console.log("300 randomized cases passed.");
}

function explainComplexity() {
    console.log("\n=== Complexity ===");
    console.log("Iterative reversal:         O(n) time, O(1) auxiliary space");
    console.log("Recursive reversal:         O(n) time, O(n) call-stack space");
    console.log("Iterative group reversal:   O(n) time, O(1) auxiliary space");
    console.log("Recursive group reversal:   O(n) time, O(n/k) call-stack space");
    console.log(
        "Production consideration: recursion depth is bounded by the JavaScript runtime."
    );
}

async function main() {
    console.log("LINKED LIST REVERSAL LABORATORY");

    demonstrateIterative();
    demonstrateRecursive();
    demonstrateGroups();
    demonstrateEventDrivenWorkflow();
    demonstrateFailureHandling();
    runRandomizedChecks();
    await demonstrateAsyncPipelines();
    explainComplexity();

    console.log("\nAll JavaScript demonstrations completed successfully.");
}

main().catch((error) => {
    console.error("Execution failed:", error);
    process.exitCode = 1;
});
