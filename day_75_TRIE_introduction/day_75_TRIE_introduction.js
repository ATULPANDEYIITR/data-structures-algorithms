"use strict";

/*
 * TRIE INTRODUCTION: EVENT-DRIVEN PREFIX INDEX
 *
 * Node.js 18+
 * Standard library only.
 *
 * Features:
 * - Map-based character transitions
 * - EventEmitter integration
 * - Exact search and prefix lookup
 * - Autocomplete with result limits
 * - Frequency tracking
 * - Safe deletion and pruning
 * - Longest-prefix matching
 * - Batch insertion using asynchronous processing
 * - JSON persistence
 * - Input validation and automated tests
 */

const fs = require("node:fs/promises");
const path = require("node:path");
const EventEmitter = require("node:events");
const assert = require("node:assert/strict");

class TrieError extends Error {}

class InvalidWordError extends TrieError {}

class TrieNode {
    constructor() {
        this.children = new Map();
        this.isEndOfWord = false;
        this.frequency = 0;
    }
}

class Trie extends EventEmitter {
    constructor({ caseSensitive = false } = {}) {
        super();

        this.root = new TrieNode();
        this.caseSensitive = caseSensitive;
        this.wordCount = 0;
        this.totalInsertions = 0;
    }

    normalize(value) {
        if (typeof value !== "string") {
            throw new InvalidWordError("Word must be a string.");
        }

        const word = value.normalize("NFC").trim();

        if (!word) {
            throw new InvalidWordError("Word cannot be empty.");
        }

        const characters = Array.from(word);

        if (characters.length > 256) {
            throw new InvalidWordError("Word exceeds 256 characters.");
        }

        if (/\p{Cc}/u.test(word)) {
            throw new InvalidWordError("Control characters are prohibited.");
        }

        return this.caseSensitive ? word : word.toLowerCase();
    }

    insert(value) {
        const word = this.normalize(value);
        let node = this.root;

        for (const character of word) {
            if (!node.children.has(character)) {
                node.children.set(character, new TrieNode());
            }

            node = node.children.get(character);
        }

        const created = !node.isEndOfWord;

        node.isEndOfWord = true;
        node.frequency++;

        this.totalInsertions++;

        if (created) {
            this.wordCount++;
            this.emit("word:created", {
                word,
                wordCount: this.wordCount
            });
        } else {
            this.emit("word:repeated", {
                word,
                frequency: node.frequency
            });
        }

        return created;
    }

    findNode(value) {
        const text = this.normalize(value);
        let node = this.root;

        for (const character of text) {
            node = node.children.get(character);

            if (!node) {
                return null;
            }
        }

        return node;
    }

    search(value) {
        const node = this.findNode(value);
        return node !== null && node.isEndOfWord;
    }

    startsWith(value) {
        return this.findNode(value) !== null;
    }

    frequency(value) {
        const node = this.findNode(value);

        return node && node.isEndOfWord
            ? node.frequency
            : 0;
    }

    autocomplete(prefix, limit = 10) {
        const normalized = this.normalize(prefix);

        if (
            !Number.isSafeInteger(limit) ||
            limit < 1 ||
            limit > 1000
        ) {
            throw new RangeError("Limit must be between 1 and 1000.");
        }

        const start = this.findNode(normalized);

        if (!start) {
            return [];
        }

        const results = [];
        const stack = [{ node: start, word: normalized }];

        while (stack.length > 0 && results.length < limit) {
            const current = stack.pop();

            if (current.node.isEndOfWord) {
                results.push(current.word);
            }

            const characters = [...current.node.children.keys()].sort();

            for (let i = characters.length - 1; i >= 0; i--) {
                const character = characters[i];

                stack.push({
                    node: current.node.children.get(character),
                    word: current.word + character
                });
            }
        }

        return results;
    }

