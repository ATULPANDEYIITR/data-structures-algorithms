/*
 * Hashing Introduction
 *
 * Demonstrates:
 * - Hash functions
 * - Hash tables
 * - Collisions
 * - Separate chaining
 * - Open addressing
 * - Linear probing
 * - Load factors
 * - Resizing
 * - JavaScript Map and Set
 * - Object identity versus value-based keys
 * - Frequency counting
 * - Two-sum
 * - Caching
 * - Performance and security considerations
 *
 * Run with:
 *   node hashing-introduction.js
 */

"use strict";

// ============================================================================
// 1. BASIC HASH FUNCTIONS
// ============================================================================

function integerHash(key, tableSize) {
    if (!Number.isInteger(tableSize) || tableSize <= 0) {
        throw new Error("tableSize must be a positive integer");
    }

    // JavaScript's % operator can return a negative value.
    return ((key % tableSize) + tableSize) % tableSize;
}

function stringHash(text, tableSize) {
    if (!Number.isInteger(tableSize) || tableSize <= 0) {
        throw new Error("tableSize must be a positive integer");
    }

    let hash = 0;
    const base = 31;

    for (const character of text) {
        hash = (hash * base + character.codePointAt(0)) % tableSize;
    }

    return hash;
}

function demonstrateBasicHashing() {
    console.log("\n=== BASIC HASHING ===");

    for (const key of [12, 25, 37, 41, 58]) {
        console.log(
            `key=${key} -> index=${integerHash(key, 10)}`
        );
    }

    for (const word of ["cat", "dog", "hash", "table", "javascript"]) {
        console.log(
            `text=${word} -> index=${stringHash(word, 10)}`
        );
    }
}


// ============================================================================
// 2. COLLISIONS
// ============================================================================

function demonstrateCollisions() {
    console.log("\n=== COLLISIONS ===");

    const tableSize = 5;
    const buckets = Array.from({ length: tableSize }, () => []);

    for (const key of [10, 15, 20, 7, 12]) {
        const index = integerHash(key, tableSize);
        buckets[index].push(key);
    }

    buckets.forEach((bucket, index) => {
        console.log(`bucket ${index}:`, bucket);
    });
}


// ============================================================================
// 3. SEPARATE CHAINING
// ============================================================================

class ChainedHashTable {
    constructor(capacity = 8) {
        if (!Number.isInteger(capacity) || capacity <= 0) {
            throw new Error("capacity must be positive");
        }

        this.buckets = Array.from({ length: capacity }, () => []);
        this.size = 0;
    }

    get capacity() {
        return this.buckets.length;
    }

    get loadFactor() {
        return this.size / this.capacity;
    }

    hash(key) {
        if (typeof key === "number") {
            return integerHash(key, this.capacity);
        }

        return stringHash(String(key), this.capacity);
    }

    put(key, value) {
        const index = this.hash(key);
        const bucket = this.buckets[index];

        const existing = bucket.find(entry => Object.is(entry.key, key));

        if (existing) {
            existing.value = value;
            return;
        }

        bucket.push({ key, value });
        this.size++;
    }

    get(key, defaultValue = undefined) {
        const index = this.hash(key);
        const entry = this.buckets[index]
            .find(item => Object.is(item.key, key));

        return entry ? entry.value : defaultValue;
    }

    has(key) {
        const index = this.hash(key);
        return this.buckets[index]
            .some(item => Object.is(item.key, key));
    }

    remove(key) {
        const index = this.hash(key);
        const bucket = this.buckets[index];

        const position = bucket.findIndex(
            item => Object.is(item.key, key)
        );

        if (position === -1) {
            throw new Error(`Key not found: ${String(key)}`);
        }

        const [removed] = bucket.splice(position, 1);
        this.size--;

        return removed.value;
    }

    resize(newCapacity) {
        const entries = [];

        for (const bucket of this.buckets) {
            entries.push(...bucket);
        }

        this.buckets = Array.from(
            { length: newCapacity },
            () => []
        );

        this.size = 0;

        for (const { key, value } of entries) {
            this.put(key, value);
        }
    }

    putWithResize(key, value) {
        this.put(key, value);

        if (this.loadFactor > 0.75) {
            this.resize(this.capacity * 2);
        }
    }

    entries() {
        const result = [];

        for (const bucket of this.buckets) {
            result.push(...bucket);
        }

        return result;
    }
}

function chainingDemo() {
    console.log("\n=== SEPARATE CHAINING ===");

    const table = new ChainedHashTable(4);

    for (const key of [0, 4, 8, 12]) {
        table.put(key, `value-${key}`);
    }

    console.log(
        "Bucket lengths:",
        table.buckets.map(bucket => bucket.length)
    );

    console.log("Lookup 8:", table.get(8));

    table.remove(8);

    console.log(
        "After removal:",
        table.buckets.map(bucket => bucket.length)
    );
}


