"use strict";

/*
 * Singly Linked List in JavaScript
 *
 * This implementation focuses on the actual mechanics of a singly linked
 * structure: every node stores a value and one reference to its successor.
 * The list owns a reference to its first node.
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
        this.size = 0;

        for (const value of values) {
            this.append(value);
        }
    }

    prepend(value) {
        const node = new ListNode(value);
        node.next = this.head;
        this.head = node;
        this.size += 1;
    }

    append(value) {
        const node = new ListNode(value);

        if (this.head === null) {
            this.head = node;
            this.size += 1;
            return;
        }

        let current = this.head;
        while (current.next !== null) {
            current = current.next;
        }

        current.next = node;
        this.size += 1;
    }

    insertAt(index, value) {
        if (!Number.isInteger(index) || index < 0 || index > this.size) {
            throw new RangeError(
                `Insertion index ${index} is outside 0..${this.size}`
            );
        }

        if (index === 0) {
            this.prepend(value);
            return;
        }

        if (index === this.size) {
            this.append(value);
            return;
        }

        const previous = this.nodeAt(index - 1);
        const node = new ListNode(value);

        node.next = previous.next;
        previous.next = node;
        this.size += 1;
    }

    insertAfter(targetValue, value) {
        let current = this.head;

        while (current !== null) {
            if (current.value === targetValue) {
                const node = new ListNode(value);
                node.next = current.next;
                current.next = node;
                this.size += 1;
                return true;
            }

            current = current.next;
        }

        return false;
    }

    deleteAt(index) {
        if (!Number.isInteger(index) || index < 0 || index >= this.size) {
            throw new RangeError(
                `Deletion index ${index} is outside 0..${this.size - 1}`
            );
        }

        if (index === 0) {
            const removed = this.head;
            this.head = removed.next;
            this.size -= 1;
            return removed.value;
        }

        const previous = this.nodeAt(index - 1);
        const removed = previous.next;

        previous.next = removed.next;
        this.size -= 1;

        return removed.value;
    }

    deleteFirst(value) {
        if (this.head === null) {
            return false;
        }

        if (this.head.value === value) {
            this.head = this.head.next;
            this.size -= 1;
            return true;
        }

        let previous = this.head;
        let current = this.head.next;

        while (current !== null) {
            if (current.value === value) {
                previous.next = current.next;
                this.size -= 1;
                return true;
            }

            previous = current;
            current = current.next;
        }

        return false;
    }

    deleteAll(value) {
        let removed = 0;

        while (this.head !== null && this.head.value === value) {
            this.head = this.head.next;
            this.size -= 1;
            removed += 1;
        }

        if (this.head === null) {
            return removed;
        }

        let previous = this.head;
        let current = this.head.next;

        while (current !== null) {
            if (current.value === value) {
                previous.next = current.next;
                current = previous.next;
                this.size -= 1;
                removed += 1;
            } else {
                previous = current;
                current = current.next;
            }
        }

        return removed;
    }

    search(value) {
        let current = this.head;
        let index = 0;

        while (current !== null) {
            if (current.value === value) {
                return index;
            }

            current = current.next;
            index += 1;
        }

        return -1;
    }

    contains(value) {
        return this.search(value) !== -1;
    }

    updateAt(index, newValue) {
        const node = this.nodeAt(index);
        const oldValue = node.value;
        node.value = newValue;
        return oldValue;
    }

    updateFirst(oldValue, newValue) {
        let current = this.head;

        while (current !== null) {
            if (current.value === oldValue) {
                current.value = newValue;
                return true;
            }

            current = current.next;
        }

        return false;
    }

    get(index) {
        return this.nodeAt(index).value;
    }

    nodeAt(index) {
        if (!Number.isInteger(index) || index < 0 || index >= this.size) {
            throw new RangeError(
                `Node index ${index} is outside 0..${this.size - 1}`
            );
        }

        let current = this.head;

        for (let position = 0; position < index; position += 1) {
            current = current.next;
        }

        return current;
    }

    reverse() {
        /*
         * Three references are sufficient:
         * previous is the reversed prefix,
         * current is the node being processed,
         * nextNode preserves the remaining unreversed suffix.
         */
        let previous = null;
        let current = this.head;

        while (current !== null) {
            const nextNode = current.next;
            current.next = previous;
            previous = current;
            current = nextNode;
        }

        this.head = previous;
    }

    *traverse() {
        let current = this.head;

        while (current !== null) {
            yield current.value;
            current = current.next;
        }
    }

    toArray() {
        return [...this.traverse()];
    }

    toString() {
        return this.toArray().join(" -> ");
    }

    clear() {
        this.head = null;
        this.size = 0;
    }

    hasCycle() {
        // Floyd's algorithm detects accidental cycles without allocating a set.
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

    validate() {
        if (this.hasCycle()) {
            return false;
        }

        let count = 0;
        let current = this.head;

        while (current !== null) {
            count += 1;
            current = current.next;
        }

        return count === this.size;
    }
}