    delete(value) {
        const word = this.normalize(value);
        const pathNodes = [];
        let node = this.root;

        for (const character of word) {
            const child = node.children.get(character);

            if (!child) {
                return false;
            }

            pathNodes.push({
                parent: node,
                character,
                child
            });

            node = child;
        }

        if (!node.isEndOfWord) {
            return false;
        }

        node.isEndOfWord = false;
        node.frequency = 0;
        this.wordCount--;

        // Remove only nodes that are no longer needed by another word.
        for (let i = pathNodes.length - 1; i >= 0; i--) {
            const entry = pathNodes[i];

            if (
                entry.child.children.size === 0 &&
                !entry.child.isEndOfWord
            ) {
                entry.parent.children.delete(entry.character);
            } else {
                break;
            }
        }

        this.emit("word:deleted", {
            word,
            wordCount: this.wordCount
        });

        return true;
    }

    longestPrefix(value) {
        const text = this.normalize(value);
        let node = this.root;
        let current = "";
        let longest = "";

        for (const character of text) {
            node = node.children.get(character);

            if (!node) {
                break;
            }

            current += character;

            if (node.isEndOfWord) {
                longest = current;
            }
        }

        return longest;
    }

    statistics() {
        let nodes = 0;
        let edges = 0;
        let maximumDepth = 0;
        let terminalNodes = 0;

        const queue = [{ node: this.root, depth: 0 }];

        while (queue.length) {
            const current = queue.shift();

            nodes++;
            maximumDepth = Math.max(
                maximumDepth,
                current.depth
            );

            if (current.node.isEndOfWord) {
                terminalNodes++;
            }

            for (const child of current.node.children.values()) {
                edges++;

                queue.push({
                    node: child,
                    depth: current.depth + 1
                });
            }
        }

        return {
            words: this.wordCount,
            totalInsertions: this.totalInsertions,
            nodes,
            edges,
            terminalNodes,
            maximumDepth
        };
    }

    async insertBatch(words, batchSize = 100) {
        if (!Array.isArray(words)) {
            throw new TypeError("Words must be an array.");
        }

        if (
            !Number.isSafeInteger(batchSize) ||
            batchSize < 1 ||
            batchSize > 10000
        ) {
            throw new RangeError("Invalid batch size.");
        }

        // Validate the entire batch before modifying the index.
        const normalized = words.map(word => this.normalize(word));

        for (let i = 0; i < normalized.length; i += batchSize) {
            const batch = normalized.slice(i, i + batchSize);

            for (const word of batch) {
                this.insert(word);
            }

            // Yield control between batches for event-loop responsiveness.
            if (i + batchSize < normalized.length) {
                await new Promise(resolve => setImmediate(resolve));
            }
        }

        return {
            processed: normalized.length,
            statistics: this.statistics()
        };
    }

    async save(filename) {
        const words = this.autocomplete("", 1000);

        // Large dictionaries are traversed without the autocomplete limit.
        const allWords = this.wordCount <= 1000
            ? words
            : this.collectAllWords();

        const data = {
            version: 1,
            caseSensitive: this.caseSensitive,
            words: allWords.map(word => ({
                word,
                frequency: this.frequency(word)
            }))
        };

        const destination = path.resolve(filename);
        const temporary = destination + ".tmp";

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(data, null, 2),
                { encoding: "utf8", mode: 0o600 }
            );

            await fs.rename(temporary, destination);
        } catch (error) {
            await fs.unlink(temporary).catch(() => {});
            throw new TrieError(`Persistence failed: ${error.message}`);
        }
    }

    collectAllWords() {
        const results = [];
        const stack = [{ node: this.root, word: "" }];

        while (stack.length) {
            const current = stack.pop();

            if (current.node.isEndOfWord) {
                results.push(current.word);
            }

            const characters = [...current.node.children.keys()].sort();

            for (let i = characters.length - 1; i >= 0; i--) {
                const character = characters[i];

                stack.push({
                    node: current.node.children.get(character),
                    word: current.word + character
                });
            }
        }

        return results;
    }

    static async load(filename) {
        let data;

        try {
            data = JSON.parse(
                await fs.readFile(filename, "utf8")
            );
        } catch (error) {
            throw new TrieError(`Unable to load dictionary: ${error.message}`);
        }

        if (
            !data ||
            data.version !== 1 ||
            typeof data.caseSensitive !== "boolean" ||
            !Array.isArray(data.words) ||
            data.words.length > 100000
        ) {
            throw new TrieError("Invalid dictionary file.");
        }

        const trie = new Trie({
            caseSensitive: data.caseSensitive
        });

        for (const record of data.words) {
            if (
                !record ||
                !Number.isSafeInteger(record.frequency) ||
                record.frequency < 1 ||
                record.frequency > 1000000
            ) {
                throw new TrieError("Invalid dictionary frequency.");
            }

            for (let i = 0; i < record.frequency; i++) {
                trie.insert(record.word);
            }
        }

        return trie;
    }
}

