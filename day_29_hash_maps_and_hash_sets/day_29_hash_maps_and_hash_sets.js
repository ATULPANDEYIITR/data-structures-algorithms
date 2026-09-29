"use strict";

/*
 * Hash Maps and Hash Sets
 * =======================
 *
 * This executable JavaScript study file demonstrates:
 * - Map and Set fundamentals
 * - Lookup, insertion, deletion
 * - Frequency counting
 * - Duplicate detection
 * - Set algebra
 * - Grouping and indexing
 * - Two-sum and related algorithms
 * - Object versus Map
 * - Hash-like data structures
 * - Custom key behavior
 * - Caching
 * - Graph representation
 * - Validation
 * - Performance considerations
 * - Error handling and edge cases
 *
 * The file requires no external packages.
 */

// ============================================================================
// 1. BASIC MAP OPERATIONS
// ============================================================================

function demonstrateMapBasics() {
    console.log("\n=== 1. JavaScript Map Basics ===");

    const student = new Map([
        ["name", "Atul"],
        ["age", 30],
        ["department", "Computer Science"]
    ]);

    console.log("Name:", student.get("name"));
    console.log("Missing city:", student.get("city"));

    // Map.set() inserts or replaces a key/value pair.
    student.set("city", "Lucknow");
    student.set("age", 31);

    console.log("Updated map:", [...student.entries()]);

    console.log("Contains name:", student.has("name"));

    // Map.delete() removes one key.
    student.delete("city");

    console.log("After deletion:", [...student.entries()]);
    console.log("Map size:", student.size);

    // Map.clear() removes all entries.
    const temporaryMap = new Map([["a", 1], ["b", 2]]);
    temporaryMap.clear();
    console.log("Cleared map size:", temporaryMap.size);
}


// ============================================================================
// 2. MAP ITERATION
// ============================================================================

function demonstrateMapIteration() {
    console.log("\n=== 2. Map Iteration ===");

    const prices = new Map([
        ["apple", 120],
        ["banana", 60],
        ["orange", 90]
    ]);

    console.log("Keys:");
    for (const product of prices.keys()) {
        console.log(" ", product);
    }

    console.log("Values:");
    for (const price of prices.values()) {
        console.log(" ", price);
    }

    console.log("Entries:");
    for (const [product, price] of prices.entries()) {
        console.log(`  ${product}: ${price}`);
    }

    // Map preserves insertion order during iteration.
    console.log("Entries as array:", [...prices]);
}


// ============================================================================
// 3. OBJECT VERSUS MAP
// ============================================================================

function demonstrateObjectVsMap() {
    console.log("\n=== 3. Object Versus Map ===");

    const objectMap = {
        name: "Atul",
        age: 30
    };

    const realMap = new Map([
        ["name", "Atul"],
        ["age", 30]
    ]);

    console.log("Object property:", objectMap.name);
    console.log("Map value:", realMap.get("name"));

    // Map supports arbitrary key types without converting them to strings.
    const objectKey = { id: 1 };

    realMap.set(objectKey, "metadata");
    console.log("Object key lookup:", realMap.get(objectKey));

    // A different object with the same fields is a different identity.
    console.log(
        "Equivalent-looking object is same key:",
        realMap.has({ id: 1 })
    );

    /*
     * Map is generally preferable when:
     * - keys are dynamic,
     * - keys are not limited to strings/symbols,
     * - frequent insertion/deletion is required,
     * - explicit map semantics are desirable.
     *
     * Plain objects remain useful for record-like data with known fields.
     */
}


// ============================================================================
// 4. SET FUNDAMENTALS
// ============================================================================

function demonstrateSetBasics() {
    console.log("\n=== 4. Set Basics ===");

    const skills = new Set(["Python", "SQL", "Git", "Python"]);

    console.log("Duplicate automatically removed:", [...skills]);

    skills.add("C++");
    console.log("After add:", [...skills]);

    console.log("Contains SQL:", skills.has("SQL"));

    skills.delete("Git");
    console.log("After delete:", [...skills]);

    skills.clear();
    console.log("After clear:", [...skills]);
}


// ============================================================================
// 5. SET OPERATIONS
// ============================================================================