// ============================================================================
// 4. OPEN ADDRESSING WITH LINEAR PROBING
// ============================================================================

const TOMBSTONE = Symbol("TOMBSTONE");

class OpenAddressingHashTable {
    constructor(capacity = 8) {
        if (!Number.isInteger(capacity) || capacity < 3) {
            throw new Error("capacity must be at least 3");
        }

        this.table = new Array(capacity).fill(null);
        this.size = 0;
    }

    get capacity() {
        return this.table.length;
    }

    get loadFactor() {
        return this.size / this.capacity;
    }

    hash(key) {
        if (typeof key === "number") {
            return integerHash(key, this.capacity);
        }

        return stringHash(String(key), this.capacity);
    }

    findSlot(key, forInsert) {
        const start = this.hash(key);
        let firstTombstone = -1;

        for (let attempt = 0; attempt < this.capacity; attempt++) {
            const index = (start + attempt) % this.capacity;
            const item = this.table[index];

            if (item === null) {
                if (forInsert) {
                    return firstTombstone >= 0
                        ? firstTombstone
                        : index;
                }

                return -1;
            }

            if (item === TOMBSTONE) {
                if (firstTombstone === -1) {
                    firstTombstone = index;
                }

                continue;
            }

            if (Object.is(item.key, key)) {
                return index;
            }
        }

        return forInsert ? firstTombstone : -1;
    }

    insertWithoutResize(key, value) {
        const index = this.findSlot(key, true);

        if (index === -1) {
            throw new Error("Hash table is full");
        }

        if (
            this.table[index] === null ||
            this.table[index] === TOMBSTONE
        ) {
            this.size++;
        }

        this.table[index] = { key, value };
    }

    resize(newCapacity) {
        const oldEntries = this.table.filter(
            item => item !== null && item !== TOMBSTONE
        );

        this.table = new Array(newCapacity).fill(null);
        this.size = 0;

        for (const entry of oldEntries) {
            this.insertWithoutResize(entry.key, entry.value);
        }
    }

    put(key, value) {
        // Open addressing generally needs a lower maximum load factor
        // than chaining because probe lengths increase as the table fills.
        if ((this.size + 1) / this.capacity > 0.70) {
            this.resize(this.capacity * 2);
        }

        this.insertWithoutResize(key, value);
    }

    get(key, defaultValue = undefined) {
        const index = this.findSlot(key, false);

        return index === -1
            ? defaultValue
            : this.table[index].value;
    }

    has(key) {
        return this.findSlot(key, false) !== -1;
    }

    remove(key) {
        const index = this.findSlot(key, false);

        if (index === -1) {
            throw new Error(`Key not found: ${String(key)}`);
        }

        const value = this.table[index].value;

        // A tombstone is necessary so a later lookup does not stop too early.
        this.table[index] = TOMBSTONE;
        this.size--;

        return value;
    }
}

function openAddressingDemo() {
    console.log("\n=== OPEN ADDRESSING ===");

    const table = new OpenAddressingHashTable(7);

    for (const key of [0, 7, 14, 21]) {
        table.put(key, `value-${key}`);
    }

    table.table.forEach((item, index) => {
        let description;

        if (item === null) {
            description = "EMPTY";
        } else if (item === TOMBSTONE) {
            description = "TOMBSTONE";
        } else {
            description = `${item.key} -> ${item.value}`;
        }

        console.log(`${index}: ${description}`);
    });

    console.log("Lookup 14:", table.get(14));

    table.remove(7);

    console.log("Lookup 14 after deleting 7:", table.get(14));
}


// ============================================================================
// 5. PROBING STRATEGIES
// ============================================================================

function linearProbe(start, attempt, capacity) {
    return (start + attempt) % capacity;
}

function quadraticProbe(start, attempt, capacity) {
    return (start + attempt * attempt) % capacity;
}

function doubleHashProbe(key, attempt, capacity, prime) {
    const firstHash = integerHash(key, capacity);
    const secondHash = prime - (key % prime);

    return (firstHash + attempt * secondHash) % capacity;
}

function probingDemo() {
    console.log("\n=== PROBING STRATEGIES ===");

    const capacity = 11;
    const key = 34;
    const start = integerHash(key, capacity);

    console.log(
        "Linear:",
        Array.from(
            { length: 6 },
            (_, i) => linearProbe(start, i, capacity)
        )
    );

    console.log(
        "Quadratic:",
        Array.from(
            { length: 6 },
            (_, i) => quadraticProbe(start, i, capacity)
        )
    );

    console.log(
        "Double hashing:",
        Array.from(
            { length: 6 },
            (_, i) => doubleHashProbe(key, i, capacity, 7)
        )
    );
}


