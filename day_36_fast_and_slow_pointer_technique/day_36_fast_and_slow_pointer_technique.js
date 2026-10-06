"use strict";

/*
 * FAST AND SLOW POINTER TECHNIQUE
 *
 * This file uses JavaScript-specific structures and event-driven execution
 * while implementing the core fast/slow pointer patterns:
 *   - middle-node discovery
 *   - Floyd cycle detection
 *   - cycle-entry discovery
 *   - cycle removal
 *   - nth-node-from-end lookup
 *   - palindrome detection
 *   - intersection detection
 *   - duplicate detection through a functional graph
 *
 * Run with:
 *   node fast-slow-pointers.js
 */

class ListNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
}

function buildLinkedList(values) {
    const iterator = values[Symbol.iterator]();
    const first = iterator.next();

    if (first.done) {
        return null;
    }

    const head = new ListNode(first.value);
    let tail = head;

    for (const value of iterator) {
        tail.next = new ListNode(value);
        tail = tail.next;
    }

    return head;
}

function buildCyclicList(values, entryIndex) {
    if (values.length === 0) {
        return null;
    }

    if (!Number.isInteger(entryIndex) ||
        entryIndex < 0 ||
        entryIndex >= values.length) {
        throw new RangeError("entryIndex must identify an existing node");
    }

    const nodes = values.map(value => new ListNode(value));

    for (let i = 0; i < nodes.length - 1; i++) {
        nodes[i].next = nodes[i + 1];
    }

    nodes[nodes.length - 1].next = nodes[entryIndex];

    return nodes[0];
}

function listToString(head, limit = 40) {
    const values = [];
    const seen = new Set();

    let current = head;

    while (current !== null && values.length < limit) {
        if (seen.has(current)) {
            values.push(`cycle->${current.value}`);
            break;
        }

        seen.add(current);
        values.push(String(current.value));
        current = current.next;
    }

    if (current !== null && values.length === limit) {
        values.push("...");
    }

    return values.join(" -> ");
}

function middleNode(head) {
    /*
     * fast advances twice as quickly as slow. When fast reaches the end,
     * slow is positioned at the second middle for an even-length list.
     */
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    return slow;
}

function firstMiddleNode(head) {
    if (head === null) {
        return null;
    }

    let slow = head;
    let fast = head.next;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    return slow;
}

function hasCycle(head) {
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;

        if (slow === fast) {
            return true;
        }
    }

    return false;
}

function findCycleMeetingNode(head) {
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;

        if (slow === fast) {
            return slow;
        }
    }

    return null;
}

function findCycleEntry(head) {
    const meeting = findCycleMeetingNode(head);

    if (meeting === null) {
        return null;
    }

    /*
     * Once the pointers meet, one pointer starts from the head and the other
     * starts from the meeting point. Equal one-step movement makes them meet
     * exactly at the cycle entry.
     */
    let fromHead = head;
    let fromMeeting = meeting;

    while (fromHead !== fromMeeting) {
        fromHead = fromHead.next;
        fromMeeting = fromMeeting.next;
    }

    return fromHead;
}

function getCycleInformation(head) {
    const entry = findCycleEntry(head);

    if (entry === null) {
        return {
            entry: null,
            distanceToEntry: -1,
            cycleLength: 0
        };
    }

    let distance = 0;
    let current = head;

    while (current !== entry) {
        current = current.next;
        distance++;
    }

    let cycleLength = 1;
    current = entry.next;

    while (current !== entry) {
        current = current.next;
        cycleLength++;
    }

    return {
        entry,
        distanceToEntry: distance,
        cycleLength
    };
}

function removeCycle(head) {
    const entry = findCycleEntry(head);

    if (entry === null) {
        return false;
    }

    let cycleTail = entry;

    while (cycleTail.next !== entry) {
        cycleTail = cycleTail.next;
    }

    cycleTail.next = null;
    return true;
}

function nthFromEnd(head, n) {
    if (!Number.isInteger(n) || n <= 0) {
        throw new RangeError("n must be a positive integer");
    }

    let fast = head;

    for (let i = 0; i < n; i++) {
        if (fast === null) {
            return null;
        }

        fast = fast.next;
    }

    let slow = head;

    while (fast !== null) {
        slow = slow.next;
        fast = fast.next;
    }

    return slow;
}

