"use strict";

/*
 * Binary Tree Traversal Engine
 * Preorder, Inorder, Postorder and Level-order.
 * Recursive, iterative, generator-based and asynchronous execution.
 * Compatible with Node.js 18+.
 */

const { EventEmitter } = require("node:events");

class TreeNode {
    constructor(value, left = null, right = null) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Node value must be a safe integer.");
        }

        if (left !== null && !(left instanceof TreeNode)) {
            throw new TypeError("Left child must be a TreeNode or null.");
        }

        if (right !== null && !(right instanceof TreeNode)) {
            throw new TypeError("Right child must be a TreeNode or null.");
        }

        this.value = value;
        this.left = left;
        this.right = right;
    }
}

class TraversalEngine extends EventEmitter {
    constructor(root = null) {
        super();

        if (root !== null && !(root instanceof TreeNode)) {
            throw new TypeError("Root must be a TreeNode or null.");
        }

        this.root = root;
        this.metrics = new Map();
    }

    preorderRecursive() {
        const result = [];

        const visit = (node) => {
            if (!node) return;

            result.push(node.value);
            visit(node.left);
            visit(node.right);
        };

        visit(this.root);
        return result;
    }

    inorderRecursive() {
        const result = [];

        const visit = (node) => {
            if (!node) return;

            visit(node.left);
            result.push(node.value);
            visit(node.right);
        };

        visit(this.root);
        return result;
    }

    postorderRecursive() {
        const result = [];

        const visit = (node) => {
            if (!node) return;

            visit(node.left);
            visit(node.right);
            result.push(node.value);
        };

        visit(this.root);
        return result;
    }

    preorderIterative() {
        if (!this.root) return [];

        const result = [];
        const stack = [this.root];

        while (stack.length) {
            const node = stack.pop();
            result.push(node.value);

            if (node.right) stack.push(node.right);
            if (node.left) stack.push(node.left);
        }

        return result;
    }

    inorderIterative() {
        const result = [];
        const stack = [];
        let current = this.root;

        while (current || stack.length) {
            while (current) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            result.push(current.value);
            current = current.right;
        }

        return result;
    }

    postorderIterative() {
        if (!this.root) return [];

        const result = [];
        const stack = [[this.root, false]];

        while (stack.length) {
            const [node, visited] = stack.pop();

            if (visited) {
                result.push(node.value);
                continue;
            }

            stack.push([node, true]);

            if (node.right) stack.push([node.right, false]);
            if (node.left) stack.push([node.left, false]);
        }

        return result;
    }

    levelOrder() {
        if (!this.root) return [];

        const result = [];
        const queue = [this.root];
        let head = 0;

        // A head index avoids the O(n) cost of repeated Array.shift().
        while (head < queue.length) {
            const node = queue[head++];
            result.push(node.value);

            if (node.left) queue.push(node.left);
            if (node.right) queue.push(node.right);
        }

        return result;
    }

    levelOrderByLevel() {
        if (!this.root) return [];

        const result = [];
        const queue = [this.root];
        let head = 0;

        while (head < queue.length) {
            const levelEnd = queue.length;
            const level = [];

            while (head < levelEnd) {
                const node = queue[head++];
                level.push(node.value);

                if (node.left) queue.push(node.left);
                if (node.right) queue.push(node.right);
            }

            result.push(level);
        }

        return result;
    }

    *preorderGenerator() {
        if (!this.root) return;

        const stack = [this.root];

        while (stack.length) {
            const node = stack.pop();
            yield node.value;

            if (node.right) stack.push(node.right);
            if (node.left) stack.push(node.left);
        }
    }

    *inorderGenerator() {
        const stack = [];
        let current = this.root;

        while (current || stack.length) {
            while (current) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            yield current.value;
            current = current.right;
        }
    }

    *postorderGenerator() {
        if (!this.root) return;

        const stack = [[this.root, false]];

        while (stack.length) {
            const [node, visited] = stack.pop();

            if (visited) {
                yield node.value;
            } else {
                stack.push([node, true]);

                if (node.right) stack.push([node.right, false]);
                if (node.left) stack.push([node.left, false]);
            }
        }
    }

    getTraversal(name, recursive = false) {
        const methods = {
            preorder: recursive
                ? this.preorderRecursive
                : this.preorderIterative,

            inorder: recursive
                ? this.inorderRecursive
                : this.inorderIterative,

            postorder: recursive
                ? this.postorderRecursive
                : this.postorderIterative,

            levelorder: this.levelOrder
        };

        if (!Object.hasOwn(methods, name)) {
            throw new RangeError(`Unknown traversal: ${name}`);
        }

        return methods[name].call(this);
    }

    height() {
        if (!this.root) return 0;

        const queue = [[this.root, 1]];
        let head = 0;
        let maximum = 0;

        while (head < queue.length) {
            const [node, depth] = queue[head++];
            maximum = Math.max(maximum, depth);

            if (node.left) queue.push([node.left, depth + 1]);
            if (node.right) queue.push([node.right, depth + 1]);
        }

        return maximum;
    }

    countNodes() {
        if (!this.root) return 0;

        let count = 0;
        const stack = [this.root];

        while (stack.length) {
            const node = stack.pop();
            count++;

            if (node.left) stack.push(node.left);
            if (node.right) stack.push(node.right);
        }

        return count;
    }

