"use strict";

/*
 * Doubly Linked List: executable JavaScript study.
 *
 * This implementation emphasizes JavaScript-specific object references,
 * iterator protocols, mutation during traversal, and an event-driven
 * navigation-history model.
 *
 * Run with:
 *     node doubly_linked_list.js
 */

class Node {
    constructor(value) {
        this.value = value;
        this.prev = null;
        this.next = null;
    }
}

class DoublyLinkedList {
    constructor(values = []) {
        this.head = null;
        this.tail = null;
        this.length = 0;

        for (const value of values) {
            this.append(value);
        }
    }

    isEmpty() {
        return this.length === 0;
    }

    append(value) {
        const node = new Node(value);

        if (this.tail === null) {
            this.head = node;
            this.tail = node;
        } else {
            node.prev = this.tail;
            this.tail.next = node;
            this.tail = node;
        }

        this.length++;
        return node;
    }

    prepend(value) {
        const node = new Node(value);

        if (this.head === null) {
            this.head = node;
            this.tail = node;
        } else {
            node.next = this.head;
            this.head.prev = node;
            this.head = node;
        }

        this.length++;
        return node;
    }

    validateIndex(index, allowEnd = false) {
        if (!Number.isInteger(index)) {
            throw new TypeError("index must be an integer");
        }

        const upperBound = allowEnd ? this.length : this.length - 1;

        if (index < 0 || index > upperBound) {
            throw new RangeError(
                `index must be between 0 and ${upperBound}, received ${index}`
            );
        }
    }

    nodeAt(index) {
        this.validateIndex(index);

        // Starting from the closer endpoint avoids unnecessary traversal.
        if (index <= Math.floor(this.length / 2)) {
            let current = this.head;

            for (let position = 0; position < index; position++) {
                current = current.next;
            }

            return current;
        }

        let current = this.tail;

        for (let position = this.length - 1; position > index; position--) {
            current = current.prev;
        }

        return current;
    }

    insertAt(index, value) {
        this.validateIndex(index, true);

        if (index === 0) {
            return this.prepend(value);
        }

        if (index === this.length) {
            return this.append(value);
        }

        const current = this.nodeAt(index);
        const previous = current.prev;
        const node = new Node(value);

        node.prev = previous;
        node.next = current;

        previous.next = node;
        current.prev = node;

        this.length++;
        return node;
    }

    removeNode(node) {
        if (!(node instanceof Node)) {
            throw new TypeError("removeNode expects a Node");
        }

        const previous = node.prev;
        const next = node.next;

        if (previous === null) {
            this.head = next;
        } else {
            previous.next = next;
        }

        if (next === null) {
            this.tail = previous;
        } else {
            next.prev = previous;
        }

        // Clear references after unlinking to make the detached state explicit.
        node.prev = null;
        node.next = null;

        this.length--;

        if (this.length === 0) {
            this.head = null;
            this.tail = null;
        }

        return node.value;
    }

    removeAt(index) {
        return this.removeNode(this.nodeAt(index));
    }

    removeFirst(value) {
        let current = this.head;

        while (current !== null) {
            if (Object.is(current.value, value)) {
                this.removeNode(current);
                return true;
            }

            current = current.next;
        }

        return false;
    }

    removeAll(value) {
        let current = this.head;
        let removed = 0;

        while (current !== null) {
            // Save next before removeNode clears current.next.
            const next = current.next;

            if (Object.is(current.value, value)) {
                this.removeNode(current);
                removed++;
            }

            current = next;
        }

        return removed;
    }

    find(value) {
        let current = this.head;

        while (current !== null) {
            if (Object.is(current.value, value)) {
                return current;
            }

            current = current.next;
        }

        return null;
    }

    *forward() {
        let current = this.head;

        while (current !== null) {
            yield current.value;
            current = current.next;
        }
    }

    *backward() {
        let current = this.tail;

        while (current !== null) {
            yield current.value;
            current = current.prev;
        }
    }

    toArray() {
        return [...this.forward()];
    }

    toReverseArray() {
        return [...this.backward()];
    }

    [Symbol.iterator]() {
        return this.forward();
    }

    clear() {
        let current = this.head;

        while (current !== null) {
            const next = current.next;
            current.prev = null;
            current.next = null;
            current = next;
        }

        this.head = null;
        this.tail = null;
        this.length = 0;
    }