function removeNthFromEnd(head, n) {
    if (!Number.isInteger(n) || n <= 0) {
        throw new RangeError("n must be a positive integer");
    }

    const dummy = new ListNode(null);
    dummy.next = head;

    let fast = dummy;

    for (let i = 0; i < n; i++) {
        if (fast.next === null) {
            return head;
        }

        fast = fast.next;
    }

    let slow = dummy;

    while (fast.next !== null) {
        slow = slow.next;
        fast = fast.next;
    }

    slow.next = slow.next.next;

    return dummy.next;
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

function isPalindrome(head) {
    if (head === null || head.next === null) {
        return true;
    }

    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }

    /*
     * The second half is reversed in-place. JavaScript references point to
     * the same nodes, so restoring the half afterward preserves the caller's
     * linked-list structure.
     */
    const reversedSecondHalf = reverseList(slow);

    let left = head;
    let right = reversedSecondHalf;
    let result = true;

    while (right !== null) {
        if (left.value !== right.value) {
            result = false;
            break;
        }

        left = left.next;
        right = right.next;
    }

    reverseList(reversedSecondHalf);

    return result;
}

function intersectionNode(headA, headB) {
    let a = headA;
    let b = headB;

    /*
     * Switching heads equalizes the total distance traveled by both pointers.
     * The comparison uses object identity because intersection means the same
     * physical node, not merely equal values.
     */
    while (a !== b) {
        a = a === null ? headB : a.next;
        b = b === null ? headA : b.next;
    }

    return a;
}

