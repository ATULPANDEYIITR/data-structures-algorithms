"use strict";

/*
 * Trie Applications
 * Node.js 18+
 *
 * Features:
 * - Trie insertion, deletion, and exact search
 * - Prefix lookup and autocomplete
 * - Frequency-based ranking
 * - Wildcard dictionary search
 * - Word Break and sentence generation
 * - Word Search II
 * - Asynchronous autocomplete service
 * - Event-driven search notifications
 * - Input validation and unit-style assertions
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");

function normalizeWord(value) {
    if (typeof value !== "string") {
        throw new TypeError("Word must be a string.");
    }

    const word = value.trim().toLowerCase();

    if (!/^[a-z]+$/.test(word)) {
        throw new Error("Word must contain alphabetic characters only.");
    }

    return word;
}

class TrieNode {
    constructor() {
        this.children = new Map();
        this.isEnd = false;
        this.frequency = 0;
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
        this.wordCount = 0;
    }

    insert(value, frequency = 1) {
        const word = normalizeWord(value);

        if (
            !Number.isSafeInteger(frequency) ||
            frequency <= 0
        ) {
            throw new RangeError("Frequency must be a positive safe integer.");
        }

        let node = this.root;

        for (const character of word) {
            if (!node.children.has(character)) {
                node.children.set(character, new TrieNode());
            }

            node = node.children.get(character);
        }

        const isNew = !node.isEnd;

        node.isEnd = true;
        node.frequency += frequency;

        if (!Number.isSafeInteger(node.frequency)) {
            throw new RangeError("Frequency limit exceeded.");
        }

        if (isNew) {
            this.wordCount++;
        }

        return isNew;
    }

    findNode(prefix) {
        let node = this.root;

        for (const character of prefix) {
            node = node.children.get(character);

            if (!node) {
                return null;
            }
        }

        return node;
    }

    search(value) {
        const word = normalizeWord(value);
        const node = this.findNode(word);

        return node !== null && node.isEnd;
    }

    startsWith(value) {
        const prefix = normalizeWord(value);
        return this.findNode(prefix) !== null;
    }

    delete(value) {
        const word = normalizeWord(value);

        const remove = (node, index) => {
            if (index === word.length) {
                if (!node.isEnd) {
                    return { deleted: false, prune: false };
                }

                node.isEnd = false;
                node.frequency = 0;

                return {
                    deleted: true,
                    prune: node.children.size === 0
                };
            }

            const character = word[index];
            const child = node.children.get(character);

            if (!child) {
                return { deleted: false, prune: false };
            }

            const result = remove(child, index + 1);

            if (result.prune) {
                node.children.delete(character);
            }

            return {
                deleted: result.deleted,
                prune: !node.isEnd && node.children.size === 0
            };
        };

        const result = remove(this.root, 0);

        if (result.deleted) {
            this.wordCount--;
        }

        return result.deleted;
    }

    autocomplete(value, limit = 10) {
        const prefix = normalizeWord(value);

        if (!Number.isSafeInteger(limit) || limit < 0) {
            throw new RangeError("Limit must be a nonnegative integer.");
        }

        if (limit === 0) {
            return [];
        }

        const start = this.findNode(prefix);

        if (!start) {
            return [];
        }

        const results = [];
        const stack = [{ node: start, word: prefix }];

        while (stack.length) {
            const { node, word } = stack.pop();

            if (node.isEnd) {
                results.push({
                    word,
                    frequency: node.frequency
                });
            }

            const children = [...node.children.entries()]
                .sort((a, b) => b[0].localeCompare(a[0]));

            for (const [character, child] of children) {
                stack.push({
                    node: child,
                    word: word + character
                });
            }
        }

        results.sort(
            (a, b) =>
                b.frequency - a.frequency ||
                a.word.localeCompare(b.word)
        );

        return results.slice(0, limit);
    }

    wildcardSearch(pattern) {
        if (typeof pattern !== "string") {
            throw new TypeError("Pattern must be a string.");
        }

        pattern = pattern.trim().toLowerCase();

        if (!/^[a-z.*]+$/.test(pattern)) {
            throw new Error("Invalid wildcard pattern.");
        }

        const results = new Set();
        const visited = new Set();

        const dfs = (node, index, current) => {
            const state = `${this.nodeId(node)}:${index}`;

            if (visited.has(state)) {
                return;
            }

            visited.add(state);

            if (index === pattern.length) {
                if (node.isEnd) {
                    results.add(current);
                }

                return;
            }

            const token = pattern[index];

            if (token === ".") {
                for (const [character, child] of node.children) {
                    dfs(child, index + 1, current + character);
                }
            } else if (token === "*") {
                dfs(node, index + 1, current);

                for (const [character, child] of node.children) {
                    dfs(child, index, current + character);
                }
            } else {
                const child = node.children.get(token);

                if (child) {
                    dfs(child, index + 1, current + token);
                }
            }
        };

        dfs(this.root, 0, "");

        return [...results].sort();
    }

    nodeId(node) {
        if (!this._nodeIds) {
            this._nodeIds = new WeakMap();
            this._nextNodeId = 1;
        }

        if (!this._nodeIds.has(node)) {
            this._nodeIds.set(node, this._nextNodeId++);
        }

        return this._nodeIds.get(node);
    }

    allWords() {
        const results = [];
        const stack = [{ node: this.root, word: "" }];

        while (stack.length) {
            const { node, word } = stack.pop();

            if (node.isEnd) {
                results.push({
                    word,
                    frequency: node.frequency
                });
            }

            for (const [character, child] of node.children) {
                stack.push({
                    node: child,
                    word: word + character
                });
            }
        }

        return results.sort((a, b) => a.word.localeCompare(b.word));
    }

    get size() {
        return this.wordCount;
    }

    toJSON() {
        return Object.fromEntries(
            this.allWords().map(({ word, frequency }) => [
                word,
                frequency
            ])
        );
    }

    static fromJSON(data) {
        if (
            data === null ||
            typeof data !== "object" ||
            Array.isArray(data)
        ) {
            throw new TypeError("Dictionary data must be an object.");
        }

        const trie = new Trie();

        for (const [word, frequency] of Object.entries(data)) {
            trie.insert(word, frequency);
        }

        return trie;
    }
}

class WordBreakService {
    constructor(trie) {
        this.trie = trie;
    }

    canSegment(value) {
        if (typeof value !== "string") {
            throw new TypeError("Text must be a string.");
        }

        const text = value.trim().toLowerCase();

        if (text === "") {
            return true;
        }

        if (!/^[a-z]+$/.test(text)) {
            throw new Error("Text must contain alphabetic characters.");
        }

        const dp = new Uint8Array(text.length + 1);
        dp[0] = 1;

        for (let start = 0; start < text.length; start++) {
            if (!dp[start]) {
                continue;
            }

            let node = this.trie.root;

            for (let end = start; end < text.length; end++) {
                node = node.children.get(text[end]);

                if (!node) {
                    break;
                }

                if (node.isEnd) {
                    dp[end + 1] = 1;
                }
            }
        }

        return dp[text.length] === 1;
    }

    sentences(value, maxResults = 100) {
        if (typeof value !== "string") {
            throw new TypeError("Text must be a string.");
        }

        if (!Number.isSafeInteger(maxResults) || maxResults < 0) {
            throw new RangeError("Invalid result limit.");
        }

        const text = value.trim().toLowerCase();

        if (!text) {
            return [];
        }

        if (!/^[a-z]+$/.test(text)) {
            throw new Error("Invalid text.");
        }

        if (maxResults === 0) {
            return [];
        }

        const memo = new Map();

        const solve = (start) => {
            if (start === text.length) {
                return [[]];
            }

            if (memo.has(start)) {
                return memo.get(start);
            }

            const results = [];
            let node = this.trie.root;

            for (let end = start; end < text.length; end++) {
                node = node.children.get(text[end]);

                if (!node) {
                    break;
                }

                if (node.isEnd) {
                    const word = text.slice(start, end + 1);

                    for (const suffix of solve(end + 1)) {
                        results.push([word, ...suffix]);

                        if (results.length >= maxResults) {
                            memo.set(start, results);
                            return results;
                        }
                    }
                }
            }

            memo.set(start, results);
            return results;
        };

        return solve(0)
            .slice(0, maxResults)
            .map(words => words.join(" "));
    }
}

function wordSearchII(board, words) {
    if (!Array.isArray(board)) {
        throw new TypeError("Board must be an array.");
    }

    if (board.length === 0) {
        return [];
    }

    if (!Array.isArray(words)) {
        throw new TypeError("Words must be an array.");
    }

    const columns = board[0].length;

    if (
        columns === 0 ||
        board.some(row => !Array.isArray(row) || row.length !== columns)
    ) {
        throw new Error("Board must be rectangular and nonempty.");
    }

    const grid = board.map(row => row.map(cell => {
        if (typeof cell !== "string" || !/^[a-zA-Z]$/.test(cell)) {
            throw new Error("Each cell must contain one alphabetic character.");
        }

        return cell.toLowerCase();
    }));

    const trie = new Trie();

    for (const word of words) {
        trie.insert(word);
    }

    const found = new Set();
    const rows = grid.length;
    const directions = [
        [1, 0],
        [-1, 0],
        [0, 1],
        [0, -1]
    ];

    function dfs(row, column, node, current) {
        const character = grid[row][column];
        const child = node.children.get(character);

        if (!child) {
            return;
        }

        current += character;

        if (child.isEnd) {
            found.add(current);
            child.isEnd = false;
            trie.wordCount--;
        }

        grid[row][column] = "#";

        for (const [dr, dc] of directions) {
            const nr = row + dr;
            const nc = column + dc;

            if (
                nr >= 0 &&
                nr < rows &&
                nc >= 0 &&
                nc < columns &&
                grid[nr][nc] !== "#"
            ) {
                dfs(nr, nc, child, current);
            }
        }

        grid[row][column] = character;
    }

    for (let row = 0; row < rows; row++) {
        for (let column = 0; column < columns; column++) {
            dfs(row, column, trie.root, "");
        }
    }

    return [...found].sort();
}

class AutocompleteService extends EventEmitter {
    constructor(trie) {
        super();
        this.trie = trie;
        this.requestCount = 0;
    }

    async search(prefix, limit = 10) {
        const requestId = ++this.requestCount;

        try {
            const normalized = normalizeWord(prefix);

            // Yield to the event loop for asynchronous consumers.
            await new Promise(resolve => setImmediate(resolve));

            const suggestions = this.trie.autocomplete(
                normalized,
                limit
            );

            const result = {
                requestId,
                prefix: normalized,
                suggestions
            };

            this.emit("results", result);

            return result;
        } catch (error) {
            this.emit("searchError", {
                requestId,
                error: error.message
            });

            throw error;
        }
    }
}

async function loadDictionary(filePath) {
    const content = await fs.readFile(filePath, "utf8");
    const trie = new Trie();

    for (const line of content.split(/\r?\n/)) {
        const word = line.trim();

        if (!word) {
            continue;
        }

        try {
            trie.insert(word);
        } catch (error) {
            process.stderr.write(
                `Invalid dictionary entry: ${word}: ${error.message}\n`
            );
        }
    }

    return trie;
}

async function saveDictionary(trie, filePath) {
    const content = JSON.stringify(trie.toJSON(), null, 2);

    await fs.writeFile(filePath, content, {
        encoding: "utf8",
        mode: 0o600
    });
}

async function runTests() {
    const trie = new Trie();

    for (const word of [
        "apple",
        "app",
        "application",
        "apply",
        "banana",
        "band",
        "bandana",
        "bat",
        "cat",
        "cats",
        "and",
        "sand",
        "dog"
    ]) {
        trie.insert(word);
    }

    trie.insert("apple", 5);

    assert.equal(trie.search("apple"), true);
    assert.equal(trie.search("appl"), false);
    assert.equal(trie.startsWith("app"), true);
    assert.equal(trie.autocomplete("app", 1)[0].word, "apple");
    assert.equal(trie.autocomplete("app", 0).length, 0);

    assert.equal(trie.delete("app"), true);
    assert.equal(trie.search("app"), false);
    assert.equal(trie.search("apple"), true);

    assert.deepEqual(
        trie.wildcardSearch("app.."),
        ["apple"]
    );

    const dictionary = new Trie();

    for (const word of ["cat", "cats", "and", "sand", "dog"]) {
        dictionary.insert(word);
    }

    const wordBreak = new WordBreakService(dictionary);

    assert.equal(wordBreak.canSegment("catsanddog"), true);
    assert.equal(wordBreak.canSegment("catsandxyz"), false);

    assert.deepEqual(
        wordBreak.sentences("catsanddog"),
        ["cat sand dog", "cats and dog"]
    );

    assert.deepEqual(
        wordSearchII(
            [
                ["o", "a", "a", "n"],
                ["e", "t", "a", "e"],
                ["i", "h", "k", "r"],
                ["i", "f", "l", "v"]
            ],
            ["oath", "pea", "eat", "rain"]
        ),
        ["eat", "oath"]
    );

    assert.throws(() => trie.insert("bad123"));
    assert.throws(() => trie.autocomplete("app", -1));

    const service = new AutocompleteService(trie);

    service.on("results", result => {
        console.log(
            `Event: ${result.suggestions.length} suggestions for ${result.prefix}`
        );
    });

    const response = await service.search("ban", 5);

    assert.equal(response.prefix, "ban");

    const restored = Trie.fromJSON(trie.toJSON());

    assert.equal(restored.search("apple"), true);

    console.log("All JavaScript tests passed.");
}

async function main() {
    console.log("TRIE APPLICATIONS");
    console.log("==============================");

    const trie = new Trie();

    const words = [
        "apple",
        "app",
        "application",
        "apply",
        "apt",
        "banana",
        "band",
        "bandana",
        "bat",
        "ball"
    ];

    for (const word of words) {
        trie.insert(word);
    }

    trie.insert("apple", 10);

    console.log("\nAutocomplete:");
    console.table(trie.autocomplete("app", 5));

    console.log("\nWildcard search:");
    console.log(trie.wildcardSearch("app.."));

    console.log("\nWord Search II:");

    console.log(wordSearchII(
        [
            ["o", "a", "a", "n"],
            ["e", "t", "a", "e"],
            ["i", "h", "k", "r"],
            ["i", "f", "l", "v"]
        ],
        ["oath", "pea", "eat", "rain"]
    ));

    console.log("\nRunning tests...");
    await runTests();
}

if (require.main === module) {
    main().catch(error => {
        console.error("Application failed:", error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    Trie,
    TrieNode,
    WordBreakService,
    AutocompleteService,
    wordSearchII,
    loadDictionary,
    saveDictionary
};
