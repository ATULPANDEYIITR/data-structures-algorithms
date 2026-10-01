/**
 * Linked List Introduction
 *
 * This Node.js-compatible file complements the Python implementation by
 * emphasizing JavaScript references, event-driven lifecycle simulation,
 * immutable-style snapshots, and a practical linked-list workflow.
 *
 * Run:
 *   node linked_list_introduction.js
 */

"use strict";

class Node {
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
        const node = new Node(value);

        if (this.head === null) {
            this.head = node;
            this.tail = node;
        } else {
            this.tail.next = node;
            this.tail = node;
        }

        this.size += 1;
    }

    prepend(value) {
        const node = new Node(value);
        node.next = this.head;
        this.head = node;

        if (this.tail === null) {
            this.tail = node;
        }

        this.size += 1;
    }

    find(value) {
        let current = this.head;

        while (current !== null) {
            if (current.value === value) {
                return current;
            }
            current = current.next;
        }

        return null;
    }

    insertAfter(target, value) {
        const current = this.find(target);

        if (current === null) {
            return false;
        }

        const node = new Node(value);
        node.next = current.next;
        current.next = node;

        if (this.tail === current) {
            this.tail = node;
        }

        this.size += 1;
        return true;
    }

    deleteFirst(value) {
        if (this.head === null) {
            return false;
        }

        if (this.head.value === value) {
            this.head = this.head.next;
            this.size -= 1;

            if (this.size === 0) {
                this.tail = null;
            }

            return true;
        }

        let previous = this.head;
        let current = this.head.next;

        while (current !== null) {
            if (current.value === value) {
                previous.next = current.next;

                if (current === this.tail) {
                    this.tail = previous;
                }

                this.size -= 1;
                return true;
            }

            previous = current;
            current = current.next;
        }

        return false;
    }

    reverse() {
        let previous = null;
        let current = this.head;

        this.tail = this.head;

        while (current !== null) {
            const nextNode = current.next;
            current.next = previous;
            previous = current;
            current = nextNode;
        }

        this.head = previous;
    }

    middle() {
        let slow = this.head;
        let fast = this.head;

        while (fast !== null && fast.next !== null) {
            slow = slow.next;
            fast = fast.next.next;
        }

        return slow === null ? null : slow.value;
    }

    hasCycle() {
        let slow = this.head;
        let fast = this.head;

        while (fast !== null && fast.next !== null) {
            slow = slow.next;
            fast = fast.next.next;

            if (slow === fast) {
                return true;
            }
        }

        return false;
    }

    toArray() {
        const result = [];
        let current = this.head;

        // A defensive traversal limit prevents accidental infinite output
        // if this diagnostic method is called on a cyclic list.
        let visited = 0;

        while (current !== null) {
            result.push(current.value);
            current = current.next;
            visited += 1;

            if (visited > this.size + 1) {
                throw new Error("Cannot serialize a cyclic linked list");
            }
        }

        return result;
    }

    toString() {
        if (this.head === null) {
            return "EMPTY";
        }

        return this.toArray().join(" -> ") + " -> null";
    }
}

/*
 * JavaScript references point to objects rather than exposing their memory
 * addresses. Assigning one node's next property to another node creates the
 * logical link while the JavaScript runtime manages memory.
 */
function demonstrateReferences() {
    console.log("\n=== JavaScript Object References ===");

    const first = new Node("A");
    const second = new Node("B");
    const third = new Node("C");

    first.next = second;
    second.next = third;

    console.log("first.value:", first.value);
    console.log("first.next.value:", first.next.value);
    console.log("second.next.value:", second.next.value);
    console.log("third.next:", third.next);
    console.log("first.next === second:", first.next === second);
}

/*
 * This section emphasizes why arrays and linked lists have different
 * access characteristics. JavaScript arrays are optimized runtime objects,
 * while this custom linked list requires pointer/reference traversal.
 */
function compareArrayAndLinkedList() {
    console.log("\n=== Array Versus Linked List ===");

    const array = ["build", "test", "review", "merge"];
    const linked = new SinglyLinkedList(array);

    console.log("Array:", array);
    console.log("Linked list:", linked.toString());
    console.log("Array index 2:", array[2]);

    let current = linked.head;

    for (let index = 0; index < 2; index += 1) {
        current = current.next;
    }

    console.log("Linked-list index 2 after traversal:", current.value);
    console.log("Array random access: approximately O(1)");
    console.log("Linked-list random access: O(n)");
}

function demonstrateOperations() {
    console.log("\n=== Core Operations ===");

    const list = new SinglyLinkedList();

    list.append(20);
    list.append(30);
    list.prepend(10);

    console.log("After append/append/prepend:", list.toString());

    console.log(
        "Insert after 20:",
        list.insertAfter(20, 25),
        list.toString()
    );

    console.log(
        "Delete first 25:",
        list.deleteFirst(25),
        list.toString()
    );

    console.log("Middle:", list.middle());

    list.reverse();

    console.log("After reverse:", list.toString());
}