    validate() {
        if (this.length === 0) {
            if (this.head !== null || this.tail !== null) {
                throw new Error("empty list has invalid endpoints");
            }
            return;
        }

        if (this.head === null || this.tail === null) {
            throw new Error("non-empty list requires head and tail");
        }

        if (this.head.prev !== null) {
            throw new Error("head.prev must be null");
        }

        if (this.tail.next !== null) {
            throw new Error("tail.next must be null");
        }

        let count = 0;
        let previous = null;
        let current = this.head;

        while (current !== null) {
            if (current.prev !== previous) {
                throw new Error("invalid prev link");
            }

            if (current.next !== null && current.next.prev !== current) {
                throw new Error("next.prev does not point back to current");
            }

            previous = current;
            current = current.next;
            count++;

            if (count > this.length) {
                throw new Error("forward traversal detected a cycle");
            }
        }

        if (previous !== this.tail) {
            throw new Error("forward traversal did not end at tail");
        }

        count = 0;
        let next = null;
        current = this.tail;

        while (current !== null) {
            if (current.next !== next) {
                throw new Error("invalid next link");
            }

            if (current.prev !== null && current.prev.next !== current) {
                throw new Error("prev.next does not point forward");
            }

            next = current;
            current = current.prev;
            count++;

            if (count > this.length) {
                throw new Error("backward traversal detected a cycle");
            }
        }

        if (next !== this.head) {
            throw new Error("backward traversal did not end at head");
        }

        if (count !== this.length) {
            throw new Error("stored length does not match backward count");
        }
    }
}


/*
 * JavaScript-specific event-driven history model.
 *
 * The EventTarget API is used here because browser-style navigation is a
 * natural fit for a doubly linked structure. The list handles structural
 * navigation while events expose state changes to observers.
 */
class NavigationHistory extends EventTarget {
    constructor(homepage) {
        super();

        if (typeof homepage !== "string" || homepage.trim() === "") {
            throw new TypeError("homepage must be a non-empty string");
        }

        this.current = new Node(homepage);
    }

    visit(url) {
        if (typeof url !== "string" || url.trim() === "") {
            throw new TypeError("url must be a non-empty string");
        }

        const nextPage = new Node(url);

        // Visiting from the middle of history removes the forward branch.
        this.current.next = null;
        nextPage.prev = this.current;
        this.current.next = nextPage;
        this.current = nextPage;

        this.dispatchEvent(
            new CustomEvent("visit", {
                detail: {
                    url,
                    canGoBack: this.current.prev !== null,
                    canGoForward: this.current.next !== null
                }
            })
        );

        return this.current.value;
    }

    back() {
        if (this.current.prev !== null) {
            this.current = this.current.prev;
        }

        this.dispatchEvent(
            new CustomEvent("navigate", {
                detail: {
                    direction: "back",
                    url: this.current.value
                }
            })
        );

        return this.current.value;
    }

    forward() {
        if (this.current.next !== null) {
            this.current = this.current.next;
        }

        this.dispatchEvent(
            new CustomEvent("navigate", {
                detail: {
                    direction: "forward",
                    url: this.current.value
                }
            })
        );

        return this.current.value;
    }

    currentPath() {
        const path = [];
        let node = this.current;

        while (node !== null) {
            path.push(node.value);
            node = node.prev;
        }

        path.reverse();
        return path;
    }
}


/*
 * A policy-oriented deque demonstrates another important use of a doubly
 * linked list: both ends can be manipulated in constant time.
 */
class TaskDeque {
    constructor() {
        this.list = new DoublyLinkedList();
    }

    addUrgent(task) {
        this.list.prepend(task);
    }

    addNormal(task) {
        this.list.append(task);
    }

    takeNext() {
        if (this.list.isEmpty()) {
            return null;
        }

        return this.list.removeAt(0);
    }

    cancelLatest() {
        if (this.list.isEmpty()) {
            return null;
        }

        return this.list.removeNode(this.list.tail);
    }

    snapshot() {
        return this.list.toArray();
    }
}


function printList(title, list) {
    console.log(`\n${title}`);
    console.log("Forward: ", list.toArray());
    console.log("Backward:", list.toReverseArray());
    console.log("Length:", list.length);
    list.validate();
    console.log("Invariant check: valid");
}


function demonstrateStructuralOperations() {
    console.log("=== Structural operations ===");

    const list = new DoublyLinkedList(["issue-101", "issue-102", "issue-103"]);
    printList("Initial", list);

    list.prepend("release-blocker");
    printList("After prepend", list);

    list.append("issue-104");
    printList("After append", list);

    list.insertAt(2, "security-review");
    printList("After insertion at index 2", list);

    const target = list.find("issue-102");
    if (target !== null) {
        list.removeNode(target);
    }

    printList("After known-node deletion", list);

    list.append("duplicate");
    list.append("duplicate");
    console.log("\nRemoved duplicates:", list.removeAll("duplicate"));
    printList("After removeAll", list);
}