function findDuplicateFloyd(values) {
    const n = values.length - 1;

    if (n < 1) {
        throw new RangeError("At least two values are required");
    }

    for (const value of values) {
        if (!Number.isInteger(value) || value < 1 || value > n) {
            throw new RangeError("Values must be integers in the range 1..n");
        }
    }

    /*
     * Treat values as pointers:
     *     index -> values[index]
     *
     * A duplicate causes two indices to eventually enter the same cycle.
     */
    let slow = values[0];
    let fast = values[values[0]];

    while (slow !== fast) {
        slow = values[slow];
        fast = values[values[fast]];
    }

    let finder = 0;

    while (finder !== slow) {
        finder = values[finder];
        slow = values[slow];
    }

    return finder;
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function demonstrateMiddleFinding() {
    console.log("\nMIDDLE NODE FINDING");

    const examples = [
        [10],
        [10, 20],
        [10, 20, 30],
        [10, 20, 30, 40],
        [10, 20, 30, 40, 50]
    ];

    for (const values of examples) {
        const head = buildLinkedList(values);
        const secondMiddle = middleNode(head);
        const firstMiddle = firstMiddleNode(head);

        console.log(
            values,
            "first middle =", firstMiddle?.value ?? null,
            "second middle =", secondMiddle?.value ?? null
        );
    }
}

function demonstrateCycleWorkflow() {
    console.log("\nCYCLE WORKFLOW");

    const head = buildCyclicList(
        [10, 20, 30, 40, 50, 60],
        2
    );

    console.log("Has cycle:", hasCycle(head));

    const meeting = findCycleMeetingNode(head);
    const information = getCycleInformation(head);

    console.log("Meeting node:", meeting?.value ?? null);
    console.log("Cycle entry:", information.entry?.value ?? null);
    console.log("Distance to entry:", information.distanceToEntry);
    console.log("Cycle length:", information.cycleLength);

    console.log("Before removal:", listToString(head));
    console.log("Removed:", removeCycle(head));
    console.log("After removal:", listToString(head));
    console.log("Has cycle:", hasCycle(head));
}

function demonstrateGapTechnique() {
    console.log("\nFIXED-GAP POINTER TECHNIQUE");

    const head = buildLinkedList([11, 22, 33, 44, 55, 66]);

    for (const n of [1, 2, 6, 7]) {
        const node = nthFromEnd(head, n);
        console.log(`${n}th from end:`, node?.value ?? null);
    }

    const modified = removeNthFromEnd(
        buildLinkedList([11, 22, 33, 44, 55]),
        2
    );

    console.log("After removing second from end:", listToString(modified));
}

function demonstratePalindrome() {
    console.log("\nPALINDROME CHECK");

    const examples = [
        [1, 2, 3, 2, 1],
        [1, 2, 2, 1],
        [1, 2, 3],
        [8],
        []
    ];

    for (const values of examples) {
        console.log(
            values,
            "is palindrome:",
            isPalindrome(buildLinkedList(values))
        );
    }
}

function demonstrateIntersection() {
    console.log("\nINTERSECTION BY NODE IDENTITY");

    const shared = buildLinkedList([100, 200, 300]);

    const headA = buildLinkedList([1, 2]);
    let tailA = headA;

    while (tailA.next !== null) {
        tailA = tailA.next;
    }

    tailA.next = shared;

    const headB = buildLinkedList([7, 8, 9]);
    let tailB = headB;

    while (tailB.next !== null) {
        tailB = tailB.next;
    }

    tailB.next = shared;

    const intersection = intersectionNode(headA, headB);

    console.log("Intersection:", intersection?.value ?? null);
}

function demonstrateDuplicateDetection() {
    console.log("\nDUPLICATE DETECTION AS A FUNCTIONAL GRAPH");

    const inputs = [
        [1, 3, 4, 2, 2],
        [3, 1, 3, 4, 2],
        [1, 1],
        [2, 2, 2, 2, 2]
    ];

    for (const values of inputs) {
        console.log(values, "duplicate:", findDuplicateFloyd(values));
    }
}

function demonstrateAsyncTraversal() {
    console.log("\nEVENT-DRIVEN POINTER OBSERVATION");

    /*
     * setImmediate schedules the observation after the current synchronous
     * call stack. This does not make Floyd's algorithm asynchronous; it shows
     * how the same state can be integrated into Node.js event-driven code.
     */
    return new Promise(resolve => {
        const head = buildLinkedList([5, 10, 15, 20, 25, 30]);

        let slow = head;
        let fast = head;
        let iteration = 0;

        const tick = () => {
            if (fast === null || fast.next === null) {
                console.log("Traversal ended without a cycle.");
                resolve();
                return;
            }

            slow = slow.next;
            fast = fast.next.next;
            iteration++;

            console.log(
                `iteration=${iteration}, slow=${slow.value}, ` +
                `fast=${fast?.value ?? null}`
            );

            if (slow === fast) {
                console.log("Pointers met.");
                resolve();
                return;
            }

            setImmediate(tick);
        };

        tick();
    });
}

function runTests() {
    assert(middleNode(null) === null, "empty middle");
    assert(
        middleNode(buildLinkedList([1, 2, 3, 4])).value === 3,
        "second middle"
    );

    const linear = buildLinkedList([1, 2, 3]);
    assert(!hasCycle(linear), "linear list must not have cycle");
    assert(findCycleEntry(linear) === null, "linear list has no entry");

    const cyclic = buildCyclicList([1, 2, 3, 4], 1);
    assert(hasCycle(cyclic), "cycle must be detected");
    assert(findCycleEntry(cyclic).value === 2, "entry must be node 2");

    const information = getCycleInformation(cyclic);
    assert(information.distanceToEntry === 1, "distance to entry");
    assert(information.cycleLength === 3, "cycle length");

    assert(removeCycle(cyclic), "cycle should be removed");
    assert(!hasCycle(cyclic), "cycle should no longer exist");

    assert(
        findDuplicateFloyd([1, 3, 4, 2, 2]) === 2,
        "duplicate 2"
    );

    assert(
        findDuplicateFloyd([3, 1, 3, 4, 2]) === 3,
        "duplicate 3"
    );

    assert(
        nthFromEnd(buildLinkedList([1, 2, 3]), 1).value === 3,
        "last node"
    );

    assert(
        nthFromEnd(buildLinkedList([1, 2, 3]), 4) === null,
        "n beyond length"
    );

    assert(
        isPalindrome(buildLinkedList([1, 2, 3, 2, 1])),
        "odd palindrome"
    );

    assert(
        isPalindrome(buildLinkedList([1, 2, 2, 1])),
        "even palindrome"
    );

    assert(
        !isPalindrome(buildLinkedList([1, 2, 3])),
        "non-palindrome"
    );

    console.log("\nALL TESTS PASSED");
}

async function main() {
    console.log("FAST AND SLOW POINTER TECHNIQUE");
    console.log("=".repeat(60));

    demonstrateMiddleFinding();
    demonstrateCycleWorkflow();
    demonstrateGapTechnique();
    demonstratePalindrome();
    demonstrateIntersection();
    demonstrateDuplicateDetection();

    await demonstrateAsyncTraversal();

    runTests();

    console.log("\nCOMPLEXITY");
    console.log("Middle node: O(n) time, O(1) auxiliary space");
    console.log("Cycle detection: O(n) time, O(1) auxiliary space");
    console.log("Cycle entry: O(n) time, O(1) auxiliary space");
    console.log("Cycle removal: O(n) time, O(1) auxiliary space");
    console.log("Nth from end: O(n) time, O(1) auxiliary space");
    console.log("Palindrome: O(n) time, O(1) auxiliary space");
    console.log("Duplicate detection: O(n) time, O(1) auxiliary space");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
