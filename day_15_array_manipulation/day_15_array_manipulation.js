 * Array Manipulation: Beginner to Advanced JavaScript Study
 *
 * JavaScript arrays are dynamic, indexed collections. They can hold values
 * of different types, although production applications commonly use
 * homogeneous arrays for predictable processing.
 *
 * Topics demonstrated:
 * - Indexing and traversal
 * - Updating
 * - Insertion and deletion
 * - Swapping
 * - Reversal
 * - Shifting
 * - Rotation
 * - Stable and unstable rearrangement
 * - Two-pointer techniques
 * - Duplicate removal
 * - Searching
 * - Advanced partitioning
 * - Functional versus in-place operations
 * - Validation and error handling
 * - A realistic order-processing case study
 * - Complexity and performance considerations
 */

"use strict";

// ---------------------------------------------------------------------------
// 1. FUNDAMENTALS
// ---------------------------------------------------------------------------

function demonstrateBasics() {
    console.log("\n=== 1. Array Fundamentals ===");

    const numbers = [10, 20, 30, 40, 50];

    console.log("Array:", numbers);
    console.log("First element:", numbers[0]);
    console.log("Last element:", numbers[numbers.length - 1]);

    // Array indexes start at zero.
    numbers[2] = 35;
    console.log("After updating index 2:", numbers);

    console.log("Traversal:");
    numbers.forEach((value, index) => {
        console.log(`  index=${index}, value=${value}`);
    });

    console.log("Slice:", numbers.slice(1, 4));
    console.log("Includes 30:", numbers.includes(30));
}

// ---------------------------------------------------------------------------
// 2. INSERTION AND DELETION
// ---------------------------------------------------------------------------

function insertAt(array, index, value) {
    if (!Number.isInteger(index) || index < 0 || index > array.length) {
        throw new RangeError("Insertion index out of range");
    }

    // splice changes the existing array.
    array.splice(index, 0, value);
}

function deleteAt(array, index) {
    if (!Number.isInteger(index) || index < 0 || index >= array.length) {
        throw new RangeError("Deletion index out of range");
    }

    const [deleted] = array.splice(index, 1);
    return deleted;
}

function demonstrateInsertionDeletion() {
    console.log("\n=== 2. Insertion and Deletion ===");

    const values = [10, 20, 40, 50];

    insertAt(values, 2, 30);
    console.log("After insertion:", values);

    const deleted = deleteAt(values, 1);
    console.log("Deleted:", deleted);
    console.log("After deletion:", values);

    values.push(60);
    console.log("After push:", values);

    const last = values.pop();
    console.log("Popped:", last);
    console.log("After pop:", values);
}

// ---------------------------------------------------------------------------
// 3. SWAPPING AND REVERSING
// ---------------------------------------------------------------------------

function swap(array, first, second) {
    if (
        first < 0 ||
        second < 0 ||
        first >= array.length ||
        second >= array.length
    ) {
        throw new RangeError("Swap index out of range");
    }

    // JavaScript supports destructuring assignment, which makes swapping
    // concise without requiring a temporary variable.
    [array[first], array[second]] = [array[second], array[first]];
}

function reverseInPlace(array) {
    let left = 0;
    let right = array.length - 1;

    while (left < right) {
        [array[left], array[right]] = [array[right], array[left]];
        left++;
        right--;
    }
}

function demonstrateSwapReverse() {
    console.log("\n=== 3. Swapping and Reversing ===");

    const values = [1, 2, 3, 4, 5];

    swap(values, 0, 4);
    console.log("After swap:", values);

    reverseInPlace(values);
    console.log("After in-place reverse:", values);

    // reverse() mutates its receiver.
    const another = [1, 2, 3];
    console.log("Built-in reverse:", another.reverse());
}

// ---------------------------------------------------------------------------
// 4. SHIFTING
// ---------------------------------------------------------------------------