function union(first, second) {
    return new Set([...first, ...second]);
}

function intersection(first, second) {
    return new Set([...first].filter(value => second.has(value)));
}

function difference(first, second) {
    return new Set([...first].filter(value => !second.has(value)));
}

function symmetricDifference(first, second) {
    return new Set([
        ...difference(first, second),
        ...difference(second, first)
    ]);
}

function isSubset(subset, superset) {
    for (const value of subset) {
        if (!superset.has(value)) {
            return false;
        }
    }

    return true;
}

function demonstrateSetOperations() {
    console.log("\n=== 5. Set Algebra ===");

    const engineers = new Set(["Python", "C++", "SQL", "Git"]);
    const analysts = new Set(["Python", "SQL", "Excel", "Power BI"]);

    console.log("Union:", [...union(engineers, analysts)]);
    console.log("Intersection:", [...intersection(engineers, analysts)]);
    console.log("Engineers only:", [...difference(engineers, analysts)]);
    console.log("Analysts only:", [...difference(analysts, engineers)]);
    console.log(
        "Symmetric difference:",
        [...symmetricDifference(engineers, analysts)]
    );

    const combined = union(engineers, analysts);
    console.log("Engineers subset of union:", isSubset(engineers, combined));
}


// ============================================================================
// 6. FREQUENCY COUNTING
// ============================================================================

function frequencyCount(values) {
    const counts = new Map();

    for (const value of values) {
        counts.set(value, (counts.get(value) ?? 0) + 1);
    }

    return counts;
}

function demonstrateFrequencyCounting() {
    console.log("\n=== 6. Frequency Counting ===");

    const words = [
        "python",
        "hash",
        "map",
        "python",
        "set",
        "hash",
        "python"
    ];

    const counts = frequencyCount(words);

    console.log("Frequency map:", [...counts.entries()]);
    console.log("Python count:", counts.get("python"));
}


// ============================================================================
// 7. DUPLICATE DETECTION
// ============================================================================

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

function duplicateValues(values) {
    const seen = new Set();
    const duplicates = new Set();

    for (const value of values) {
        if (seen.has(value)) {
            duplicates.add(value);
        } else {
            seen.add(value);
        }
    }

    return duplicates;
}

function demonstrateDuplicateDetection() {
    console.log("\n=== 7. Duplicate Detection ===");

    const values = [10, 20, 30, 20, 40, 10];

    console.log("Contains duplicate:", containsDuplicate(values));
    console.log("Duplicate values:", [...duplicateValues(values)]);
}


// ============================================================================
// 8. TWO-SUM
// ============================================================================

function twoSum(numbers, target) {
    const seen = new Map();

    for (let index = 0; index < numbers.length; index++) {
        const number = numbers[index];
        const complement = target - number;

        if (seen.has(complement)) {
            return [seen.get(complement), index];
        }

        seen.set(number, index);
    }

    return null;
}

function demonstrateTwoSum() {
    console.log("\n=== 8. Two-Sum ===");

    const numbers = [2, 7, 11, 15];

    console.log(
        "Result:",
        twoSum(numbers, 9)
    );

    console.log(
        "No solution:",
        twoSum([1, 2, 3], 100)
    );
}


// ============================================================================
// 9. FIRST NON-REPEATING CHARACTER
// ============================================================================

function firstNonRepeatingCharacter(text) {
    const counts = frequencyCount([...text]);

    for (const character of text) {
        if (counts.get(character) === 1) {
            return character;
        }
    }

    return null;
}

function demonstrateFirstNonRepeating() {
    console.log("\n=== 9. First Non-Repeating Character ===");

    for (const text of ["swiss", "aabbcc", "python"]) {
        console.log(
            `${text} -> ${firstNonRepeatingCharacter(text)}`
        );
    }
}


// ============================================================================
// 10. ANAGRAM DETECTION
// ============================================================================

function mapsAreEqual(first, second) {
    if (first.size !== second.size) {
        return false;
    }

    for (const [key, value] of first) {
        if (second.get(key) !== value) {
            return false;
        }
    }

    return true;
}