function demonstrateLifecycle() {
    console.log("\n=== Lifecycle of a singly linked list ===");

    const list = new SinglyLinkedList([20, 30]);

    console.log("Initial:", list.toString());

    list.prepend(10);
    console.log("After prepend:", list.toString());

    list.append(40);
    console.log("After append:", list.toString());

    list.insertAt(2, 25);
    console.log("After insertAt(2, 25):", list.toString());

    list.insertAfter(30, 35);
    console.log("After insertAfter(30, 35):", list.toString());

    console.log("Search 35:", list.search(35));
    console.log("Search 999:", list.search(999));

    list.updateAt(2, 26);
    console.log("After updateAt(2, 26):", list.toString());

    list.deleteFirst(35);
    console.log("After deleting first 35:", list.toString());

    list.deleteAt(0);
    console.log("After deleting head:", list.toString());

    list.reverse();
    console.log("After reversal:", list.toString());
}


function demonstrateGeneratorTraversal() {
    console.log("\n=== Generator-based traversal ===");

    const list = new SinglyLinkedList(["API", "service", "database"]);

    for (const item of list.traverse()) {
        console.log(`Visited: ${item}`);
    }

    console.log(
        "Generator traversal preserves the linked-list's sequential nature " +
        "without constructing an intermediate array."
    );
}


function demonstrateEdgeCases() {
    console.log("\n=== Edge cases and validation ===");

    const empty = new SinglyLinkedList();

    console.log("Empty:", empty.toString());
    console.log("Search empty:", empty.search("missing"));
    console.log("Delete missing:", empty.deleteFirst("missing"));

    empty.prepend("only");
    console.log("Single node:", empty.toString());

    empty.reverse();
    console.log("Reversed single node:", empty.toString());

    empty.deleteAt(0);
    console.log("After deleting only node:", empty.toString());

    const duplicates = new SinglyLinkedList([7, 7, 8, 7]);
    console.log("Duplicates:", duplicates.toString());
    console.log("Removed:", duplicates.deleteAll(7));
    console.log("After deleteAll:", duplicates.toString());

    try {
        duplicates.insertAt(-1, 10);
    } catch (error) {
        console.log("Invalid insertion handled:", error.message);
    }

    try {
        duplicates.deleteAt(99);
    } catch (error) {
        console.log("Invalid deletion handled:", error.message);
    }
}


function demonstrateReferenceMechanics() {
    console.log("\n=== Reference mechanics ===");

    const list = new SinglyLinkedList(["A", "B", "C"]);

    let current = list.head;

    while (current !== null) {
        const next = current.next === null
            ? "null"
            : current.next.value;

        console.log(`node=${current.value}, next=${next}`);
        current = current.next;
    }

    /*
     * JavaScript objects are reference values. Changing current.next changes
     * the actual node object stored in the linked structure.
     */
    const first = list.head;
    const second = first.next;

    second.value = "B-updated";

    console.log("After changing the second node through a reference:");
    console.log(list.toString());

    console.log(
        "The list remains connected because the nodes themselves hold the links."
    );
}


function demonstrateCycleDetection() {
    console.log("\n=== Structural validation ===");

    const list = new SinglyLinkedList([1, 2, 3, 4]);

    console.log("Valid before corruption:", list.validate());

    const tail = list.nodeAt(3);
    tail.next = list.head;

    console.log("Cycle detected:", list.hasCycle());
    console.log("Validation result:", list.validate());

    // Restore the tail so the object is usable after the demonstration.
    tail.next = null;

    console.log("Valid after restoration:", list.validate());
}


function runAssertions() {
    console.log("\n=== Verification ===");

    const list = new SinglyLinkedList([10, 20, 30]);

    console.assert(
        list.toArray().join(",") === "10,20,30",
        "Initial construction failed"
    );

    list.prepend(5);
    console.assert(list.get(0) === 5, "Prepend failed");

    list.append(40);
    console.assert(list.get(4) === 40, "Append failed");

    list.insertAt(2, 15);
    console.assert(
        list.toString() === "5 -> 10 -> 15 -> 20 -> 30 -> 40",
        "Insertion failed"
    );

    console.assert(list.search(30) === 4, "Search failed");
    console.assert(list.search(999) === -1, "Missing search failed");

    list.updateAt(3, 21);
    console.assert(list.get(3) === 21, "Update failed");

    console.assert(list.deleteFirst(21), "Deletion by value failed");
    console.assert(list.deleteAt(0) === 5, "Head deletion failed");

    list.reverse();

    console.assert(
        list.toString() === "40 -> 30 -> 15 -> 10",
        "Reverse failed"
    );

    console.assert(list.validate(), "Integrity validation failed");

    console.log("All JavaScript assertions passed.");
}


function main() {
    console.log("SINGLY LINKED LIST: JAVASCRIPT IMPLEMENTATION");

    demonstrateLifecycle();
    demonstrateGeneratorTraversal();
    demonstrateEdgeCases();
    demonstrateReferenceMechanics();
    demonstrateCycleDetection();
    runAssertions();

    console.log("\nComplexity notes:");
    console.log("prepend: O(1)");
    console.log("append without tail pointer: O(n)");
    console.log("search: O(n)");
    console.log("indexed access: O(n)");
    console.log("insertion/deletion after locating predecessor: O(1)");
    console.log("insertAt/deleteAt: O(n) because locating a predecessor is sequential");
    console.log("reverse: O(n) time and O(1) auxiliary space");
}


main();