function shiftLeft(array, positions, fillValue = 0) {
    if (!Number.isInteger(positions) || positions < 0) {
        throw new RangeError("Positions must be a non-negative integer");
    }

    if (array.length === 0) {
        return;
    }

    const count = Math.min(positions, array.length);

    for (let index = 0; index < array.length - count; index++) {
        array[index] = array[index + count];
    }

    for (let index = array.length - count; index < array.length; index++) {
        array[index] = fillValue;
    }
}

function shiftRight(array, positions, fillValue = 0) {
    if (!Number.isInteger(positions) || positions < 0) {
        throw new RangeError("Positions must be a non-negative integer");
    }

    if (array.length === 0) {
        return;
    }

    const count = Math.min(positions, array.length);

    // Right shifting must proceed from right to left so values are not
    // overwritten before they are copied.
    for (let index = array.length - 1; index >= count; index--) {
        array[index] = array[index - count];
    }

    for (let index = 0; index < count; index++) {
        array[index] = fillValue;
    }
}

function demonstrateShifting() {
    console.log("\n=== 4. Shifting ===");

    const left = [1, 2, 3, 4, 5];
    shiftLeft(left, 2);
    console.log("Left shift:", left);

    const right = [1, 2, 3, 4, 5];
    shiftRight(right, 2);
    console.log("Right shift:", right);
}

// ---------------------------------------------------------------------------
// 5. ROTATION
// ---------------------------------------------------------------------------

function reverseRange(array, left, right) {
    while (left < right) {
        [array[left], array[right]] = [array[right], array[left]];
        left++;
        right--;
    }
}

function rotateLeft(array, positions) {
    if (array.length === 0) {
        return;
    }

    if (!Number.isInteger(positions)) {
        throw new TypeError("Positions must be an integer");
    }

    const count = ((positions % array.length) + array.length) % array.length;

    if (count === 0) {
        return;
    }

    // Three reversals produce a left rotation in O(n) time and O(1)
    // auxiliary space.
    reverseRange(array, 0, count - 1);
    reverseRange(array, count, array.length - 1);
    reverseRange(array, 0, array.length - 1);
}

function rotateRight(array, positions) {
    if (array.length === 0) {
        return;
    }

    const count = ((positions % array.length) + array.length) % array.length;
    rotateLeft(array, array.length - count);
}

function demonstrateRotation() {
    console.log("\n=== 5. Rotation ===");

    const left = [1, 2, 3, 4, 5];
    rotateLeft(left, 2);
    console.log("Left rotation:", left);

    const right = [1, 2, 3, 4, 5];
    rotateRight(right, 2);
    console.log("Right rotation:", right);

    const largeRotation = [1, 2, 3];
    rotateLeft(largeRotation, 100);
    console.log("Rotation by 100:", largeRotation);

    const negativeRotation = [1, 2, 3, 4];
    rotateLeft(negativeRotation, -1);
    console.log("Negative rotation normalized:", negativeRotation);
}

// ---------------------------------------------------------------------------
// 6. REARRANGEMENT
// ---------------------------------------------------------------------------

function moveZeroesToEnd(array) {
    let writeIndex = 0;

    // Copy every non-zero value toward the beginning.
    for (const value of array) {
        if (value !== 0) {
            array[writeIndex++] = value;
        }
    }

    // Fill the remaining positions with zero.
    while (writeIndex < array.length) {
        array[writeIndex++] = 0;
    }
}

function partitionByPivot(array, pivot) {
    let left = 0;
    let right = array.length - 1;

    while (left <= right) {
        while (left <= right && array[left] < pivot) {
            left++;
        }

        while (left <= right && array[right] >= pivot) {
            right--;
        }

        if (left < right) {
            swap(array, left, right);
            left++;
            right--;
        }
    }
}

function rearrangeEvenOdd(array) {
    let left = 0;
    let right = array.length - 1;

    while (left < right) {
        while (left < right && array[left] % 2 === 0) {
            left++;
        }

        while (left < right && array[right] % 2 !== 0) {
            right--;
        }

        if (left < right) {
            swap(array, left, right);
            left++;
            right--;
        }
    }
}

