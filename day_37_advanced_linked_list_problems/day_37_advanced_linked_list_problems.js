"use strict";

/*
 * Advanced Linked List Problems
 *
 * This file focuses on linked-list-specific techniques:
 * - intersection by node identity
 * - sorted-list merging
 * - stable merge sort
 * - partitioning
 * - copying lists with random pointers
 * - flattening multilevel lists
 * - cycle detection
 *
 * The implementation intentionally uses JavaScript objects as mutable nodes.
 * This makes object identity (`===`) directly useful when determining whether
 * two lists physically share a node.
 */

class ListNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

class RandomNode {
    constructor(value) {
        this.value = value;
        this.next = null;
        this.random = null;
    }
}

class MultiNode {
    constructor(value) {
        this.value = value;
        this.prev = null;
        this.next = null;
        this.child = null;
    }
}

function buildList(values) {
    let head = null;
    let tail = null;

    for (const value of values) {
        const node = new ListNode(value);

        if (head === null) {
            head = node;
        } else {
            tail.next = node;
        }

        tail = node;
    }

    return head;
}

function valuesOf(head, limit = 100) {
    const values = [];
    let current = head;

    while (current !== null && values.length < limit) {
        values.push(current.value);
        current = current.next;
    }

    if (current !== null) {
        values.push("...");
    }

    return values;
}

function printList(label, head) {
    console.log(`${label}: ${valuesOf(head).join(" -> ")}`);
}

function reverseList(head) {
    let previous = null;
    let current = head;

    while (current !== null) {
        const next = current.next;
        current.next = previous;
        previous = current;
        current = next;
    }

    return previous;
}

function listLength(head) {
    let count = 0;

    for (let current = head; current !== null; current = current.next) {
        count++;
    }

    return count;
}

/*
 * Two-pointer intersection.
 *
 * The pointers traverse A+B and B+A. If the lists intersect, both reach the
 * same object. If they do not, both become null at the same time.
 *
 * Equality must be object identity, not value equality.
 */
function findIntersection(headA, headB) {
    if (headA === null || headB === null) {
        return null;
    }

    let a = headA;
    let b = headB;

    while (a !== b) {
        a = a === null ? headB : a.next;
        b = b === null ? headA : b.next;
    }

    return a;
}

function mergeSortedLists(headA, headB) {
    const dummy = new ListNode(0);
    let tail = dummy;

    let a = headA;
    let b = headB;

    while (a !== null && b !== null) {
        if (a.value <= b.value) {
            tail.next = a;
            a = a.next;
        } else {
            tail.next = b;
            b = b.next;
        }

        tail = tail.next;
    }

    tail.next = a !== null ? a : b;
    return dummy.next;
}

function splitList(head) {
    if (head === null || head.next === null) {
        return [head, null];
    }

    let slow = head;
    let fast = head.next;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    const second = slow.next;
    slow.next = null;

    return [head, second];
}

function mergeSort(head) {
    if (head === null || head.next === null) {
        return head;
    }

    const [left, right] = splitList(head);

    const sortedLeft = mergeSort(left);
    const sortedRight = mergeSort(right);

    return mergeSortedLists(sortedLeft, sortedRight);
}

function stablePartition(head, pivot) {
    const lessDummy = new ListNode(0);
    const greaterDummy = new ListNode(0);

    let lessTail = lessDummy;
    let greaterTail = greaterDummy;

    let current = head;

    while (current !== null) {
        const next = current.next;
        current.next = null;

        if (current.value < pivot) {
            lessTail.next = current;
            lessTail = current;
        } else {
            greaterTail.next = current;
            greaterTail = current;
        }

        current = next;
    }

    lessTail.next = greaterDummy.next;
    return lessDummy.next;
}

function detectCycle(head) {
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;

        if (slow === fast) {
            let entry = head;

            while (entry !== slow) {
                entry = entry.next;
                slow = slow.next;
            }

            return entry;
        }
    }

    return null;
}

