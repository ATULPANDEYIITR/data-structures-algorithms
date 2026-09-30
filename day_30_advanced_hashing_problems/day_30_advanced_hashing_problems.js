/**
 * Advanced Hashing Problems
 *
 * This Node.js program complements the Python implementation by emphasizing
 * JavaScript's Map and Set APIs, object-key pitfalls, event-driven workflow
 * modeling, immutable canonical keys, and hash-based analytics.
 *
 * Run:
 *     node advanced_hashing.js
 */

"use strict";

// -----------------------------------------------------------------------------
// Fundamental Map and Set operations
// -----------------------------------------------------------------------------

function frequencyMap(values) {
    const counts = new Map();

    for (const value of values) {
        counts.set(value, (counts.get(value) ?? 0) + 1);
    }

    return counts;
}

function containsDuplicate(values) {
    const seen = new Set();

    for (const value of values) {
        if (seen.has(value)) {
            return true;
        }

        seen.add(value);
    }

    return false;
}

function firstUniqueValue(values) {
    const counts = frequencyMap(values);

    for (const value of values) {
        if (counts.get(value) === 1) {
            return value;
        }
    }

    return null;
}

// -----------------------------------------------------------------------------
// Pair-sum hashing
// -----------------------------------------------------------------------------

function twoSum(values, target) {
    const seen = new Map();

    for (let index = 0; index < values.length; index += 1) {
        const value = values[index];
        const complement = target - value;

        if (seen.has(complement)) {
            return [seen.get(complement), index];
        }

        seen.set(value, index);
    }

    return null;
}

function countPairsWithSum(values, target) {
    const frequencies = new Map();
    let result = 0;

    for (const value of values) {
        const complement = target - value;

        result += frequencies.get(complement) ?? 0;
        frequencies.set(value, (frequencies.get(value) ?? 0) + 1);
    }

    return result;
}

function distinctValuePairs(values, target) {
    const seen = new Set();
    const pairs = new Map();

    for (const value of values) {
        const complement = target - value;

        if (seen.has(complement)) {
            const low = Math.min(value, complement);
            const high = Math.max(value, complement);
            pairs.set(`${low}:${high}`, [low, high]);
        }

        seen.add(value);
    }

    return [...pairs.values()];
}

// -----------------------------------------------------------------------------
// Prefix-sum hashing
// -----------------------------------------------------------------------------

function hasSubarraySum(values, target) {
    const seenPrefixes = new Set([0]);
    let running = 0;

    for (const value of values) {
        running += value;

        if (seenPrefixes.has(running - target)) {
            return true;
        }

        seenPrefixes.add(running);
    }

    return false;
}

function countSubarraysWithSum(values, target) {
    const prefixFrequency = new Map([[0, 1]]);
    let running = 0;
    let result = 0;

    for (const value of values) {
        running += value;

        result += prefixFrequency.get(running - target) ?? 0;

        prefixFrequency.set(
            running,
            (prefixFrequency.get(running) ?? 0) + 1
        );
    }

    return result;
}

function longestSubarrayWithSum(values, target) {
    // Earliest prefix occurrence is retained because it maximizes length.
    const firstIndex = new Map([[0, -1]]);
    let running = 0;
    let best = null;

    for (let index = 0; index < values.length; index += 1) {
        running += values[index];

        const required = running - target;

        if (firstIndex.has(required)) {
            const boundary = firstIndex.get(required);
            const candidate = {
                length: index - boundary,
                start: boundary + 1,
                end: index,
                sum: target,
            };

            if (best === null || candidate.length > best.length) {
                best = candidate;
            }
        }

        if (!firstIndex.has(running)) {
            firstIndex.set(running, index);
        }
    }

    return best;
}

// -----------------------------------------------------------------------------
// Modular prefix hashing
// -----------------------------------------------------------------------------