async function main() {
    const trie = new Trie();

    // Event-driven monitoring of index changes.
    trie.on("word:created", event => {
        console.log(
            `[EVENT] New word: ${event.word}`
        );
    });

    trie.on("word:deleted", event => {
        console.log(
            `[EVENT] Deleted word: ${event.word}`
        );
    });

    trie.on("word:repeated", event => {
        console.log(
            `[EVENT] Frequency updated: ${event.word} (${event.frequency})`
        );
    });

    console.log("\n1. BATCH INSERTION");

    const words = [
        "apple",
        "application",
        "apply",
        "app",
        "apt",
        "banana",
        "band",
        "batch",
        "bath",
        "car",
        "care",
        "carbon"
    ];

    const result = await trie.insertBatch(words, 4);

    console.log("Batch result:", result.processed);

    console.log("\n2. EXACT SEARCH");

    for (const word of ["apple", "app", "ap", "dog"]) {
        console.log(word, "=>", trie.search(word));
    }

    console.log("\n3. PREFIX MATCHING");

    for (const prefix of ["app", "ba", "car", "xyz"]) {
        console.log(
            prefix,
            "=>",
            trie.startsWith(prefix)
        );
    }

    console.log("\n4. AUTOCOMPLETE");

    console.log("app:", trie.autocomplete("app"));
    console.log("ba:", trie.autocomplete("ba", 3));

    console.log("\n5. DUPLICATE INSERTION");

    trie.insert("band");
    console.log("band frequency:", trie.frequency("band"));

    console.log("\n6. LONGEST PREFIX");

    console.log(
        "application_server:",
        trie.longestPrefix("application_server")
    );

    console.log("\n7. DELETION");

    console.log("Delete app:", trie.delete("app"));
    console.log("Search app:", trie.search("app"));
    console.log("Search apple:", trie.search("apple"));

    console.log("\n8. STATISTICS");

    console.log(trie.statistics());

    console.log("\n9. PERSISTENCE");

    const filename = "javascript_trie.json";

    try {
        await trie.save(filename);

        const restored = await Trie.load(filename);

        console.log(
            "Restored dictionary:",
            restored.autocomplete("app")
        );

        await fs.unlink(filename);
    } catch (error) {
        console.error(error.message);
    }

    console.log("\n10. AUTOMATED TESTS");

    const test = new Trie();

    assert.equal(test.insert("car"), true);
    assert.equal(test.insert("cart"), true);
    assert.equal(test.insert("cat"), true);
    assert.equal(test.insert("car"), false);

    assert.equal(test.search("car"), true);
    assert.equal(test.search("ca"), false);
    assert.equal(test.startsWith("ca"), true);

    assert.deepEqual(
        test.autocomplete("car"),
        ["car", "cart"]
    );

    assert.equal(test.frequency("car"), 2);
    assert.equal(test.delete("car"), true);
    assert.equal(test.search("car"), false);
    assert.equal(test.search("cart"), true);

    assert.equal(test.delete("cart"), true);
    assert.equal(test.startsWith("car"), false);
    assert.equal(test.search("cat"), true);

    await assert.rejects(
        test.insertBatch(["valid", ""]),
        InvalidWordError
    );

    assert.equal(test.search("valid"), false);

    assert.throws(
        () => test.autocomplete("ca", 0),
        RangeError
    );

    console.log("All tests passed.");

    console.log("\n11. PERFORMANCE CHARACTERISTICS");

    console.log("Insertion: O(L) expected");
    console.log("Search: O(L) expected");
    console.log("Prefix lookup: O(P) expected");
    console.log("Autocomplete: O(P + V + output)");
    console.log("Deletion: O(L)");
    console.log("Memory: O(total distinct trie nodes)");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