function demonstrateRearrangement() {
    console.log("\n=== 6. Rearrangement ===");

    const zeros = [0, 1, 0, 3, 12, 0];
    moveZeroesToEnd(zeros);
    console.log("Zeroes at end:", zeros);

    const partitioned = [9, 2, 7, 4, 6, 1, 8, 3];
    partitionByPivot(partitioned, 5);
    console.log("Partitioned around 5:", partitioned);

    const parity = [1, 2, 3, 4, 5, 6];
    rearrangeEvenOdd(parity);
    console.log("Even before odd:", parity);
}

// ---------------------------------------------------------------------------
// 7. DUPLICATES AND SEARCHING
// ---------------------------------------------------------------------------

function removeDuplicatesPreserveOrder(array) {
    const seen = new Set();
    const result = [];

    for (const value of array) {
        if (!seen.has(value)) {
            seen.add(value);
            result.push(value);
        }
    }

    return result;
}

function linearSearch(array, target) {
    for (let index = 0; index < array.length; index++) {
        if (array[index] === target) {
            return index;
        }
    }

    return -1;
}

function binarySearch(sortedArray, target) {
    let left = 0;
    let right = sortedArray.length - 1;

    while (left <= right) {
        const middle = Math.floor((left + right) / 2);

        if (sortedArray[middle] === target) {
            return middle;
        }

        if (sortedArray[middle] < target) {
            left = middle + 1;
        } else {
            right = middle - 1;
        }
    }

    return -1;
}

function demonstrateSearchAndDuplicates() {
    console.log("\n=== 7. Searching and Duplicate Removal ===");

    const values = [3, 1, 3, 2, 1, 4];
    console.log("Unique:", removeDuplicatesPreserveOrder(values));

    console.log("Linear search:", linearSearch(values, 4));

    const sorted = [1, 2, 4, 7, 9, 12];
    console.log("Binary search:", binarySearch(sorted, 9));
}

// ---------------------------------------------------------------------------
// 8. ADVANCED ARRAY ALGORITHMS
// ---------------------------------------------------------------------------

function dutchNationalFlag(array) {
    let low = 0;
    let current = 0;
    let high = array.length - 1;

    while (current <= high) {
        if (array[current] === 0) {
            swap(array, low, current);
            low++;
            current++;
        } else if (array[current] === 1) {
            current++;
        } else if (array[current] === 2) {
            swap(array, current, high);
            high--;
        } else {
            throw new RangeError("Only 0, 1, and 2 are allowed");
        }
    }
}

function wiggleRearrange(array) {
    // Produces a0 <= a1 >= a2 <= a3...
    for (let index = 0; index < array.length - 1; index++) {
        if (index % 2 === 0 && array[index] > array[index + 1]) {
            swap(array, index, index + 1);
        }

        if (index % 2 === 1 && array[index] < array[index + 1]) {
            swap(array, index, index + 1);
        }
    }
}

function rearrangeAlternatingSign(array) {
    const positives = array.filter(value => value >= 0);
    const negatives = array.filter(value => value < 0);

    const result = [];
    let positiveIndex = 0;
    let negativeIndex = 0;
    let usePositive = positives.length > 0;

    while (
        positiveIndex < positives.length ||
        negativeIndex < negatives.length
    ) {
        if (usePositive && positiveIndex < positives.length) {
            result.push(positives[positiveIndex++]);
        } else if (!usePositive && negativeIndex < negatives.length) {
            result.push(negatives[negativeIndex++]);
        } else if (positiveIndex < positives.length) {
            result.push(positives[positiveIndex++]);
        } else {
            result.push(negatives[negativeIndex++]);
        }

        usePositive = !usePositive;
    }

    return result;
}

function demonstrateAdvancedRearrangement() {
    console.log("\n=== 8. Advanced Rearrangement ===");

    const values = [2, 0, 2, 1, 1, 0, 2];
    dutchNationalFlag(values);
    console.log("Three-way partition:", values);

    const wiggle = [3, 5, 2, 1, 6, 4];
    wiggleRearrange(wiggle);
    console.log("Wiggle arrangement:", wiggle);

    console.log(
        "Alternating signs:",
        rearrangeAlternatingSign([1, -2, 3, -4, -5, 6])
    );
}

