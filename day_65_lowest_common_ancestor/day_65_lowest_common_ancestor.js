"use strict";

/*
 * Lowest Common Ancestor:
 * Binary-tree traversal, parent-pointer indexing, Euler tour,
 * binary lifting, multiple queries, and ancestor-related operations.
 */

class TreeNode {
    constructor(value) {
        if (!Number.isSafeInteger(value)) {
            throw new TypeError("Node value must be a safe integer.");
        }

        this.value = value;
        this.left = null;
        this.right = null;
        this.parent = null;
    }
}

class BinaryTree {
    constructor(rootValue) {
        this.root = new TreeNode(rootValue);
        this.nodes = new Map([[rootValue, this.root]]);
    }

    addChild(parentValue, childValue, side) {
        const parent = this.getNode(parentValue);

        if (!Number.isSafeInteger(childValue)) {
            throw new TypeError("Child value must be a safe integer.");
        }

        if (this.nodes.has(childValue)) {
            throw new Error("Duplicate node value.");
        }

        if (side !== "left" && side !== "right") {
            throw new Error("Side must be left or right.");
        }

        if (parent[side] !== null) {
            throw new Error(`${side} child already exists.`);
        }

        const child = new TreeNode(childValue);
        child.parent = parent;
        parent[side] = child;

        this.nodes.set(childValue, child);

        return child;
    }

    getNode(value) {
        const node = this.nodes.get(value);

        if (!node) {
            throw new Error(`Node ${value} does not exist.`);
        }

        return node;
    }

    recursiveLCA(p, q) {
        const first = this.nodes.get(p);
        const second = this.nodes.get(q);

        if (!first || !second) {
            return null;
        }

        const search = node => {
            if (!node || node === first || node === second) {
                return node;
            }

            const left = search(node.left);
            const right = search(node.right);

            if (left && right) {
                return node;
            }

            return left || right;
        };

        const result = search(this.root);
        return result ? result.value : null;
    }

    parentLCA(p, q) {
        let first = this.getNode(p);
        let second = this.getNode(q);

        const ancestors = new Set();

        while (first !== null) {
            ancestors.add(first.value);
            first = first.parent;
        }

        while (second !== null) {
            if (ancestors.has(second.value)) {
                return second.value;
            }

            second = second.parent;
        }

        throw new Error("No common ancestor.");
    }

    depth(value) {
        let node = this.getNode(value);
        let depth = 0;

        while (node.parent !== null) {
            depth++;
            node = node.parent;
        }

        return depth;
    }

    depthLCA(p, q) {
        let first = this.getNode(p);
        let second = this.getNode(q);

        let firstDepth = this.depth(p);
        let secondDepth = this.depth(q);

        while (firstDepth > secondDepth) {
            first = first.parent;
            firstDepth--;
        }

        while (secondDepth > firstDepth) {
            second = second.parent;
            secondDepth--;
        }

        while (first !== second) {
            first = first.parent;
            second = second.parent;
        }

        if (first === null) {
            throw new Error("No common ancestor.");
        }

        return first.value;
    }

    isAncestor(ancestor, descendant) {
        let current = this.getNode(descendant);
        const target = this.getNode(ancestor);

        while (current !== null) {
            if (current === target) {
                return true;
            }

            current = current.parent;
        }

        return false;
    }

    distance(p, q) {
        const ancestor = this.getNode(this.parentLCA(p, q));

        const count = node => {
            let distance = 0;

            while (node !== ancestor) {
                node = node.parent;
                distance++;
            }

            return distance;
        };

        return count(this.getNode(p)) + count(this.getNode(q));
    }

    kthAncestor(value, k) {
        if (!Number.isSafeInteger(k) || k < 0) {
            throw new RangeError("k must be a non-negative integer.");
        }

        let current = this.getNode(value);

        while (k > 0 && current !== null) {
            current = current.parent;
            k--;
        }

        return current ? current.value : null;
    }

    buildIndex() {
        return new AncestorIndex(this);
    }
}

class AncestorIndex {
    constructor(tree) {
        this.tree = tree;
        this.depth = new Map();
        this.up = new Map();

        this.n = tree.nodes.size;
        this.levels = Math.max(1, Math.ceil(Math.log2(this.n + 1)));

        // Iterative traversal avoids recursive stack overflow.
        const stack = [[tree.root, 0, null]];

        while (stack.length) {
            const [node, depth, parent] = stack.pop();

            this.depth.set(node.value, depth);

            const ancestors = Array(this.levels).fill(null);
            ancestors[0] = parent;

            this.up.set(node.value, ancestors);

            if (node.right) {
                stack.push([node.right, depth + 1, node.value]);
            }

            if (node.left) {
                stack.push([node.left, depth + 1, node.value]);
            }
        }

        for (let j = 1; j < this.levels; j++) {
            for (const value of tree.nodes.keys()) {
                const previous = this.up.get(value)[j - 1];

                if (previous !== null) {
                    this.up.get(value)[j] =
                        this.up.get(previous)[j - 1];
                }
            }
        }
    }

