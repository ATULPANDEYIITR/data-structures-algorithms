"use strict";

/*
 * Circular Linked Lists in JavaScript
 *
 * This file uses JavaScript's object references to model circular
 * singly and doubly linked lists. It also demonstrates an event-driven
 * round-robin workflow where a circular list represents repeatedly
 * scheduled jobs.
 *
 * Run with:
 *   node circular_linked_lists.js
 */

// ============================================================
// Circular Singly Linked List
// ============================================================

class SinglyNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

class CircularSinglyLinkedList {
    constructor(values = []) {
        this.tail = null;
        this.length = 0;

        for (const value of values) {
            this.append(value);
        }
    }

    get head() {
        return this.tail === null ? null : this.tail.next;
    }

    isEmpty() {
        return this.tail === null;
    }

    append(value) {
        const node = new SinglyNode(value);

        if (this.tail === null) {
            // A one-node circle points back to itself.
            node.next = node;
            this.tail = node;
        } else {
            node.next = this.tail.next;
            this.tail.next = node;
            this.tail = node;
        }

        this.length++;
    }

    prepend(value) {
        const node = new SinglyNode(value);

        if (this.tail === null) {
            node.next = node;
            this.tail = node;
        } else {
            node.next = this.tail.next;
            this.tail.next = node;
        }

        this.length++;
    }

    insertAfter(target, value) {
        if (this.tail === null) {
            return false;
        }

        let current = this.head;

        // A circular structure requires a bounded traversal.
        // Using current !== null would never terminate.
        for (let i = 0; i < this.length; i++) {
            if (current.value === target) {
                const node = new SinglyNode(value);
                node.next = current.next;
                current.next = node;

                if (current === this.tail) {
                    this.tail = node;
                }

                this.length++;
                return true;
            }

            current = current.next;
        }

        return false;
    }

    insertAt(index, value) {
        if (!Number.isInteger(index) || index < 0 || index > this.length) {
            throw new RangeError("index must be an integer between 0 and length");
        }

        if (index === 0) {
            this.prepend(value);
            return;
        }

        if (index === this.length) {
            this.append(value);
            return;
        }

        let previous = this.head;

        for (let i = 1; i < index; i++) {
            previous = previous.next;
        }

        const node = new SinglyNode(value);
        node.next = previous.next;
        previous.next = node;
        this.length++;
    }

    removeFirst(value) {
        if (this.tail === null) {
            return false;
        }

        let previous = this.tail;
        let current = this.head;

        for (let i = 0; i < this.length; i++) {
            if (current.value === value) {
                if (this.length === 1) {
                    this.tail = null;
                } else {
                    previous.next = current.next;

                    if (current === this.tail) {
                        this.tail = previous;
                    }
                }

                current.next = null;
                this.length--;
                return true;
            }

            previous = current;
            current = current.next;
        }

        return false;
    }

    rotate() {
        if (this.tail !== null) {
            this.tail = this.tail.next;
        }
    }

    find(value) {
        if (this.tail === null) {
            return -1;
        }

        let current = this.head;

        for (let index = 0; index < this.length; index++) {
            if (current.value === value) {
                return index;
            }

            current = current.next;
        }

        return -1;
    }

    toArray() {
        const result = [];

        if (this.tail === null) {
            return result;
        }

        let current = this.head;

        for (let i = 0; i < this.length; i++) {
            result.push(current.value);
            current = current.next;
        }

        return result;
    }

    validate() {
        if (this.tail === null) {
            if (this.length !== 0) {
                throw new Error("Empty list has invalid length");
            }
            return true;
        }

        if (this.length <= 0) {
            throw new Error("Non-empty list has invalid length");
        }

        if (this.tail.next === null) {
            throw new Error("Circular list cannot have a null head link");
        }

        let current = this.head;

        for (let i = 0; i < this.length; i++) {
            if (current === null) {
                throw new Error("Broken circular link");
            }
            current = current.next;
        }

        if (current !== this.head) {
            throw new Error("Traversal did not return to head");
        }

        return true;
    }
}