    find(value) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Search value must be a safe integer.");
        }

        const queue = [];
        let head = 0;

        if (this.root) queue.push(this.root);

        while (head < queue.length) {
            const node = queue[head++];

            if (node.value === value) return node;

            if (node.left) queue.push(node.left);
            if (node.right) queue.push(node.right);
        }

        return null;
    }

    async traverseAsync(name, options = {}) {
        const {
            batchSize = 3,
            signal = undefined
        } = options;

        if (!Number.isInteger(batchSize) || batchSize < 1) {
            throw new RangeError("batchSize must be a positive integer.");
        }

        if (signal && signal.aborted) {
            throw new Error("Traversal aborted.");
        }

        const generators = {
            preorder: this.preorderGenerator,
            inorder: this.inorderGenerator,
            postorder: this.postorderGenerator
        };

        if (!Object.hasOwn(generators, name)) {
            throw new RangeError("Asynchronous traversal supports preorder, inorder and postorder.");
        }

        const iterator = generators[name].call(this);
        const result = [];
        let batch = [];

        while (true) {
            if (signal && signal.aborted) {
                throw new Error("Traversal aborted.");
            }

            const item = iterator.next();

            if (item.done) break;

            result.push(item.value);
            batch.push(item.value);

            this.emit("visit", {
                order: name,
                value: item.value
            });

            if (batch.length === batchSize) {
                this.emit("batch", [...batch]);
                batch = [];

                // Yield control to the event loop between batches.
                await new Promise(resolve => setImmediate(resolve));
            }
        }

        if (batch.length) {
            this.emit("batch", [...batch]);
        }

        this.emit("complete", {
            order: name,
            count: result.length
        });

        return result;
    }

    recordMetrics(name, duration, nodeCount) {
        this.metrics.set(name, {
            durationMilliseconds: duration,
            nodesProcessed: nodeCount
        });
    }
}

function buildSampleTree() {
    return new TreeNode(
        50,
        new TreeNode(
            30,
            new TreeNode(20, new TreeNode(10)),
            new TreeNode(40)
        ),
        new TreeNode(
            70,
            new TreeNode(60, null, new TreeNode(65)),
            new TreeNode(80)
        )
    );
}

function runTests(engine) {
    const expected = {
        preorder: [50, 30, 20, 10, 40, 70, 60, 65, 80],
        inorder: [10, 20, 30, 40, 50, 60, 65, 70, 80],
        postorder: [10, 20, 40, 30, 65, 60, 80, 70, 50],
        levelorder: [50, 30, 70, 20, 40, 60, 80, 10, 65]
    };

    for (const [name, values] of Object.entries(expected)) {
        const actual = engine.getTraversal(name);

        if (JSON.stringify(actual) !== JSON.stringify(values)) {
            throw new Error(`Test failed for ${name}`);
        }
    }

    if (JSON.stringify(engine.preorderRecursive()) !==
        JSON.stringify(engine.preorderIterative())) {
        throw new Error("Preorder implementations disagree.");
    }

    if (JSON.stringify(engine.inorderRecursive()) !==
        JSON.stringify(engine.inorderIterative())) {
        throw new Error("Inorder implementations disagree.");
    }

    if (JSON.stringify(engine.postorderRecursive()) !==
        JSON.stringify(engine.postorderIterative())) {
        throw new Error("Postorder implementations disagree.");
    }

    const empty = new TraversalEngine(null);

    if (empty.levelOrder().length !== 0 || empty.height() !== 0) {
        throw new Error("Empty tree test failed.");
    }

    const single = new TraversalEngine(new TreeNode(42));

    if (single.inorderIterative()[0] !== 42) {
        throw new Error("Single-node test failed.");
    }

    if (engine.countNodes() !== 9 || engine.height() !== 4) {
        throw new Error("Tree metrics test failed.");
    }

    if (!engine.find(65) || engine.find(999) !== null) {
        throw new Error("Search test failed.");
    }

    console.log("All synchronous traversal tests passed.");
}

async function main() {
    const engine = new TraversalEngine(buildSampleTree());

    console.log("BINARY TREE TRAVERSAL REPORT");
    console.log("============================");

    for (const order of [
        "preorder",
        "inorder",
        "postorder",
        "levelorder"
    ]) {
        const start = process.hrtime.bigint();
        const result = engine.getTraversal(order);
        const end = process.hrtime.bigint();

        engine.recordMetrics(
            order,
            Number(end - start) / 1_000_000,
            result.length
        );

        console.log(`${order.padEnd(12)}: ${result.join(", ")}`);
    }

    console.log("\nLEVELS");
    console.log(engine.levelOrderByLevel());

    console.log("\nTREE METRICS");
    console.log({
        nodeCount: engine.countNodes(),
        height: engine.height(),
        contains65: engine.find(65) !== null
    });

    console.log("\nASYNC EVENT-DRIVEN TRAVERSAL");

    engine.on("visit", event => {
        console.log(`Visited ${event.value}`);
    });

    engine.on("complete", event => {
        console.log(`Completed ${event.order}: ${event.count} nodes`);
    });

    const asyncResult = await engine.traverseAsync("inorder", {
        batchSize: 3
    });

    console.log("Async result:", asyncResult);

    console.log("\nPERFORMANCE METRICS");
    console.log(Object.fromEntries(engine.metrics));

    runTests(engine);
}

main().catch(error => {
    console.error("Traversal failure:", error.message);
    process.exitCode = 1;
});
