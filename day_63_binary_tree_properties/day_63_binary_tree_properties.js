'use strict';

/*
 * Binary Tree Properties
 * Node.js standard library only.
 *
 * This implementation treats structural analysis as an event-driven workflow:
 * tree events are emitted while properties are calculated, allowing validation,
 * monitoring, and policy evaluation to remain separate from traversal logic.
 */

const fs = require('node:fs');
const path = require('node:path');
const EventEmitter = require('node:events');

class TreeNode {
    constructor(value, left = null, right = null) {
        if (!Number.isInteger(value)) {
            throw new TypeError('Tree node value must be an integer');
        }
        this.value = value;
        this.left = left;
        this.right = right;
    }

    get isLeaf() {
        return this.left === null && this.right === null;
    }
}

class BinaryTree extends EventEmitter {
    constructor(root = null) {
        super();
        this.root = root;
    }

    static fromLevelOrder(values) {
        if (!Array.isArray(values)) {
            throw new TypeError('Level-order input must be an array');
        }

        if (values.length === 0 || values[0] === null) {
            return new BinaryTree();
        }

        if (!Number.isInteger(values[0])) {
            throw new TypeError('Root must be an integer or null');
        }

        const root = new TreeNode(values[0]);
        const queue = [root];
        let index = 1;

        while (queue.length > 0 && index < values.length) {
            const node = queue.shift();

            if (index < values.length && values[index] !== null) {
                node.left = new TreeNode(values[index]);
                queue.push(node.left);
            }
            index++;

            if (index < values.length && values[index] !== null) {
                node.right = new TreeNode(values[index]);
                queue.push(node.right);
            }
            index++;
        }

        if (index < values.length) {
            throw new Error('Input contains unreachable non-null nodes');
        }

        return new BinaryTree(root);
    }

    validate() {
        if (this.root === null) {
            return;
        }

        const seen = new Set();
        const stack = [this.root];

        while (stack.length) {
            const node = stack.pop();

            if (seen.has(node)) {
                throw new Error('Cycle or repeated node reference detected');
            }
            seen.add(node);

            if (node.left === node || node.right === node) {
                throw new Error('A node cannot reference itself');
            }

            if (node.left) stack.push(node.left);
            if (node.right) stack.push(node.right);
        }
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

    countLeaves() {
        if (!this.root) return 0;

        let count = 0;
        const stack = [this.root];

        while (stack.length) {
            const node = stack.pop();

            if (node.isLeaf) {
                count++;
            } else {
                if (node.left) stack.push(node.left);
                if (node.right) stack.push(node.right);
            }
        }

        return count;
    }

    countInternalNodes() {
        return this.countNodes() - this.countLeaves();
    }

    heightEdges() {
        const visit = node => {
            if (!node) return -1;
            return 1 + Math.max(visit(node.left), visit(node.right));
        };

        return this.root ? visit(this.root) : -1;
    }

    diameterEdges() {
        const visit = node => {
            if (!node) return { height: -1, diameter: 0 };

            const left = visit(node.left);
            const right = visit(node.right);

            const height = 1 + Math.max(left.height, right.height);
            const throughNode = left.height + right.height + 2;
            const diameter = Math.max(
                left.diameter,
                right.diameter,
                throughNode
            );

            return { height, diameter };
        };

        return this.root ? visit(this.root).diameter : 0;
    }

    isBalanced() {
        const check = node => {
            if (!node) return 0;

            const left = check(node.left);
            if (left === -Infinity) return -Infinity;

            const right = check(node.right);
            if (right === -Infinity) return -Infinity;

            if (Math.abs(left - right) > 1) return -Infinity;

            return 1 + Math.max(left, right);
        };

        return check(this.root) !== -Infinity;
    }

    isFull() {
        if (!this.root) return true;

        const stack = [this.root];

        while (stack.length) {
            const node = stack.pop();
            const children = Number(node.left !== null) +
                Number(node.right !== null);

            if (children === 1) return false;

            if (node.left) stack.push(node.left);
            if (node.right) stack.push(node.right);
        }

        return true;
    }

    isComplete() {
        if (!this.root) return true;

        const queue = [this.root];
        let missingChildSeen = false;

        while (queue.length) {
            const node = queue.shift();

            if (node.left) {
                if (missingChildSeen) return false;
                queue.push(node.left);
            } else {
                missingChildSeen = true;
            }

            if (node.right) {
                if (missingChildSeen) return false;
                queue.push(node.right);
            } else {
                missingChildSeen = true;
            }
        }

        return true;
    }

    isPerfect() {
        if (!this.root) return true;

        let expectedDepth = null;
        const stack = [[this.root, 0]];

        while (stack.length) {
            const [node, depth] = stack.pop();
            const hasLeft = node.left !== null;
            const hasRight = node.right !== null;

            if (!hasLeft && !hasRight) {
                if (expectedDepth === null) {
                    expectedDepth = depth;
                } else if (expectedDepth !== depth) {
                    return false;
                }
                continue;
            }

            if (!hasLeft || !hasRight) return false;

            stack.push([node.left, depth + 1]);
            stack.push([node.right, depth + 1]);
        }

        return true;
    }

    traversals() {
        const preorder = [];
        const inorder = [];
        const postorder = [];
        const levelOrder = [];

        const walk = node => {
            if (!node) return;

            this.emit('visit', {
                value: node.value,
                phase: 'preorder'
            });
            preorder.push(node.value);

            walk(node.left);

            inorder.push(node.value);
            this.emit('visit', {
                value: node.value,
                phase: 'inorder'
            });

            walk(node.right);

            postorder.push(node.value);
            this.emit('visit', {
                value: node.value,
                phase: 'postorder'
            });
        };

        walk(this.root);

        if (this.root) {
            const queue = [this.root];
            while (queue.length) {
                const node = queue.shift();
                levelOrder.push(node.value);
                if (node.left) queue.push(node.left);
                if (node.right) queue.push(node.right);
            }
        }

        return { preorder, inorder, postorder, levelOrder };
    }

    profile() {
        this.validate();

        const nodes = this.countNodes();
        const leaves = this.countLeaves();
        const internal = nodes - leaves;
        const height = this.heightEdges();

        const result = {
            nodes,
            leaves,
            internalNodes: internal,
            heightEdges: height,
            heightNodes: nodes === 0 ? 0 : height + 1,
            diameterEdges: this.diameterEdges(),
            balanced: this.isBalanced(),
            full: this.isFull(),
            complete: this.isComplete(),
            perfect: this.isPerfect(),
            leafInternalIdentityHolds:
                nodes > 0 && this.isFull() ? leaves === internal + 1 : null
        };

        this.emit('profile', result);
        return result;
    }
}

class GovernancePolicy {
    constructor({ maxHeight, requireBalanced, requireComplete }) {
        this.maxHeight = maxHeight;
        this.requireBalanced = requireBalanced;
        this.requireComplete = requireComplete;
    }