// ============================================================================
// 6. LOAD FACTOR AND RESIZING
// ============================================================================

function loadFactorDemo() {
    console.log("\n=== LOAD FACTOR ===");

    for (const [size, capacity] of [
        [0, 10],
        [3, 10],
        [5, 10],
        [7, 10],
        [9, 10]
    ]) {
        console.log(
            `size=${size}, capacity=${capacity}, ` +
            `load factor=${(size / capacity).toFixed(2)}`
        );
    }
}


// ============================================================================
// 7. FREQUENCY COUNTING
// ============================================================================

function characterFrequency(text) {
    const frequencies = new Map();

    for (const character of text) {
        frequencies.set(
            character,
            (frequencies.get(character) ?? 0) + 1
        );
    }

    return frequencies;
}

function wordFrequency(text) {
    const frequencies = new Map();

    const words = text
        .toLowerCase()
        .split(/\s+/)
        .map(word => word.replace(/[^\p{L}\p{N}]/gu, ""))
        .filter(Boolean);

    for (const word of words) {
        frequencies.set(
            word,
            (frequencies.get(word) ?? 0) + 1
        );
    }

    return frequencies;
}

function frequencyDemo() {
    console.log("\n=== FREQUENCY COUNTING ===");

    console.log(
        "Characters:",
        Object.fromEntries(characterFrequency("banana"))
    );

    console.log(
        "Words:",
        Object.fromEntries(
            wordFrequency(
                "Hash tables make fast lookup possible and hash tables count data"
            )
        )
    );
}


// ============================================================================
// 8. TWO-SUM
// ============================================================================

function twoSum(values, target) {
    const positions = new Map();

    for (let index = 0; index < values.length; index++) {
        const value = values[index];
        const needed = target - value;

        if (positions.has(needed)) {
            return [positions.get(needed), index];
        }

        positions.set(value, index);
    }

    return null;
}

function twoSumDemo() {
    console.log("\n=== TWO-SUM ===");

    const values = [4, 9, 1, 7, 5, 3];
    const target = 12;

    const result = twoSum(values, target);

    console.log("Values:", values);
    console.log("Target:", target);
    console.log("Result:", result);

    if (result) {
        const [first, second] = result;

        console.log(
            `Verification: ${values[first]} + ${values[second]} = ${target}`
        );
    }
}


// ============================================================================
// 9. SET-BASED DEDUPLICATION
// ============================================================================

function deduplicate(values) {
    return [...new Set(values)];
}

function deduplicationDemo() {
    console.log("\n=== SET AND HASH-BASED DEDUPLICATION ===");

    const values = [4, 2, 4, 1, 2, 8, 1, 9];

    console.log("Input:", values);
    console.log("Unique:", deduplicate(values));
}


// ============================================================================
// 10. JAVASCRIPT MAP AND SET SEMANTICS
// ============================================================================

function nativeMapSetDemo() {
    console.log("\n=== NATIVE MAP AND SET ===");

    const map = new Map();

    map.set("user:1", {
        name: "Alice",
        role: "admin"
    });

    map.set("user:2", {
        name: "Bob",
        role: "analyst"
    });

    console.log("Map lookup:", map.get("user:1"));

    const set = new Set([1, 2, 2, 3, 3, 3]);

    console.log("Set contents:", [...set]);

    // JavaScript Map supports object keys by object identity.
    const firstObject = { id: 1 };
    const secondObject = { id: 1 };

    const objectMap = new Map();
    objectMap.set(firstObject, "first");

    console.log(
        "Same object lookup:",
        objectMap.get(firstObject)
    );

    console.log(
        "Equivalent-looking but different object:",
        objectMap.get(secondObject)
    );

    console.log(
        "Object identity comparison:",
        firstObject === secondObject
    );
}


// ============================================================================
// 11. CACHE
// ============================================================================

class SimpleCache {
    constructor(maxItems) {
        if (!Number.isInteger(maxItems) || maxItems <= 0) {
            throw new Error("maxItems must be positive");
        }

        this.maxItems = maxItems;
        this.data = new Map();
    }

    get(key) {
        return this.data.get(key);
    }

    set(key, value) {
        if (
            !this.data.has(key) &&
            this.data.size >= this.maxItems
        ) {
            const oldestKey = this.data.keys().next().value;
            this.data.delete(oldestKey);
        }

        this.data.set(key, value);
    }

    has(key) {
        return this.data.has(key);
    }
}

