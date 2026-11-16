"use strict";

/*
 * Advanced Trie Engineering
 *
 * Components:
 * 1. Compressed radix trie.
 * 2. Binary XOR trie.
 * 3. Event-driven dictionary service.
 * 4. Streaming maximum XOR pair processor.
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only.
 */

const { EventEmitter } = require("node:events");
const { performance } = require("node:perf_hooks");

// ============================================================
// 1. COMPRESSED RADIX TRIE
// ============================================================

class RadixNode {
    constructor(edge = "", terminal = false, value = null) {
        this.edge = edge;
        this.terminal = terminal;
        this.value = value;
        this.children = new Map();
    }
}

class RadixTrie {
    constructor() {
        this.root = new RadixNode();
        this.size = 0;
    }

    commonPrefix(a, b) {
        let i = 0;

        while (
            i < a.length &&
            i < b.length &&
            a[i] === b[i]
        ) {
            i++;
        }

        return i;
    }

    validateWord(word) {
        if (typeof word !== "string" || word.length === 0) {
            throw new TypeError("A non-empty string is required.");
        }
    }

    insert(word, value = word) {
        this.validateWord(word);

        let node = this.root;
        let remaining = word;

        while (remaining.length > 0) {
            const first = remaining[0];
            let child = node.children.get(first);

            if (!child) {
                child = new RadixNode(remaining, true, value);
                node.children.set(first, child);
                this.size++;
                return true;
            }

            const common = this.commonPrefix(
                remaining,
                child.edge
            );

            if (common === child.edge.length) {
                remaining = remaining.slice(common);
                node = child;

                if (remaining.length === 0) {
                    if (node.terminal) {
                        node.value = value;
                        return false;
                    }

                    node.terminal = true;
                    node.value = value;
                    this.size++;
                    return true;
                }

                continue;
            }

            const intermediate = new RadixNode(
                child.edge.slice(0, common)
            );

            child.edge = child.edge.slice(common);

            intermediate.children.set(child.edge[0], child);
            node.children.set(first, intermediate);

            remaining = remaining.slice(common);

            if (remaining.length === 0) {
                intermediate.terminal = true;
                intermediate.value = value;
            } else {
                const newChild = new RadixNode(
                    remaining,
                    true,
                    value
                );

                intermediate.children.set(remaining[0], newChild);
            }

            this.size++;
            return true;
        }

        return false;
    }

    search(word) {
        if (typeof word !== "string" || word.length === 0) {
            return false;
        }

        let node = this.root;
        let remaining = word;

        while (remaining.length > 0) {
            const child = node.children.get(remaining[0]);

            if (!child || !remaining.startsWith(child.edge)) {
                return false;
            }

            remaining = remaining.slice(child.edge.length);
            node = child;
        }

        return node.terminal;
    }

    startsWith(prefix) {
        if (typeof prefix !== "string" || prefix.length === 0) {
            return false;
        }

        let node = this.root;
        let remaining = prefix;

        while (remaining.length > 0) {
            const child = node.children.get(remaining[0]);

            if (!child) {
                return false;
            }

            const common = this.commonPrefix(
                remaining,
                child.edge
            );

            if (common === remaining.length) {
                return true;
            }

            if (common !== child.edge.length) {
                return false;
            }

            remaining = remaining.slice(common);
            node = child;
        }

        return true;
    }

    autocomplete(prefix, limit = 10) {
        if (!Number.isInteger(limit) || limit < 0) {
            throw new RangeError("Limit must be a non-negative integer.");
        }

        if (limit === 0) return [];

        let node = this.root;
        let remaining = prefix;
        let accumulated = "";

        while (remaining.length > 0) {
            const child = node.children.get(remaining[0]);

            if (!child) return [];

            const common = this.commonPrefix(
                remaining,
                child.edge
            );

            if (common < remaining.length &&
                common < child.edge.length) {
                return [];
            }

            accumulated += child.edge;
            remaining = remaining.slice(common);
            node = child;
        }

        const results = [];

        const collect = (current, word) => {
            if (results.length >= limit) return;

            if (current.terminal) {
                results.push({
                    word,
                    value: current.value
                });
            }

            const keys = [...current.children.keys()].sort();

            for (const key of keys) {
                const child = current.children.get(key);

                collect(child, word + child.edge);

                if (results.length >= limit) break;
            }
        };

        collect(node, accumulated);
        return results;
    }