function areAnagrams(first, second) {
    return mapsAreEqual(
        frequencyCount([...first]),
        frequencyCount([...second])
    );
}

function demonstrateAnagrams() {
    console.log("\n=== 10. Anagram Detection ===");

    console.log("listen / silent:", areAnagrams("listen", "silent"));
    console.log("hello / world:", areAnagrams("hello", "world"));
}


// ============================================================================
// 11. GROUPING RECORDS
// ============================================================================

function groupTransactionsByCustomer(transactions) {
    const groups = new Map();

    for (const transaction of transactions) {
        const { customer, amount } = transaction;

        if (!groups.has(customer)) {
            groups.set(customer, []);
        }

        groups.get(customer).push(amount);
    }

    return groups;
}

function demonstrateGrouping() {
    console.log("\n=== 11. Grouping Records ===");

    const transactions = [
        { customer: "C001", amount: 1200 },
        { customer: "C002", amount: 800 },
        { customer: "C001", amount: 450 },
        { customer: "C003", amount: 2100 },
        { customer: "C002", amount: 300 }
    ];

    const grouped = groupTransactionsByCustomer(transactions);

    for (const [customer, amounts] of grouped) {
        const total = amounts.reduce((sum, amount) => sum + amount, 0);

        console.log(customer, "->", amounts, "total =", total);
    }
}


// ============================================================================
// 12. DATA CLEANING
// ============================================================================

function normalizeEmails(emails) {
    const normalized = new Set();

    for (const email of emails) {
        const cleaned = email.trim().toLowerCase();

        if (cleaned !== "") {
            normalized.add(cleaned);
        }
    }

    return normalized;
}

function demonstrateDataCleaning() {
    console.log("\n=== 12. Data Cleaning ===");

    const emails = [
        " ATUL@example.com ",
        "atul@example.com",
        "ADMIN@example.com",
        "",
        "admin@example.com"
    ];

    console.log([...normalizeEmails(emails)]);
}


// ============================================================================
// 13. CACHE
// ============================================================================

class SimpleCache {
    constructor(capacity) {
        if (!Number.isInteger(capacity) || capacity <= 0) {
            throw new RangeError("Cache capacity must be positive.");
        }

        this.capacity = capacity;
        this.data = new Map();
    }

    get(key) {
        if (!this.data.has(key)) {
            return undefined;
        }

        const value = this.data.get(key);

        // Reinsert to implement a simple LRU-like behavior.
        this.data.delete(key);
        this.data.set(key, value);

        return value;
    }

    set(key, value) {
        if (this.data.has(key)) {
            this.data.delete(key);
        }

        this.data.set(key, value);

        if (this.data.size > this.capacity) {
            const oldestKey = this.data.keys().next().value;
            this.data.delete(oldestKey);
        }
    }

    size() {
        return this.data.size;
    }
}

function demonstrateCache() {
    console.log("\n=== 13. Map-Based Cache ===");

    const cache = new SimpleCache(2);

    cache.set("user:101", { name: "Atul" });
    cache.set("user:102", { name: "Priya" });

    console.log("User 101:", cache.get("user:101"));

    cache.set("user:103", { name: "Rahul" });

    console.log("User 102 after eviction:", cache.get("user:102"));
    console.log("Cache size:", cache.size());
}


// ============================================================================
// 14. GRAPH REPRESENTATION
// ============================================================================

function buildGraph(edges) {
    const graph = new Map();

    for (const [source, destination] of edges) {
        if (!graph.has(source)) {
            graph.set(source, new Set());
        }

        if (!graph.has(destination)) {
            graph.set(destination, new Set());
        }

        graph.get(source).add(destination);
    }

    return graph;
}

function demonstrateGraph() {
    console.log("\n=== 14. Graph with Map and Set ===");

    const edges = [
        ["A", "B"],
        ["A", "C"],
        ["B", "D"],
        ["C", "D"]
    ];

    const graph = buildGraph(edges);

    for (const [node, neighbors] of graph) {
        console.log(node, "->", [...neighbors]);
    }
}


// ============================================================================
// 15. SET-BASED VALIDATION
// ============================================================================