function demonstrateMutationWhileTraversing() {
    console.log("\n=== Safe mutation during traversal ===");

    const list = new DoublyLinkedList([
        "retain",
        "delete",
        "retain",
        "delete",
        "retain"
    ]);

    let current = list.head;

    while (current !== null) {
        const next = current.next;

        if (current.value === "delete") {
            list.removeNode(current);
        }

        current = next;
    }

    printList("After traversal-based deletion", list);
}


function demonstrateNavigationEvents() {
    console.log("\n=== Event-driven navigation ===");

    const history = new NavigationHistory("home");

    history.addEventListener("visit", (event) => {
        console.log(
            `Visited ${event.detail.url}; ` +
            `back=${event.detail.canGoBack}, ` +
            `forward=${event.detail.canGoForward}`
        );
    });

    history.addEventListener("navigate", (event) => {
        console.log(
            `Navigation ${event.detail.direction}: ${event.detail.url}`
        );
    });

    history.visit("products");
    history.visit("products/database");
    history.visit("docs");

    history.back();
    history.back();
    history.forward();

    // Visiting here discards the old forward node.
    history.visit("security");

    console.log("Current path:", history.currentPath());
    console.log("Forward after branch replacement:", history.forward());
}


function demonstrateDeque() {
    console.log("\n=== Double-ended queue behavior ===");

    const queue = new TaskDeque();

    queue.addNormal("compile");
    queue.addNormal("run-tests");
    queue.addUrgent("security-scan");

    console.log("Queue:", queue.snapshot());
    console.log("Next:", queue.takeNext());
    console.log("After taking next:", queue.snapshot());

    console.log("Cancel latest:", queue.cancelLatest());
    console.log("After cancelling latest:", queue.snapshot());
}


function demonstrateErrors() {
    console.log("\n=== Validation and failure cases ===");

    const list = new DoublyLinkedList();

    try {
        list.removeAt(0);
    } catch (error) {
        console.log("Empty-list removal rejected:", error.message);
    }

    try {
        list.insertAt(2, "invalid");
    } catch (error) {
        console.log("Invalid insertion rejected:", error.message);
    }

    try {
        list.nodeAt("1");
    } catch (error) {
        console.log("Non-integer index rejected:", error.message);
    }

    try {
        new NavigationHistory("");
    } catch (error) {
        console.log("Invalid history rejected:", error.message);
    }
}


function runAssertions() {
    console.log("\n=== Assertions ===");

    const list = new DoublyLinkedList();

    console.assert(list.isEmpty());
    console.assert(list.length === 0);

    list.append("B");
    list.prepend("A");
    list.append("D");
    list.insertAt(2, "C");

    console.assert(
        JSON.stringify(list.toArray()) === JSON.stringify(["A", "B", "C", "D"])
    );

    console.assert(
        JSON.stringify(list.toReverseArray()) ===
        JSON.stringify(["D", "C", "B", "A"])
    );

    list.validate();

    console.assert(list.removeFirst("B") === true);
    console.assert(
        JSON.stringify(list.toArray()) === JSON.stringify(["A", "C", "D"])
    );

    console.assert(list.removeAt(1) === "C");
    console.assert(list.removeNode(list.tail) === "D");
    console.assert(list.removeNode(list.head) === "A");
    console.assert(list.isEmpty());

    const history = new NavigationHistory("home");
    history.visit("docs");
    history.visit("search");

    console.assert(history.back() === "docs");
    console.assert(history.forward() === "search");

    console.log("Assertions passed.");
}


function main() {
    demonstrateStructuralOperations();
    demonstrateMutationWhileTraversing();
    demonstrateNavigationEvents();
    demonstrateDeque();
    demonstrateErrors();
    runAssertions();

    console.log("\n=== Complexity characteristics ===");
    console.log("append: O(1) when tail is maintained");
    console.log("prepend: O(1)");
    console.log("known-node removal: O(1)");
    console.log("search: O(n)");
    console.log("indexed access: O(n), starting from the closer endpoint");
    console.log("forward/backward traversal: O(n)");
    console.log(
        "The extra prev reference increases memory usage and mutation " +
        "responsibility, but enables direct reverse navigation."
    );
}


main();