// ============================================================
// Circular Doubly Linked List
// ============================================================

class DoublyNode {
    constructor(value) {
        this.value = value;
        this.prev = null;
        this.next = null;
    }
}

class CircularDoublyLinkedList {
    constructor(values = []) {
        this.headNode = null;
        this.length = 0;

        for (const value of values) {
            this.append(value);
        }
    }

    get head() {
        return this.headNode;
    }

    get tail() {
        return this.headNode === null ? null : this.headNode.prev;
    }

    append(value) {
        const node = new DoublyNode(value);

        if (this.headNode === null) {
            node.next = node;
            node.prev = node;
            this.headNode = node;
        } else {
            const tail = this.tail;

            node.prev = tail;
            node.next = this.headNode;

            tail.next = node;
            this.headNode.prev = node;
        }

        this.length++;
    }

    prepend(value) {
        this.append(value);
        this.headNode = this.headNode.prev;
    }

    insertAfterNode(node, value) {
        if (!(node instanceof DoublyNode)) {
            throw new TypeError("node must be a DoublyNode");
        }

        const successor = node.next;
        const newNode = new DoublyNode(value);

        newNode.prev = node;
        newNode.next = successor;

        node.next = newNode;
        successor.prev = newNode;

        this.length++;
    }

    findNode(value) {
        if (this.headNode === null) {
            return null;
        }

        let current = this.headNode;

        for (let i = 0; i < this.length; i++) {
            if (current.value === value) {
                return current;
            }

            current = current.next;
        }

        return null;
    }

    removeNode(node) {
        if (this.length === 0 || node === null) {
            return false;
        }

        if (this.length === 1) {
            if (node !== this.headNode) {
                return false;
            }

            node.next = null;
            node.prev = null;
            this.headNode = null;
            this.length = 0;
            return true;
        }

        node.prev.next = node.next;
        node.next.prev = node.prev;

        if (node === this.headNode) {
            this.headNode = node.next;
        }

        node.next = null;
        node.prev = null;
        this.length--;

        return true;
    }

    removeFirst(value) {
        const node = this.findNode(value);
        return node === null ? false : this.removeNode(node);
    }

    forward() {
        const result = [];

        if (this.headNode === null) {
            return result;
        }

        let current = this.headNode;

        for (let i = 0; i < this.length; i++) {
            result.push(current.value);
            current = current.next;
        }

        return result;
    }

    backward() {
        const result = [];

        if (this.headNode === null) {
            return result;
        }

        let current = this.tail;

        for (let i = 0; i < this.length; i++) {
            result.push(current.value);
            current = current.prev;
        }

        return result;
    }

    validate() {
        if (this.headNode === null) {
            if (this.length !== 0) {
                throw new Error("Empty list has invalid length");
            }
            return true;
        }

        const tail = this.tail;

        if (tail.next !== this.headNode) {
            throw new Error("tail.next must reference head");
        }

        if (this.headNode.prev !== tail) {
            throw new Error("head.prev must reference tail");
        }

        let current = this.headNode;

        for (let i = 0; i < this.length; i++) {
            if (current.next.prev !== current) {
                throw new Error("next/prev relationship is broken");
            }

            if (current.prev.next !== current) {
                throw new Error("prev/next relationship is broken");
            }

            current = current.next;
        }

        if (current !== this.headNode) {
            throw new Error("Forward traversal did not return to head");
        }

        return true;
    }
}


// ============================================================
// Event-Driven Round-Robin Model
// ============================================================

class RoundRobinScheduler {
    constructor(quantum) {
        if (!Number.isInteger(quantum) || quantum <= 0) {
            throw new RangeError("quantum must be a positive integer");
        }

        this.quantum = quantum;
        this.jobs = new CircularSinglyLinkedList();
        this.events = [];
    }