function normalizedModulo(value, divisor) {
    // JavaScript's % retains the dividend's sign. Normalizing avoids negative
    // keys when prefix sums contain negative values.
    return ((value % divisor) + divisor) % divisor;
}

function countSubarraysDivisibleBy(values, divisor) {
    if (!Number.isInteger(divisor) || divisor === 0) {
        throw new RangeError("divisor must be a non-zero integer");
    }

    const remainderFrequency = new Map([[0, 1]]);
    let running = 0;
    let result = 0;

    for (const value of values) {
        running += value;

        const remainder = normalizedModulo(running, divisor);
        result += remainderFrequency.get(remainder) ?? 0;

        remainderFrequency.set(
            remainder,
            (remainderFrequency.get(remainder) ?? 0) + 1
        );
    }

    return result;
}

// -----------------------------------------------------------------------------
// Frequency analytics
// -----------------------------------------------------------------------------

function topKFrequent(values, k) {
    if (!Number.isInteger(k) || k < 0) {
        throw new RangeError("k must be a non-negative integer");
    }

    const entries = [...frequencyMap(values).entries()];

    entries.sort((a, b) => {
        if (b[1] !== a[1]) {
            return b[1] - a[1];
        }

        return a[0] - b[0];
    });

    return entries.slice(0, k).map(([value]) => value);
}

function majorityElement(values) {
    if (values.length === 0) {
        return null;
    }

    const counts = frequencyMap(values);
    const threshold = Math.floor(values.length / 2);

    for (const [value, count] of counts) {
        if (count > threshold) {
            return value;
        }
    }

    return null;
}

// -----------------------------------------------------------------------------
// Canonical grouping
// -----------------------------------------------------------------------------

function anagramSignature(word) {
    const frequencies = new Array(26).fill(0);

    for (const character of word.toLowerCase()) {
        const code = character.charCodeAt(0);

        if (code < 97 || code > 122) {
            throw new TypeError("Only ASCII letters are supported.");
        }

        frequencies[code - 97] += 1;
    }

    return frequencies.join("#");
}

function groupAnagrams(words) {
    const groups = new Map();

    for (const word of words) {
        const key = anagramSignature(word);

        if (!groups.has(key)) {
            groups.set(key, []);
        }

        groups.get(key).push(word);
    }

    return [...groups.values()];
}

function shiftedStringSignature(word) {
    if (word.length === 0) {
        return "";
    }

    for (const character of word) {
        if (character < "a" || character > "z") {
            throw new TypeError("Expected lowercase ASCII characters.");
        }
    }

    const differences = [];

    for (let index = 1; index < word.length; index += 1) {
        const current = word.charCodeAt(index);
        const previous = word.charCodeAt(index - 1);

        differences.push((current - previous + 26) % 26);
    }

    return differences.join(",");
}

function groupShiftedStrings(words) {
    const groups = new Map();

    for (const word of words) {
        const key = shiftedStringSignature(word);

        if (!groups.has(key)) {
            groups.set(key, []);
        }

        groups.get(key).push(word);
    }

    return [...groups.values()];
}

// -----------------------------------------------------------------------------
// Advanced equal-balance transformation
// -----------------------------------------------------------------------------

function longestEqualBinarySubarray(values) {
    const firstBalance = new Map([[0, -1]]);
    let balance = 0;
    let best = null;

    for (let index = 0; index < values.length; index += 1) {
        const value = values[index];

        if (value === 0) {
            balance -= 1;
        } else if (value === 1) {
            balance += 1;
        } else {
            throw new TypeError("Binary input must contain only 0 and 1.");
        }

        if (firstBalance.has(balance)) {
            const boundary = firstBalance.get(balance);
            const candidate = {
                length: index - boundary,
                start: boundary + 1,
                end: index,
            };

            if (best === null || candidate.length > best.length) {
                best = candidate;
            }
        } else {
            firstBalance.set(balance, index);
        }
    }

    return best;
}

// -----------------------------------------------------------------------------
// Event-driven hash analytics
// -----------------------------------------------------------------------------

