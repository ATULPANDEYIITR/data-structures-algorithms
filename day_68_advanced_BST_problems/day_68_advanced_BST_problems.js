"use strict";

const { EventEmitter } = require("node:events");

class BSTError extends Error {}
class InvalidKeyError extends BSTError {}
class InvalidKError extends BSTError {}

class TreeNode {
    constructor(key) {
        this.key = key;
        this.left = null;
        this.right = null;
    }
}

class ListNode {
    constructor(key) {
        this.key = key;
        this.prev = null;
        this.next = null;
    }
}

class BinarySearchTree extends EventEmitter {
    constructor(values = []) {
        super();
        this.root = null;
        this.size = 0;

        for (const value of values) {
            this.insert(value);
        }
    }

    static validateKey(key) {
        if (!Number.isSafeInteger(key)) {
            throw new InvalidKeyError(
                "BST keys must be safe JavaScript integers."
            );
        }
    }

    get length() {
        return this.size;
    }

    insert(key) {
        BinarySearchTree.validateKey(key);

        if (this.root === null) {
            this.root = new TreeNode(key);
            this.size++;
            this.emit("inserted", { key, size: this.size });
            return true;
        }

        let current = this.root;

        while (true) {
            if (key === current.key) {
                return false;
            }

            const direction = key < current.key ? "left" : "right";

            if (current[direction] === null) {
                current[direction] = new TreeNode(key);
                this.size++;
                this.emit("inserted", { key, size: this.size });
                return true;
            }

            current = current[direction];
        }
    }

    search(key) {
        BinarySearchTree.validateKey(key);

        let current = this.root;

        while (current !== null) {
            if (current.key === key) return true;
            current = key < current.key
                ? current.left
                : current.right;
        }

        return false;
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

            if (node.right) stack.push(node.right);
            if (node.left) stack.push(node.left);
        }