function cacheDemo() {
    console.log("\n=== SIMPLE HASH-BASED CACHE ===");

    const cache = new SimpleCache(3);

    cache.set("user:1", { name: "Alice" });
    cache.set("user:2", { name: "Bob" });
    cache.set("user:3", { name: "Carol" });

    console.log("user:2:", cache.get("user:2"));

    cache.set("user:4", { name: "David" });

    console.log("user:1 cached:", cache.has("user:1"));
    console.log("user:4 cached:", cache.has("user:4"));
}


// ============================================================================
// 12. ASYNCHRONOUS APPLICATION EXAMPLE
// ============================================================================

function delay(milliseconds) {
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

const requestCache = new Map();

async function fetchUserSimulated(userId) {
    if (requestCache.has(userId)) {
        return {
            source: "cache",
            user: requestCache.get(userId)
        };
    }

    // Simulate asynchronous I/O.
    await delay(20);

    const user = {
        id: userId,
        name: `User ${userId}`
    };

    requestCache.set(userId, user);

    return {
        source: "simulated network",
        user
    };
}

async function asyncCacheDemo() {
    console.log("\n=== ASYNCHRONOUS CACHE ===");

    console.log(await fetchUserSimulated(101));
    console.log(await fetchUserSimulated(101));
}


// ============================================================================
// 13. ERROR HANDLING
// ============================================================================

function errorHandlingDemo() {
    console.log("\n=== ERROR HANDLING ===");

    try {
        integerHash(10, 0);
    } catch (error) {
        console.log("Expected validation error:", error.message);
    }

    try {
        const table = new OpenAddressingHashTable(3);
        table.remove("missing");
    } catch (error) {
        console.log("Expected lookup error:", error.message);
    }
}


// ============================================================================
// 14. PERFORMANCE EXPERIMENT
// ============================================================================

function performanceDemo() {
    console.log("\n=== PERFORMANCE EXPERIMENT ===");

    const itemCount = 100_000;
    const lookupCount = 50_000;

    const map = new Map();

    for (let i = 0; i < itemCount; i++) {
        map.set(i, i * 2);
    }

    let checksum = 0;

    const start = performance.now();

    for (let i = 0; i < lookupCount; i++) {
        checksum += map.get(i % itemCount);
    }

    const elapsed = performance.now() - start;

    console.log("Checksum:", checksum);
    console.log(`Lookup time: ${elapsed.toFixed(3)} ms`);

    console.log(
        "This benchmark is illustrative. JavaScript engine, hardware, " +
        "key distribution, and runtime optimization affect actual results."
    );
}


// ============================================================================
// 15. SECURITY CONSIDERATIONS
// ============================================================================

function securityDemo() {
    console.log("\n=== SECURITY CONSIDERATIONS ===");

    console.log(
        "Hash-table collision behavior can matter in attacker-controlled " +
        "input. Production systems should rely on mature runtime and " +
        "library implementations rather than assuming that a simple custom " +
        "hash is resistant to adversarial input."
    );

    console.log(
        "Cryptographic hashing and hash-table indexing solve different problems."
    );
}


// ============================================================================
// 16. SELF-TESTS
// ============================================================================

function runTests() {
    console.log("\n=== SELF-TESTS ===");

    const chained = new ChainedHashTable(4);

    chained.put("a", 1);
    console.assert(chained.get("a") === 1);
    chained.put("a", 2);
    console.assert(chained.get("a") === 2);
    console.assert(chained.has("a"));

    chained.remove("a");
    console.assert(!chained.has("a"));

    const open = new OpenAddressingHashTable(5);

    open.put(1, 10);
    open.put(6, 60);
    open.put(11, 110);

    console.assert(open.get(11) === 110);

    open.remove(6);

    console.assert(open.get(11) === 110);

    console.assert(
        JSON.stringify(twoSum([2, 7, 11, 15], 9)) ===
        JSON.stringify([0, 1])
    );

    console.assert(
        JSON.stringify(deduplicate([1, 2, 1, 3, 2])) ===
        JSON.stringify([1, 2, 3])
    );

    console.log("All tests passed.");
}


// ============================================================================
// MAIN
// ============================================================================

async function main() {
    console.log("=".repeat(78));
    console.log("HASHING INTRODUCTION: COMPLETE JAVASCRIPT STUDY");
    console.log("=".repeat(78));

    demonstrateBasicHashing();
    demonstrateCollisions();
    chainingDemo();
    openAddressingDemo();
    probingDemo();
    loadFactorDemo();
    frequencyDemo();
    twoSumDemo();
    deduplicationDemo();
    nativeMapSetDemo();
    cacheDemo();
    await asyncCacheDemo();
    errorHandlingDemo();
    performanceDemo();
    securityDemo();
    runTests();

    console.log("\n=== STUDY COMPLETE ===");
}

main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
