/**
 * Queue Introduction
 *
 * Demonstrates FIFO behavior, queue operations, an array-backed circular
 * queue, a linked-list queue, and an event-driven repository-style queue.
 *
 * Runtime: Node.js 18+
 */

"use strict";

// ---------------------------------------------------------------------------
// Basic FIFO behavior
// ---------------------------------------------------------------------------

function demonstrateFifo() {
    console.log("\n=== FIFO Behavior ===");

    const queue = [];

    queue.push("TASK-001");
    queue.push("TASK-002");
    queue.push("TASK-003");

    console.log("Arrival order:", queue);

    // shift() removes the oldest element, so this directly expresses FIFO.
    const first = queue.shift();
    console.log("Processed first:", first);
    console.log("Remaining:", queue);

    while (queue.length > 0) {
        console.log("Processing:", queue.shift());
    }

    // Array.shift() is convenient but can require moving remaining elements.
    // A production queue with a large workload should avoid repeated shifts.
}

// ---------------------------------------------------------------------------
// Efficient array-backed circular queue
// ---------------------------------------------------------------------------

class CircularQueue {
    constructor(capacity = 8) {
        if (!Number.isInteger(capacity) || capacity <= 0) {
            throw new RangeError("Queue capacity must be a positive integer");
        }

        this.items = new Array(capacity);
        this.capacity = capacity;
        this.front = 0;
        this.rear = 0;
        this.size = 0;
    }

    enqueue(value) {
        if (this.isFull()) {
            throw new Error("Queue is full");
        }

        this.items[this.rear] = value;
        this.rear = (this.rear + 1) % this.capacity;
        this.size += 1;
    }

    dequeue() {
        if (this.isEmpty()) {
            throw new Error("Cannot dequeue from an empty queue");
        }

        const value = this.items[this.front];
        this.items[this.front] = undefined;
        this.front = (this.front + 1) % this.capacity;
        this.size -= 1;

        return value;
    }

    peek() {
        if (this.isEmpty()) {
            throw new Error("Cannot inspect an empty queue");
        }

        return this.items[this.front];
    }

    isEmpty() {
        return this.size === 0;
    }

    isFull() {
        return this.size === this.capacity;
    }

    toArray() {
        const result = [];

        for (let offset = 0; offset < this.size; offset += 1) {
            const index = (this.front + offset) % this.capacity;
            result.push(this.items[index]);
        }

        return result;
    }
}

function demonstrateCircularQueue() {
    console.log("\n=== Circular Array Queue ===");

    const queue = new CircularQueue(4);

    queue.enqueue("ORDER-101");
    queue.enqueue("ORDER-102");
    queue.enqueue("ORDER-103");
    queue.enqueue("ORDER-104");

    console.log("Full queue:", queue.toArray());
    console.log("Front:", queue.peek());

    console.log("Dequeued:", queue.dequeue());
    console.log("Dequeued:", queue.dequeue());

    // The rear wraps to the beginning of the array rather than shifting
    // existing elements.
    queue.enqueue("ORDER-105");
    queue.enqueue("ORDER-106");

    console.log("After wrap-around:", queue.toArray());

    try {
        queue.enqueue("ORDER-107");
        queue.enqueue("ORDER-108");
        queue.enqueue("ORDER-109");
    } catch (error) {
        console.log("Expected capacity error:", error.message);
    }

    while (!queue.isEmpty()) {
        console.log("Processing:", queue.dequeue());
    }
}

// ---------------------------------------------------------------------------
// Linked-list queue
// ---------------------------------------------------------------------------

class QueueNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

class LinkedQueue {
    constructor() {
        this.front = null;
        this.rear = null;
        this.size = 0;
    }

    enqueue(value) {
        const node = new QueueNode(value);

        if (this.rear === null) {
            // Empty queues require both references to point to the new node.
            this.front = node;
            this.rear = node;
        } else {
            this.rear.next = node;
            this.rear = node;
        }

        this.size += 1;
    }

    dequeue() {
        if (this.front === null) {
            throw new Error("Cannot dequeue from an empty queue");
        }

        const value = this.front.value;
        this.front = this.front.next;
        this.size -= 1;

        if (this.front === null) {
            // The last element was removed, so there is no rear node either.
            this.rear = null;
        }

        return value;
    }

    peek() {
        if (this.front === null) {
            throw new Error("Cannot inspect an empty queue");
        }

        return this.front.value;
    }

    isEmpty() {
        return this.front === null;
    }

    toArray() {
        const values = [];
        let current = this.front;

        while (current !== null) {
            values.push(current.value);
            current = current.next;
        }

        return values;
    }
}

function demonstrateLinkedQueue() {
    console.log("\n=== Linked Queue ===");

    const queue = new LinkedQueue();

    queue.enqueue("REQUEST-201");
    queue.enqueue("REQUEST-202");
    queue.enqueue("REQUEST-203");

    console.log("Queue:", queue.toArray());
    console.log("Front:", queue.peek());

    console.log("Dequeued:", queue.dequeue());
    console.log("Queue:", queue.toArray());

    console.log("Dequeued:", queue.dequeue());
    console.log("Dequeued:", queue.dequeue());

    try {
        queue.dequeue();
    } catch (error) {
        console.log("Expected empty-queue error:", error.message);
    }
}

