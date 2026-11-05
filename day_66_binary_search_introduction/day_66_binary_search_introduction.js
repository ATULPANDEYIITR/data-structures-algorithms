"use strict";

const { EventEmitter } = require("node:events");

class BSTNode {
    constructor(key) {
        this.key = key;
        this.left = null;
        this.right = null;
    }
}

class BinarySearchTree extends EventEmitter {
    constructor(options = {}) {
        super();

        this.root = null;
        this.size = 0;
        this.operationCount = 0;

        this.maxNodes = options.maxNodes ?? 100000;

        if (!Number.isSafeInteger(this.maxNodes) || this.maxNodes < 0) {
            throw new RangeError("maxNodes must be a non-negative safe integer.");
        }
    }

    static validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new TypeError("BST keys must be safe integers.");
        }
    }

    insert(key) {
        BinarySearchTree.validateKey(key);

        if (this.size >= this.maxNodes) {
            throw new RangeError("BST capacity exceeded.");
        }

        const node = new BSTNode(key);

        if (this.root === null) {
            this.root = node;
            this.size++;
            this._record("insert", key);
            return true;
        }

        let current = this.root;

        while (true) {
            if (key === current.key) {
                this._record("duplicate", key);
                return false;
            }

            const direction = key < current.key ? "left" : "right";

            if (current[direction] === null) {
                current[direction] = node;
                break;
            }

            current = current[direction];
        }

        this.size++;
        this._record("insert", key);
        return true;
    }

    search(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let comparisons = 0;

        while (current !== null) {
            comparisons++;

            if (key === current.key) {
                return {
                    found: true,
                    key: current.key,
                    comparisons
                };
            }

            current = key < current.key
                ? current.left
                : current.right;
        }

        return {
            found: false,
            key,
            comparisons
        };
    }

    minimum(node = this.root) {
        if (node === null) return null;

        while (node.left !== null) {
            node = node.left;
        }

        return node.key;
    }

    maximum(node = this.root) {
        if (node === null) return null;

        while (node.right !== null) {
            node = node.right;
        }

        return node.key;
    }

    predecessor(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current !== null) {
            if (current.key < key) {
                candidate = current.key;
                current = current.right;
            } else {
                current = current.left;
            }
        }

        return candidate;
    }

    successor(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;
        let candidate = null;

        while (current !== null) {
            if (current.key > key) {
                candidate = current.key;
                current = current.left;
            } else {
                current = current.right;
            }
        }

        return candidate;
    }

    delete(key) {
        BinarySearchTree.validateKey(key);

        let parent = null;
        let current = this.root;

        while (current !== null && current.key !== key) {
            parent = current;
            current = key < current.key
                ? current.left
                : current.right;
        }

        if (current === null) {
            this._record("delete-missing", key);
            return false;
        }

        // Replace a two-child node with its inorder successor.
        if (current.left !== null && current.right !== null) {
            let successorParent = current;
            let successorNode = current.right;

            while (successorNode.left !== null) {
                successorParent = successorNode;
                successorNode = successorNode.left;
            }

            current.key = successorNode.key;
            parent = successorParent;
            current = successorNode;
        }

        // The node has at most one child.
        const child = current.left ?? current.right;

        if (parent === null) {
            this.root = child;
        } else if (parent.left === current) {
            parent.left = child;
        } else {
            parent.right = child;
        }

        this.size--;
        this._record("delete", key);
        return true;
    }

    inorder() {
        const result = [];
        const stack = [];
        let current = this.root;

        while (current !== null || stack.length > 0) {
            while (current !== null) {
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
        if (this.root === null) return [];

        const result = [];
        const stack = [this.root];

        while (stack.length > 0) {
            const node = stack.pop();
            result.push(node.key);

            if (node.right !== null) stack.push(node.right);
            if (node.left !== null) stack.push(node.left);
        }

        return result;
    }

    postorder() {
        if (this.root === null) return [];

        const result = [];
        const stack = [[this.root, false]];

        while (stack.length > 0) {
            const [node, visited] = stack.pop();

            if (visited) {
                result.push(node.key);
            } else {
                stack.push([node, true]);

                if (node.right !== null) {
                    stack.push([node.right, false]);
                }

                if (node.left !== null) {
                    stack.push([node.left, false]);
                }
            }
        }

        return result;
    }

    levelOrder() {
        if (this.root === null) return [];

        const result = [];
        const queue = [this.root];

        for (let index = 0; index < queue.length; index++) {
            const node = queue[index];
            result.push(node.key);

            if (node.left !== null) queue.push(node.left);
            if (node.right !== null) queue.push(node.right);
        }

        return result;
    }

    rangeSearch(low, high) {
        BinarySearchTree.validateKey(low);
        BinarySearchTree.validateKey(high);

        if (low > high) {
            throw new RangeError("Invalid range.");
        }

        const result = [];
        const stack = [];
        let current = this.root;

        while (current !== null || stack.length > 0) {
            while (current !== null) {
                if (current.key >= low) {
                    stack.push(current);
                    current = current.left;
                } else {
                    current = current.right;
                }
            }

            if (stack.length === 0) break;

            current = stack.pop();

            if (current.key > high) break;

            result.push(current.key);
            current = current.right;
        }

        return result;
    }

    height() {
        if (this.root === null) return 0;

        const stack = [[this.root, 1]];
        let maximum = 0;

        while (stack.length > 0) {
            const [node, depth] = stack.pop();
            maximum = Math.max(maximum, depth);

            if (node.left !== null) {
                stack.push([node.left, depth + 1]);
            }

            if (node.right !== null) {
                stack.push([node.right, depth + 1]);
            }
        }

        return maximum;
    }

    validate() {
        const stack = this.root === null
            ? []
            : [[this.root, null, null]];

        let count = 0;

        while (stack.length > 0) {
            const [node, lower, upper] = stack.pop();
            count++;

            if (lower !== null && node.key <= lower) return false;
            if (upper !== null && node.key >= upper) return false;

            if (node.left !== null) {
                stack.push([node.left, lower, node.key]);
            }

            if (node.right !== null) {
                stack.push([node.right, node.key, upper]);
            }
        }

        return count === this.size;
    }

    clear() {
        this.root = null;
        this.size = 0;
        this._record("clear", null);
    }

    _record(operation, key) {
        const event = Object.freeze({
            operation,
            key,
            size: this.size,
            sequence: ++this.operationCount,
            timestamp: new Date().toISOString()
        });

        // Consumers can subscribe to operation events.
        this.emit("operation", event);
    }
}

function runTests() {
    const tree = new BinarySearchTree({ maxNodes: 100 });

    const events = [];
    tree.on("operation", event => events.push(event));

    for (const key of [50, 30, 70, 20, 40, 60, 80]) {
        if (!tree.insert(key)) {
            throw new Error("Unexpected insertion failure.");
        }
    }

    console.assert(!tree.insert(50));
    console.assert(tree.search(40).found);
    console.assert(!tree.search(99).found);

    console.assert(
        JSON.stringify(tree.inorder()) ===
        JSON.stringify([20, 30, 40, 50, 60, 70, 80])
    );

    console.assert(tree.minimum() === 20);
    console.assert(tree.maximum() === 80);
    console.assert(tree.predecessor(50) === 40);
    console.assert(tree.successor(50) === 60);
    console.assert(tree.predecessor(10) === null);
    console.assert(tree.successor(100) === null);

    console.assert(
        JSON.stringify(tree.rangeSearch(30, 60)) ===
        JSON.stringify([30, 40, 50, 60])
    );

    console.assert(tree.delete(20));
    console.assert(tree.delete(30));
    console.assert(tree.delete(70));
    console.assert(tree.delete(50));
    console.assert(!tree.delete(999));

    console.assert(tree.validate());
    console.assert(tree.size === 3);

    const empty = new BinarySearchTree();
    console.assert(empty.height() === 0);
    console.assert(empty.minimum() === null);

    try {
        tree.insert(Number.MAX_SAFE_INTEGER + 1);
        throw new Error("Unsafe integer was accepted.");
    } catch (error) {
        if (!(error instanceof TypeError)) throw error;
    }

    console.assert(events.length > 0);

    const limited = new BinarySearchTree({ maxNodes: 1 });
    limited.insert(10);

    try {
        limited.insert(20);
        throw new Error("Capacity limit was ignored.");
    } catch (error) {
        if (!(error instanceof RangeError)) throw error;
    }

    console.log("All JavaScript BST tests passed.");
}

function demonstrate() {
    const tree = new BinarySearchTree();

    tree.on("operation", event => {
        console.log(
            `[${event.sequence}] ${event.operation}:`,
            event.key,
            `size=${event.size}`
        );
    });

    [50, 30, 70, 20, 40, 60, 80].forEach(key => tree.insert(key));

    console.log("\nBINARY SEARCH TREE");
    console.log("Inorder:", tree.inorder());
    console.log("Preorder:", tree.preorder());
    console.log("Postorder:", tree.postorder());
    console.log("Level order:", tree.levelOrder());
    console.log("Search 40:", tree.search(40));
    console.log("Minimum:", tree.minimum());
    console.log("Maximum:", tree.maximum());
    console.log("Predecessor of 50:", tree.predecessor(50));
    console.log("Successor of 50:", tree.successor(50));
    console.log("Height:", tree.height());

    tree.delete(50);

    console.log("After deleting 50:", tree.inorder());
    console.log("Valid BST:", tree.validate());
}

if (require.main === module) {
    runTests();
    demonstrate();
}

module.exports = { BSTNode, BinarySearchTree };
