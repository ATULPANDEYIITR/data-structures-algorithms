"use strict";

/*
 * Circular Queue in JavaScript
 *
 * The queue uses a fixed array plus three pieces of state:
 *   front -> position of the oldest element
 *   rear  -> position where the next element is inserted
 *   size  -> number of elements currently stored
 *
 * The modulo operator provides wrap-around without moving existing elements.
 */

class QueueFullError extends Error {
    constructor(message) {
        super(message);
        this.name = "QueueFullError";
    }
}

class QueueEmptyError extends Error {
    constructor(message) {
        super(message);
        this.name = "QueueEmptyError";
    }
}

class CircularQueue {
    constructor(capacity) {
        if (!Number.isInteger(capacity) || capacity <= 0) {
            throw new TypeError("Capacity must be a positive integer.");
        }

        this.capacity = capacity;
        this.buffer = new Array(capacity);
        this.front = 0;
        this.rear = 0;
        this.size = 0;
    }

    get isEmpty() {
        return this.size === 0;
    }

    get isFull() {
        return this.size === this.capacity;
    }

    nextIndex(index) {
        return (index + 1) % this.capacity;
    }

    enqueue(value) {
        if (this.isFull) {
            throw new QueueFullError("Circular queue overflow.");
        }

        this.buffer[this.rear] = value;
        this.rear = this.nextIndex(this.rear);
        this.size += 1;
    }

    dequeue() {
        if (this.isEmpty) {
            throw new QueueEmptyError("Circular queue underflow.");
        }

        const value = this.buffer[this.front];

        // Clearing the slot prevents an obsolete object reference from being
        // retained after the value has logically left the queue.
        this.buffer[this.front] = undefined;
        this.front = this.nextIndex(this.front);
        this.size -= 1;

        return value;
    }

    peek() {
        if (this.isEmpty) {
            throw new QueueEmptyError("Cannot peek at an empty queue.");
        }

        return this.buffer[this.front];
    }

    values() {
        const result = [];
        let index = this.front;

        for (let count = 0; count < this.size; count += 1) {
            result.push(this.buffer[index]);
            index = this.nextIndex(index);
        }

        return result;
    }

    clear() {
        this.buffer.fill(undefined);
        this.front = 0;
        this.rear = 0;
        this.size = 0;
    }

    snapshot() {
        return {
            capacity: this.capacity,
            front: this.front,
            rear: this.rear,
            size: this.size,
            isEmpty: this.isEmpty,
            isFull: this.isFull,
            logicalValues: this.values(),
            physicalBuffer: [...this.buffer]
        };
    }
}

/*
 * Event-driven workflow.
 *
 * A circular queue can serve as a bounded event buffer. The producer creates
 * events and the consumer removes them in FIFO order. A bounded buffer makes
 * back-pressure visible: the producer cannot silently exceed available memory.
 */
class EventBuffer {
    constructor(capacity) {
        this.queue = new CircularQueue(capacity);
        this.processed = 0;
        this.rejected = 0;
    }

    publish(event) {
        try {
            this.queue.enqueue(event);
            return true;
        } catch (error) {
            if (error instanceof QueueFullError) {
                this.rejected += 1;
                return false;
            }
            throw error;
        }
    }

    consume() {
        if (this.queue.isEmpty) {
            return null;
        }

        const event = this.queue.dequeue();
        this.processed += 1;
        return event;
    }
}

/*
 * Dynamic variant.
 *
 * A fixed circular buffer has deterministic capacity. This implementation
 * grows the buffer when necessary. Resizing requires copying logical queue
 * order into a new contiguous representation, so growth is an O(n) event.
 */
class DynamicCircularQueue extends CircularQueue {
    enqueue(value) {
        if (this.isFull) {
            this.resize(this.capacity * 2);
        }

        super.enqueue(value);
    }