    delete(word) {
        if (!this.search(word)) return false;

        const remove = (node, remaining) => {
            const child = node.children.get(remaining[0]);
            const suffix = remaining.slice(child.edge.length);

            if (suffix.length > 0) {
                remove(child, suffix);
            } else {
                child.terminal = false;
                child.value = null;
            }

            if (!child.terminal && child.children.size === 0) {
                node.children.delete(child.edge[0]);
            } else if (
                !child.terminal &&
                child.children.size === 1
            ) {
                const next = child.children.values().next().value;

                child.edge += next.edge;
                child.children = next.children;
                child.terminal = next.terminal;
                child.value = next.value;
            }
        };

        remove(this.root, word);
        this.size--;

        return true;
    }
}


// ============================================================
// 2. BINARY XOR TRIE USING BIGINT
// ============================================================

class BinaryTrie {
    constructor(width = 32) {
        if (!Number.isInteger(width) || width < 1 || width > 64) {
            throw new RangeError("Width must be between 1 and 64.");
        }

        this.width = width;
        this.mask = (1n << BigInt(width)) - 1n;
        this.root = this.createNode();
        this.size = 0;
    }

    createNode() {
        return {
            children: [null, null],
            count: 0
        };
    }

    validate(number) {
        if (typeof number !== "bigint") {
            throw new TypeError("Binary trie values must be BigInt.");
        }

        if (number < 0n || number > this.mask) {
            throw new RangeError("Number exceeds configured bit width.");
        }
    }

    insert(number) {
        this.validate(number);

        let node = this.root;
        node.count++;

        for (let i = this.width - 1; i >= 0; i--) {
            const bit = Number((number >> BigInt(i)) & 1n);

            if (!node.children[bit]) {
                node.children[bit] = this.createNode();
            }

            node = node.children[bit];
            node.count++;
        }

        this.size++;
    }

    contains(number) {
        this.validate(number);

        let node = this.root;

        for (let i = this.width - 1; i >= 0; i--) {
            const bit = Number((number >> BigInt(i)) & 1n);
            node = node.children[bit];

            if (!node || node.count === 0) return false;
        }

        return true;
    }

    delete(number) {
        this.validate(number);

        if (!this.contains(number)) return false;

        let node = this.root;
        node.count--;

        for (let i = this.width - 1; i >= 0; i--) {
            const bit = Number((number >> BigInt(i)) & 1n);
            const child = node.children[bit];

            child.count--;

            if (child.count === 0) {
                node.children[bit] = null;
                break;
            }

            node = child;
        }

        this.size--;
        return true;
    }

    query(number, maximize = true) {
        this.validate(number);

        if (this.size === 0) {
            throw new Error("Cannot query an empty trie.");
        }

        let node = this.root;
        let matched = 0n;
        let xor = 0n;

        for (let i = this.width - 1; i >= 0; i--) {
            const bit = Number((number >> BigInt(i)) & 1n);

            const preferred = maximize ? 1 - bit : bit;
            const alternative = 1 - preferred;

            let chosen;

            if (
                node.children[preferred] &&
                node.children[preferred].count > 0
            ) {
                chosen = preferred;
            } else {
                chosen = alternative;
            }

            if (chosen !== bit) {
                xor |= 1n << BigInt(i);
            }

            matched |= BigInt(chosen) << BigInt(i);
            node = node.children[chosen];
        }

        return { xor, matched };
    }
}


// ============================================================
// 3. STREAMING MAXIMUM XOR PROCESSOR
// ============================================================

class XORStreamProcessor extends EventEmitter {
    constructor(width = 32) {
        super();

        this.trie = new BinaryTrie(width);
        this.best = -1n;
        this.bestPair = null;
        this.processed = 0;
    }

    add(number) {
        this.trie.validate(number);

        let result = null;

        if (this.trie.size > 0) {
            result = this.trie.query(number, true);

            if (result.xor > this.best) {
                this.best = result.xor;
                this.bestPair = [number, result.matched];

                this.emit("maximum", {
                    xor: this.best,
                    pair: [...this.bestPair]
                });
            }
        }

        this.trie.insert(number);
        this.processed++;

        this.emit("inserted", {
            number,
            count: this.processed
        });

        return result;
    }