        return result;
    }

    postorder() {
        const result = [];

        const visit = (node) => {
            if (!node) return;
            visit(node.left);
            visit(node.right);
            result.push(node.key);
        };

        visit(this.root);
        return result;
    }

    kthSmallest(k) {
        if (!Number.isSafeInteger(k) || k < 1 || k > this.size) {
            throw new InvalidKError(
                `k must be between 1 and ${this.size}.`
            );
        }

        let current = this.root;
        const stack = [];
        let visited = 0;

        while (current || stack.length) {
            while (current) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();

            if (++visited === k) return current.key;

            current = current.right;
        }

        throw new BSTError("Unexpected traversal failure.");
    }

    kthLargest(k) {
        if (!Number.isSafeInteger(k) || k < 1 || k > this.size) {
            throw new InvalidKError("Invalid k value.");
        }

        let current = this.root;
        const stack = [];
        let visited = 0;

        while (current || stack.length) {
            while (current) {
                stack.push(current);
                current = current.right;
            }

            current = stack.pop();

            if (++visited === k) return current.key;

            current = current.left;
        }

        throw new BSTError("Unexpected traversal failure.");
    }

    lowestCommonAncestor(first, second) {
        BinarySearchTree.validateKey(first);
        BinarySearchTree.validateKey(second);

        if (!this.search(first) || !this.search(second)) {
            throw new BSTError("Both keys must exist in the tree.");
        }

        let current = this.root;

        while (current) {
            if (first < current.key && second < current.key) {
                current = current.left;
            } else if (first > current.key && second > current.key) {
                current = current.right;
            } else {
                return current.key;
            }
        }

        throw new BSTError("LCA not found.");
    }

    delete(key) {
        BinarySearchTree.validateKey(key);

        let deleted = false;

        const remove = (node, target) => {
            if (!node) return null;

            if (target < node.key) {
                node.left = remove(node.left, target);
                return node;
            }

            if (target > node.key) {
                node.right = remove(node.right, target);
                return node;
            }

            deleted = true;

            if (!node.left) return node.right;
            if (!node.right) return node.left;

            let successor = node.right;

            while (successor.left) {
                successor = successor.left;
            }

            node.key = successor.key;
            node.right = removeSuccessor(node.right, successor.key);

            return node;
        };

        const removeSuccessor = (node, target) => {
            if (target < node.key) {
                node.left = removeSuccessor(node.left, target);
            } else if (target > node.key) {
                node.right = removeSuccessor(node.right, target);
            } else {
                return node.right;
            }
            return node;
        };

        this.root = remove(this.root, key);

        if (deleted) {
            this.size--;
            this.emit("deleted", { key, size: this.size });
        }

        return deleted;
    }

    height() {
        if (!this.root) return 0;

        const stack = [[this.root, 1]];
        let maximum = 0;

        while (stack.length) {
            const [node, depth] = stack.pop();
            maximum = Math.max(maximum, depth);

            if (node.left) stack.push([node.left, depth + 1]);
            if (node.right) stack.push([node.right, depth + 1]);
        }

        return maximum;
    }

    isBalanced() {
        const check = (node) => {
            if (!node) return 0;

            const left = check(node.left);
            if (left === -1) return -1;

            const right = check(node.right);
            if (right === -1) return -1;

            if (Math.abs(left - right) > 1) return -1;

            return 1 + Math.max(left, right);
        };

        return check(this.root) !== -1;
    }

    validate() {
        const check = (node, lower, upper) => {
            if (!node) return 0;

            if (lower !== null && node.key <= lower) {
                throw new BSTError("Lower-bound violation.");
            }

            if (upper !== null && node.key >= upper) {
                throw new BSTError("Upper-bound violation.");
            }

            return 1
                + check(node.left, lower, node.key)
                + check(node.right, node.key, upper);
        };

        const count = check(this.root, null, null);

        if (count !== this.size) {
            throw new BSTError("Tree size invariant violated.");
        }

        return true;
    }

    static fromSorted(values) {
        const data = [...values];

        data.forEach(BinarySearchTree.validateKey);

        for (let i = 1; i < data.length; i++) {
            if (data[i - 1] >= data[i]) {
                throw new TypeError(
                    "Input must be strictly increasing."
                );
            }
        }

        const tree = new BinarySearchTree();

        const build = (start, end) => {
            if (start > end) return null;

            const middle = Math.floor((start + end) / 2);
            const node = new TreeNode(data[middle]);

            node.left = build(start, middle - 1);
            node.right = build(middle + 1, end);

            return node;
        };

        tree.root = build(0, data.length - 1);
        tree.size = data.length;

        return tree;
    }

    static fromPreorder(values) {
        const data = [...values];

        data.forEach(BinarySearchTree.validateKey);

        if (new Set(data).size !== data.length) {
            throw new TypeError("Duplicate preorder keys.");
        }

        let index = 0;

        const build = (lower, upper) => {
            if (index >= data.length) return null;

            const value = data[index];

            if (value <= lower || value >= upper) return null;

            index++;

            const node = new TreeNode(value);
            node.left = build(lower, value);
            node.right = build(value, upper);

            return node;
        };

        const tree = new BinarySearchTree();
        tree.root = build(-Infinity, Infinity);

        if (index !== data.length) {
            throw new TypeError("Invalid BST preorder traversal.");
        }

        tree.size = data.length;
        return tree;
    }

    rebalance() {
        const rebuilt = BinarySearchTree.fromSorted(this.inorder());
        this.root = rebuilt.root;
        this.size = rebuilt.size;
        this.emit("rebalanced", this.statistics());
    }

    toDoublyLinkedList() {
        let head = null;
        let tail = null;
        let count = 0;

        const visit = (node) => {
            if (!node) return;

            visit(node.left);

            const linked = new ListNode(node.key);

            if (!head) {
                head = linked;
            } else {
                tail.next = linked;
                linked.prev = tail;
            }

            tail = linked;
            count++;

            visit(node.right);
        };

        visit(this.root);

        return { head, tail, size: count };
    }

    rangeSearch(low, high) {
        BinarySearchTree.validateKey(low);
        BinarySearchTree.validateKey(high);

        if (low > high) throw new RangeError("Invalid range.");

        const result = [];

        const visit = (node) => {
            if (!node) return;

            if (node.key > low) visit(node.left);

            if (node.key >= low && node.key <= high) {
                result.push(node.key);
            }

            if (node.key < high) visit(node.right);
        };

        visit(this.root);
        return result;
    }

    statistics() {
        return {
            size: this.size,
            height: this.height(),
            balanced: this.isBalanced(),
            minimum: this.inorder()[0] ?? null,
            maximum: this.inorder().at(-1) ?? null,
            valid: this.validate()
        };
    }
}