class EventHashAnalyzer {
    #events;
    #frequency;
    #listeners;

    constructor(events = []) {
        this.#events = [];
        this.#frequency = new Map();
        this.#listeners = new Map();

        for (const event of events) {
            this.add(event);
        }
    }

    on(eventType, listener) {
        if (typeof listener !== "function") {
            throw new TypeError("listener must be a function");
        }

        if (!this.#listeners.has(eventType)) {
            this.#listeners.set(eventType, new Set());
        }

        this.#listeners.get(eventType).add(listener);

        return () => {
            this.#listeners.get(eventType)?.delete(listener);
        };
    }

    #emit(eventType, payload) {
        for (const listener of this.#listeners.get(eventType) ?? []) {
            listener(payload);
        }
    }

    add(event) {
        if (typeof event !== "string" || event.length === 0) {
            throw new TypeError("event must be a non-empty string");
        }

        this.#events.push(event);
        this.#frequency.set(
            event,
            (this.#frequency.get(event) ?? 0) + 1
        );

        this.#emit("added", {
            event,
            count: this.#frequency.get(event),
        });
    }

    frequency(event) {
        return this.#frequency.get(event) ?? 0;
    }

    topEvents(limit) {
        return [...this.#frequency.entries()]
            .sort((a, b) => {
                if (b[1] !== a[1]) {
                    return b[1] - a[1];
                }

                return a[0].localeCompare(b[0]);
            })
            .slice(0, limit);
    }
}

// -----------------------------------------------------------------------------
// Demonstration
// -----------------------------------------------------------------------------

function runDemo() {
    console.log("Advanced Hashing Problems");
    console.log("=========================");

    const numbers = [4, 7, 1, 9, 7, 4, 7];

    console.log("\nFrequency and uniqueness");
    console.log("frequency:", [...frequencyMap(numbers)]);
    console.log("duplicate:", containsDuplicate(numbers));
    console.log("first unique:", firstUniqueValue(numbers));
    console.log("top two:", topKFrequent(numbers, 2));
    console.log("majority:", majorityElement(numbers));

    console.log("\nPair-sum hashing");

    const pairValues = [2, 7, 11, 15, 7, 3];

    console.log("two sum:", twoSum(pairValues, 9));
    console.log("pair count:", countPairsWithSum(pairValues, 14));
    console.log("distinct pairs:", distinctValuePairs(pairValues, 10));

    console.log("\nPrefix-sum hashing");

    const values = [3, 4, -7, 2, 2, -2, 5, -5];

    console.log("has target sum 0:", hasSubarraySum(values, 0));
    console.log("count target sum 0:", countSubarraysWithSum(values, 0));
    console.log("longest target sum 0:", longestSubarrayWithSum(values, 0));
    console.log("longest target sum 5:", longestSubarrayWithSum(values, 5));

    console.log("\nModular prefix hashing");

    console.log(
        "subarrays divisible by 6:",
        countSubarraysDivisibleBy([23, 2, 4, 6, 7], 6)
    );

    console.log("\nGrouping");

    console.log(
        "anagrams:",
        groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    );

    console.log(
        "shifted strings:",
        groupShiftedStrings(["abc", "bcd", "acef", "xyz", "az", "ba"])
    );

    console.log("\nEqual binary counts");

    console.log(
        longestEqualBinarySubarray([0, 0, 1, 0, 0, 0, 1, 1])
    );

    console.log("\nEvent-driven frequency analyzer");

    const analyzer = new EventHashAnalyzer();

    const unsubscribe = analyzer.on("added", ({ event, count }) => {
        console.log(`event=${event}, currentFrequency=${count}`);
    });

    analyzer.add("login");
    analyzer.add("search");
    analyzer.add("login");
    analyzer.add("checkout");
    analyzer.add("login");

    unsubscribe();

    console.log("top events:", analyzer.topEvents(3));
}

runDemo();