// ---------------------------------------------------------------------------
// 9. FUNCTIONAL VERSUS IN-PLACE OPERATIONS
// ---------------------------------------------------------------------------

function rotateCopy(array, positions) {
    if (array.length === 0) {
        return [];
    }

    const count = ((positions % array.length) + array.length) % array.length;

    // slice() creates new arrays. The original array remains unchanged.
    return array.slice(count).concat(array.slice(0, count));
}

function demonstrateMutationDifference() {
    console.log("\n=== 9. Mutation versus Copy ===");

    const original = [1, 2, 3, 4];

    const copiedRotation = rotateCopy(original, 2);
    console.log("Original after copy-based rotation:", original);
    console.log("New rotated array:", copiedRotation);

    const mutable = [1, 2, 3, 4];
    rotateLeft(mutable, 2);
    console.log("Original changed by in-place rotation:", mutable);
}

// ---------------------------------------------------------------------------
// 10. REALISTIC CASE STUDY: ORDER PRIORITY QUEUE
// ---------------------------------------------------------------------------

class OrderQueue {
    constructor() {
        this.orders = [];
    }

    addOrder(order) {
        if (!order || typeof order !== "object") {
            throw new TypeError("Order must be an object");
        }

        if (!Number.isInteger(order.priority) || order.priority < 0) {
            throw new RangeError("Priority must be a non-negative integer");
        }

        if (typeof order.id !== "string" || order.id.length === 0) {
            throw new TypeError("Order ID must be a non-empty string");
        }

        this.orders.push({
            id: order.id,
            priority: order.priority,
            quantity: order.quantity ?? 1
        });
    }

    cancelOrder(orderId) {
        const index = this.orders.findIndex(order => order.id === orderId);

        if (index === -1) {
            return false;
        }

        this.orders.splice(index, 1);
        return true;
    }

    promoteOrder(orderId) {
        const index = this.orders.findIndex(order => order.id === orderId);

        if (index === -1) {
            return false;
        }

        // Move the order to the front. This is O(n) because intervening
        // elements must change positions.
        const [order] = this.orders.splice(index, 1);
        this.orders.unshift(order);
        return true;
    }

    rotateForBatchProcessing(offset) {
        rotateLeft(this.orders, offset);
    }

    processNext() {
        return this.orders.shift() ?? null;
    }

    snapshot() {
        return this.orders.map(order => ({ ...order }));
    }
}

function demonstrateOrderCaseStudy() {
    console.log("\n=== 10. Order Queue Case Study ===");

    const queue = new OrderQueue();

    queue.addOrder({ id: "ORD-101", priority: 2, quantity: 10 });
    queue.addOrder({ id: "ORD-102", priority: 1, quantity: 5 });
    queue.addOrder({ id: "ORD-103", priority: 3, quantity: 2 });

    console.log("Initial orders:", queue.snapshot());

    queue.promoteOrder("ORD-103");
    console.log("After promotion:", queue.snapshot());

    queue.cancelOrder("ORD-102");
    console.log("After cancellation:", queue.snapshot());

    queue.rotateForBatchProcessing(1);
    console.log("After rotation:", queue.snapshot());

    console.log("Processed order:", queue.processNext());
    console.log("Remaining:", queue.snapshot());
}

// ---------------------------------------------------------------------------
// 11. ERROR HANDLING AND EDGE CASES
// ---------------------------------------------------------------------------

function demonstrateEdgeCases() {
    console.log("\n=== 11. Edge Cases ===");

    const empty = [];
    rotateLeft(empty, 5);
    reverseInPlace(empty);
    console.log("Empty array:", empty);

    const single = [42];
    rotateRight(single, 100);
    console.log("Single-element array:", single);

    try {
        insertAt([1, 2, 3], 10, 99);
    } catch (error) {
        console.log("Handled invalid insertion:", error.message);
    }

    try {
        dutchNationalFlag([0, 1, 3]);
    } catch (error) {
        console.log("Handled invalid three-way input:", error.message);
    }

    try {
        const queue = new OrderQueue();
        queue.addOrder({ id: "", priority: 1 });
    } catch (error) {
        console.log("Handled invalid order:", error.message);
    }
}