/*
 * A queue is a useful linked-list application. Enqueue modifies the tail,
 * while dequeue removes the head. No array elements need to be shifted.
 */
class LinkedTaskQueue {
    constructor() {
        this.list = new SinglyLinkedList();
    }

    enqueue(task) {
        this.list.append(task);
    }

    dequeue() {
        if (this.list.head === null) {
            throw new Error("Cannot dequeue an empty queue");
        }

        const task = this.list.head.value;
        this.list.deleteFirst(task);
        return task;
    }

    peek() {
        return this.list.head === null ? null : this.list.head.value;
    }

    get length() {
        return this.list.size;
    }
}

function demonstrateTaskQueue() {
    console.log("\n=== Practical Task Queue ===");

    const queue = new LinkedTaskQueue();

    queue.enqueue({
        id: 501,
        title: "Validate changes",
        priority: "high"
    });

    queue.enqueue({
        id: 502,
        title: "Run tests",
        priority: "medium"
    });

    queue.enqueue({
        id: 503,
        title: "Publish documentation",
        priority: "low"
    });

    console.log("Next task:", queue.peek());

    while (queue.length > 0) {
        console.log("Processing:", queue.dequeue());
    }
}

/*
 * The following event-driven model shows how a linked list can represent
 * a sequence of workflow events. EventEmitter is intentionally avoided:
 * the example implements the small event mechanism directly so the
 * relationship between events and stored nodes remains visible.
 */
class EventHistory {
    constructor() {
        this.events = new SinglyLinkedList();
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (typeof listener !== "function") {
            throw new TypeError("listener must be a function");
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        this.events.append({
            eventName,
            payload,
            timestamp: new Date().toISOString()
        });

        const listeners = this.listeners.get(eventName) || [];

        for (const listener of listeners) {
            listener(payload);
        }
    }

    history() {
        return this.events.toArray();
    }
}

function demonstrateEventHistory() {
    console.log("\n=== Event History Backed by a Linked List ===");

    const history = new EventHistory();

    history.on("task-added", task => {
        console.log("Listener received task:", task.title);
    });

    history.emit("task-added", {
        id: 601,
        title: "Analyze linked-list traversal"
    });

    history.emit("task-completed", {
        id: 601
    });

    console.log("Stored events:", history.history());
}

/*
 * A deliberate cycle is useful for understanding reference graphs. It is
 * not a valid ordinary singly linked list, so diagnostic methods must not
 * assume that every reference chain eventually reaches null.
 */
function demonstrateCycleDetection() {
    console.log("\n=== Cycle Detection ===");

    const list = new SinglyLinkedList([10, 20, 30, 40]);

    console.log("Normal list:", list.toString());
    console.log("Has cycle:", list.hasCycle());

    list.tail.next = list.head.next;

    console.log("After creating a cycle:", list.hasCycle());

    // Restore the invariant expected by the rest of the program.
    list.tail.next = null;

    console.log("Cycle removed:", list.hasCycle());
}

function demonstrateFailureConditions() {
    console.log("\n=== Failure Conditions ===");

    const empty = new SinglyLinkedList();

    try {
        empty.toArray();
        console.log("Empty list serialization:", empty.toString());
    } catch (error) {
        console.error(error.message);
    }

    try {
        const queue = new LinkedTaskQueue();
        queue.dequeue();
    } catch (error) {
        console.log("Invalid dequeue rejected:", error.message);
    }

    try {
        const list = new SinglyLinkedList([1, 2, 3]);
        list.tail.next = list.head;
        list.toArray();
    } catch (error) {
        console.log("Cyclic serialization rejected:", error.message);
    }
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runChecks() {
    console.log("\n=== Executable Checks ===");

    const list = new SinglyLinkedList([1, 2, 3]);

    assert(list.size === 3, "initial size");
    assert(list.head.value === 1, "head value");
    assert(list.tail.value === 3, "tail value");

    list.prepend(0);
    assert(
        JSON.stringify(list.toArray()) === JSON.stringify([0, 1, 2, 3]),
        "prepend"
    );

    assert(list.insertAfter(2, 99), "insert after target");
    assert(
        JSON.stringify(list.toArray()) === JSON.stringify([0, 1, 2, 99, 3]),
        "insertion result"
    );

    assert(list.deleteFirst(99), "delete existing value");

    list.reverse();

    assert(
        JSON.stringify(list.toArray()) === JSON.stringify([3, 2, 1, 0]),
        "reverse"
    );

    assert(!list.hasCycle(), "cycle invariant");

    console.log("All JavaScript checks passed.");
}

function main() {
    console.log("=".repeat(72));
    console.log("LINKED LIST INTRODUCTION");
    console.log("=".repeat(72));

    demonstrateReferences();
    compareArrayAndLinkedList();
    demonstrateOperations();
    demonstrateTaskQueue();
    demonstrateEventHistory();
    demonstrateCycleDetection();
    demonstrateFailureConditions();
    runChecks();
}

main();