    addJob(name, duration) {
        if (typeof name !== "string" || name.trim() === "") {
            throw new TypeError("job name must be a non-empty string");
        }

        if (!Number.isInteger(duration) || duration <= 0) {
            throw new RangeError("job duration must be a positive integer");
        }

        this.jobs.append({
            name,
            remaining: duration
        });
    }

    async run(onTick = null) {
        while (!this.jobs.isEmpty()) {
            const current = this.jobs.head;
            const job = current.value;

            const consumed = Math.min(this.quantum, job.remaining);
            job.remaining -= consumed;

            const event = {
                job: job.name,
                consumed,
                remaining: job.remaining
            };

            this.events.push(event);

            if (typeof onTick === "function") {
                await onTick(event);
            }

            if (job.remaining === 0) {
                this.jobs.removeFirst(job);
            } else {
                this.jobs.rotate();
            }

            // A microtask boundary demonstrates that the data structure
            // can participate in an asynchronous JavaScript workflow
            // without changing the circular-list invariants.
            await Promise.resolve();
        }

        return this.events;
    }
}


// ============================================================
// Demonstrations
// ============================================================

function demonstrateSingly() {
    console.log("\n=== Circular Singly Linked List ===");

    const list = new CircularSinglyLinkedList([10, 20, 30]);

    console.log("Initial:", list.toArray());

    list.prepend(5);
    console.log("After prepend:", list.toArray());

    list.append(40);
    console.log("After append:", list.toArray());

    list.insertAfter(20, 25);
    console.log("After insertAfter(20, 25):", list.toArray());

    list.insertAt(3, 27);
    console.log("After insertAt(3, 27):", list.toArray());

    list.removeFirst(25);
    console.log("After removing 25:", list.toArray());

    list.rotate();
    console.log("After rotation:", list.toArray());

    console.log("Index of 30:", list.find(30));
    console.log("Validation:", list.validate());
}

function demonstrateDoubly() {
    console.log("\n=== Circular Doubly Linked List ===");

    const list = new CircularDoublyLinkedList(["A", "B", "C", "D"]);

    console.log("Forward:", list.forward());
    console.log("Backward:", list.backward());

    const nodeB = list.findNode("B");
    list.insertAfterNode(nodeB, "B2");

    console.log("After insertion after B:", list.forward());

    list.removeFirst("C");

    console.log("After removing C:", list.forward());
    console.log("Reverse traversal:", list.backward());
    console.log("Validation:", list.validate());
}

async function demonstrateScheduler() {
    console.log("\n=== Asynchronous Round-Robin Scheduler ===");

    const scheduler = new RoundRobinScheduler(2);

    scheduler.addJob("compile", 5);
    scheduler.addJob("test", 3);
    scheduler.addJob("package", 4);

    await scheduler.run((event) => {
        console.log(
            `${event.job}: consumed=${event.consumed}, remaining=${event.remaining}`
        );
    });
}

function demonstrateEdgeCases() {
    console.log("\n=== Edge Cases ===");

    const singly = new CircularSinglyLinkedList();

    console.log("Empty list:", singly.toArray());
    console.log("Removing absent value:", singly.removeFirst("missing"));

    singly.append("only");
    console.log("One-node circular list:", singly.toArray());

    singly.removeFirst("only");
    console.log("After removing only node:", singly.toArray());

    try {
        singly.insertAt(2, "invalid");
    } catch (error) {
        console.log("Expected validation error:", error.message);
    }

    const doubly = new CircularDoublyLinkedList(["only"]);

    console.log("Doubly forward:", doubly.forward());
    console.log("Doubly backward:", doubly.backward());

    doubly.removeFirst("only");

    console.log("Doubly after deletion:", doubly.forward());
}

async function main() {
    demonstrateSingly();
    demonstrateDoubly();
    demonstrateEdgeCases();
    await demonstrateScheduler();
}

main().catch((error) => {
    console.error("Unexpected failure:", error);
    process.exitCode = 1;
});
