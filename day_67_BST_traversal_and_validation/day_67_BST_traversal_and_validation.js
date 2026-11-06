"use strict";

/*
 * BST Traversal and Validation
 *
 * Engineering perspective:
 * - Event-driven tree updates
 * - Version tracking
 * - Iterative traversals
 * - Strict ordering validation
 * - Range and boundary queries
 * - Asynchronous batch processing
 * - Snapshot-based change auditing
 */

const { EventEmitter } = require("node:events");

class BSTError extends Error {}
class DuplicateKeyError extends BSTError {}
class EmptyTreeError extends BSTError {}

class BinarySearchTree extends EventEmitter {
    constructor() {
        super();
        this.root = null;
        this.size = 0;
        this.version = 0;
        this.auditLog = [];
    }

    static validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new TypeError("Keys must be safe integers.");
        }
    }

    _record(action, key) {
        this.version++;

        const event = Object.freeze({
            action,
            key,
            version: this.version,
            timestamp: new Date().toISOString()
        });

        this.auditLog.push(event);
        this.emit("change", event);
    }

    insert(key) {
        BinarySearchTree.validateKey(key);

        if (this.root === null) {
            this.root = { key, left: null, right: null };
            this.size = 1;
            this._record("INSERT", key);
            return;
        }

        let current = this.root;

        while (true) {
            if (key === current.key) {
                throw new DuplicateKeyError(`Duplicate key: ${key}`);
            }

            const side = key < current.key ? "left" : "right";

            if (current[side] === null) {
                current[side] = { key, left: null, right: null };
                this.size++;
                this._record("INSERT", key);
                return;
            }

            current = current[side];
        }
    }

    async insertBatch(keys) {
        if (!Array.isArray(keys)) {
            throw new TypeError("Batch input must be an array.");
        }

        // Validate before applying changes to prevent partial batches.
        for (const key of keys) {
            BinarySearchTree.validateKey(key);
        }

        if (new Set(keys).size !== keys.length) {
            throw new DuplicateKeyError("Batch contains duplicate keys.");
        }

        const existing = new Set(this.inorder());

        if (keys.some(key => existing.has(key))) {
            throw new DuplicateKeyError("Batch conflicts with existing keys.");
        }

        const snapshot = this.inorder();

        try {
            for (const key of keys) {
                this.insert(key);
                await Promise.resolve();
            }
        } catch (error) {
            // Restore the original logical state if an unexpected failure occurs.
            this.root = BinarySearchTree.build(snapshot);
            this.size = snapshot.length;
            this._record("BATCH_ROLLBACK", null);
            throw error;
        }
    }

    search(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;

        while (current !== null) {
            if (key === current.key) return current;
            current = key < current.key ? current.left : current.right;
        }

        return null;
    }

    inorder() {
        const result = [];
        const stack = [];
        let current = this.root;

        while (current || stack.length) {
            while (current) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            result.push(current.key);
            current = current.right;
        }

        return result;
    }

    preorder() {
        if (!this.root) return [];

        const result = [];
        const stack = [this.root];

        while (stack.length) {
            const node = stack.pop();
            result.push(node.key);

            if (node.right) stack.push(node.right);
            if (node.left) stack.push(node.left);
        }

        return result;
    }

    postorder() {
        if (!this.root) return [];

        const result = [];
        const stack = [[this.root, false]];

        while (stack.length) {
            const [node, visited] = stack.pop();

            if (visited) {
                result.push(node.key);
            } else {
                stack.push([node, true]);

                if (node.right) stack.push([node.right, false]);
                if (node.left) stack.push([node.left, false]);
            }
        }

        return result;
    }

    levelOrder() {
        if (!this.root) return [];

        const result = [];
        const queue = [this.root];
        let head = 0;

        while (head < queue.length) {
            const node = queue[head++];
            result.push(node.key);

            if (node.left) queue.push(node.left);
            if (node.right) queue.push(node.right);
        }

        return result;
    }

    minimum() {
        if (!this.root) throw new EmptyTreeError("Tree is empty.");

        let node = this.root;
        while (node.left) node = node.left;

        return node.key;
    }

    maximum() {
        if (!this.root) throw new EmptyTreeError("Tree is empty.");

        let node = this.root;
        while (node.right) node = node.right;

        return node.key;
    }

    floor(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current) {
            if (current.key === key) return key;

            if (current.key < key) {
                candidate = current.key;
                current = current.right;
            } else {
                current = current.left;
            }
        }

        return candidate;
    }

    ceiling(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current) {
            if (current.key === key) return key;

            if (current.key > key) {
                candidate = current.key;
                current = current.left;
            } else {
                current = current.right;
            }
        }

        return candidate;
    }

    rangeQuery(low, high) {
        BinarySearchTree.validateKey(low);
        BinarySearchTree.validateKey(high);

        if (low > high) {
            throw new RangeError("Invalid range.");
        }

        const result = [];
        const stack = [];
        let current = this.root;

        while (current || stack.length) {
            while (current) {
                if (current.key >= low) {
                    stack.push(current);
                    current = current.left;
                } else {
                    current = current.right;
                }
            }

            if (!stack.length) break;

            current = stack.pop();

            if (current.key > high) break;

            result.push(current.key);
            current = current.right;
        }

        return result;
    }

    successor(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current) {
            if (current.key > key) {
                candidate = current.key;
                current = current.left;
            } else {
                current = current.right;
            }
        }

        return candidate;
    }

    predecessor(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current) {
            if (current.key < key) {
                candidate = current.key;
                current = current.right;
            } else {
                current = current.left;
            }
        }

        return candidate;
    }

    delete(key) {
        BinarySearchTree.validateKey(key);

        let deleted = false;

        const remove = (node, target) => {
            if (!node) return null;

            if (target < node.key) {
                node.left = remove(node.left, target);
            } else if (target > node.key) {
                node.right = remove(node.right, target);
            } else {
                deleted = true;

                if (!node.left) return node.right;
                if (!node.right) return node.left;

                let successor = node.right;

                while (successor.left) {
                    successor = successor.left;
                }

                node.key = successor.key;
                node.right = remove(node.right, successor.key);
            }

            return node;
        };

        this.root = remove(this.root, key);

        if (deleted) {
            this.size--;
            this._record("DELETE", key);
        }

        return deleted;
    }

    validate() {
        const visited = new Set();
        const stack = [[this.root, null, null]];
        let count = 0;

        while (stack.length) {
            const [node, lower, upper] = stack.pop();

            if (!node) continue;

            if (visited.has(node)) return false;
            visited.add(node);
            count++;

            if (lower !== null && node.key <= lower) return false;
            if (upper !== null && node.key >= upper) return false;

            stack.push([node.right, node.key, upper]);
            stack.push([node.left, lower, node.key]);
        }

        return count === this.size;
    }

    height() {
        if (!this.root) return 0;

        let maximumDepth = 0;
        const queue = [[this.root, 1]];
        let head = 0;

        while (head < queue.length) {
            const [node, depth] = queue[head++];
            maximumDepth = Math.max(maximumDepth, depth);

            if (node.left) queue.push([node.left, depth + 1]);
            if (node.right) queue.push([node.right, depth + 1]);
        }

        return maximumDepth;
    }

    static build(sortedValues) {
        if (!Array.isArray(sortedValues)) {
            throw new TypeError("Expected an array.");
        }

        for (let i = 0; i < sortedValues.length; i++) {
            BinarySearchTree.validateKey(sortedValues[i]);

            if (i > 0 && sortedValues[i - 1] >= sortedValues[i]) {
                throw new RangeError("Values must be strictly increasing.");
            }
        }

        const tree = new BinarySearchTree();

        const construct = (left, right) => {
            if (left > right) return null;

            const middle = Math.floor((left + right) / 2);

            return {
                key: sortedValues[middle],
                left: construct(left, middle - 1),
                right: construct(middle + 1, right)
            };
        };

        tree.root = construct(0, sortedValues.length - 1);
        tree.size = sortedValues.length;

        return tree;
    }
}