// ---------------------------------------------------------------------------
// 12. TESTING
// ---------------------------------------------------------------------------

function assertEqual(actual, expected, message) {
    const actualJson = JSON.stringify(actual);
    const expectedJson = JSON.stringify(expected);

    if (actualJson !== expectedJson) {
        throw new Error(
            `${message}\nExpected: ${expectedJson}\nActual: ${actualJson}`
        );
    }
}

function runTests() {
    console.log("\n=== 12. Tests ===");

    const left = [1, 2, 3, 4, 5];
    rotateLeft(left, 2);
    assertEqual(left, [3, 4, 5, 1, 2], "Left rotation failed");

    const right = [1, 2, 3, 4, 5];
    rotateRight(right, 2);
    assertEqual(right, [4, 5, 1, 2, 3], "Right rotation failed");

    const reversed = [1, 2, 3];
    reverseInPlace(reversed);
    assertEqual(reversed, [3, 2, 1], "Reverse failed");

    const zeros = [0, 1, 0, 3, 12];
    moveZeroesToEnd(zeros);
    assertEqual(zeros, [1, 3, 12, 0, 0], "Zero movement failed");

    const colors = [2, 0, 2, 1, 1, 0];
    dutchNationalFlag(colors);
    assertEqual(colors, [0, 0, 1, 1, 2, 2], "Three-way partition failed");

    if (binarySearch([1, 3, 5, 7], 5) !== 2) {
        throw new Error("Binary search failed");
    }

    if (linearSearch([4, 7, 9], 8) !== -1) {
        throw new Error("Linear search failure case failed");
    }

    console.log("All tests passed.");
}

// ---------------------------------------------------------------------------
// 13. PERFORMANCE DEMONSTRATION
// ---------------------------------------------------------------------------

function benchmarkRotation() {
    console.log("\n=== 13. Performance ===");

    const size = 100000;
    const source = Array.from({ length: size }, (_, index) => index);

    const inPlace = source.slice();
    const startInPlace = performance.now();
    rotateLeft(inPlace, 12345);
    const inPlaceTime = performance.now() - startInPlace;

    const startCopy = performance.now();
    const copied = rotateCopy(source, 12345);
    const copyTime = performance.now() - startCopy;

    console.log(`In-place rotation: ${inPlaceTime.toFixed(3)} ms`);
    console.log(`Copy-based rotation: ${copyTime.toFixed(3)} ms`);
    console.log(
        "Both are O(n), but copy-based rotation requires additional memory."
    );

    // Referencing the result prevents the example from being purely
    // dead computation in some runtimes.
    console.log("Verification:", copied[0], inPlace[0]);
}

// ---------------------------------------------------------------------------
// 14. MAIN
// ---------------------------------------------------------------------------

function main() {
    console.log("=".repeat(72));
    console.log("ARRAY MANIPULATION: COMPLETE JAVASCRIPT STUDY PROGRAM");
    console.log("=".repeat(72));

    demonstrateBasics();
    demonstrateInsertionDeletion();
    demonstrateSwapReverse();
    demonstrateShifting();
    demonstrateRotation();
    demonstrateRearrangement();
    demonstrateSearchAndDuplicates();
    demonstrateAdvancedRearrangement();
    demonstrateMutationDifference();
    demonstrateOrderCaseStudy();
    demonstrateEdgeCases();
    runTests();
    benchmarkRotation();

    console.log("\n=== Complexity Reference ===");
    console.log("Indexed access: O(1)");
    console.log("Update by index: O(1)");
    console.log("Append: O(1) amortized");
    console.log("Insert/delete near beginning: O(n)");
    console.log("Linear search: O(n)");
    console.log("Binary search on sorted array: O(log n)");
    console.log("Reverse: O(n) time, O(1) auxiliary space");
    console.log("Rotation: O(n) time, O(1) auxiliary space");
    console.log("Set-based duplicate removal: O(n) average time, O(n) space");
}

main();