    evaluate(profile) {
        const violations = [];

        if (profile.heightEdges > this.maxHeight) {
            violations.push(`height ${profile.heightEdges} exceeds ${this.maxHeight}`);
        }

        if (this.requireBalanced && !profile.balanced) {
            violations.push('tree is not balanced');
        }

        if (this.requireComplete && !profile.complete) {
            violations.push('tree is not complete');
        }

        return {
            eligible: violations.length === 0,
            violations
        };
    }
}

async function persistProfile(profile, filename = 'binary_tree_profile.json') {
    const target = path.resolve(process.cwd(), filename);
    const cwd = path.resolve(process.cwd());

    if (path.dirname(target) !== cwd) {
        throw new Error('Output file must remain in the current working directory');
    }

    await fs.promises.writeFile(
        target,
        JSON.stringify(profile, null, 2),
        { encoding: 'utf8', mode: 0o600 }
    );
}

function runTests() {
    const tree = BinaryTree.fromLevelOrder([10, 5, 15, 2, 7, 12, 20]);

    const events = [];
    tree.on('visit', event => events.push(event));
    tree.on('profile', profile => {
        if (profile.nodes !== 7) {
            throw new Error('Unexpected node count');
        }
    });

    const profile = tree.profile();

    if (profile.leaves !== 4) throw new Error('Leaf count failed');
    if (profile.internalNodes !== 3) throw new Error('Internal count failed');
    if (profile.heightEdges !== 2) throw new Error('Height failed');
    if (profile.diameterEdges !== 4) throw new Error('Diameter failed');
    if (!profile.balanced || !profile.complete || !profile.perfect) {
        throw new Error('Structural classification failed');
    }

    const chain = BinaryTree.fromLevelOrder([1, 2, null, 3, null, 4]);
    if (chain.isBalanced()) throw new Error('Chain should be unbalanced');
    if (chain.diameterEdges() !== 3) throw new Error('Chain diameter failed');

    const policy = new GovernancePolicy({
        maxHeight: 3,
        requireBalanced: true,
        requireComplete: true
    });

    const decision = policy.evaluate(profile);
    if (!decision.eligible) throw new Error('Balanced tree should pass policy');

    const single = BinaryTree.fromLevelOrder([42]);
    if (single.countLeaves() !== 1 || single.heightEdges() !== 0) {
        throw new Error('Single-node edge case failed');
    }

    return { profile, events, decision };
}

async function main() {
    const result = runTests();

    console.log('Binary Tree Structural Analysis');
    console.log('================================');
    console.log(JSON.stringify(result.profile, null, 2));
    console.log('Traversal events:', result.events.length);
    console.log('Policy decision:', JSON.stringify(result.decision, null, 2));

    await persistProfile(result.profile);
    console.log('Profile written to binary_tree_profile.json');
    console.log('Validation: all assertions passed.');
}

main().catch(error => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