// ---------------------------------------------------------------------------
// Event-driven queue workflow
// ---------------------------------------------------------------------------

class TicketQueue {
    constructor() {
        this.pending = [];
        this.ids = new Set();
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) || [];

        for (const listener of listeners) {
            listener(payload);
        }
    }

    submit(ticket) {
        if (!ticket || typeof ticket !== "object") {
            throw new TypeError("A ticket object is required");
        }

        if (!ticket.id || typeof ticket.id !== "string") {
            throw new TypeError("Ticket ID must be a non-empty string");
        }

        if (!ticket.issue || typeof ticket.issue !== "string") {
            throw new TypeError("Ticket issue must be a non-empty string");
        }

        if (this.ids.has(ticket.id)) {
            throw new Error(`Duplicate ticket ID: ${ticket.id}`);
        }

        this.pending.push(Object.freeze({ ...ticket }));
        this.ids.add(ticket.id);

        this.emit("submitted", ticket);
    }

    processNext() {
        if (this.pending.length === 0) {
            throw new Error("No tickets are waiting");
        }

        const ticket = this.pending.shift();
        this.ids.delete(ticket.id);

        this.emit("processed", ticket);
        return ticket;
    }

    next() {
        if (this.pending.length === 0) {
            return null;
        }

        return this.pending[0];
    }

    count() {
        return this.pending.length;
    }
}

function demonstrateEventDrivenQueue() {
    console.log("\n=== Event-Driven Ticket Queue ===");

    const queue = new TicketQueue();

    queue.on("submitted", ticket => {
        console.log(`Ticket accepted: ${ticket.id}`);
    });

    queue.on("processed", ticket => {
        console.log(`Ticket processed: ${ticket.id}`);
    });

    queue.submit({
        id: "SUP-301",
        customer: "Asha",
        issue: "Payroll access failure"
    });

    queue.submit({
        id: "SUP-302",
        customer: "Rahul",
        issue: "Report export failure"
    });

    queue.submit({
        id: "SUP-303",
        customer: "Meera",
        issue: "Password reset"
    });

    console.log("Next ticket:", queue.next());

    while (queue.count() > 0) {
        queue.processNext();
    }

    try {
        queue.submit({
            id: "SUP-301",
            customer: "Duplicate",
            issue: "Duplicate ID test"
        });
    } catch (error) {
        console.log("Duplicate validation:", error.message);
    }
}

// ---------------------------------------------------------------------------
// Asynchronous producer and consumer
// ---------------------------------------------------------------------------

function sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function demonstrateAsyncQueue() {
    console.log("\n=== Asynchronous Producer and Consumer ===");

    const queue = [];
    let producerFinished = false;

    async function producer() {
        const requests = [
            { id: "ASYNC-1", delay: 20 },
            { id: "ASYNC-2", delay: 10 },
            { id: "ASYNC-3", delay: 15 }
        ];

        for (const request of requests) {
            await sleep(request.delay);
            queue.push(request.id);
            console.log(`Produced: ${request.id}`);
        }

        producerFinished = true;
    }

    async function consumer() {
        while (!producerFinished || queue.length > 0) {
            if (queue.length > 0) {
                const item = queue.shift();
                console.log(`Consumed: ${item}`);
            } else {
                // Waiting briefly prevents a tight polling loop from wasting
                // CPU while the asynchronous producer has not produced data.
                await sleep(5);
            }
        }
    }

    await Promise.all([producer(), consumer()]);
}

// ---------------------------------------------------------------------------
// Invariant verification
// ---------------------------------------------------------------------------

function verifyInvariants() {
    console.log("\n=== Queue Invariant Verification ===");

    const queue = new CircularQueue(3);

    if (!queue.isEmpty()) {
        throw new Error("New queue must be empty");
    }

    queue.enqueue(10);
    queue.enqueue(20);
    queue.enqueue(30);

    if (!queue.isFull()) {
        throw new Error("Queue should be full");
    }

    if (queue.dequeue() !== 10 || queue.dequeue() !== 20) {
        throw new Error("FIFO order was violated");
    }

    queue.enqueue(40);

    if (JSON.stringify(queue.toArray()) !== JSON.stringify([30, 40])) {
        throw new Error("Circular wrap-around failed");
    }

    if (queue.dequeue() !== 30 || queue.dequeue() !== 40) {
        throw new Error("FIFO order failed after wrap-around");
    }

    if (!queue.isEmpty()) {
        throw new Error("Queue should be empty");
    }

    console.log("All queue invariants passed.");
}

// ---------------------------------------------------------------------------
// Complexity notes
// ---------------------------------------------------------------------------

function printComplexity() {
    console.log("\n=== Complexity ===");
    console.log("Array push():             O(1) amortized");
    console.log("Array shift():            O(n) in typical array implementations");
    console.log("Circular enqueue():       O(1)");
    console.log("Circular dequeue():       O(1)");
    console.log("Linked enqueue():         O(1)");
    console.log("Linked dequeue():         O(1)");
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
    demonstrateFifo();
    demonstrateCircularQueue();
    demonstrateLinkedQueue();
    demonstrateEventDrivenQueue();
    await demonstrateAsyncQueue();
    verifyInvariants();
    printComplexity();
}

main().catch(error => {
    console.error("Queue demonstration failed:", error.message);
    process.exitCode = 1;
});