/*
 * Deep-copy a random-pointer list using interleaving.
 *
 * JavaScript object identity is important here. A Map would make the
 * implementation easier, but the interleaving method demonstrates the
 * pointer technique with O(1) auxiliary space.
 */
function copyRandomList(head) {
    if (head === null) {
        return null;
    }

    let current = head;

    while (current !== null) {
        const copy = new RandomNode(current.value);
        copy.next = current.next;
        current.next = copy;
        current = copy.next;
    }

    current = head;

    while (current !== null) {
        const copy = current.next;

        if (current.random !== null) {
            copy.random = current.random.next;
        }

        current = copy.next;
    }

    const copiedHead = head.next;
    current = head;

    while (current !== null) {
        const copy = current.next;
        const originalNext = copy.next;

        current.next = originalNext;
        copy.next = originalNext === null ? null : originalNext.next;

        current = originalNext;
    }

    return copiedHead;
}

function randomDescription(head) {
    const output = [];
    let current = head;

    while (current !== null) {
        output.push({
            value: current.value,
            random: current.random === null ? null : current.random.value
        });

        current = current.next;
    }

    return output;
}

function flattenMultilevelList(head) {
    if (head === null) {
        return null;
    }

    /*
     * A stack preserves the original next chain while child lists are
     * inserted into traversal order. This avoids recursive calls that could
     * overflow the JavaScript call stack on deeply nested structures.
     */
    const stack = [head];
    let previous = null;

    while (stack.length > 0) {
        const current = stack.pop();

        if (previous !== null) {
            previous.next = current;
            current.prev = previous;
        }

        if (current.next !== null) {
            stack.push(current.next);
        }

        if (current.child !== null) {
            stack.push(current.child);
            current.child = null;
        }

        previous = current;
    }

    return head;
}

function multiValues(head) {
    const values = [];
    let current = head;

    while (current !== null) {
        values.push(current.value);
        current = current.next;
    }

    return values;
}

function reverseKGroup(head, k) {
    if (!Number.isInteger(k) || k <= 1 || head === null) {
        return head;
    }

    const dummy = new ListNode(0);
    dummy.next = head;

    let groupPrevious = dummy;

    while (true) {
        let kth = groupPrevious;

        for (let i = 0; i < k; i++) {
            kth = kth.next;

            if (kth === null) {
                return dummy.next;
            }
        }

        const groupNext = kth.next;

        let previous = groupNext;
        let current = groupPrevious.next;

        while (current !== groupNext) {
            const next = current.next;
            current.next = previous;
            previous = current;
            current = next;
        }

        const oldGroupHead = groupPrevious.next;
        groupPrevious.next = kth;
        groupPrevious = oldGroupHead;
    }
}

function buildIntersectionExample() {
    const shared = buildList([8, 10, 12]);

    const first = buildList([3, 7]);
    let tail = first;

    while (tail.next !== null) {
        tail = tail.next;
    }

    tail.next = shared;

    const second = buildList([99, 1, 5]);
    tail = second;

    while (tail.next !== null) {
        tail = tail.next;
    }

    tail.next = shared;

    return { first, second, shared };
}

function buildRandomExample() {
    const nodes = [7, 13, 11, 10, 1].map(value => new RandomNode(value));

    for (let i = 0; i < nodes.length - 1; i++) {
        nodes[i].next = nodes[i + 1];
    }

    nodes[0].random = null;
    nodes[1].random = nodes[0];
    nodes[2].random = nodes[4];
    nodes[3].random = nodes[2];
    nodes[4].random = nodes[4];

    return nodes[0];
}

