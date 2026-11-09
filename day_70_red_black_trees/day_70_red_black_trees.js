"use strict";

/*
 * Red-Black Tree: Event-Driven Ordered Index
 *
 * Features:
 * - Generic numeric-key ordered index
 * - Rotations and insertion balancing
 * - Deletion and deletion balancing
 * - Promise-based serialized updates
 * - Event-driven mutation notifications
 * - Range queries and ordered traversal
 * - Structural validation
 * - Concurrent-request safety through a mutation queue
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");

const RED = "RED";
const BLACK = "BLACK";

class TreeNode {
    constructor(key, color, nil) {
        this.key = key;
        this.color = color;
        this.left = nil;
        this.right = nil;
        this.parent = nil;
    }
}

class RedBlackTree extends EventEmitter {
    constructor() {
        super();

        this.nil = {};
        this.nil.key = null;
        this.nil.color = BLACK;
        this.nil.left = this.nil;
        this.nil.right = this.nil;
        this.nil.parent = this.nil;

        this.root = this.nil;
        this.size = 0;

        // Mutations are serialized to prevent overlapping state changes.
        this.mutationQueue = Promise.resolve();
    }

    validateKey(key) {
        if (
            typeof key !== "number" ||
            !Number.isFinite(key)
        ) {
            throw new TypeError("Tree keys must be finite numbers");
        }
    }

    search(key) {
        this.validateKey(key);

        let current = this.root;

        while (current !== this.nil) {
            if (key === current.key) return current;

            current = key < current.key
                ? current.left
                : current.right;
        }

        return null;
    }

    leftRotate(x) {
        const y = x.right;

        if (y === this.nil) {
            throw new Error("Invalid left rotation");
        }

        x.right = y.left;

        if (y.left !== this.nil) {
            y.left.parent = x;
        }

        y.parent = x.parent;

        if (x.parent === this.nil) {
            this.root = y;
        } else if (x === x.parent.left) {
            x.parent.left = y;
        } else {
            x.parent.right = y;
        }

        y.left = x;
        x.parent = y;
    }

    rightRotate(y) {
        const x = y.left;

        if (x === this.nil) {
            throw new Error("Invalid right rotation");
        }

        y.left = x.right;

        if (x.right !== this.nil) {
            x.right.parent = y;
        }

        x.parent = y.parent;

        if (y.parent === this.nil) {
            this.root = x;
        } else if (y === y.parent.right) {
            y.parent.right = x;
        } else {
            y.parent.left = x;
        }

        x.right = y;
        y.parent = x;
    }

    insert(key) {
        this.validateKey(key);

        let parent = this.nil;
        let current = this.root;

        while (current !== this.nil) {
            parent = current;

            if (key === current.key) {
                return false;
            }

            current = key < current.key
                ? current.left
                : current.right;
        }

        const node = new TreeNode(key, RED, this.nil);
        node.parent = parent;

        if (parent === this.nil) {
            this.root = node;
        } else if (key < parent.key) {
            parent.left = node;
        } else {
            parent.right = node;
        }

        this.size++;
        this.insertFixup(node);

        return true;
    }

    insertFixup(z) {
        while (z.parent.color === RED) {
            if (z.parent === z.parent.parent.left) {
                let uncle = z.parent.parent.right;

                if (uncle.color === RED) {
                    z.parent.color = BLACK;
                    uncle.color = BLACK;
                    z.parent.parent.color = RED;
                    z = z.parent;
                } else {
                    if (z === z.parent.right) {
                        z = z.parent;
                        this.leftRotate(z);
                    }

                    z.parent.color = BLACK;
                    z.parent.parent.color = RED;
                    this.rightRotate(z.parent.parent);
                }
            } else {
                let uncle = z.parent.parent.left;

                if (uncle.color === RED) {
                    z.parent.color = BLACK;
                    uncle.color = BLACK;
                    z.parent.parent.color = RED;
                    z = z.parent;
                } else {
                    if (z === z.parent.left) {
                        z = z.parent;
                        this.rightRotate(z);
                    }

                    z.parent.color = BLACK;
                    z.parent.parent.color = RED;
                    this.leftRotate(z.parent.parent);
                }
            }
        }

        this.root.color = BLACK;
        this.root.parent = this.nil;
    }

    minimum(node) {
        while (node.left !== this.nil) {
            node = node.left;
        }
        return node;
    }

    transplant(u, v) {
        if (u.parent === this.nil) {
            this.root = v;
        } else if (u === u.parent.left) {
            u.parent.left = v;
        } else {
            u.parent.right = v;
        }

        v.parent = u.parent;
    }

    delete(key) {
        const z = this.search(key);

        if (!z) return false;

        let y = z;
        let originalColor = y.color;
        let x;

        if (z.left === this.nil) {
            x = z.right;
            this.transplant(z, z.right);
        } else if (z.right === this.nil) {
            x = z.left;
            this.transplant(z, z.left);
        } else {
            y = this.minimum(z.right);
            originalColor = y.color;
            x = y.right;

            if (y.parent === z) {
                x.parent = y;
            } else {
                this.transplant(y, y.right);
                y.right = z.right;
                y.right.parent = y;
            }

            this.transplant(z, y);
            y.left = z.left;
            y.left.parent = y;
            y.color = z.color;
        }

        this.size--;

        if (originalColor === BLACK) {
            this.deleteFixup(x);
        }

        this.nil.color = BLACK;

        if (this.root !== this.nil) {
            this.root.parent = this.nil;
        }

        return true;
    }

    deleteFixup(x) {
        while (x !== this.root && x.color === BLACK) {
            if (x === x.parent.left) {
                let sibling = x.parent.right;

                if (sibling.color === RED) {
                    sibling.color = BLACK;
                    x.parent.color = RED;
                    this.leftRotate(x.parent);
                    sibling = x.parent.right;
                }

                if (
                    sibling.left.color === BLACK &&
                    sibling.right.color === BLACK
                ) {
                    sibling.color = RED;
                    x = x.parent;
                } else {
                    if (sibling.right.color === BLACK) {
                        sibling.left.color = BLACK;
                        sibling.color = RED;
                        this.rightRotate(sibling);
                        sibling = x.parent.right;
                    }

                    sibling.color = x.parent.color;
                    x.parent.color = BLACK;
                    sibling.right.color = BLACK;
                    this.leftRotate(x.parent);
                    x = this.root;
                }
            } else {
                let sibling = x.parent.left;

                if (sibling.color === RED) {
                    sibling.color = BLACK;
                    x.parent.color = RED;
                    this.rightRotate(x.parent);
                    sibling = x.parent.left;
                }

                if (
                    sibling.right.color === BLACK &&
                    sibling.left.color === BLACK
                ) {
                    sibling.color = RED;
                    x = x.parent;
                } else {
                    if (sibling.left.color === BLACK) {
                        sibling.right.color = BLACK;
                        sibling.color = RED;
                        this.leftRotate(sibling);
                        sibling = x.parent.left;
                    }

                    sibling.color = x.parent.color;
                    x.parent.color = BLACK;
                    sibling.left.color = BLACK;
                    this.rightRotate(x.parent);
                    x = this.root;
                }
            }
        }

        x.color = BLACK;
    }

    // Every write enters the same Promise chain.
    enqueueMutation(operation, key) {
        const task = this.mutationQueue.then(() => {
            let changed;

            if (operation === "insert") {
                changed = this.insert(key);
            } else if (operation === "delete") {
                changed = this.delete(key);
            } else {
                throw new Error("Unsupported mutation");
            }

            if (changed) {
                const event = Object.freeze({
                    operation,
                    key,
                    size: this.size,
                    timestamp: new Date().toISOString()
                });

                this.emit("mutation", event);
            }

            return changed;
        });

        // A failed operation must not permanently poison the queue.
        this.mutationQueue = task.catch(() => undefined);

        return task;
    }

    inorder() {
        const result = [];
        const stack = [];
        let current = this.root;

        while (current !== this.nil || stack.length > 0) {
            while (current !== this.nil) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            result.push(current.key);
            current = current.right;
        }

        return result;
    }

    rangeQuery(low, high) {
        this.validateKey(low);
        this.validateKey(high);

        if (low > high) {
            throw new RangeError("Invalid range");
        }

        const result = [];

        const visit = node => {
            if (node === this.nil) return;

            if (node.key > low) visit(node.left);

            if (node.key >= low && node.key <= high) {
                result.push(node.key);
            }

            if (node.key < high) visit(node.right);
        };

        visit(this.root);
        return result;
    }

    validate() {
        if (this.nil.color !== BLACK) {
            throw new Error("Sentinel is not black");
        }

        if (this.root === this.nil) {
            if (this.size !== 0) {
                throw new Error("Invalid empty-tree size");
            }
            return true;
        }

        if (this.root.color !== BLACK) {
            throw new Error("Root is not black");
        }

        if (this.root.parent !== this.nil) {
            throw new Error("Invalid root parent");
        }

        let count = 0;

        const inspect = (node, lower, upper, parent) => {
            if (node === this.nil) return 1;

            count++;

            if (node.parent !== parent) {
                throw new Error("Invalid parent pointer");
            }

            if (lower !== null && node.key <= lower) {
                throw new Error("BST ordering violation");
            }

            if (upper !== null && node.key >= upper) {
                throw new Error("BST ordering violation");
            }

            if (node.color === RED) {
                if (
                    node.left.color === RED ||
                    node.right.color === RED
                ) {
                    throw new Error("Adjacent red nodes");
                }
            }

            const leftHeight = inspect(
                node.left, lower, node.key, node
            );

            const rightHeight = inspect(
                node.right, node.key, upper, node
            );

            if (leftHeight !== rightHeight) {
                throw new Error("Black-height violation");
            }

            return leftHeight + (node.color === BLACK ? 1 : 0);
        };

        inspect(this.root, null, null, this.nil);

        if (count !== this.size) {
            throw new Error("Incorrect node count");
        }

        return true;
    }

    getStatistics() {
        let red = 0;
        let black = 0;

        const visit = node => {
            if (node === this.nil) return 0;

            if (node.color === RED) red++;
            else black++;

            return 1 + Math.max(
                visit(node.left),
                visit(node.right)
            );
        };

        const height = visit(this.root);

        return Object.freeze({
            size: this.size,
            height,
            redNodes: red,
            blackNodes: black,
            maximumHeightBound: this.size === 0
                ? 0
                : 2 * Math.ceil(Math.log2(this.size + 1))
        });
    }
}

async function main() {
    const tree = new RedBlackTree();

    const events = [];

    tree.on("mutation", event => {
        events.push(event);
        console.log(
            `[EVENT] ${event.operation} ${event.key}; size=${event.size}`
        );
    });

    console.log("SERIALIZED INSERTIONS");

    await Promise.all(
        [50, 30, 70, 20, 40, 60, 80, 35, 45, 65].map(
            key => tree.enqueueMutation("insert", key)
        )
    );

    tree.validate();

    console.log("\nORDERED INDEX:", tree.inorder());
    console.log("RANGE 30-65:", tree.rangeQuery(30, 65));
    console.log("STATISTICS:", tree.getStatistics());

    console.log("\nDUPLICATE INSERTION:");
    console.log(await tree.enqueueMutation("insert", 50));

    console.log("\nDELETIONS:");

    await Promise.all(
        [20, 30, 50, 999].map(
            key => tree.enqueueMutation("delete", key)
        )
    );

    tree.validate();

    console.log("\nFINAL INDEX:", tree.inorder());
    console.log("FINAL STATISTICS:", tree.getStatistics());
    console.log("RECORDED EVENTS:", events.length);

    // Verify failed inputs do not corrupt the existing tree.
    try {
        tree.insert(Infinity);
    } catch (error) {
        console.log("EXPECTED VALIDATION ERROR:", error.message);
    }

    tree.validate();
    console.log("All structural checks passed.");
}

if (require.main === module) {
    main().catch(error => {
        console.error("Execution failed:", error);
        process.exitCode = 1;
    });
}

module.exports = { RedBlackTree };