// Simulates a repository-style event-driven asset index.
async function processTreeOperations(tree, operations) {
    const results = [];

    for (const operation of operations) {
        await Promise.resolve();

        switch (operation.type) {
            case "insert":
                results.push(tree.insert(operation.key));
                break;

            case "delete":
                results.push(tree.delete(operation.key));
                break;

            case "search":
                results.push(tree.search(operation.key));
                break;

            case "kth":
                results.push(tree.kthSmallest(operation.k));
                break;

            default:
                throw new TypeError(
                    `Unsupported operation: ${operation.type}`
                );
        }
    }

    return results;
}

async function runTests() {
    const tree = new BinarySearchTree(
        [50, 30, 70, 20, 40, 60, 80]
    );

    const events = [];

    tree.on("inserted", event => events.push(event));
    tree.on("deleted", event => events.push(event));

    console.assert(tree.validate());
    console.assert(
        JSON.stringify(tree.inorder()) ===
        JSON.stringify([20, 30, 40, 50, 60, 70, 80])
    );

    console.assert(tree.kthSmallest(3) === 40);
    console.assert(tree.kthLargest(2) === 70);
    console.assert(tree.lowestCommonAncestor(20, 40) === 30);

    console.assert(tree.insert(90));
    console.assert(!tree.insert(50));
    console.assert(tree.delete(70));
    console.assert(!tree.search(70));

    console.assert(tree.rangeSearch(30, 60).join(",") === "30,40,50,60");

    const linked = tree.toDoublyLinkedList();
    const listValues = [];
    let current = linked.head;

    while (current) {
        listValues.push(current.key);
        current = current.next;
    }

    console.assert(listValues.join(",") === tree.inorder().join(","));

    const balanced = BinarySearchTree.fromSorted(
        Array.from({ length: 31 }, (_, i) => i + 1)
    );

    console.assert(balanced.isBalanced());

    const skewed = new BinarySearchTree(
        Array.from({ length: 100 }, (_, i) => i + 1)
    );

    console.assert(!skewed.isBalanced());

    skewed.rebalance();
    console.assert(skewed.isBalanced());
    console.assert(skewed.validate());

    const reconstructed = BinarySearchTree.fromPreorder(
        [50, 30, 20, 40, 70, 60, 80]
    );

    console.assert(reconstructed.inorder().join(",") ===
        "20,30,40,50,60,70,80");

    const operations = await processTreeOperations(
        new BinarySearchTree([10, 20, 30]),
        [
            { type: "search", key: 20 },
            { type: "insert", key: 40 },
            { type: "kth", k: 3 },
            { type: "delete", key: 10 }
        ]
    );

    console.assert(
        JSON.stringify(operations) ===
        JSON.stringify([true, true, 30, true])
    );

    console.assert(events.length === 2);

    try {
        tree.kthSmallest(0);
        throw new Error("Invalid k was accepted.");
    } catch (error) {
        console.assert(error instanceof InvalidKError);
    }

    try {
        BinarySearchTree.fromSorted([1, 2, 2, 3]);
        throw new Error("Duplicate sorted input was accepted.");
    } catch (error) {
        console.assert(error instanceof TypeError);
    }

    console.log("All JavaScript BST tests passed.");
}

async function main() {
    await runTests();

    const tree = new BinarySearchTree(
        [50, 30, 70, 20, 40, 60, 80]
    );

    console.log("\nADVANCED BST DEMONSTRATION");
    console.log("Inorder:", tree.inorder());
    console.log("Preorder:", tree.preorder());
    console.log("3rd smallest:", tree.kthSmallest(3));
    console.log("2nd largest:", tree.kthLargest(2));
    console.log("LCA:", tree.lowestCommonAncestor(20, 40));
    console.log("Statistics:", tree.statistics());

    const linked = tree.toDoublyLinkedList();
    const values = [];
    let node = linked.head;

    while (node) {
        values.push(node.key);
        node = node.next;
    }

    console.log("Doubly linked list:", values);
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
