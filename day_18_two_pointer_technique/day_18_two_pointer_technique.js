"use strict";

/*
 * Two Pointer Technique
 * =====================
 *
 * Self-contained JavaScript study file.
 *
 * The examples cover:
 * - opposite-direction pointers
 * - same-direction read/write pointers
 * - sorted pair search
 * - partitioning
 * - duplicate removal
 * - three-sum
 * - sliding windows
 * - linked-list cycle detection
 * - advanced linear-time problems
 *
 * Run with:
 *   node two-pointer-technique.js
 */

// ============================================================================
// 1. BASIC OPPOSITE-DIRECTION POINTERS
// ============================================================================

function reverseInPlace(values) {
    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        [values[left], values[right]] = [values[right], values[left]];
        left++;
        right--;
    }

    return values;
}

function isPalindrome(text) {
    const normalized = [...text.toLowerCase()]
        .filter(character => /[\p{L}\p{N}]/u.test(character));

    let left = 0;
    let right = normalized.length - 1;

    while (left < right) {
        if (normalized[left] !== normalized[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}

// ============================================================================
// 2. SORTED TWO-SUM
// ============================================================================

function twoSumSorted(values, target) {
    let left = 0;
    let right = values.length - 1;

    while (left < right) {
        const sum = values[left] + values[right];

        if (sum === target) {
            return [left, right];
        }

        if (sum < target) {
            left++;
        } else {
            right--;
        }
    }

    return null;
}

function twoSumHash(values, target) {
    const seen = new Map();

    for (let index = 0; index < values.length; index++) {
        const value = values[index];
        const complement = target - value;

        if (seen.has(complement)) {
            return [seen.get(complement), index];
        }

        seen.set(value, index);
    }

    return null;
}

// ============================================================================
// 3. REMOVE DUPLICATES
// ============================================================================

function removeDuplicatesSorted(values) {
    if (values.length === 0) {
        return 0;
    }

    let slow = 1;

    for (let fast = 1; fast < values.length; fast++) {
        if (values[fast] !== values[slow - 1]) {
            values[slow] = values[fast];
            slow++;
        }
    }

    return slow;
}

// ============================================================================
// 4. MOVE ZEROES
// ============================================================================

function moveZeroes(values) {
    let slow = 0;

    for (let fast = 0; fast < values.length; fast++) {
        if (values[fast] !== 0) {
            [values[slow], values[fast]] = [values[fast], values[slow]];
            slow++;
        }
    }

    return values;
}

// ============================================================================
// 5. PARTITIONING
// ============================================================================

function partitionByPivot(values, pivot) {
    let left = 0;
    let right = values.length - 1;

    while (left <= right) {
        while (left <= right && values[left] < pivot) {
            left++;
        }

        while (left <= right && values[right] >= pivot) {
            right--;
        }

        if (left <= right) {
            [values[left], values[right]] = [values[right], values[left]];
            left++;
            right--;
        }
    }

    return left;
}

function dutchNationalFlag(values) {
    let low = 0;
    let middle = 0;
    let high = values.length - 1;

    while (middle <= high) {
        if (values[middle] === 0) {
            [values[low], values[middle]] =
                [values[middle], values[low]];
            low++;
            middle++;
        } else if (values[middle] === 1) {
            middle++;
        } else if (values[middle] === 2) {
            [values[middle], values[high]] =
                [values[high], values[middle]];
            high--;
        } else {
            throw new Error("Expected only 0, 1, and 2.");
        }
    }

    return values;
}

// ============================================================================
// 6. THREE-SUM
// ============================================================================

function threeSum(values, target = 0) {
    const numbers = [...values].sort((a, b) => a - b);
    const results = [];

    for (let first = 0; first < numbers.length - 2; first++) {
        if (first > 0 && numbers[first] === numbers[first - 1]) {
            continue;
        }

        let left = first + 1;
        let right = numbers.length - 1;

        while (left < right) {
            const sum =
                numbers[first] +
                numbers[left] +
                numbers[right];

            if (sum === target) {
                results.push([
                    numbers[first],
                    numbers[left],
                    numbers[right]
                ]);

                const leftValue = numbers[left];
                const rightValue = numbers[right];

                while (
                    left < right &&
                    numbers[left] === leftValue
                ) {
                    left++;
                }

                while (
                    left < right &&
                    numbers[right] === rightValue
                ) {
                    right--;
                }
            } else if (sum < target) {
                left++;
            } else {
                right--;
            }
        }
    }

    return results;
}

// ============================================================================
// 7. CONTAINER WITH MOST WATER
// ============================================================================

function maxContainerArea(heights) {
    let left = 0;
    let right = heights.length - 1;
    let best = 0;

    while (left < right) {
        const width = right - left;
        const limitingHeight =
            Math.min(heights[left], heights[right]);

        best = Math.max(best, width * limitingHeight);

        // The shorter boundary is the bottleneck.
        // Moving the taller boundary alone cannot improve that bottleneck.
        if (heights[left] < heights[right]) {
            left++;
        } else {
            right--;
        }
    }

    return best;
}

// ============================================================================
// 8. SORTED SQUARES
// ============================================================================

function sortedSquares(values) {
    const result = new Array(values.length);
    let left = 0;
    let right = values.length - 1;
    let write = values.length - 1;

    while (left <= right) {
        const leftSquare = values[left] ** 2;
        const rightSquare = values[right] ** 2;

        if (leftSquare > rightSquare) {
            result[write] = leftSquare;
            left++;
        } else {
            result[write] = rightSquare;
            right--;
        }

        write--;
    }

    return result;
}

// ============================================================================
// 9. MERGE SORTED ARRAYS
// ============================================================================

function mergeSortedArrays(first, second) {
    const result = [];
    let left = 0;
    let right = 0;

    while (left < first.length && right < second.length) {
        if (first[left] <= second[right]) {
            result.push(first[left]);
            left++;
        } else {
            result.push(second[right]);
            right++;
        }
    }

    while (left < first.length) {
        result.push(first[left]);
        left++;
    }

    while (right < second.length) {
        result.push(second[right]);
        right++;
    }

    return result;
}

// ============================================================================
// 10. INTERSECTION OF SORTED ARRAYS
// ============================================================================

function intersectionSorted(first, second) {
    let left = 0;
    let right = 0;
    const result = [];

    while (left < first.length && right < second.length) {
        if (first[left] === second[right]) {
            if (
                result.length === 0 ||
                result[result.length - 1] !== first[left]
            ) {
                result.push(first[left]);
            }

            left++;
            right++;
        } else if (first[left] < second[right]) {
            left++;
        } else {
            right++;
        }
    }

    return result;
}

// ============================================================================
// 11. SLIDING WINDOW
// ============================================================================

function longestUniqueSubstring(text) {
    const lastSeen = new Map();
    let left = 0;
    let best = 0;

    for (let right = 0; right < text.length; right++) {
        const character = text[right];

        if (
            lastSeen.has(character) &&
            lastSeen.get(character) >= left
        ) {
            left = lastSeen.get(character) + 1;
        }

        lastSeen.set(character, right);
        best = Math.max(best, right - left + 1);
    }

    return best;
}

function minimumSizeSubarraySum(target, values) {
    let left = 0;
    let currentSum = 0;
    let best = Infinity;

    for (let right = 0; right < values.length; right++) {
        if (values[right] < 0) {
            throw new Error(
                "This implementation requires non-negative values."
            );
        }

        currentSum += values[right];

        while (currentSum >= target) {
            best = Math.min(best, right - left + 1);
            currentSum -= values[left];
            left++;
        }
    }

    return best === Infinity ? 0 : best;
}

// ============================================================================
// 12. LINKED-LIST CYCLE DETECTION
// ============================================================================

class ListNode {
    constructor(value) {
        this.value = value;
        this.next = null;
    }
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

function findCycleStart(head) {
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;

        if (slow === fast) {
            let pointer = head;

            while (pointer !== slow) {
                pointer = pointer.next;
                slow = slow.next;
            }

            return pointer;
        }
    }

    return null;
}

// ============================================================================
// 13. TRAPPING RAIN WATER
// ============================================================================

function trapRainWater(heights) {
    let left = 0;
    let right = heights.length - 1;
    let leftMax = 0;
    let rightMax = 0;
    let water = 0;

    while (left <= right) {
        if (heights[left] <= heights[right]) {
            if (heights[left] >= leftMax) {
                leftMax = heights[left];
            } else {
                water += leftMax - heights[left];
            }

            left++;
        } else {
            if (heights[right] >= rightMax) {
                rightMax = heights[right];
            } else {
                water += rightMax - heights[right];
            }

            right--;
        }
    }

    return water;
}

// ============================================================================
// 14. ASYNCHRONOUS STREAM EXAMPLE
// ============================================================================

async function* numberStream(values, delayMilliseconds = 0) {
    /*
     * Two-pointer algorithms also appear in streaming applications.
     * This generator represents a source that yields values progressively.
     */
    for (const value of values) {
        if (delayMilliseconds > 0) {
            await new Promise(resolve =>
                setTimeout(resolve, delayMilliseconds)
            );
        }

        yield value;
    }
}

async function findTargetPairFromSortedStream(values, target) {
    /*
     * A normal two-pointer algorithm needs random access to both ends.
     * A one-way asynchronous stream does not provide that capability.
     *
     * This example materializes the stream first, making the limitation
     * explicit rather than pretending a forward-only stream supports
     * ordinary opposite-end pointers.
     */
    const materialized = [];

    for await (const value of numberStream(values)) {
        materialized.push(value);
    }

    return twoSumSorted(materialized, target);
}

// ============================================================================
// 15. TESTS
// ============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

async function runTests() {
    assert(
        JSON.stringify(reverseInPlace([1, 2, 3])) ===
        JSON.stringify([3, 2, 1]),
        "reverse"
    );

    assert(isPalindrome("racecar"), "palindrome");
    assert(!isPalindrome("javascript"), "non-palindrome");

    assert(
        JSON.stringify(twoSumSorted([1, 2, 4, 7, 9], 11)) ===
        JSON.stringify([1, 4]),
        "sorted two sum"
    );

    assert(
        JSON.stringify(twoSumHash([2, 7, 11, 15], 9)) ===
        JSON.stringify([0, 1]),
        "hash two sum"
    );

    const duplicateValues = [1, 1, 2, 2, 3];
    const uniqueLength = removeDuplicatesSorted(duplicateValues);
    assert(
        JSON.stringify(duplicateValues.slice(0, uniqueLength)) ===
        JSON.stringify([1, 2, 3]),
        "duplicate removal"
    );

    assert(
        JSON.stringify(moveZeroes([0, 1, 0, 3, 12])) ===
        JSON.stringify([1, 3, 12, 0, 0]),
        "move zeroes"
    );

    const partitioned = [4, 1, 7, 2, 8, 3, 5];
    const boundary = partitionByPivot(partitioned, 5);

    assert(
        partitioned.slice(0, boundary).every(value => value < 5),
        "partition lower region"
    );

    assert(
        partitioned.slice(boundary).every(value => value >= 5),
        "partition upper region"
    );

    assert(
        JSON.stringify(dutchNationalFlag([2, 0, 2, 1, 1, 0])) ===
        JSON.stringify([0, 0, 1, 1, 2, 2]),
        "Dutch National Flag"
    );

    assert(
        JSON.stringify(
            threeSum([-1, 0, 1, 2, -1, -4], 0)
        ) ===
        JSON.stringify([
            [-1, -1, 2],
            [-1, 0, 1]
        ]),
        "three sum"
    );

    assert(
        maxContainerArea([1, 8, 6, 2, 5, 4, 8, 3, 7]) === 49,
        "container"
    );

    assert(
        JSON.stringify(
            sortedSquares([-7, -3, -1, 4, 8])
        ) ===
        JSON.stringify([1, 9, 16, 49, 64]),
        "sorted squares"
    );

    assert(
        JSON.stringify(
            mergeSortedArrays([1, 3, 5], [2, 4, 6])
        ) ===
        JSON.stringify([1, 2, 3, 4, 5, 6]),
        "merge"
    );

    assert(
        JSON.stringify(
            intersectionSorted([1, 2, 2, 4], [2, 2, 3, 4])
        ) ===
        JSON.stringify([2, 4]),
        "intersection"
    );

    assert(
        longestUniqueSubstring("abcabcbb") === 3,
        "unique substring"
    );

    assert(
        minimumSizeSubarraySum(7, [2, 3, 1, 2, 4, 3]) === 2,
        "minimum window"
    );

    const first = new ListNode(1);
    const second = new ListNode(2);
    const third = new ListNode(3);
    const fourth = new ListNode(4);

    first.next = second;
    second.next = third;
    third.next = fourth;
    fourth.next = second;

    assert(hasCycle(first), "cycle detection");
    assert(findCycleStart(first) === second, "cycle entry");

    assert(
        trapRainWater([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) === 6,
        "rain water"
    );

    const streamResult =
        await findTargetPairFromSortedStream([1, 2, 4, 7, 9], 11);

    assert(
        JSON.stringify(streamResult) === JSON.stringify([1, 4]),
        "async stream"
    );

    console.log("All JavaScript assertions passed.");
}

// ============================================================================
// 16. DEMONSTRATION
// ============================================================================

async function main() {
    console.log("=== TWO POINTER TECHNIQUE ===");

    console.log(
        "Reverse:",
        reverseInPlace([1, 2, 3, 4, 5])
    );

    console.log(
        "Palindrome:",
        isPalindrome("A man, a plan, a canal: Panama")
    );

    console.log(
        "Sorted two sum:",
        twoSumSorted([1, 2, 4, 7, 9, 12], 16)
    );

    console.log(
        "Unsorted hash two sum:",
        twoSumHash([11, 3, 7, 2, 9, 14], 16)
    );

    const values = [1, 1, 2, 2, 3, 4, 4];
    const length = removeDuplicatesSorted(values);

    console.log(
        "Unique prefix:",
        values.slice(0, length)
    );

    console.log(
        "Three sum:",
        threeSum([-1, 0, 1, 2, -1, -4])
    );

    console.log(
        "Maximum container:",
        maxContainerArea([1, 8, 6, 2, 5, 4, 8, 3, 7])
    );

    console.log(
        "Sorted squares:",
        sortedSquares([-7, -3, -1, 4, 8])
    );

    console.log(
        "Trapped water:",
        trapRainWater([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])
    );

    console.log(
        "Longest unique substring:",
        longestUniqueSubstring("pwwkew")
    );

    await runTests();
}

main().catch(error => {
    console.error(error.message);
    process.exitCode = 1;
});
