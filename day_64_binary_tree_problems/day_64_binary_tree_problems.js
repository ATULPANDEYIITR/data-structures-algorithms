"use strict";

const { EventEmitter } = require("node:events");

class TreeNode {
    constructor(value, left = null, right = null) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Node values must be safe integers.");
        }

        this.value = value;
        this.left = left;
        this.right = right;
    }
}

class BinaryTree {
    constructor(root = null) {
        this.root = root;
    }

    static fromLevelOrder(values) {
        if (!Array.isArray(values)) {
            throw new TypeError("Level-order input must be an array.");
        }

        if (values.length === 0) {
            return new BinaryTree();
        }

        if (values[0] === null) {
            if (values.slice(1).some(value => value !== null)) {
                throw new RangeError("A non-empty tree must have a root.");
            }
            return new BinaryTree();
        }

        const root = new TreeNode(values[0]);
        const queue = [root];
        let head = 0;
        let index = 1;

        while (head < queue.length && index < values.length) {
            const parent = queue[head++];

            const leftValue = values[index++];
            if (leftValue !== null && leftValue !== undefined) {
                parent.left = new TreeNode(leftValue);
                queue.push(parent.left);
            }

            if (index < values.length) {
                const rightValue = values[index++];
                if (rightValue !== null && rightValue !== undefined) {
                    parent.right = new TreeNode(rightValue);
                    queue.push(parent.right);
                }
            }
        }

        if (values.slice(index).some(value => value !== null)) {
            throw new RangeError("Input contains nodes with no available parent.");
        }

        return new BinaryTree(root);
    }

    validate() {
        if (this.root === null) {
            return 0;
        }

        const stack = [this.root];
        const visited = new Set();

        while (stack.length > 0) {
            const node = stack.pop();

            if (!(node instanceof TreeNode)) {
                throw new TypeError("Every child must be a TreeNode or null.");
            }

            if (visited.has(node)) {
                throw new Error("Cycle or shared child detected.");
            }

            visited.add(node);

            if (!Number.isSafeInteger(node.value)) {
                throw new TypeError("Node values must be safe integers.");
            }

            if (node.right !== null) {
                stack.push(node.right);
            }
            if (node.left !== null) {
                stack.push(node.left);
            }
        }

        return visited.size;
    }

    maxDepth() {
        this.validate();

        if (this.root === null) {
            return 0;
        }

        const queue = [[this.root, 1]];
        let head = 0;
        let maximum = 0;

        while (head < queue.length) {
            const [node, depth] = queue[head++];
            maximum = Math.max(maximum, depth);

            if (node.left !== null) {
                queue.push([node.left, depth + 1]);
            }
            if (node.right !== null) {
                queue.push([node.right, depth + 1]);
            }
        }

        return maximum;
    }

    minDepth() {
        this.validate();

        if (this.root === null) {
            return 0;
        }

        const queue = [[this.root, 1]];
        let head = 0;

        while (head < queue.length) {
            const [node, depth] = queue[head++];

            if (node.left === null && node.right === null) {
                return depth;
            }

            if (node.left !== null) {
                queue.push([node.left, depth + 1]);
            }
            if (node.right !== null) {
                queue.push([node.right, depth + 1]);
            }
        }

        return 0;
    }

    hasPathSum(targetSum) {
        this.validate();

        let target;
        try {
            target = BigInt(targetSum);
        } catch {
            throw new TypeError("The target sum must be an integer.");
        }

        if (
            typeof targetSum === "number" &&
            !Number.isSafeInteger(targetSum)
        ) {
            throw new TypeError("Numeric target sums must be safe integers.");
        }

        if (this.root === null) {
            return false;
        }

        const stack = [[this.root, 0n]];

        while (stack.length > 0) {
            const [node, accumulated] = stack.pop();
            const current = accumulated + BigInt(node.value);

            if (node.left === null && node.right === null) {
                if (current === target) {
                    return true;
                }
                continue;
            }

            if (node.right !== null) {
                stack.push([node.right, current]);
            }
            if (node.left !== null) {
                stack.push([node.left, current]);
            }
        }

        return false;
    }

    analyze(targetSum) {
        this.validate();

        if (this.root === null) {
            return Object.freeze({
                maxDepth: 0,
                minDepth: 0,
                hasPathSum: false,
                diameterEdges: 0,
                balanced: true,
                nodeCount: 0
            });
        }

        // Postorder statistics are stored by object identity.
        const stats = new Map();
        const stack = [[this.root, false]];

        while (stack.length > 0) {
            const [node, expanded] = stack.pop();

            if (!expanded) {
                stack.push([node, true]);

                if (node.right !== null) {
                    stack.push([node.right, false]);
                }
                if (node.left !== null) {
                    stack.push([node.left, false]);
                }
                continue;
            }

            const left = stats.get(node.left) || {
                height: 0,
                minDepth: 0,
                diameter: 0,
                balanced: true,
                count: 0
            };

            const right = stats.get(node.right) || {
                height: 0,
                minDepth: 0,
                diameter: 0,
                balanced: true,
                count: 0
            };

            const height = 1 + Math.max(left.height, right.height);

            let minimum;
            if (node.left === null && node.right === null) {
                minimum = 1;
            } else if (node.left === null) {
                minimum = 1 + right.minDepth;
            } else if (node.right === null) {
                minimum = 1 + left.minDepth;
            } else {
                minimum = 1 + Math.min(left.minDepth, right.minDepth);
            }

            const diameter = Math.max(
                left.height + right.height,
                left.diameter,
                right.diameter
            );

            stats.set(node, {
                height,
                minDepth: minimum,
                diameter,
                balanced:
                    left.balanced &&
                    right.balanced &&
                    Math.abs(left.height - right.height) <= 1,
                count: 1 + left.count + right.count
            });
        }

        const rootStats = stats.get(this.root);

        return Object.freeze({
            maxDepth: rootStats.height,
            minDepth: rootStats.minDepth,
            hasPathSum: this.hasPathSum(targetSum),
            diameterEdges: rootStats.diameter,
            balanced: rootStats.balanced,
            nodeCount: rootStats.count
        });
    }

