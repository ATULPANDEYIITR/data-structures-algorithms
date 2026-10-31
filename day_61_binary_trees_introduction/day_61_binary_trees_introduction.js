"use strict";

class TreeNode {
    constructor(value, left = null, right = null) {
        if (!Number.isInteger(value)) {
            throw new TypeError("Tree node values must be integers.");
        }

        this.value = value;
        this.left = left;
        this.right = right;
    }
}

class BinaryTree {
    constructor(root = null) {
        this.root = root;
        this.listeners = new Map();
    }

    on(eventName, handler) {
        if (typeof handler !== "function") {
            throw new TypeError("Event handler must be a function.");
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        this.listeners.get(eventName).add(handler);
        return () => this.listeners.get(eventName)?.delete(handler);
    }

    emit(eventName, payload) {
        const handlers = this.listeners.get(eventName);
        if (!handlers) {
            return;
        }

        for (const handler of handlers) {
            handler(payload);
        }
    }

    validate() {
        const seen = new Set();

        const visit = (node) => {
            if (node === null) {
                return;
            }

            if (!(node instanceof TreeNode)) {
                throw new TypeError("Invalid tree node.");
            }

            if (seen.has(node)) {
                throw new Error("Cycle detected in binary tree.");
            }

            seen.add(node);
            visit(node.left);
            visit(node.right);
        };

        visit(this.root);
        return true;
    }

    async inspect(target) {
        await Promise.resolve();

        this.validate();

        if (this.root === null) {
            return null;
        }

        const queue = [{ node: this.root, depth: 0, parent: null }];

        while (queue.length > 0) {
            const current = queue.shift();
            const { node, depth, parent } = current;

            if (node.value === target) {
                const children = [node.left, node.right]
                    .filter(Boolean)
                    .map((child) => child.value);

                const result = {
                    value: node.value,
                    parent: parent?.value ?? null,
                    children,
                    degree: children.length,
                    depth,
                    level: depth + 1,
                    leaf: children.length === 0
                };

                this.emit("nodeInspected", result);
                return result;
            }

            if (node.left !== null) {
                queue.push({
                    node: node.left,
                    depth: depth + 1,
                    parent: node
                });
            }

            if (node.right !== null) {
                queue.push({
                    node: node.right,
                    depth: depth + 1,
                    parent: node
                });
            }
        }

        return null;
    }

    async levelOrder() {
        await Promise.resolve();
        this.validate();

        if (this.root === null) {
            return [];
        }

        const result = [];
        const queue = [this.root];

        while (queue.length > 0) {
            const node = queue.shift();
            result.push(node.value);

            if (node.left !== null) {
                queue.push(node.left);
            }

            if (node.right !== null) {
                queue.push(node.right);
            }
        }

        return result;
    }

    async height() {
        await Promise.resolve();
        this.validate();

        const queue = this.root ? [{ node: this.root, depth: 0 }] : [];
        let height = -1;

        while (queue.length > 0) {
            const { node, depth } = queue.shift();
            height = Math.max(height, depth);

            if (node.left !== null) {
                queue.push({ node: node.left, depth: depth + 1 });
            }

            if (node.right !== null) {
                queue.push({ node: node.right, depth: depth + 1 });
            }
        }

        return height;
    }
}

function createRepositoryTree() {
    return new BinaryTree(
        new TreeNode(
            100,
            new TreeNode(
                50,
                new TreeNode(25),
                new TreeNode(75)
            ),
            new TreeNode(
                150,
                new TreeNode(125),
                new TreeNode(
                    175,
                    new TreeNode(160)
                )
            )
        )
    );
}

async function run() {
    const tree = createRepositoryTree();

    tree.on("nodeInspected", (node) => {
        console.log(
            `Inspected ${node.value}: ` +
            `parent=${node.parent}, ` +
            `children=[${node.children.join(", ")}], ` +
            `degree=${node.degree}, ` +
            `depth=${node.depth}, ` +
            `level=${node.level}, ` +
            `leaf=${node.leaf}`
        );
    });

    const values = await tree.levelOrder();
    const height = await tree.height();
    const node = await tree.inspect(175);
    const missing = await tree.inspect(999);

    console.log("Level-order:", values);
    console.log("Height:", height);
    console.log("Node 175:", node);
    console.log("Missing node:", missing);

    if (height !== 3) {
        throw new Error("Unexpected tree height.");
    }

    if (node.depth !== 2 || node.level !== 3) {
        throw new Error("Depth/level calculation failed.");
    }

    if (missing !== null) {
        throw new Error("Missing-node lookup failed.");
    }

    console.log("Validation completed successfully.");
}

run().catch((error) => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