function validateUniqueIds(ids) {
    const seen = new Set();
    const duplicates = new Set();

    for (const id of ids) {
        if (typeof id !== "string" || id.trim() === "") {
            throw new TypeError("Every ID must be a non-empty string.");
        }

        if (seen.has(id)) {
            duplicates.add(id);
        }

        seen.add(id);
    }

    return {
        valid: duplicates.size === 0,
        duplicates
    };
}

function demonstrateValidation() {
    console.log("\n=== 15. Set-Based Validation ===");

    const result = validateUniqueIds([
        "A100",
        "A101",
        "A102",
        "A101"
    ]);

    console.log("Valid:", result.valid);
    console.log("Duplicates:", [...result.duplicates]);

    try {
        validateUniqueIds(["A100", ""]);
    } catch (error) {
        console.log("Validation error:", error.message);
    }
}


// ============================================================================
// 16. MULTIPLE TWO-SUM PAIRS
// ============================================================================

function allTwoSumPairs(numbers, target) {
    const seen = new Map();
    const results = [];

    for (let index = 0; index < numbers.length; index++) {
        const number = numbers[index];
        const complement = target - number;

        if (seen.has(complement)) {
            for (const previousIndex of seen.get(complement)) {
                results.push([previousIndex, index]);
            }
        }

        if (!seen.has(number)) {
            seen.set(number, []);
        }

        seen.get(number).push(index);
    }

    return results;
}

function demonstrateAllTwoSumPairs() {
    console.log("\n=== 16. Multiple Two-Sum Pairs ===");

    console.log(
        allTwoSumPairs([2, 7, 2, 7, 4], 9)
    );
}


// ============================================================================
// 17. OBJECT KEY COERCION EDGE CASE
// ============================================================================

function demonstrateObjectKeyEdgeCase() {
    console.log("\n=== 17. Object Key Coercion Edge Case ===");

    const object = {};

    object[1] = "number key";
    object["1"] = "string key";

    // Plain object property keys are converted to strings in this example.
    console.log("Object:", object);
    console.log("Object key 1:", object[1]);

    const map = new Map();

    map.set(1, "number key");
    map.set("1", "string key");

    // Map distinguishes the two keys.
    console.log("Map numeric key:", map.get(1));
    console.log("Map string key:", map.get("1"));
}


// ============================================================================
// 18. SPECIAL VALUES
// ============================================================================

function demonstrateSpecialValues() {
    console.log("\n=== 18. Special Values ===");

    const map = new Map();

    map.set(NaN, "not-a-number");

    // Map uses SameValueZero-style equality, so NaN can be found by NaN.
    console.log("NaN lookup:", map.get(NaN));

    const set = new Set([NaN, NaN, 0, -0]);

    console.log("Special-value set size:", set.size);
    console.log("Set contains NaN:", set.has(NaN));
    console.log("Set contains -0:", set.has(-0));
}


// ============================================================================
// 19. FREQUENCY-BASED TOP VALUES
// ============================================================================

function topFrequentValues(values, limit) {
    if (!Number.isInteger(limit) || limit < 0) {
        throw new RangeError("Limit must be a non-negative integer.");
    }

    const counts = frequencyCount(values);

    return [...counts.entries()]
        .sort((a, b) => {
            if (b[1] !== a[1]) {
                return b[1] - a[1];
            }

            return String(a[0]).localeCompare(String(b[0]));
        })
        .slice(0, limit);
}

function demonstrateTopFrequency() {
    console.log("\n=== 19. Top Frequent Values ===");

    console.log(
        topFrequentValues(
            ["a", "b", "a", "c", "b", "a", "d", "c"],
            3
        )
    );
}


// ============================================================================
// 20. PERFORMANCE DEMONSTRATION
// ============================================================================

function measureMembershipPerformance(size = 100000) {
    console.log("\n=== 20. Membership Performance ===");

    const values = Array.from(
        { length: size },
        (_, index) => index
    );

    const valueSet = new Set(values);
    const target = size - 1;

    const listStart = performance.now();
    values.includes(target);
    const listElapsed = performance.now() - listStart;

    const setStart = performance.now();
    valueSet.has(target);
    const setElapsed = performance.now() - setStart;

    console.log(
        `Array membership: ${listElapsed.toFixed(6)} ms`
    );

    console.log(
        `Set membership:   ${setElapsed.toFixed(6)} ms`
    );

    /*
     * Array.includes() is O(n).
     * Set.has() is expected O(1) average.
     *
     * Exact timings vary with runtime, hardware, JIT optimization,
     * cache behavior, and workload.
     */
}