    countNodes() {
        return this.validate();
    }

    isComplete() {
        this.validate();

        if (this.root === null) {
            return true;
        }

        const queue = [this.root];
        let head = 0;
        let missingChildSeen = false;

        while (head < queue.length) {
            const node = queue[head++];

            for (const child of [node.left, node.right]) {
                if (child === null) {
                    missingChildSeen = true;
                } else {
                    if (missingChildSeen) {
                        return false;
                    }
                    queue.push(child);
                }
            }
        }

        return true;
    }

    static leftmostHeight(node) {
        let height = 0;

        while (node !== null) {
            height++;
            node = node.left;
        }

        return height;
    }

    countCompleteNodes(verify = true) {
        this.validate();

        if (this.root === null) {
            return 0n;
        }

        if (verify && !this.isComplete()) {
            throw new Error("Optimized counting requires a complete binary tree.");
        }

        let total = 0n;
        let current = this.root;

        while (current !== null) {
            const leftHeight = BinaryTree.leftmostHeight(current.left);
            const rightHeight = BinaryTree.leftmostHeight(current.right);

            if (leftHeight === rightHeight) {
                total += 1n << BigInt(leftHeight);
                current = current.right;
            } else {
                total += 1n << BigInt(rightHeight);
                current = current.left;
            }
        }

        return total;
    }
}

class TreeAnalysisService extends EventEmitter {
    /**
     * Execute analysis asynchronously and publish its result.
     *
     * Consumers can listen for "analysis" and "analysisError" events.
     * Promise rejection is retained so callers cannot accidentally
     * treat a failed analysis as a successful result.
     */
    analyzeAsync(tree, targetSum) {
        if (!(tree instanceof BinaryTree)) {
            return Promise.reject(new TypeError("A BinaryTree instance is required."));
        }

        return new Promise((resolve, reject) => {
            setImmediate(() => {
                try {
                    const result = tree.analyze(targetSum);
                    this.emit("analysis", result);
                    resolve(result);
                } catch (error) {
                    this.emit("analysisError", error);
                    reject(error);
                }
            });
        });
    }
}

async function runTests() {
    const balanced = BinaryTree.fromLevelOrder([
        10, 5, 15, 3, 7, 12, 18
    ]);

    const metrics = balanced.analyze(22);

    console.assert(metrics.maxDepth === 3);
    console.assert(metrics.minDepth === 3);
    console.assert(metrics.hasPathSum === true);
    console.assert(metrics.diameterEdges === 4);
    console.assert(metrics.balanced === true);
    console.assert(metrics.nodeCount === 7);
    console.assert(balanced.isComplete());
    console.assert(balanced.countCompleteNodes() === 7n);

    const skewed = BinaryTree.fromLevelOrder([
        5, 4, null, 3, null, 2
    ]);

    console.assert(skewed.maxDepth() === 4);
    console.assert(skewed.minDepth() === 4);
    console.assert(skewed.analyze(14).diameterEdges === 3);
    console.assert(skewed.analyze(14).balanced === false);
    console.assert(skewed.isComplete() === false);

    const oneChild = new BinaryTree(new TreeNode(1, new TreeNode(2)));
    console.assert(oneChild.minDepth() === 2);

    const empty = new BinaryTree();
    console.assert(empty.maxDepth() === 0);
    console.assert(empty.minDepth() === 0);
    console.assert(empty.countNodes() === 0);
    console.assert(empty.analyze(0).balanced === true);

    const negative = BinaryTree.fromLevelOrder([-2, -3, -4]);
    console.assert(negative.hasPathSum(-5));

    let rejectedIncompleteTree = false;
    try {
        skewed.countCompleteNodes();
    } catch (error) {
        rejectedIncompleteTree = error instanceof Error;
    }
    console.assert(rejectedIncompleteTree);

    let rejectedMalformedInput = false;
    try {
        BinaryTree.fromLevelOrder([null, 1]);
    } catch (error) {
        rejectedMalformedInput = error instanceof Error;
    }
    console.assert(rejectedMalformedInput);

    const shared = new TreeNode(9);
    const invalid = new BinaryTree(
        new TreeNode(1, new TreeNode(2, shared), new TreeNode(3, shared))
    );

    let rejectedSharedNode = false;
    try {
        invalid.validate();
    } catch (error) {
        rejectedSharedNode = true;
    }
    console.assert(rejectedSharedNode);

    const service = new TreeAnalysisService();

    service.on("analysis", result => {
        console.log("Analysis event received:", result);
    });

    const asyncResult = await service.analyzeAsync(balanced, 22);
    console.assert(asyncResult.hasPathSum === true);

    console.log("All JavaScript binary tree tests passed.");
}

async function main() {
    await runTests();

    const tree = BinaryTree.fromLevelOrder([
        10, 5, 15, 3, 7, 12, 18
    ]);

    const metrics = tree.analyze(22);

    console.log("\nBinary Tree Analysis");
    console.log(JSON.stringify(metrics, null, 2));
    console.log("Complete tree:", tree.isComplete());
    console.log("Complete-tree node count:", tree.countCompleteNodes().toString());
}

if (require.main === module) {
    main().catch(error => {
        console.error("Execution failed:", error.message);
        process.exitCode = 1;
    });
}

module.exports = {
    TreeNode,
    BinaryTree,
    TreeAnalysisService
};