async function main() {
    const tree = new BinarySearchTree();

    tree.on("change", event => {
        console.log(
            `Event ${event.version}: ${event.action} ${event.key ?? ""}`
        );
    });

    await tree.insertBatch([50, 30, 70, 20, 40, 60, 80]);

    console.log("\nTraversal results");
    console.log("Inorder:", tree.inorder());
    console.log("Preorder:", tree.preorder());
    console.log("Postorder:", tree.postorder());
    console.log("Level order:", tree.levelOrder());

    console.log("\nQueries");
    console.log("Minimum:", tree.minimum());
    console.log("Maximum:", tree.maximum());
    console.log("Floor 45:", tree.floor(45));
    console.log("Ceiling 45:", tree.ceiling(45));
    console.log("Range 30-70:", tree.rangeQuery(30, 70));
    console.log("Successor 50:", tree.successor(50));
    console.log("Predecessor 50:", tree.predecessor(50));

    console.log("\nValidation:", tree.validate());
    console.log("Height:", tree.height());

    tree.delete(50);

    console.log("After deletion:", tree.inorder());
    console.log("Valid after deletion:", tree.validate());

    const balanced = BinarySearchTree.build(
        Array.from({ length: 15 }, (_, i) => i + 1)
    );

    console.log("\nBalanced tree height:", balanced.height());
    console.log("Balanced tree valid:", balanced.validate());

    try {
        tree.insert(30);
    } catch (error) {
        console.log("Expected failure:", error.message);
    }

    try {
        await tree.insertBatch([100, 100]);
    } catch (error) {
        console.log("Batch rejected:", error.message);
    }

    console.log("Final audit events:", tree.auditLog.length);

    // Automated verification.
    console.assert(tree.validate());
    console.assert(balanced.height() === 4);
    console.assert(balanced.inorder().length === 15);
    console.assert(tree.floor(15) === null);
    console.assert(tree.ceiling(85) === null);
    console.log("\nAll JavaScript checks completed.");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