function buildMultilevelExample() {
    const nodes = new Map();

    for (let i = 1; i <= 7; i++) {
        nodes.set(i, new MultiNode(i));
    }

    nodes.get(1).next = nodes.get(2);
    nodes.get(2).prev = nodes.get(1);

    nodes.get(2).next = nodes.get(3);
    nodes.get(3).prev = nodes.get(2);

    nodes.get(3).next = nodes.get(4);
    nodes.get(4).prev = nodes.get(3);

    nodes.get(2).child = nodes.get(5);

    nodes.get(5).next = nodes.get(6);
    nodes.get(6).prev = nodes.get(5);

    nodes.get(6).child = nodes.get(7);

    return nodes.get(1);
}

function demonstrateIntersection() {
    const { first, second, shared } = buildIntersectionExample();
    const result = findIntersection(first, second);

    console.log("Intersection:");
    console.log(`  value = ${result ? result.value : null}`);
    console.log(`  shared object = ${result === shared}`);
}

function demonstrateSorting() {
    const input = buildList([7, 2, 9, 1, 5, 2, 8, 3]);

    printList("Before merge sort", input);

    const sorted = mergeSort(input);

    printList("After merge sort", sorted);

    const left = buildList([1, 4, 7, 10]);
    const right = buildList([2, 3, 8, 9]);

    printList("Merged sorted lists", mergeSortedLists(left, right));
}

function demonstratePartitioning() {
    const input = buildList([1, 4, 3, 2, 5, 2]);
    const result = stablePartition(input, 3);

    printList("Stable partition around 3", result);
}

function demonstrateRandomCopy() {
    const original = buildRandomExample();
    const copy = copyRandomList(original);

    console.log("Random-pointer original:");
    console.log(randomDescription(original));

    console.log("Random-pointer copy:");
    console.log(randomDescription(copy));

    if (original === copy) {
        throw new Error("Copy unexpectedly reused the original head.");
    }

    original.value = 700;

    if (copy.value !== 7) {
        throw new Error("Copy is not independent from original.");
    }

    console.log("Deep-copy independence verified.");
}

function demonstrateFlattening() {
    const multilevel = buildMultilevelExample();
    const flattened = flattenMultilevelList(multilevel);

    console.log("Flattened multilevel list:");
    console.log(multiValues(flattened).join(" -> "));
}

function demonstrateCycles() {
    const head = buildList([1, 2, 3, 4, 5]);

    let tail = head;
    let cycleEntry = head.next.next;

    while (tail.next !== null) {
        tail = tail.next;
    }

    tail.next = cycleEntry;

    const detected = detectCycle(head);

    console.log("Cycle detection:");
    console.log(`  entry value = ${detected ? detected.value : null}`);

    /*
     * Never pass a cyclic list to a normal list printer unless a traversal
     * limit is present. Otherwise debugging code itself can become infinite.
     */
}

function randomizedMergeSortCheck() {
    for (let trial = 0; trial < 100; trial++) {
        const values = [];

        const size = Math.floor(Math.random() * 21);

        for (let i = 0; i < size; i++) {
            values.push(Math.floor(Math.random() * 41) - 20);
        }

        const actual = valuesOf(mergeSort(buildList(values)));
        const expected = [...values].sort((a, b) => a - b);

        if (JSON.stringify(actual) !== JSON.stringify(expected)) {
            throw new Error(
                `Merge sort failed. Expected ${expected}, got ${actual}`
            );
        }
    }

    console.log("Randomized merge-sort verification: passed 100 cases.");
}

function main() {
    console.log("=== Advanced Linked List Algorithms ===\n");

    demonstrateIntersection();
    console.log();

    demonstrateSorting();
    console.log();

    demonstratePartitioning();
    console.log();

    demonstrateRandomCopy();
    console.log();

    demonstrateFlattening();
    console.log();

    demonstrateCycles();
    console.log();

    const grouped = reverseKGroup(buildList([1, 2, 3, 4, 5, 6, 7]), 3);
    printList("Reverse every group of three", grouped);
    console.log();

    randomizedMergeSortCheck();

    console.log("\nAll demonstrations completed successfully.");
}

main();