// ============================================================================
// 21. INVENTORY CASE STUDY
// ============================================================================

class Inventory {
    constructor() {
        this.stock = new Map();
    }

    addProduct(productId, quantity) {
        if (typeof productId !== "string" || productId.trim() === "") {
            throw new TypeError("Product ID must be non-empty.");
        }

        if (!Number.isInteger(quantity) || quantity < 0) {
            throw new RangeError("Quantity must be a non-negative integer.");
        }

        const current = this.stock.get(productId) ?? 0;
        this.stock.set(productId, current + quantity);
    }

    removeProduct(productId, quantity) {
        if (!Number.isInteger(quantity) || quantity <= 0) {
            throw new RangeError(
                "Removal quantity must be a positive integer."
            );
        }

        if (!this.stock.has(productId)) {
            throw new Error(`Unknown product: ${productId}`);
        }

        const current = this.stock.get(productId);

        if (quantity > current) {
            throw new Error("Insufficient stock.");
        }

        const remaining = current - quantity;

        if (remaining === 0) {
            this.stock.delete(productId);
        } else {
            this.stock.set(productId, remaining);
        }
    }

    quantity(productId) {
        return this.stock.get(productId) ?? 0;
    }

    snapshot() {
        return Object.fromEntries(this.stock);
    }
}

function demonstrateInventory() {
    console.log("\n=== 21. Inventory Case ===");

    const inventory = new Inventory();

    inventory.addProduct("LAPTOP", 10);
    inventory.addProduct("MOUSE", 25);
    inventory.addProduct("LAPTOP", 5);

    console.log("Inventory:", inventory.snapshot());

    inventory.removeProduct("MOUSE", 5);

    console.log("After removal:", inventory.snapshot());

    try {
        inventory.removeProduct("MOUSE", 100);
    } catch (error) {
        console.log("Inventory error:", error.message);
    }
}


// ============================================================================
// 22. TESTS
// ============================================================================

function runTests() {
    console.log("\n=== 22. Self-Tests ===");

    const counts = frequencyCount("banana".split(""));
    console.assert(counts.get("b") === 1);
    console.assert(counts.get("a") === 3);
    console.assert(counts.get("n") === 2);

    console.assert(containsDuplicate([1, 2, 3, 1]));
    console.assert(!containsDuplicate([1, 2, 3]));

    console.assert(areAnagrams("listen", "silent"));
    console.assert(!areAnagrams("listen", "python"));

    const pair = twoSum([2, 7, 11, 15], 9);
    console.assert(pair[0] === 0 && pair[1] === 1);

    const customSet = new Set([1, 2, 3]);
    console.assert(customSet.has(2));

    const map = new Map();
    map.set("a", 1);
    map.set("a", 10);
    console.assert(map.get("a") === 10);

    console.log("All tests passed.");
}


// ============================================================================
// 23. MAIN
// ============================================================================

function main() {
    console.log("HASH MAPS AND HASH SETS");
    console.log("Executable JavaScript study guide.");

    demonstrateMapBasics();
    demonstrateMapIteration();
    demonstrateObjectVsMap();
    demonstrateSetBasics();
    demonstrateSetOperations();
    demonstrateFrequencyCounting();
    demonstrateDuplicateDetection();
    demonstrateTwoSum();
    demonstrateFirstNonRepeating();
    demonstrateAnagrams();
    demonstrateGrouping();
    demonstrateDataCleaning();
    demonstrateCache();
    demonstrateGraph();
    demonstrateValidation();
    demonstrateAllTwoSumPairs();
    demonstrateObjectKeyEdgeCase();
    demonstrateSpecialValues();
    demonstrateTopFrequency();
    measureMembershipPerformance();
    demonstrateInventory();
    runTests();
}

main();