    kthAncestor(value, k) {
        if (!this.up.has(value)) {
            throw new Error("Unknown node.");
        }

        if (!Number.isSafeInteger(k) || k < 0) {
            throw new RangeError("k must be non-negative.");
        }

        if (k > this.depth.get(value)) {
            return null;
        }

        let current = value;
        let bit = 0;

        while (k > 0) {
            if (k % 2 === 1) {
                current = this.up.get(current)[bit];

                if (current === null) {
                    return null;
                }
            }

            k = Math.floor(k / 2);
            bit++;
        }

        return current;
    }

    lca(p, q) {
        if (!this.up.has(p) || !this.up.has(q)) {
            throw new Error("Both nodes must exist.");
        }

        if (this.depth.get(p) < this.depth.get(q)) {
            [p, q] = [q, p];
        }

        p = this.kthAncestor(p, this.depth.get(p) - this.depth.get(q));

        if (p === q) {
            return p;
        }

        for (let j = this.levels - 1; j >= 0; j--) {
            const a = this.up.get(p)[j];
            const b = this.up.get(q)[j];

            if (a !== b) {
                p = a;
                q = b;
            }
        }

        return this.up.get(p)[0];
    }

    distance(p, q) {
        const ancestor = this.lca(p, q);

        return (
            this.depth.get(p) +
            this.depth.get(q) -
            2 * this.depth.get(ancestor)
        );
    }

    batchLCA(queries) {
        if (!Array.isArray(queries)) {
            throw new TypeError("Queries must be an array.");
        }

        return queries.map(([p, q]) => ({
            p,
            q,
            lca: this.lca(p, q)
        }));
    }
}

class QueryService {
    constructor(index) {
        this.index = index;
        this.cache = new Map();
    }

    execute(p, q) {
        const key = p <= q ? `${p}:${q}` : `${q}:${p}`;

        if (this.cache.has(key)) {
            return {
                lca: this.cache.get(key),
                cached: true
            };
        }

        const result = this.index.lca(p, q);
        this.cache.set(key, result);

        return {
            lca: result,
            cached: false
        };
    }

    clearCache() {
        this.cache.clear();
    }
}

function createSampleTree() {
    const tree = new BinaryTree(1);

    tree.addChild(1, 2, "left");
    tree.addChild(1, 3, "right");

    tree.addChild(2, 4, "left");
    tree.addChild(2, 5, "right");

    tree.addChild(3, 6, "left");
    tree.addChild(3, 7, "right");

    tree.addChild(4, 8, "left");
    tree.addChild(4, 9, "right");

    tree.addChild(5, 10, "left");

    return tree;
}

function runTests() {
    const tree = createSampleTree();
    const index = tree.buildIndex();

    console.assert(tree.recursiveLCA(8, 9) === 4);
    console.assert(tree.recursiveLCA(8, 10) === 2);
    console.assert(tree.recursiveLCA(8, 6) === 1);
    console.assert(tree.recursiveLCA(5, 10) === 5);
    console.assert(tree.recursiveLCA(8, 999) === null);

    console.assert(tree.parentLCA(8, 10) === 2);
    console.assert(tree.depthLCA(8, 6) === 1);

    console.assert(index.lca(8, 10) === 2);
    console.assert(index.lca(8, 6) === 1);
    console.assert(index.kthAncestor(8, 3) === 1);
    console.assert(index.kthAncestor(8, 4) === null);

    console.assert(index.distance(8, 10) === 4);
    console.assert(tree.isAncestor(2, 8));
    console.assert(!tree.isAncestor(3, 8));

    const service = new QueryService(index);

    console.assert(service.execute(8, 10).cached === false);
    console.assert(service.execute(10, 8).cached === true);

    let failed = false;

    try {
        index.lca(8, 999);
    } catch (error) {
        failed = true;
    }

    console.assert(failed);

    console.log("All JavaScript LCA tests passed.");
}

async function main() {
    const tree = createSampleTree();
    const index = tree.buildIndex();
    const service = new QueryService(index);

    console.log("LOWEST COMMON ANCESTOR");

    const queries = [
        [8, 9],
        [8, 10],
        [8, 6],
        [5, 10],
        [2, 8]
    ];

    for (const [p, q] of queries) {
        const result = service.execute(p, q);

        console.log(
            `Nodes ${p}, ${q}: LCA = ${result.lca}, ` +
            `cached = ${result.cached}`
        );
    }

    console.log("Distance 8 to 10:", index.distance(8, 10));
    console.log("3rd ancestor of 8:", index.kthAncestor(8, 3));

    console.log(
        "Batch queries:",
        index.batchLCA([[8, 10], [8, 6], [5, 10]])
    );

    await Promise.resolve();
    runTests();
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
    AncestorIndex,
    QueryService
};