    getReport() {
        return {
            processed: this.processed,
            maximumXor: this.best,
            pair: this.bestPair
        };
    }
}


// ============================================================
// 4. EVENT-DRIVEN DICTIONARY SERVICE
// ============================================================

class DictionaryService extends EventEmitter {
    constructor() {
        super();

        this.trie = new RadixTrie();
        this.records = new Map();
    }

    async register(word, category) {
        if (typeof category !== "string" || !category.trim()) {
            throw new TypeError("Category is required.");
        }

        const inserted = this.trie.insert(word, category);

        this.records.set(word, {
            word,
            category,
            updatedAt: new Date().toISOString()
        });

        this.emit(inserted ? "registered" : "updated", {
            word,
            category
        });

        return this.records.get(word);
    }

    async lookup(word) {
        if (!this.trie.search(word)) {
            return null;
        }

        return this.records.get(word) ?? null;
    }

    async suggest(prefix, limit = 10) {
        return this.trie.autocomplete(prefix, limit);
    }

    async remove(word) {
        if (!this.trie.delete(word)) return false;

        this.records.delete(word);

        this.emit("removed", { word });
        return true;
    }
}


// ============================================================
// 5. VALIDATION AND TESTING
// ============================================================

async function main() {
    console.log("\nCOMPRESSED RADIX TRIE");

    const trie = new RadixTrie();

    const words = [
        "application",
        "apply",
        "apple",
        "app",
        "binary",
        "bitwise",
        "bit",
        "database"
    ];

    for (const word of words) {
        trie.insert(word);
    }

    console.log("Exact search:", trie.search("application"));
    console.log("Prefix search:", trie.startsWith("appl"));
    console.log("Autocomplete:", trie.autocomplete("app"));

    console.log("Deletion:", trie.delete("apple"));
    console.log("After deletion:", trie.search("apple"));

    console.log("\nBINARY XOR TRIE");

    const binary = new BinaryTrie(8);

    for (const value of [3n, 10n, 5n, 25n, 2n, 8n]) {
        binary.insert(value);
    }

    const xorResult = binary.query(5n);

    console.log({
        maximumXor: xorResult.xor.toString(),
        matchedValue: xorResult.matched.toString()
    });

    binary.insert(12n);
    binary.insert(12n);

    console.log("Duplicate present:", binary.contains(12n));
    binary.delete(12n);
    console.log("After one deletion:", binary.contains(12n));
    binary.delete(12n);
    console.log("After second deletion:", binary.contains(12n));

    console.log("\nSTREAMING MAXIMUM XOR");

    const stream = new XORStreamProcessor(8);

    stream.on("maximum", event => {
        console.log("New maximum:", {
            xor: event.xor.toString(),
            pair: event.pair.map(String)
        });
    });

    for (const value of [3n, 10n, 5n, 25n, 2n, 8n]) {
        stream.add(value);
    }

    console.log(stream.getReport());

    console.log("\nASYNC DICTIONARY SERVICE");

    const service = new DictionaryService();

    service.on("registered", event => {
        console.log("Registered:", event.word);
    });

    service.on("removed", event => {
        console.log("Removed:", event.word);
    });

    await service.register("postgresql", "database");
    await service.register("postman", "api");
    await service.register("protocol", "networking");
    await service.register("python", "programming");

    console.log("Lookup:", await service.lookup("postgresql"));
    console.log("Suggestions:", await service.suggest("post"));

    await service.remove("postman");

    console.log("\nEDGE CASES");

    try {
        binary.insert(256n);
    } catch (error) {
        console.log("Range validation:", error.message);
    }

    try {
        new BinaryTrie(8).query(1n);
    } catch (error) {
        console.log("Empty query validation:", error.message);
    }

    try {
        trie.insert("");
    } catch (error) {
        console.log("Empty word validation:", error.message);
    }

    console.log("\nPERFORMANCE TEST");

    const benchmark = new BinaryTrie(16);
    const start = performance.now();

    for (let i = 0; i < 10000; i++) {
        benchmark.insert(BigInt((i * 7919) % 65536));
    }

    console.log({
        inserted: benchmark.size,
        elapsedMilliseconds: Number(
            (performance.now() - start).toFixed(3)
        )
    });

    console.log("\nALL OPERATIONS COMPLETED");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