    resize(newCapacity) {
        if (!Number.isInteger(newCapacity) || newCapacity <= this.capacity) {
            throw new RangeError("New capacity must exceed current capacity.");
        }

        const ordered = this.values();

        this.capacity = newCapacity;
        this.buffer = new Array(newCapacity);

        for (let index = 0; index < ordered.length; index += 1) {
            this.buffer[index] = ordered[index];
        }

        this.front = 0;
        this.rear = ordered.length;
    }
}

function demonstrateBasicQueue() {
    console.log("\n=== Basic Queue ===");

    const queue = new CircularQueue(4);

    queue.enqueue("request-A");
    queue.enqueue("request-B");
    queue.enqueue("request-C");

    console.log(queue.snapshot());
    console.log("Peek:", queue.peek());
    console.log("Dequeue:", queue.dequeue());

    queue.enqueue("request-D");
    queue.enqueue("request-E");

    console.log("Logical FIFO order:", queue.values());
    console.log("Physical storage:", queue.buffer);
}

function demonstrateWrapAround() {
    console.log("\n=== Wrap-Around ===");

    const queue = new CircularQueue(5);

    for (const value of ["A", "B", "C", "D", "E"]) {
        queue.enqueue(value);
    }

    queue.dequeue();
    queue.dequeue();

    queue.enqueue("F");
    queue.enqueue("G");

    console.log(queue.snapshot());

    if (JSON.stringify(queue.values()) !== JSON.stringify(["C", "D", "E", "F", "G"])) {
        throw new Error("Wrap-around behavior is incorrect.");
    }
}

function demonstrateErrors() {
    console.log("\n=== Overflow and Underflow ===");

    const queue = new CircularQueue(2);

    queue.enqueue(10);
    queue.enqueue(20);

    try {
        queue.enqueue(30);
    } catch (error) {
        if (error instanceof QueueFullError) {
            console.log("Overflow correctly rejected:", error.message);
        } else {
            throw error;
        }
    }

    console.log(queue.dequeue());
    console.log(queue.dequeue());

    try {
        queue.dequeue();
    } catch (error) {
        if (error instanceof QueueEmptyError) {
            console.log("Underflow correctly rejected:", error.message);
        } else {
            throw error;
        }
    }
}

function demonstrateEventBuffer() {
    console.log("\n=== Event Buffer ===");

    const buffer = new EventBuffer(3);

    const events = [
        { type: "LOGIN", userId: 17 },
        { type: "FILE_UPLOAD", userId: 17 },
        { type: "PASSWORD_CHANGE", userId: 42 },
        { type: "LOGOUT", userId: 17 }
    ];

    for (const event of events) {
        console.log("Published:", buffer.publish(event), event);
    }

    let event;
    while ((event = buffer.consume()) !== null) {
        console.log("Consumed:", event);
    }

    console.log({
        processed: buffer.processed,
        rejected: buffer.rejected
    });
}

function demonstrateDynamicQueue() {
    console.log("\n=== Dynamic Queue ===");

    const queue = new DynamicCircularQueue(2);

    for (const value of [100, 200, 300, 400, 500]) {
        queue.enqueue(value);
        console.log(queue.snapshot());
    }
}

function runAssertions() {
    console.log("\n=== Assertions ===");

    const queue = new CircularQueue(3);

    console.assert(queue.isEmpty);
    console.assert(!queue.isFull);

    queue.enqueue(1);
    queue.enqueue(2);
    queue.enqueue(3);

    console.assert(queue.isFull);
    console.assert(JSON.stringify(queue.values()) === JSON.stringify([1, 2, 3]));

    console.assert(queue.dequeue() === 1);
    queue.enqueue(4);

    console.assert(JSON.stringify(queue.values()) === JSON.stringify([2, 3, 4]));

    queue.dequeue();
    queue.dequeue();
    queue.dequeue();

    console.assert(queue.isEmpty);

    console.log("Assertions completed.");
}

function main() {
    console.log("CIRCULAR QUEUE IN JAVASCRIPT");

    demonstrateBasicQueue();
    demonstrateWrapAround();
    demonstrateErrors();
    demonstrateEventBuffer();
    demonstrateDynamicQueue();
    runAssertions();
}

main();
