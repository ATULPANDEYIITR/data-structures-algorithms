"use strict";

/*
 * AVL Trees
 * Event-driven inventory indexing system.
 *
 * Node height convention:
 *   Empty subtree = 0
 *   Leaf node = 1
 *
 * Balance factor = left height - right height.
 *
 * Supports:
 * - Four AVL rotation cases
 * - Insertion and deletion
 * - Search and range queries
 * - Iterators and traversal
 * - EventEmitter-based operation monitoring
 * - Structural validation
 * - JSON persistence
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

class AVLValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "AVLValidationError";
    }
}

class AVLNode {
    constructor(key) {
        this.key = key;
        this.height = 1;
        this.left = null;
        this.right = null;
    }
}

class AVLTree extends EventEmitter {
    constructor() {
        super();

        this.root = null;

        this.statistics = {
            insertions: 0,
            deletions: 0,
            searches: 0,
            duplicates: 0,
            rotations: {
                LL: 0,
                RR: 0,
                LR: 0,
                RL: 0
            }
        };
    }

    static validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new AVLValidationError(
                "Key must be a safe JavaScript integer."
            );
        }
    }

    static height(node) {
        return node ? node.height : 0;
    }

    balanceFactor(node) {
        if (!node) return 0;

        return (
            AVLTree.height(node.left) -
            AVLTree.height(node.right)
        );
    }

    updateHeight(node) {
        node.height = 1 + Math.max(
            AVLTree.height(node.left),
            AVLTree.height(node.right)
        );
    }

    rotateRight(y) {
        const x = y.left;

        if (!x) {
            throw new Error("Invalid right rotation.");
        }

        const transferred = x.right;

        x.right = y;
        y.left = transferred;

        this.updateHeight(y);
        this.updateHeight(x);

        return x;
    }

    rotateLeft(x) {
        const y = x.right;

        if (!y) {
            throw new Error("Invalid left rotation.");
        }

        const transferred = y.left;

        y.left = x;
        x.right = transferred;

        this.updateHeight(x);
        this.updateHeight(y);

        return y;
    }

    rebalance(node) {
        this.updateHeight(node);

        const balance = this.balanceFactor(node);

        if (balance > 1) {
            if (this.balanceFactor(node.left) < 0) {
                this.statistics.rotations.LR++;

                this.emit("rotation", {
                    type: "LR",
                    pivot: node.key
                });

                node.left = this.rotateLeft(node.left);
            } else {
                this.statistics.rotations.LL++;

                this.emit("rotation", {
                    type: "LL",
                    pivot: node.key
                });
            }

            return this.rotateRight(node);
        }

        if (balance < -1) {
            if (this.balanceFactor(node.right) > 0) {
                this.statistics.rotations.RL++;

                this.emit("rotation", {
                    type: "RL",
                    pivot: node.key
                });

                node.right = this.rotateRight(node.right);
            } else {
                this.statistics.rotations.RR++;

                this.emit("rotation", {
                    type: "RR",
                    pivot: node.key
                });
            }

            return this.rotateLeft(node);
        }

        return node;
    }

    insertNode(node, key) {
        if (!node) {
            return new AVLNode(key);
        }

        if (key < node.key) {
            node.left = this.insertNode(node.left, key);
        } else if (key > node.key) {
            node.right = this.insertNode(node.right, key);
        } else {
            return node;
        }

        return this.rebalance(node);
    }

    insert(key) {
        AVLTree.validateKey(key);

        if (this.search(key)) {
            this.statistics.duplicates++;

            this.emit("duplicate", { key });

            return false;
        }

        this.root = this.insertNode(this.root, key);

        this.statistics.insertions++;

        this.emit("insert", {
            key,
            height: this.root.height
        });

        return true;
    }

    search(key) {
        AVLTree.validateKey(key);

        this.statistics.searches++;

        let current = this.root;

        while (current) {
            if (key === current.key) return true;

            current = key < current.key
                ? current.left
                : current.right;
        }

        return false;
    }

    findNode(key) {
        AVLTree.validateKey(key);

        let current = this.root;

        while (current) {
            if (key === current.key) return current;

            current = key < current.key
                ? current.left
                : current.right;
        }

        return null;
    }

    minimumNode(node) {
        while (node.left) {
            node = node.left;
        }

        return node;
    }

    deleteNode(node, key) {
        if (!node) return null;

        if (key < node.key) {
            node.left = this.deleteNode(node.left, key);
        } else if (key > node.key) {
            node.right = this.deleteNode(node.right, key);
        } else {
            if (!node.left) return node.right;
            if (!node.right) return node.left;

            const successor = this.minimumNode(node.right);

            node.key = successor.key;

            node.right = this.deleteNode(
                node.right,
                successor.key
            );
        }

        return this.rebalance(node);
    }

    delete(key) {
        AVLTree.validateKey(key);

        if (!this.search(key)) {
            return false;
        }

        this.root = this.deleteNode(this.root, key);

        this.statistics.deletions++;

        this.emit("delete", { key });

        return true;
    }

    *inOrderIterator() {
        const stack = [];
        let current = this.root;

        while (current || stack.length > 0) {
            while (current) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();

            yield current.key;

            current = current.right;
        }
    }

    inOrder() {
        return [...this.inOrderIterator()];
    }

    preOrder() {
        const result = [];

        const stack = this.root ? [this.root] : [];

        while (stack.length) {
            const node = stack.pop();

            result.push(node.key);

            if (node.right) stack.push(node.right);
            if (node.left) stack.push(node.left);
        }

        return result;
    }

    postOrder() {
        if (!this.root) return [];

        const stack = [[this.root, false]];
        const result = [];

        while (stack.length) {
            const [node, visited] = stack.pop();

            if (visited) {
                result.push(node.key);
                continue;
            }

            stack.push([node, true]);

            if (node.right) {
                stack.push([node.right, false]);
            }

            if (node.left) {
                stack.push([node.left, false]);
            }
        }

        return result;
    }

    levelOrder() {
        if (!this.root) return [];

        const queue = [this.root];
        const result = [];

        let index = 0;

        while (index < queue.length) {
            const levelSize = queue.length - index;
            const level = [];

            for (let i = 0; i < levelSize; i++) {
                const node = queue[index++];

                level.push(node.key);

                if (node.left) queue.push(node.left);
                if (node.right) queue.push(node.right);
            }

            result.push(level);
        }

        return result;
    }

    rangeQuery(lower, upper) {
        AVLTree.validateKey(lower);
        AVLTree.validateKey(upper);

        if (lower > upper) {
            throw new AVLValidationError(
                "Invalid range boundaries."
            );
        }

        const result = [];
        const stack = this.root ? [this.root] : [];

        while (stack.length) {
            const node = stack.pop();

            if (node.key >= lower && node.key <= upper) {
                result.push(node.key);
            }

            if (node.left && node.key > lower) {
                stack.push(node.left);
            }

            if (node.right && node.key < upper) {
                stack.push(node.right);
            }
        }

        return result.sort((a, b) => a - b);
    }

    get height() {
        return AVLTree.height(this.root);
    }

    get size() {
        let count = 0;

        for (const ignored of this.inOrderIterator()) {
            count++;
        }

        return count;
    }

    get minimum() {
        return this.root
            ? this.minimumNode(this.root).key
            : null;
    }

    get maximum() {
        if (!this.root) return null;

        let current = this.root;

        while (current.right) {
            current = current.right;
        }

        return current.key;
    }

    validate() {
        const visited = new Set();

        const inspect = (node, min, max) => {
            if (!node) {
                return {
                    valid: true,
                    height: 0
                };
            }

            if (visited.has(node)) {
                return { valid: false, height: 0 };
            }

            visited.add(node);

            if (
                !Number.isSafeInteger(node.key) ||
                (min !== null && node.key <= min) ||
                (max !== null && node.key >= max)
            ) {
                return { valid: false, height: 0 };
            }

            const left = inspect(node.left, min, node.key);
            const right = inspect(node.right, node.key, max);

            const expectedHeight = 1 + Math.max(
                left.height,
                right.height
            );

            const valid = (
                left.valid &&
                right.valid &&
                node.height === expectedHeight &&
                Math.abs(left.height - right.height) <= 1
            );

            return {
                valid,
                height: expectedHeight
            };
        };

        return inspect(this.root, null, null).valid;
    }

    toJSON() {
        const serialize = (node) => {
            if (!node) return null;

            return {
                key: node.key,
                height: node.height,
                left: serialize(node.left),
                right: serialize(node.right)
            };
        };

        return {
            version: 1,
            root: serialize(this.root)
        };
    }

    static fromJSON(data) {
        if (
            !data ||
            data.version !== 1 ||
            !Object.hasOwn(data, "root")
        ) {
            throw new AVLValidationError(
                "Invalid AVL document."
            );
        }

        const tree = new AVLTree();

        const restore = (item, min, max) => {
            if (item === null) return null;

            if (
                typeof item !== "object" ||
                Array.isArray(item) ||
                !Number.isSafeInteger(item.key)
            ) {
                throw new AVLValidationError(
                    "Invalid node data."
                );
            }

            if (
                (min !== null && item.key <= min) ||
                (max !== null && item.key >= max)
            ) {
                throw new AVLValidationError(
                    "Invalid BST ordering."
                );
            }

            const node = new AVLNode(item.key);

            node.left = restore(item.left, min, item.key);
            node.right = restore(item.right, item.key, max);

            tree.updateHeight(node);

            if (
                item.height !== node.height ||
                Math.abs(tree.balanceFactor(node)) > 1
            ) {
                throw new AVLValidationError(
                    "Invalid height or AVL balance."
                );
            }

            return node;
        };

        tree.root = restore(data.root, null, null);

        if (!tree.validate()) {
            throw new AVLValidationError(
                "Tree integrity validation failed."
            );
        }

        return tree;
    }

    async save(filename) {
        const temporary = `${filename}.tmp`;

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(this.toJSON(), null, 2),
                { encoding: "utf8", flag: "wx" }
            );

            await fs.rename(temporary, filename);
        } catch (error) {
            await fs.rm(temporary, { force: true })
                .catch(() => {});

            throw new Error(
                `Unable to save AVL tree: ${error.message}`
            );
        }
    }

    static async load(filename) {
        try {
            const content = await fs.readFile(
                filename,
                "utf8"
            );

            return AVLTree.fromJSON(JSON.parse(content));
        } catch (error) {
            if (error instanceof AVLValidationError) {
                throw error;
            }

            throw new Error(
                `Unable to load AVL tree: ${error.message}`
            );
        }
    }
}


async function main() {
    const tree = new AVLTree();

    // Event-driven monitoring.
    tree.on("rotation", event => {
        console.log(
            `Rotation: ${event.type}, pivot=${event.pivot}`
        );
    });

    tree.on("insert", event => {
        console.log(`Inserted inventory ID ${event.key}`);
    });

    tree.on("delete", event => {
        console.log(`Deleted inventory ID ${event.key}`);
    });

    tree.on("duplicate", event => {
        console.log(`Duplicate inventory ID: ${event.key}`);
    });

    console.log("\nAVL ROTATION TESTS");

    const cases = {
        LL: [30, 20, 10],
        RR: [10, 20, 30],
        LR: [30, 10, 20],
        RL: [10, 30, 20]
    };

    for (const [name, values] of Object.entries(cases)) {
        const sample = new AVLTree();

        for (const value of values) {
            sample.insert(value);
        }

        console.log(name, {
            root: sample.root.key,
            inorder: sample.inOrder(),
            valid: sample.validate()
        });

        if (sample.root.key !== 20 || !sample.validate()) {
            throw new Error(`${name} rotation test failed.`);
        }
    }

    console.log("\nINVENTORY INDEX");

    const inventory = [
        100, 50, 150, 25, 75,
        125, 175, 10, 35, 60, 90
    ];

    for (const id of inventory) {
        tree.insert(id);
    }

    tree.insert(100);

    console.log("In-order:", tree.inOrder());
    console.log("Pre-order:", tree.preOrder());
    console.log("Post-order:", tree.postOrder());
    console.log("Level-order:", tree.levelOrder());

    console.log("Height:", tree.height);
    console.log("Size:", tree.size);
    console.log("Minimum:", tree.minimum);
    console.log("Maximum:", tree.maximum);

    console.log("Find 125:", tree.search(125));
    console.log("Range 50-150:", tree.rangeQuery(50, 150));

    tree.delete(100);

    console.log("After deletion:", tree.inOrder());
    console.log("Valid:", tree.validate());

    console.log("Statistics:", tree.statistics);

    const filename = "inventory_avl.json";

    await tree.save(filename);

    const restored = await AVLTree.load(filename);

    console.log(
        "Restored tree:",
        restored.inOrder()
    );

    if (!restored.validate()) {
        throw new Error("Persistence validation failed.");
    }

    await fs.rm(filename, { force: true });

    // Invalid input handling.
    try {
        tree.insert(1.5);
    } catch (error) {
        console.log("Validation error:", error.message);
    }

    try {
        tree.rangeQuery(150, 50);
    } catch (error) {
        console.log("Range error:", error.message);
    }

    // Empty-tree behavior.
    const empty = new AVLTree();

    console.log("Empty tree:", {
        height: empty.height,
        size: empty.size,
        minimum: empty.minimum,
        maximum: empty.maximum,
        traversal: empty.inOrder()
    });

    if (!tree.validate()) {
        throw new Error("Final AVL validation failed.");
    }

    console.log("\nAll JavaScript AVL tests passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
